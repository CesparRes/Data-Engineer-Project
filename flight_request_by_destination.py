import requests
import json
import sys
import pprint


## argument is bearer token
headers = {
    "accept": "application/json",
    "Authorization": "Bearer " + sys.argv[1],
}

# Argument 2 is destination country
# for now we use fixed date (6-7 October 2022) - but this can be made argument too
params = {
    "airlines": "LH",
    "startDate": "06OCT22",
    "endDate": "07OCT22",
    "daysOfOperation": "1234567",
    "timeMode": "UTC",
    "destination": sys.argv[2],
}

# return passenger flight schedules of flights to argument 2 country on selected date
response = requests.get(
    "https://api.lufthansa.com/v1/flight-schedules/flightschedules/passenger",
    params=params,
    headers=headers,
)


print(json.dumps(response.json()))
