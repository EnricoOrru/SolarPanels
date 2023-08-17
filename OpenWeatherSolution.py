import ipdb
import requests
from geopy import Nominatim

def create_location(location):
    latitude = calculateLatitude(location)
    longitude = calculateLongitude(location)
    url = 'https://api.openweathermap.org/energy/1.0/locations?appid=eb1b77df1c8a2ea0a4b2b4aea35e80e5'
    json = {"type": "point", "coordinates": [{"lat": latitude,
                                              "lon": longitude}]}
    response = requests.post(url, json)
    ipdb.set_trace()

    if response.status_code == 200:
        return response
    else:
        print('Error:', response.status_code)


def calculateLatitude(location):
    geolocator = Nominatim(user_agent="Myapp")
    location_info = geolocator.geocode(location)
    return location_info.latitude


def calculateLongitude(location):
    geolocator = Nominatim(user_agent="Myapp")
    location_info = geolocator.geocode(location)
    return location_info.longitude