import requests
from requests.auth import HTTPBasicAuth
import configparser
from check_request import check_request
import json
import sys
import pprint

### load config.ini file - holds the clientid and clientsecret and last bearer token for lufthansa API
conf = configparser.ConfigParser()
conf.read("config.ini")

## function that checks the bearer token is valid, if it's not valid, the new bearer token is returned and added to the config file
bearer = check_request(conf["lufthansa"]["bearer"])

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
        "limit": "2",
    }
    query_response = requests.get(
        "https://api.lufthansa.com/v1/flight-schedules/flightschedules/passenger",
        params=params,
        headers=headers,
    )
    print(json.dumps(query_response.json()))
except:
    print(json.dumps(query_response.json()))
