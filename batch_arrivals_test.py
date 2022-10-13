import requests
import json
import sys
import configparser
from check_request import check_request

### load config.ini file - holds the clientid and clientsecret and last bearer token for lufthansa API
conf = configparser.ConfigParser()
conf.read("config.ini")

## function that checks the bearer token is valid, if it's not valid, the new bearer token is returned and added to the config file
bearer = check_request(conf["lufthansa"]["bearer"])

## as usual - bearer token handed by command line argument
headers = {
    "accept": "application/json",
    "Authorization": "Bearer " + bearer,
}

results = []

## arrays of arrival airports and 4 hour windows
IATA = ["MAD", "LHR", "CDG", "ORY", "MAN", "ABZ", "ATH"]
times = ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"]

# loop through the IATA codes and append the response to an array
# for the test we're only using 1 specific time and date - 12-10-2022 12:00
for code in IATA:
    for time in times:
        response = requests.get(
            "https://api.lufthansa.com/v1/operations/customerflightinformation/arrivals/"
            + code
            + "/2022-10-12T"
            + time,
            headers=headers,
        )
        ## if there are no arrivals within a window, we get the resource not found error, so we want to filter these out of the response
        if "ResourceNotFound" not in response.text:
            results.append(response)


## output the responses - can be piped to a file easily
for result in results:
    print(json.dumps(result.json()))
