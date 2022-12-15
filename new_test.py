#%%
import requests
import json
import pandas as pd
import configparser
import time
import asyncio
from check_request import check_request
from datetime import datetime, timedelta

## read the iata codes previously scraped
iata_codes = pd.read_csv("iata_codes.csv")
result_out = []

#%%

## Quick code to retrieve yesterdays date and format it correctly for requests
day_arg = datetime.today() - timedelta(days=1)
day_arg = day_arg.strftime("/%Y-%m-%dT")

#%%
day_arg

#%%
## set up the IATA codes for each country into sub-dataframes
france = iata_codes.loc[iata_codes["Country"] == "France"]
spain = iata_codes.loc[iata_codes["Country"] == "Spain"]
germany = iata_codes.loc[iata_codes["Country"] == "Germany"]
italy = iata_codes.loc[iata_codes["Country"] == "Italy"]
uk = iata_codes.loc[iata_codes["Country"] == "United Kingdom"]

## the lufthansa API only allows 3 app keys, so we need to group some countries
IATA_grouped = [france["IATA"], italy["IATA"], uk["IATA"]]

## concatenate the grouped sub-dataframes into one
IATA = pd.concat(IATA_grouped)

## set up a list of the 3 "application" groups of IATA to be requested with different keys
IATA_countries = [IATA]

#%%
### load config.ini files - holds the clientid and clientsecret and last bearer token for lufthansa API per country
conf = configparser.ConfigParser()
"""conf_spain = configparser.ConfigParser()
conf_germany = configparser.ConfigParser()"""

conf.read("config.ini")
"""conf_spain.read("config_spain.ini")
conf_germany.read("config_germany.ini")"""

results = []

#%%

## arrays of arrival airports and 4 hour windows
times = ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"]

#%%
### what we want to do is loop through a function that calls each countries requests - can we make a function and then async run it in a loop?
### note that we also have 3 "apps" with different bearers to use so we don't hit the 1k per hour limit


async def arrivals_request(IATA_list):

    ## check which country's IATA list has been passed to the function, and then load the appropriate bearer token
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
                + day_arg
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
    await asyncio.gather(*[arrivals_request(country) for country in IATA_countries])


asyncio.run(main())

## output the responses - can be piped to a file easily
for result in results:
    print(json.dumps(result.json(), indent=4, ensure_ascii=True))
    result_out.append(json.dumps(result.json(), ensure_ascii=True))

with open("all_airports.txt", "w") as f:
    f.write(str(result_out))

"""#%%
headers = {
    "accept": "application/json",
    "authorization" : "Bearer 63yrk7ybr43qywa5a7f7m562",
}

results = []
result_out = []

for i in ['12:00','18:00']:
    response = requests.get(
                    "https://api.lufthansa.com/v1/operations/customerflightinformation/arrivals"
                    + "LYS"
                    + "/2022-12-14T"
                    + i,
                    headers=headers,
    )
    if "ResourceNotFound" and "Error" not in response.text:
        results.append(response)

for result in results:
    print(json.dumps(result.json(), indent=4, ensure_ascii=True))
    result_out.append(json.dumps(result.json(), ensure_ascii=True))

with open("some_airports.txt", "w") as f:
    f.write(str(result_out))"""
