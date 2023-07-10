import math
import datetime as dt
from datetime import datetime, date, timedelta
from timezonefinder import TimezoneFinder
import pytz
import scipy.integrate as integrate
from geopy import Nominatim


def calculate_sun_position(date):
    # Step 1: Convert the date to Julian centuries since J2000.0
    JD = date.toordinal() + 1721424.5
    T = (JD - 2451545.0) / 36525

    # Step 2: Calculate the Sun's mean longitude
    L = 280.460 + 36000.771 * T

    # Step 3: Calculate the Sun's mean anomaly
    G = 357.528 + 35999.050 * T

    # Step 4: Calculate the Earth's mean eccentricity of the orbit
    e = 0.016708634 - 0.000042037 * T

    # Step 5: Calculate the Sun's equation of center
    C = math.sin(math.radians(G)) * (1.914602 - T * (0.004817 + 0.000014 * T)) + \
        math.sin(math.radians(2 * G)) * (0.019993 - 0.000101 * T) + \
        math.sin(math.radians(3 * G)) * 0.000289

    # Step 6: Calculate the Sun's true longitude
    lam = L + C

    # Step 7: Calculate the Sun's true anomaly
    v = G + C

    # Step 8: Calculate the Sun's radius vector
    R = 1.000001018 * (1 - e * e) / (1 + e * math.cos(math.radians(v)))

    # Step 9: Calculate the Sun's apparent longitude
    lam_apparent = lam - 0.00569 - 0.00478 * math.sin(math.radians(125.04 - 1934.136 * T))

    # Step 10: Calculate the Sun's true obliquity of the ecliptic
    epsilon = 23.439 - 0.00000036 * T

    # Step 11: Calculate the Sun's right ascension
    alpha = math.atan2(math.cos(math.radians(epsilon)) * math.sin(math.radians(lam_apparent)), math.cos(math.radians(lam_apparent)))
    alpha = math.degrees(alpha)

    # Step 12: Calculate the Sun's declination
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


def calculateDifferentialEnergy(initial_date: datetime, final_date: datetime, location, area_of_effect_cm2):

    sC = calculateSolarConstant(calculateLatitude(location), initial_date)
    initial_altitude = calculateElevation(initial_date, location)
    final_altitude = calculateElevation(final_date, location)

    dE = sC * (3600 * (calculateTimeOfDay(initial_date,calculateLatitude(location))/math.pi)) * \
         calculateIntegral(lambda A: math.sin(A),initial_altitude,final_altitude) * area_of_effect_cm2
    return dE


def calculateIntegral(function, lower_range, higher_range):
    i = integrate.quad(function, lower_range, higher_range)[0]
    return i


def calculateDeclinationAngle(input_date: datetime):
    d = calculateNumberOfDaysSinceStartOfYear(input_date)
    b = (360/365) * (d - 81)
    b = math.radians(b)
    dA = 23.45 * math.sin(b)
    dA = math.radians(dA)
    return dA


def calculateNumberOfDaysSinceStartOfYear(input_date: datetime):
    days = (input_date - datetime(input_date.year, 1, 1)).days
    return days


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
    b = (360/365) * (d - 81)
    b = math.radians(b)
    EoT = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    return EoT


def calculateDifferenceCurrentAndGreenwichTime(location):
    local_timezone = calculateTimezoneFromLocation(location)
    differenceFromGreenwich = (datetime.now().astimezone(pytz.timezone(local_timezone)).utcoffset().total_seconds())/3600
    return differenceFromGreenwich


def calculateTimezoneFromLocation(location):
    latitude = calculateLatitude(location)
    longitude = calculateLongitude(location)
    timezone = TimezoneFinder().timezone_at(lat=latitude, lng=longitude)
    return timezone


def calculateLocalStandardTimeMeridian(location):
    LSTM = 15 * calculateDifferenceCurrentAndGreenwichTime(location)
    return LSTM


def calculateTimeCorrectionFactor(location, input_date):
    TC = 4 * (calculateLongitude(location) - calculateLocalStandardTimeMeridian(location)) + \
         calculateEquationOfTime(input_date)
    return TC


def calculateLocalSolarTime(input_date: datetime, location):
    LST = addHours(input_date, calculateTimeCorrectionFactor(location, input_date)/60)
    return LST


def addHours(input_date: datetime, hours):
    new_date = input_date + dt.timedelta(hours=hours)
    return new_date


def calculateHourAngle(input_date, location):
    HRA = 15 * (calculateLocalSolarTime(input_date, location).hour - 12)
    return HRA


def calculateElevation(input_date,location):
    declination = calculateDeclinationAngle(input_date)
    latitude = calculateLatitude(location)
    latitude = math.radians(latitude)
    HRA = calculateHourAngle(input_date,location)
    HRA = math.radians(HRA)

    El = math.asin((math.sin(declination) * math.sin(latitude)) +
                   (math.cos(declination) * math.cos(latitude) * math.cos(HRA)))

    if (input_date.time().hour > 12):
        El = -1 * El + math.pi
    return El


def calculateTimeOfDay(input_date, latitude):
    tD = 24/math.pi * math.acos((-1 * math.tan(math.radians(calculate_sun_position(input_date)))) * math.tan(math.radians(latitude)))
    return tD
