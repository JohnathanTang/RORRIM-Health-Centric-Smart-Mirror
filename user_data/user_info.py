# user_info.py

import os
import requests
import json

OWM_KEY = "6ae55c65d84835e00eaf7fda7e45bffa"

FITBIT = "fitbit"
OURA = "oura"
EMOTIV = "emotiv" #delete later

PATH_DB = os.path.join(os.path.abspath(os.path.dirname(__file__)), "users.json")


def openJson():
    with open(PATH_DB) as f:
        return json.load(f)

def writeJson(d):
    with open(PATH_DB, "w") as jsonFile:
        json.dump(d, jsonFile)

def printJson(d):
    print(json.dumps(d, indent = 4, sort_keys=True))


def addNewUser(name, location, wearDev=None, wearId=None, wearToken=None) -> (str,str):
    """
    Assumes never has mismatching keys (ie. numbers aren't off)
    Assumes provides all information
    """
    data = openJson()
    num = len(data) + 1

    lat, lon = getLatLon(location)

    newUser = {"username": str(name),
                   "location" : location
                  }

    if wearDev is not None:
        newUser[str(wearDev)] = [str(wearId), str(wearToken)]
        
    data[str(num)] = newUser
    
    writeJson(data)

    return (lat, lon)
    

def getLatLon(location: str) -> (str,str):
    """
    Takes in location as a string and retrieves the latitude and longitude from
    OpenWeatherMap
    """
    
    api_url = "https://api.openweathermap.org/data/2.5/weather"
    api_params = "q=" + location.replace(" ", "+") + "&appid=" + OWM_KEY

    j = requests.get(url=api_url, params=api_params).json()
    lat = j["coord"]["lat"]
    lon = j["coord"]["lon"]

    return (str(lat), str(lon))

def setUsername(num, name):
    data = openJson()
    data[str(num)]["username"] = str(name)
    writeJson(data)
    
def setLocation(num, location):
    data = openJson()
    data[str(num)]["location"] = str(location)
    writeJson(data)

def setWearable(num, wearDev, wearId, wearToken):
    data = openJson()
    data[str(num)][str(wearDev)] = [str(wearId), str(wearToken)]
    writeJson(data)
    

def getUserInfo(num):
    data = openJson()

    username = data[str(num)]["username"]
    location = data[str(num)]["location"]
    fbit = data[str(num)].get(FITBIT)
    ora = data[str(num)].get(OURA)

    return (username, location, fbit, ora)

def getUsername(num):
    data = openJson()
    return data[str(num)]["username"]

def getLocation(num):
    data = openJson()
    return data[str(num)]["location"]

def getFitbit(num):
    """
    Returns None if user has no Fitbit
    """
    data = openJson()
    return data[str(num)].get(FITBIT)

def getOura(num):
    """
    Returns None if user has no Oura Ring
    """
    data = openJson()
    return data[str(num)].get(OURA)
