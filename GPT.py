import pdb
from datetime import datetime
import datetime as dt
from statistics import mean
import ipdb
import numpy as np
import pandas as pd
import pvlib
import pytz
import requests
from geopy import Nominatim
from matplotlib import pyplot as plt
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
import matplotlib.dates as mdates
import time as t

from timezonefinder import TimezoneFinder


def get_location():
    latitude = 56.652163
    longitude = -2.907930
    timezone = "Europe/London"
    location = Location(latitude, longitude, timezone)
    return location


def set_up_system():
    # find module and inverter through the database
    sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
    cec_inverters = pvlib.pvsystem.retrieve_sam('CECinverter')

    # for modules in sandia_modules.columns.tolist():
    #     print(modules)

    module = sandia_modules['SunPower_SPR_315E_WHT__2007__E__']
    inverter = cec_inverters['SMA_America__SB2000HFUS_30__240V_']

    temperature_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

    # modules_per_string number of modules connected in series with a string
    # strings_per_inverter is the number of strings connected in parallel to an inverter
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
    # The system rapresents the PV system and the location the physical location of our system on the planet
    modelchain = ModelChain(system, location, clearsky_model='ineichen')
    return modelchain


def set_up_timerange(location, start, end):
    # create the time for which I want the weather information
    time_range = pd.date_range(start=start,
                               end=end,
                               freq='1h',
                               tz=location.tz)
    return time_range


def set_up_clearsky(location, time_range):
    # retrieve weather information about the time range
    clear_sky = location.get_clearsky(time_range)
    return clear_sky


def main():
    location = get_location()
    system = set_up_system()
    modelchain = set_up_modelchain(system, location)
    energy, list = calculate_actual_solar_energy(dt.datetime(2023, 8, 17, 0), dt.datetime(2023, 8, 18, 0), modelchain)
    # ghi = global horizontal irradiance which is the total irradiance
    # dni = direct normal irradiance which is the energy that directly hits the module we created
    # dhi = defuse horizontal irradiance which is the energy reflected from the clouds that hits the module
    # ac means the energy yield in watts behind the inverter(alternating current side)

    # modelchain.run_model(set_up_clearsky(modelchain.location,set_up_timerange(modelchain.location,dt.datetime(2023, 10, 5, 0), dt.datetime(2023, 10, 6, 0))))
    # modelchain.results.ac.plot(figsize=(16, 9))
    # plt.show()
    # energy = modelchain.results.ac.sum()

    plot_graph(list, dt.datetime(2023, 5, 24, 0))
    return energy


def calculate_actual_solar_energy(initial_date, final_date, modelchain):
    hour_difference = int(calculate_difference_between_times(initial_date, final_date))
    if check_days_difference(initial_date, modelchain.location) >= -2 and check_days_difference(initial_date, modelchain.location) < 0:
        list_of_cloudiness = callToWeatherAPIFuture(initial_date)
    else:
        list_of_cloudiness = callToWeatherAPIPast(initial_date, final_date)

    if list_of_cloudiness == None:
        return 0

    if final_date.day == initial_date.day:
        final_date = replace_hour(final_date, addHours(initial_date, 1).hour)
    else:
        final_date = replace_day(final_date, initial_date.day)
        final_date = replace_hour(final_date, addHours(initial_date, 1).hour)

    energy = 0
    time_range = set_up_timerange(modelchain.location, initial_date, final_date)
    clear_sky = set_up_clearsky(modelchain.location, time_range)
    modelchain.run_model(clear_sky)
    cloud_cover = (1 - (get_dissipation_value(list_of_cloudiness[0]) / 100))
    energy += modelchain.results.ac.values[0] * cloud_cover
    list_of_cloudiness.pop(0)

    list = []
    list.append(modelchain.results.ac.values[0])
    initial_date = addHours(initial_date, 1)
    final_date = addHours(final_date, 1)
    for i in range(hour_difference - 1):
        time_range = set_up_timerange(modelchain.location, initial_date, final_date)
        clear_sky = set_up_clearsky(modelchain.location, time_range)
        modelchain.run_model(clear_sky)
        cloud_cover = (1 - (get_dissipation_value(list_of_cloudiness[i]) / 100))
        energy += modelchain.results.ac.values[0] * cloud_cover
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


# def callToWeatherAPI(initial_date: datetime, final_date: datetime):
#     location = get_location()
#     inital_date_utc = convert_to_utc(initial_date, location.tz)
#     final_date_utc = convert_to_utc(final_date, location.tz)
#     initial_time = str(inital_date_utc).replace(' ', ':')[:-6]
#     final_time = str(final_date_utc).replace(' ', ':')[:-6]
#     latitude = str(location.latitude)
#     longitude = str(location.longitude)
#     url = 'https://api.weatherbit.io/v2.0/history/hourly?lat='+latitude+'&lon='+longitude+'&' \
#           'start_date='+initial_time+'&end_date='+final_time+'&tz=utc&key=692afbc7b1184804b4598a5998ddf629'
#     #ipdb.set_trace()
#     # url = 'https://api.weatherbit.io/v2.0/history/hourly?lat=56.64482956171486&lon=-2.888728934975756&' \
#     #        'start_date=2023-05-12:00&end_date=2023-05-13:00&tz=local&key=692afbc7b1184804b4598a5998ddf629'
#     response = requests.get(url)
#
#     if response.status_code == 200:
#         data = response.json()
#         list_of_cloudiness = []
#         for entry in data['data']:
#             clouds = entry['clouds']
#             list_of_cloudiness.append(clouds)
#         return list_of_cloudiness
#     else:
#         print('Error:', response.status_code)


