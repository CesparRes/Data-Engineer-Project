#%%
import requests
import json
import sys
import pandas as pd
import configparser
import time
from check_request import check_request

## read the iata codes previously scraped
iata_codes = pd.read_csv("iata_codes.csv")

#%%
## test with the french airport codes only
france = iata_codes.loc[iata_codes["Country"] == "France"]
spain = iata_codes.loc[iata_codes["Country"] == "Spain"]
germany = iata_codes.loc[iata_codes["Country"] == "Germany"]
italy = iata_codes.loc[iata_codes["Country"] == "Italy"]
uk = iata_codes.loc[iata_codes["Country"] == "United Kingdom"]

IATA_grouped = [france["IATA"],spain["IATA"]] #,germany["IATA"],italy["IATA"],uk["IATA"]]

IATA = pd.concat(IATA_grouped)

#%%
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
# IATA = ["MAD", "LHR", "CDG", "ORY", "MAN", "ABZ", "ATH"]
times = ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"]

# loop through the IATA codes and append the response to an array
# for the test we're using only a single date, but looping through
# the 4 hour "windows" covering the day
for code in IATA:
    for dtime in times:
        response = requests.get(
            "https://api.lufthansa.com/v1/operations/customerflightinformation/arrivals/"
            + code
            + "/2022-10-20T"
            + dtime,
            headers=headers,
        )
        time.sleep(0.5)
        ## if there are no arrivals within a window, we get the resource not found error, so we want to filter these out of the response
        if "ResourceNotFound" not in response.text:
            results.append(response)


## output the responses - can be piped to a file easily
for result in results:
    print(json.dumps(result.json(), ensure_ascii=True))
