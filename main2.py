import math
import datetime as dt
from datetime import datetime, date, timedelta
import ephem
import requests
from timezonefinder import TimezoneFinder
import pytz
import scipy.integrate as integrate
from geopy import Nominatim


# def calculateUTC(timezone, date: datetime):
# def calculate_unixTS(date: datetime):
# unix_timestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
import test


def calculate_sun_position(date):
    JD = date.toordinal() + 1721424.5
    T = (JD - 2451545.0) / 36525
    L = 280.460 + 36000.771 * T
    G = 357.528 + 35999.050 * T
    e = 0.016708634 - 0.000042037 * T
    C = math.sin(math.radians(G)) * (1.914602 - T * (0.004817 + 0.000014 * T)) + \
        math.sin(math.radians(2 * G)) * (0.019993 - 0.000101 * T) + \
        math.sin(math.radians(3 * G)) * 0.000289
    lam = L + C
    v = G + C
    R = 1.000001018 * (1 - e * e) / (1 + e * math.cos(math.radians(v)))
    lam_apparent = lam - 0.00569 - 0.00478 * math.sin(math.radians(125.04 - 1934.136 * T))
    epsilon = 23.439 - 0.00000036 * T
    alpha = math.atan2(math.cos(math.radians(epsilon)) * math.sin(math.radians(lam_apparent)),
                       math.cos(math.radians(lam_apparent)))
    alpha = math.degrees(alpha)
    delta = math.asin(math.sin(math.radians(epsilon)) * math.sin(math.radians(lam_apparent)))
    delta = math.degrees(delta)

    return delta


def calculateSolarConstant(location, input_date):
    latitude = calculateLatitude(location)
    daily_variation = 137 * math.cos(math.radians(latitude - calculate_sun_position(input_date)))
    return daily_variation


def calculateDifferentialAltitude(differential_time):
    differential_altitude = differential_time / (12 / math.pi)
    return differential_altitude


def calculateIntegral(function, lower_range, higher_range):
    i = integrate.quad(function, lower_range, higher_range)[0]
    return i


def calculateDeclinationAngle(input_date: datetime):
    d = calculateNumberOfDaysSinceStartOfYear(input_date)
    b = (360 / 365) * (d - 81)
    b = math.radians(b)
    dA = 23.45 * math.sin(b)
    dA = math.radians(dA)
    return dA


def calculateNumberOfDaysSinceStartOfYear(input_date: datetime):
    days = (input_date - datetime(input_date.year, 1, 1)).days
    return days


def create_date_from_string(string,format):
    date = dt.datetime.strptime(string, format)
    return date


def calculateLatitude(location):
    geolocator = Nominatim(user_agent="Myapp")
    location_info = geolocator.geocode(location)
    return location_info.latitude


def calculateLongitude(location):
    geolocator = Nominatim(user_agent="Myapp")
    location_info = geolocator.geocode(location)
    return location_info.longitude


def calculateEquationOfTime(input_date: datetime):
    d = calculateNumberOfDaysSinceStartOfYear(input_date)
    b = (360 / 365) * (d - 81)
    b = math.radians(b)
    EoT = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    return EoT


def calculateTimezoneFromLocation(location):
    latitude = calculateLatitude(location)
    longitude = calculateLongitude(location)
    timezone = TimezoneFinder().timezone_at(lat=latitude, lng=longitude)
    return timezone


def calculateDifferenceCurrentAndGreenwichTime(location):
    local_timezone = calculateTimezoneFromLocation(location)
    differenceFromGreenwich = (datetime.now().astimezone(
        pytz.timezone(local_timezone)).utcoffset().total_seconds()) / 3600
    return differenceFromGreenwich


def calculateLocalStandardTimeMeridian(location):
    LSTM = 15 * calculateDifferenceCurrentAndGreenwichTime(location)
    return LSTM


def calculateTimeCorrectionFactor(location, input_date):
    TC = 4 * (calculateLongitude(location) - calculateLocalStandardTimeMeridian(location)) + \
         calculateEquationOfTime(input_date)
    return TC


