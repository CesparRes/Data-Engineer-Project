import requests
from requests.auth import HTTPBasicAuth
import configparser
import json
import sys
import pprint

### load config.ini file - holds the clientid and clientsecret and last bearer token for lufthansa API
conf = configparser.ConfigParser()
conf.read("config.ini")

bearer = conf["lufthansa"]["bearer"]

### lets test the current bearer token is working first
try:
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + conf["lufthansa"]["bearer"],
    }

    response = requests.get(
        "https://api.lufthansa.com/v1/mds-references/airports/FRA", headers=headers
    )

    ### if the response is 401 (not authorised) we'll request a new token
    if response.status_code == 401:
        print("401 failure - getting new auth token")
        data = {
            "client_id": conf["lufthansa"]["clientId"],
            "client_secret": conf["lufthansa"]["clientSecret"],
            "grant_type": "client_credentials",
        }
        response = requests.post("https://api.lufthansa.com/v1/oauth/token", data=data)

        ## probably this can be done more tidily, but essentially we turn the response into readable JSON
        temp_json = json.dumps(response.json())
        temp_resp = json.loads(temp_json)

        ## save the received bearer token into the bearer variable, and update config.ini with the updated bearer
        bearer = temp_resp["access_token"]
        conf["lufthansa"]["bearer"] = bearer
        with open("config.ini", "w") as configfile:
            conf.write(configfile)

## failure code
except:
    print(json.dumps(response))

## now the real request
try:
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + bearer,
    }

    params = {
        "airlines": "LH",
        "startDate": "06OCT22",
        "endDate": "07OCT22",
        "daysOfOperation": "1234567",
        "timeMode": "UTC",
        "destination": "LHR",
    }
    query_response = requests.get(
        "https://api.lufthansa.com/v1/flight-schedules/flightschedules/passenger",
        params=params,
        headers=headers,
    )
    print(json.dumps(query_response.json()))
except:
    print(json.dumps(query_response.json()))
