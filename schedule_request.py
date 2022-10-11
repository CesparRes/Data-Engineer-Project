import requests
import json
import sys

headers = {
    "accept": "application/json",
    "Authorization": "Bearer " + sys.argv[1],
}

### Arguments 2: origin, 3: destination, 4: date(YYYY-MM-DD), 5: directflight (true/false)
response = requests.get(
    "https://api.lufthansa.com/v1/operations/schedules/"
    + sys.argv[2]
    + "/"
    + sys.argv[3]
    + "/"
    + sys.argv[4]
    + "?directFlights="
    + sys.argv[5],
    headers=headers,
)


print(json.dumps(response.json()))
