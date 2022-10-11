import requests
import json
import sys

headers = {
    "accept": "application/json",
    "Authorization": "Bearer " + sys.argv[1],
}

response = requests.get(
    "https://api.lufthansa.com/v1/operations/schedules/"
    + sys.argv[2]
    + "/"
    + sys.argv[3]
    + "/"
    + sys.argv[4]
    + "?directFlights=true",
    headers=headers,
)


print(json.dumps(response.json()))