def callToWeatherAPIPast(initial_date: datetime, final_date: datetime):
    location = get_location()
    inital_time = str(int(convert_to_unix_time(initial_date, location)))
    final_time = str(int(convert_to_unix_time(final_date, location)))
    latitude = str(round(location.latitude, 5))
    longitude = str(round(location.longitude, 5))
    url = 'https://history.openweathermap.org/data/2.5/history/city?lat=' + latitude + '&lon=' + longitude \
          + '&type=hour&start=' + inital_time + '&end=' + final_time + '&appid=eb1b77df1c8a2ea0a4b2b4aea35e80e5'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        list_of_cloudiness = []
        for data_point in data['list']:
            list_of_cloudiness.append(data_point['clouds']['all'])
        return list_of_cloudiness
    else:
        print('Error:', response.status_code)

def callToWeatherAPIFuture(desired_local_start_time):
    location = get_location()
    latitude = str(round(location.latitude, 5))
    longitude = str(round(location.longitude, 5))
    url = "https://pro.openweathermap.org/data/2.5/forecast/hourly?lat="+ latitude +"&lon="+longitude+"&appid=eb1b77df1c8a2ea0a4b2b4aea35e80e5"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        unix_times = [entry['dt'] for entry in data['list']]
        desidered_time = unix_times[0]
        for time in unix_times:
            time_in_utc = unix_timestamp_to_utc(time)
            time_localized = convert_utc_to_timezone(time_in_utc, calculateTimezoneFromLocation(location))
            if(time_localized.day == desired_local_start_time.day and time_localized.hour == desired_local_start_time.hour):
                desidered_time = time

        clouds_info = []
        for entry in data['list']:
            if entry['dt'] >= desidered_time:
                clouds_info.append(entry['clouds']['all'])

            if len(clouds_info) >= 24:
                break

        return clouds_info

    else:
        print('Error:', response.status_code)

def convert_to_unix_time(date: datetime, location):
    tz = location.tz
    current_timezone = pytz.timezone(tz)
    utc_time = current_timezone.localize(date).astimezone(pytz.utc)
    unix_time = utc_time.timestamp()
    return unix_time


def replace_hour(dateToChange: datetime, hourToSwap):
    dateToReturn = dateToChange.replace(hour=hourToSwap)
    return dateToReturn


def replace_day(dateToChange: datetime, dayToSwap):
    dateToReturn = dateToChange.replace(day=dayToSwap)
    return dateToReturn


def addHours(input_date: datetime, hours):
    new_date = input_date + dt.timedelta(hours=hours)
    return new_date


def get_dissipation_value(cloudiness):
    value = (25 * cloudiness) / 100
    return value


def convert_to_utc(dt, timezone_str):
    # Get the time zone object corresponding to the given timezone_str
    timezone = pytz.timezone(timezone_str)

    # Localize the input datetime to the specified timezone
    localized_datetime = timezone.localize(dt)

    # Convert the localized datetime to UTC, but keep the hour value unchanged
    utc_datetime = localized_datetime.astimezone(pytz.UTC).replace(tzinfo=None)

    return utc_datetime


def plot_graph(energy_values, start_date):
    # plot the list of values
    plt.plot(energy_values,
             color='green',  # set the color to green
             marker='o',  # use circle markers
             linewidth=2)  # set the line width to 2

    # add labels and title
    plt.xlabel('Hour')  # set the x-axis label
    plt.ylabel('Energy (kWh)')  # set the y-axis label
    plt.title('Energy Production during: ' + str(start_date))  # set the title
    plt.xticks(np.arange(0, 24, 1))

    # show the plot
    plt.show()
    return None


def calculate_optimal_time(list_of_consumption, list_of_production):
    indexes_of_remaining_energy = list()
    for startHour in range(0, 23):
        production_after_consumption = [x for x in list_of_production]
        for i in range(0, len(list_of_consumption), 6):
            production_after_consumption[int(i / 6) + startHour] -= mean(list_of_consumption[i:i + 6])
        indexes_of_remaining_energy.append(sum(production_after_consumption))


def check_if_date_is_today(date, location):
    input_datetime = date.replace(tzinfo=pytz.UTC)
    desired_timezone = pytz.timezone(location.tz)
    input_datetime_in_timezone = input_datetime.astimezone(desired_timezone)

    today = datetime.now(desired_timezone).date()

    return input_datetime_in_timezone.date() == today


def check_days_difference(date, location):
    input_datetime = date.replace(tzinfo=pytz.UTC)
    desired_timezone = pytz.timezone(location.tz)
    input_datetime_in_timezone = input_datetime.astimezone(desired_timezone)

    current_datetime = datetime.now(desired_timezone)

    difference = current_datetime.date() - input_datetime_in_timezone.date()
    return difference.days

def unix_timestamp_to_utc(unix_timestamp):
    utc_datetime = dt.datetime.utcfromtimestamp(unix_timestamp)
    return utc_datetime


def convert_utc_to_timezone(utc_datetime, target_timezone):
    utc_timezone = pytz.timezone('UTC')
    target_timezone = pytz.timezone(target_timezone)
    localized_datetime = utc_datetime.replace(tzinfo=utc_timezone).astimezone(target_timezone)

    return localized_datetime


def calculateTimezoneFromLocation(location):
    timezone = TimezoneFinder().timezone_at(lat=location.latitude, lng=location.longitude)
    return timezone


def calculateLatitude(location):
    geolocator = Nominatim(user_agent="Myapp")
    location_info = geolocator.geocode(location)
    return location_info.latitude


def calculateLongitude(location):
    geolocator = Nominatim(user_agent="Myapp")
    location_info = geolocator.geocode(location)
    return location_info.longitude