def calculateLocalSolarTime(input_date: datetime, location):
    LST = addHours(input_date, calculateTimeCorrectionFactor(location, input_date) / 60)
    return LST


def addHours(input_date: datetime, hours):
    new_date = input_date + dt.timedelta(hours=hours)
    return new_date


def calculateHourAngle(input_date, location):
    HRA = 15 * (calculateLocalSolarTime(input_date, location).hour - 12)
    return HRA


def calculate_support_elevation(peak_time, location):
    declination = calculateDeclinationAngle(peak_time)
    latitude = calculateLatitude(location)
    latitude = math.radians(latitude)
    HRA = calculateHourAngle(peak_time, location)
    HRA = math.radians(HRA)

    peakEl = math.asin((math.sin(declination) * math.sin(latitude)) +
                   (math.cos(declination) * math.cos(latitude) * math.cos(HRA)))
    return peakEl


def calculateElevation(input_date, location, peak):
    declination = calculateDeclinationAngle(input_date)
    latitude = calculateLatitude(location)
    latitude = math.radians(latitude)
    HRA = calculateHourAngle(input_date, location)
    HRA = math.radians(HRA)

    El = math.asin((math.sin(declination) * math.sin(latitude)) +
                   (math.cos(declination) * math.cos(latitude) * math.cos(HRA)))

    if input_date.hour > peak[0].hour:
        angleToAdd = calculate_support_elevation(peak[0], location)
        El = El + angleToAdd
    return El


def calculateTimeOfDay(input_date, latitude):
    tD = 24 / math.pi * math.acos(
        (-1 * math.tan(math.radians(calculate_sun_position(input_date)))) * math.tan(math.radians(latitude)))
    return tD


def calculateTest(location):
    latitude = calculateLatitude(location)
    longitude = calculateLongitude(location)
    timezone = TimezoneFinder().timezone_at(lat=latitude, lng=longitude)
    timezone = pytz.timezone(timezone)
    return timezone


def convert_to_unix_time(date: datetime, location):
    tz = calculateTimezoneFromLocation(location)
    current_timezone = pytz.timezone(tz)
    utc_time = current_timezone.localize(date).astimezone(pytz.utc)
    unix_time = utc_time.timestamp()
    return unix_time


def callToWeatherAPI(initial_date: datetime, final_date: datetime, location):
    inital_time = str(int(convert_to_unix_time(initial_date, location)))
    final_time = str(int(convert_to_unix_time(final_date, location)))
    latitude = str(round(calculateLatitude(location), 2))
    longitude = str(round(calculateLongitude(location), 2))
    url = 'https://history.openweathermap.org/data/2.5/history/city?lat=' + latitude + '&lon=' + longitude \
          + '&type=hour&start=' + inital_time + '&end=' + final_time +'&appid=eb1b77df1c8a2ea0a4b2b4aea35e80e5'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        list_of_cloudiness = []
        for data_point in data['list']:
            list_of_cloudiness.append(data_point['clouds']['all'])
        #average_cloudiness = sum(list_of_cloudiness) / len(list_of_cloudiness)
        return list_of_cloudiness
    else:
        print('Error:', response.status_code)


def convert_mj_to_kwh(mj):
    joules = mj / 1000
    kwh = joules / 3600000
    return kwh


# def calculate_solar_energy_clouded(initial_date: datetime, final_date: datetime, location, area_of_effect_cm2, solar_panel_percentage):
#     max_solar_energy = calculateDifferentialEnergy(initial_date, final_date, location, area_of_effect_cm2)
#     max_solar_energy_converted = convert_mj_to_kwh(max_solar_energy)
#     print(callToWeatherAPI(initial_date, final_date, location))
#     cloudiness = callToWeatherAPI(initial_date, final_date, location)
#     cloud_cover = 1 - (cloudiness / 100)
#     solar_energy = max_solar_energy_converted * cloud_cover * (solar_panel_percentage/100)
#     return solar_energy


def calculate_difference_between_times(initial_date: datetime, final_date: datetime):
    initial_hour = initial_date.hour
    final_hour = final_date.hour
    hour_difference = final_hour-initial_hour
    return hour_difference


