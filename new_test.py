#%%
import requests
import json
import sys
import pandas as pd
import configparser
import time
import asyncio
from check_request import check_request
from check_request_spain import check_request_spain
from check_request_germany import check_request_germany

## read the iata codes previously scraped
iata_codes = pd.read_csv("iata_codes.csv")

#%%
## set up the IATA codes for each country into sub-dataframes
france = iata_codes.loc[iata_codes["Country"] == "France"]
spain = iata_codes.loc[iata_codes["Country"] == "Spain"]
germany = iata_codes.loc[iata_codes["Country"] == "Germany"]
italy = iata_codes.loc[iata_codes["Country"] == "Italy"]
uk = iata_codes.loc[iata_codes["Country"] == "United Kingdom"]

## the lufthansa API only allows 3 app keys, so we need to group some countries
IATA_grouped = [france["IATA"], italy["IATA"], uk["IATA"]]
IATA_spain = spain["IATA"].head()
IATA_germany = germany["IATA"].head()

## concatenate the grouped sub-dataframes into one
IATA = pd.concat(IATA_grouped)

## set up a list of the 3 "application" groups of IATA to be requested with different keys
IATA_countries = [IATA, IATA_spain, IATA_germany]

#%%
### load config.ini files - holds the clientid and clientsecret and last bearer token for lufthansa API per country
conf = configparser.ConfigParser()
conf_spain = configparser.ConfigParser()
conf_germany = configparser.ConfigParser()

conf.read("config.ini")
conf_spain.read("config_spain.ini")
conf_germany.read("config_germany.ini")

results = []

## arrays of arrival airports and 4 hour windows
times = ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"]


### what we want to do is loop through a function that calls each countries requests - can we make a function and then async run it in a loop?
### note that we also have 3 "apps" with different bearers to use so we don't hit the 1k per hour limit


def arrivals_request(IATA_list):

    ## check which country's IATA list has been passed to the function, and then load the appropriate bearer token
    if IATA_list.reset_index(drop=True).equals(IATA_spain.reset_index(drop=True)):
        bearer = check_request_spain(conf_spain["lufthansa"]["bearer"])

    elif IATA_list.reset_index(drop=True).equals(IATA_germany.reset_index(drop=True)):
        bearer = check_request_germany(conf_germany["lufthansa"]["bearer"])

    else:
        bearer = check_request(conf["lufthansa"]["bearer"])

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + bearer,
    }

    for code in IATA_list:
        for dtime in times:
            response = requests.get(
                "https://api.lufthansa.com/v1/operations/customerflightinformation/arrivals/"
                + code
                + "/2022-10-26T"
                + dtime,
                headers=headers,
            )
        time.sleep(0.2)
        ## if there are no arrivals within a window, we get the resource not found error, so we want to filter these out of the response
        ## we also want to filter out any "error" messages
        if "ResourceNotFound" and "Error" not in response.text:
            results.append(response)


## Now the function is created, what we need to do is make tasks for each of the 3 groups of IATA lists, and run them async


async def main():
    await asyncio.gather(arrivals_request(country) for country in IATA_countries)


asyncio.run(main())

## output the responses - can be piped to a file easily
for result in results:
    print(json.dumps(result.json(), ensure_ascii=True))
