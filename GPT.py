from datetime import datetime
import datetime as dt
import pandas as pd
import pvlib
import requests
from matplotlib import pyplot as plt
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS


def get_location():
    latitude = 56.652163
    longitude = -2.907930
    timezone = "Europe/London"
    location = Location(latitude, longitude, timezone)
    return location


def set_up_system():
    #find module and inverter through the database
    sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
    cec_inverters = pvlib.pvsystem.retrieve_sam('CECinverter')

    # for modules in sandia_modules.columns.tolist():
    #     print(modules)

    module = sandia_modules['SunPower_SPR_315E_WHT__2007__E__']
    inverter = cec_inverters['SMA_America__SB2000HFUS_30__240V_']


    temperature_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

    #modules_per_string number of modules connected in series with a string
    #strings_per_inverter is the number of strings connected in parallel to an inverter
    surface_tilt = 40
    surface_azimuth = 90
    system = PVSystem(surface_tilt=surface_tilt,
                      surface_azimuth=surface_azimuth,
                      module_parameters=module,
                      inverter_parameters=inverter,
                      temperature_model_parameters=temperature_parameters,
                      modules_per_string=6,
                      strings_per_inverter=1)
    return system


def set_up_modelchain(system, location):
    #The system rapresents the PV system and the location the physical location of our system on the planet
    modelchain = ModelChain(system, location, clearsky_model='ineichen')
    return modelchain


def set_up_timerange(location, start, end):
    #create the time for which I want the weather information
    time_range = pd.date_range(start=start,
                         end=end,
                         freq='1h',
                         tz=location.tz)
    return time_range


def set_up_clearsky(location, time_range):
    #retrieve weather information about the time range
    clear_sky = location.get_clearsky(time_range)
    return clear_sky


def main():
    location = get_location()
    system = set_up_system()
    modelchain = set_up_modelchain(system, location)
    energy, list = calculate_actual_solar_energy(dt.datetime(2023, 5, 24, 0), dt.datetime(2023, 5, 25, 0), modelchain)
    # ghi = global horizontal irradiance which is the total irradiance
    # dni = direct normal irradiance which is the energy that directly hits the module we created
    # dhi = defuse horizontal irradiance which is the energy reflected from the clouds that hits the module
    # ac means the energy yield in watts behind the inverter(alternating current side)

    #modelchain.run_model(set_up_clearsky(modelchain.location,set_up_timerange(modelchain.location,dt.datetime(2022, 5, 24, 0), dt.datetime(2022, 5, 25, 0))))
    # modelchain.results.ac.plot(figsize=(16, 9))
    # plt.show()
    # 11184.0971737474
    #energy = modelchain.results.ac.sum()
    return energy, list, len(list)


def calculate_actual_solar_energy(initial_date, final_date, modelchain):
    hour_difference = int(calculate_difference_between_times(initial_date, final_date))
    if final_date.day == initial_date.day:
        final_date = replace_hour(final_date, addHours(initial_date, 1).hour)
    else:
        final_date = replace_day(final_date, initial_date.day)
        final_date = replace_hour(final_date, addHours(initial_date, 1).hour)
    energy = 0
    time_range = set_up_timerange(modelchain.location, initial_date, final_date)
    clear_sky = set_up_clearsky(modelchain.location, time_range)
    modelchain.run_model(clear_sky)
    energy += modelchain.results.ac.values[0]
    list = []
    list.append(modelchain.results.ac.values[0])
    initial_date = addHours(initial_date, 1)
    final_date = addHours(final_date, 1)
    for i in range(hour_difference):
        time_range = set_up_timerange(modelchain.location, initial_date, final_date)
        clear_sky = set_up_clearsky(modelchain.location, time_range)
        modelchain.run_model(clear_sky)
        energy += modelchain.results.ac.values[0]
        list.append(modelchain.results.ac.values[0])
        initial_date = addHours(initial_date, 1)
        final_date = addHours(final_date, 1)
    return energy, list


def calculate_difference_between_times(datetime1, datetime2):
    diff = datetime2 - datetime1
    hours = diff.total_seconds() / 3600
    return hours

# def calculate_difference_between_times(initial_date: datetime, final_date: datetime):
#     initial_hour = initial_date.hour
#     final_hour = final_date.hour
#     hour_difference = final_hour - initial_hour
#     return hour_difference


def callToWeatherAPI(initial_date: datetime, final_date: datetime):
    location = get_location()
    inital_time = str(initial_date)
    final_time = str(final_date)
    latitude = str(location.latitude)
    longitude = str(location.longitude)
    url = 'https://api.weatherbit.io/v2.0/history/hourly?lat=56.64482956171486&lon=-2.888728934975756&start_date=2023-05-24:01&end_date=2023-05-25:01&tz=local&key=692afbc7b1184804b4598a5998ddf629'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        list_of_cloudiness = []
        for entry in data['data']:
            clouds = entry['clouds']
            list_of_cloudiness.append(clouds)
        return list_of_cloudiness
    else:
        print('Error:', response.status_code)

def replace_hour(dateToChange: datetime, hourToSwap):
    dateToReturn = dateToChange.replace(hour=hourToSwap)
    return dateToReturn


def replace_day(dateToChange: datetime, dayToSwap):
    dateToReturn = dateToChange.replace(day=dayToSwap)
    return dateToReturn


def addHours(input_date: datetime, hours):
    new_date = input_date + dt.timedelta(hours=hours)
    return new_date