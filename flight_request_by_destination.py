import requests
import json
import sys
import pprint
import configparser
from check_request import check_request

### load config.ini file - holds the clientid and clientsecret and last bearer token for lufthansa API
conf = configparser.ConfigParser()
conf.read("config.ini")

## function that checks the bearer token is valid, if it's not valid, the new bearer token is returned and added to the config file
bearer = check_request(conf["lufthansa"]["bearer"])

## argument is bearer token
headers = {
    "accept": "application/json",
    "Authorization": "Bearer " + bearer,
}

# Argument 2 is destination country
# for now we use fixed date (6-7 October 2022) - but this can be made argument too
params = {
    "airlines": "LH",
    "startDate": "06OCT22",
    "endDate": "07OCT22",
    "daysOfOperation": "1234567",
    "timeMode": "UTC",
    "destination": sys.argv[1],
}

# return passenger flight schedules of flights to argument 2 country on selected date
response = requests.get(
    "https://api.lufthansa.com/v1/flight-schedules/flightschedules/passenger",
    params=params,
    headers=headers,
)
print(json.dumps(response.json()))
