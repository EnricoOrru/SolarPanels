import math
import datetime as dt
from datetime import datetime, date, timedelta
import pysolar.solar as pysolar
#import suncalc
#import sunposition
import astropy.coordinates as coord
from astropy.time import Time
import astropy.units as u
import requests
from timezonefinder import TimezoneFinder
import pytz
import scipy.integrate as integrate
from geopy import Nominatim
import main2


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

    # if El > (math.pi/2) - 0.001:
    #     El = -1 * El + math.pi

    return El


# def calculate_sun_altitude(input_date, location):
#     latitude = calculateLatitude(location)
#     longitude = calculateLongitude(location)
#     timezone_string = main2.calculateTimezoneFromLocation(location)
#     timezone = pytz.timezone(timezone_string)
#     input_date = timezone.localize(input_date)
#     altitude = pysolar.get_altitude(latitude, longitude, input_date)
#
#     return altitude


def calculate_sun_altitude(input_date, location):
    latitude = calculateLatitude(location)
    longitude = calculateLongitude(location)
    timezone_string = main2.calculateTimezoneFromLocation(location)
    timezone = pytz.timezone(timezone_string)
    input_date = timezone.localize(input_date)
    loc = coord.EarthLocation(lon=longitude * u.deg, lat=latitude * u.deg)
    time = Time(input_date)
    altaz = coord.AltAz(location=loc, obstime=time)
    sun = coord.get_sun(time)
    altitude = sun.transform_to(altaz).alt.value

    return altitude


# def calculate_sun_altitude(input_date, location):
#     latitude = calculateLatitude(location)
#     longitude = calculateLongitude(location)
#     timezone_string = main2.calculateTimezoneFromLocation(location)
#     timezone = pytz.timezone(timezone_string)
#     input_date = timezone.localize(input_date)
#     altitude = suncalc.get_position(input_date, longitude, latitude)
#
#     return altitude