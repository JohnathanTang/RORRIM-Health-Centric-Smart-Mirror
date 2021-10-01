# user_info.py

import os
import requests
import json
from user_data.fitbit import Fitbit

OWM_KEY = "6ae55c65d84835e00eaf7fda7e45bffa"
API_URL = "https://api.openweathermap.org/data/2.5/weather"

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


class User(object):
    def __init__(self, user_id, user_name, user_loc, fitbit=None, ouraring=None):
        self.id = user_id
        self.name = user_name
        self.location = user_loc
        self.fbit = fitbit  # Fitbit object
        self.oura = ouraring  # OuraRing object

        api_params = "q=" + self.location.replace(" ", "+") + "&appid=" + OWM_KEY
        j = requests.get(url=API_URL, params=api_params).json()
        self.lat = j["coord"]["lat"]
        self.lon = j["coord"]["lon"]

    # def update_log(self):
        # will call update_logs(user_id) of fitbit and/or ouraring

    def get_heart_rate(self):
        return self.fbit.get_heart_rate()

    def get_steps(self):
        return self.fbit.get_steps()

def get_user(user_id: int) -> User:
    """Retrieve user from Json file and return User object"""
    # TODO: del old User object when switching?

    data = openJson()

    user_name = data[str(user_id)]["username"]
    user_loc = data[str(user_id)]["location"]

    fbit = data[str(user_id)].get(FITBIT)
    oura = data[str(user_id)].get(OURA)
    fitbit = None
    ouraring = None

    if fbit is not None:
        fitbit = Fitbit(user_id, fbit[0], fbit[1])

    # if oura in not None:
    #     ouraring = Ouraring(...)

    return User(user_id, user_name, user_loc, fitbit, ouraring)

def add_new_user(user_id, name, location, wearDev=None, wearId=None, wearToken=None):
    """
    Assumes never has mismatching keys (ie. numbers aren't off)
    Assumes provides all information
    """
    # TODO: del old User object when switching?

    data = openJson()

    newUser = {"username": str(name), "location" : location}

    if wearDev is not None:
        newUser[str(wearDev)] = [str(wearId), str(wearToken)]
        
    data[str(user_id)] = newUser
    writeJson(data)


# The functions below are deprecated

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
    