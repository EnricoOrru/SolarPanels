import math
import datetime as dt
from datetime import datetime, date, timedelta
import pysolar.solar as pysolar
#import suncalc
#import sunposition
import pvlib
import pandas as pd
import astropy.coordinates as coord
from astropy.time import Time
import astropy.units as u
import requests
from timezonefinder import TimezoneFinder
import pytz
import scipy.integrate as integrate
from geopy import Nominatim
import main2


def calculateDifferentialEnergy(initial_date: datetime, final_date: datetime, location, area_of_effect_cm2, peak,
                                surface_tilt, surface_azimuth):
    sC = calculateSolarConstant(calculateLatitude(location), initial_date)
    initial_altitude = calculateElevation(initial_date, location, peak)
    final_altitude = calculateElevation(final_date, location, peak)

    # Calculate solar insolation on a surface at a particular tilt angle as a function of latitude and day of the year
    max_solar_insolation = calculateMaxSolarInsolation(calculateLatitude(location),calculateLongitude(location), initial_date,
                                                        surface_tilt)

    # Calculate solar radiation incident on a tilted surface
    solar_radiation_on_tilted_surface = max_solar_insolation * math.sin(surface_tilt) * math.cos(
        initial_altitude - final_altitude) + math.cos(surface_tilt) * math.sin(
        initial_altitude - final_altitude) * math.sin(surface_azimuth)

    dE = solar_radiation_on_tilted_surface * area_of_effect_cm2

    return dE

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


def calculateSolarConstant(location, input_date):
    latitude = calculateLatitude(location)
    daily_variation = 137 * math.cos(math.radians(latitude - calculate_sun_position(input_date)))
    return daily_variation


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

def calculate_support_elevation(peak_time, location):
    declination = calculateDeclinationAngle(peak_time)
    latitude = calculateLatitude(location)
    latitude = math.radians(latitude)
    HRA = calculateHourAngle(peak_time, location)
    HRA = math.radians(HRA)

    peakEl = math.asin((math.sin(declination) * math.sin(latitude)) +
                       (math.cos(declination) * math.cos(latitude) * math.cos(HRA)))
    return peakEl

def calculateDeclinationAngle(date):
    # Calculate day of year
    day_of_year = date.timetuple().tm_yday

    # Calculate declination angle
    declination_angle = -23.45 * math.cos(2 * math.pi * (day_of_year + 10) / 365)

    return declination_angle


def calculateHourAngle(date, longitude):
    # Calculate time offset from UTC
    time_offset = date.utcoffset().total_seconds() / 3600

    # Calculate solar noon time
    solar_noon_time = 12 - (longitude / 15) - time_offset

    # Calculate hour angle
    hour_angle = (datetime.datetime.now().hour - solar_noon_time) * 15

    return hour_angle


def calculateSolarAltitudeAngle(latitude, declination_angle, hour_angle):
    # Convert latitude and declination angle to radians
    latitude_radians = math.radians(latitude)
    declination_angle_radians = math.radians(declination_angle)

    # Calculate solar altitude angle
    solar_altitude_angle = math.asin(math.sin(latitude_radians) * math.sin(declination_angle_radians) +
                                     math.cos(latitude_radians) * math.cos(declination_angle_radians) *
                                     math.cos(math.radians(hour_angle)))

    return solar_altitude_angle


def calculateSolarAzimuthAngle(latitude, declination_angle, hour_angle):
    # Convert latitude and declination angle to radians
    latitude_radians = math.radians(latitude)
    declination_angle_radians = math.radians(declination_angle)

    # Calculate solar azimuth angle
    solar_azimuth_angle = math.atan2(-math.sin(math.radians(hour_angle)),
                                     math.cos(latitude_radians) * math.tan(declination_angle_radians) -
                                     math.sin(latitude_radians) * math.cos(math.radians(hour_angle)))

    return solar_azimuth_angle


def calculateSolarInsolation(solar_altitude_angle, solar_azimuth_angle, surface_tilt):
    # Convert surface tilt angle to radians
    surface_tilt_radians = math.radians(surface_tilt)

    # Calculate angle of incidence
    angle_of_incidence = math.acos(math.sin(solar_altitude_angle) * math.sin(surface_tilt_radians) +
                                   math.cos(solar_altitude_angle) * math.cos(surface_tilt_radians) *
                                   math.cos(solar_azimuth_angle))

    # Calculate maximum amount of solar insolation on a surface at a particular tilt angle as a function of latitude and day of the year
    max_solar_insolation = 1367 * (math.sin(solar_altitude_angle) * math.sin(surface_tilt_radians) +
                                   math.cos(solar_altitude_angle) * math.cos(surface_tilt_radians) *
                                   math.cos(angle_of_incidence))

    return max_solar_insolation


def calculateMaxSolarInsolation(latitude, longitude, date, surface_tilt):
    # Calculate declination angle
    declination_angle = calculateDeclinationAngle(date)

    # Calculate hour angle
    hour_angle = calculateHourAngle(date, longitude)

    # Calculate solar altitude angle
    solar_altitude_angle = calculateSolarAltitudeAngle(latitude, declination_angle, hour_angle)

    # Calculate solar azimuth angle
    solar_azimuth_angle = calculateSolarAzimuthAngle(latitude, declination_angle, hour_angle)

    # Calculate maximum amount of solar insolation on a surface at a particular tilt angle as a function of latitude and day of the year
    max_solar_insolation = calculateSolarInsolation(solar_altitude_angle, solar_azimuth_angle,
                                                     surface_tilt)

    return max_solar_insolation





















def calculateSunEnergy(location, initial_date, final_date, surface_tilt, surface_azimuth, area_cm2):
    # Create a time range within the specified time frame
    time_range = pd.date_range(start=initial_date, end=final_date, freq='30min')

    # Initialize total energy
    total_energy = 0

    # Calculate energy for each time step within the time frame
    for datetime_obj in time_range:
        # Calculate altitude of the sun using your custom function
        sun_altitude = main2.calculateElevation(datetime_obj, location, 0)

        # Get extraterrestrial radiation
        dni_extra = pvlib.irradiance.get_extra_radiation(datetime_obj)

        # Calculate solar irradiance on the surface
        surface_irradiance = pvlib.irradiance.get_total_irradiance(surface_tilt=surface_tilt, surface_azimuth=surface_azimuth,
                                                                   solar_zenith=90 - sun_altitude,
                                                                   solar_azimuth=180,
                                                                   dni=dni_extra, ghi=0, dhi=0,
                                                                   model='haydavies',
                                                                   dni_extra=dni_extra)

        # Calculate energy on the surface
        energy = surface_irradiance['poa_global'] * area_cm2 * 0.001  # Convert from W/m^2 to mJ

        # Accumulate total energy
        total_energy += energy

    return total_energy


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