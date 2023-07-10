import math
import datetime as dt
from datetime import datetime, date, timedelta

import requests
from timezonefinder import TimezoneFinder
import pytz
import scipy.integrate as integrate
from geopy import Nominatim


def calculateLatitude(location):
    geolocator = Nominatim(user_agent="Myapp")
    location_info = geolocator.geocode(location)
    return location_info.latitude


def calculateLongitude(location):
    geolocator = Nominatim(user_agent="Myapp")
    location_info = geolocator.geocode(location)
    return location_info.longitude


def calculateNumberOfDaysSinceStartOfYear(input_date: datetime):
    days = (input_date - datetime(input_date.year, 1, 1)).days
    return days


def calculateDeclinationAngle(input_date: datetime):
    d = calculateNumberOfDaysSinceStartOfYear(input_date)
    b = (360 / 365) * (d + 10)
    b = math.radians(b)
    dA = -23.45 * math.cos(b)
    dA = math.radians(dA)
    return dA

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


def calculateTimezoneFromLocation(location):
    latitude = calculateLatitude(location)
    longitude = calculateLongitude(location)
    timezone = TimezoneFinder().timezone_at(lat=latitude, lng=longitude)
    return timezone


def addHours(input_date: datetime, hours):
    new_date = input_date + dt.timedelta(hours=hours)
    return new_date


def calculateEquationOfTime(input_date: datetime):
    d = calculateNumberOfDaysSinceStartOfYear(input_date)
    b = (360 / 365) * (d - 81)
    b = math.radians(b)
    EoT = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    return EoT


def calculateHourAngle(input_date, location):
    HRA = 15 * (calculateLocalSolarTime(input_date, location).hour - 12)
    return HRA


def calculateElevation(input_date, location):
    declination = calculateDeclinationAngle(input_date)
    latitude = calculateLatitude(location)
    latitude = math.radians(latitude)
    HRA = calculateHourAngle(input_date, location)
    HRA = math.radians(HRA)

    El = math.asin((math.sin(declination) * math.sin(latitude)) +
                   (math.cos(declination) * math.cos(latitude) * math.cos(HRA)))

    El = math

    if (input_date.time().hour > 12):
        El = -1 * El + math.pi
    return El

def calculateAltitude(input_date, location):
    altitude = 90 - calculateElevation(input_date, location)
    return altitude



    # def calculateAltitude(input_date, location):
    #
    #     hour_ang = sidereal - rasc
    #     elevation = asin(sin(decl) * sin(rlat) + cos(decl) *
    #                      cos(rlat) * cos(hour_ang))