def add_hours_to_datetime(dateToChange: datetime, hoursToAdd):
    dateToReturn = dateToChange + datetime.timedelta(hours=hoursToAdd)
    return dateToReturn


def replace_hour(dateToChange: datetime, hourToSwap):
    dateToReturn = dateToChange.replace(hour=hourToSwap)
    return dateToReturn


# def calculate_average_altitude(initial_date: datetime, final_date: datetime, location):
#     initial_altitude = calculateElevation(initial_date, location)
#     final_altitude = calculateElevation(final_date, location)
#     altitude_average = (initial_altitude + final_altitude) / 2
#     return altitude_average

def calculate_average_altitude(initial_date: datetime, final_date: datetime, location):
    initial_altitude = calculateElevation(initial_date, location)
    final_altitude = calculateElevation(final_date, location)
    x = math.cos(initial_altitude) + math.cos(final_altitude)
    y = math.sin(initial_altitude) + math.sin(final_altitude)
    return math.atan2(y, x)


def get_solar_noon(initial_date, final_date, location):
    diff = calculate_difference_between_times(initial_date,final_date)
    final_date = replace_hour(final_date, addHours(initial_date, 1).hour)
    max = 0
    max_inital_date = initial_date
    max_final_date = final_date
    for i in range(diff):
        el = calculate_support_elevation(initial_date, location)

        if max < el:
            max = el
            max_inital_date = initial_date
            max_final_date = final_date


        initial_date = addHours(initial_date, 1)
        final_date = addHours(final_date, 1)
    return [max_inital_date, max_final_date]






# def get_solar_noon(input_date, location):
#     observer = ephem.Observer()
#     latitude = calculateLatitude(location)
#     longitude = calculateLongitude(location)
#     observer.lat = str(latitude)
#     observer.lon = str(longitude)
#     observer.elevation = 0
#
#     sun = ephem.Sun()
#     observer.date = input_date
#
#     solar_noon = observer.next_transit(sun).datetime()
#     local_timezone = pytz.timezone(calculateTimezoneFromLocation(location))
#
#     return solar_noon.astimezone(local_timezone).strftime('%Y-%m-%d %H:%M:%S')


def calculate_solar_energy_clouded(initial_date: datetime, final_date: datetime, location, area_of_effect_cm2, solar_panel_percentage, cloudiness, peak):
    max_solar_energy = calculateDifferentialEnergy(initial_date, final_date, location, area_of_effect_cm2, peak)
    max_solar_energy_converted = convert_mj_to_kwh(max_solar_energy)
    cloud_cover = 1 - (cloudiness / 100)
    solar_energy = max_solar_energy_converted * cloud_cover * (solar_panel_percentage/100)
    return solar_energy


def calculateDifferentialEnergy(initial_date: datetime, final_date: datetime, location, area_of_effect_cm2, peak):
    sC = calculateSolarConstant(calculateLatitude(location), initial_date)
    initial_altitude = calculateElevation(initial_date, location, peak)
    final_altitude = calculateElevation(final_date, location, peak)

    dE = sC * (3600 * (calculateTimeOfDay(initial_date, calculateLatitude(location)) / math.pi)) * \
         abs(calculateIntegral(lambda A: math.sin(A), initial_altitude, final_altitude)) * area_of_effect_cm2
    return dE


def calculate_actual_solar_energy(initial_date: datetime, final_date: datetime, location, area_of_effect_cm2, solar_panel_percentage):
    hour_difference = calculate_difference_between_times(initial_date, final_date)
    list_of_cloudiness = callToWeatherAPI(initial_date, final_date, location)
    final_date = replace_hour(final_date, addHours(initial_date, 1).hour)
    energy = 0
    peak = get_solar_noon(initial_date, final_date, location)
    for i in range(hour_difference):
        hourlyEnergy = calculate_solar_energy_clouded(initial_date, final_date, location, area_of_effect_cm2,
                                                      solar_panel_percentage, list_of_cloudiness[i], peak)
        if hourlyEnergy >= 2.0:
            energy = energy + 2.0
        else:
            energy = energy + hourlyEnergy
        initial_date = addHours(initial_date, 1)
        final_date = addHours(final_date, 1)
    return energy
