import requests
import json
import sys

## as usual - bearer token handed by command line argument
headers = {
    "accept": "application/json",
    "Authorization": "Bearer " + sys.argv[1],
}

results = []

## make a test array of IATA codes to look up arrivals for
IATA = ["MAD", "LHR", "CDG", "ORY"]

# loop through the IATA codes and append the response to an array
# for the test we're only using 1 specific time and date - 12-10-2022 12:00
for code in IATA:
    response = requests.get(
        "https://api.lufthansa.com/v1/operations/customerflightinformation/arrivals/"
        + code
        + "/2022-10-12T12:00",
        headers=headers,
    )
    results.append(response)


## output the responses - can be piped to a file easily
for result in results:
    print(json.dumps(result.json()))
