from fastapi import FastAPI, Header, Query, Request, HTTPException
from fastapi.responses import JSONResponse
import json
from pymongo import MongoClient
import pandas as pd
from pprint import pprint
import re

## import the list of IATA codes
iata_codes = pd.read_csv("iata_codes.csv")

## Save each country into it's own dataframe
france = iata_codes.loc[iata_codes["Country"] == "France"]
italy = iata_codes.loc[iata_codes["Country"] == "Italy"]
uk = iata_codes.loc[iata_codes["Country"] == "United Kingdom"]


def country_selector(country):
    if country.lower() == "uk":
        return uk
    if country.lower() == "france":
        return france
    if country.lower() == "italy":
        return italy
    else:
        return "error"


def code_selector(code):
    if code.upper() not in ["DV", "FE", "LD", "CD", "DL", "OT"]:
        return "error"
    else:
        return code


def flatten(results):
    """Flattens a list of lists down to simply a list
    takes the list
    returns the flattened list
    """
    return [item for sublist in results for item in sublist]


def mongo_connect():

    client = MongoClient(host="localhost", port=27017, authSource="admin")

    db = client.flight_info
    flights = db.flights

    return flights, client


api = FastAPI(
    title="Lufthansa Arrivals API",
    description="API used to query mongo DB of Lufthansa flight arrivals in uk, france and italy",
    version="1.0",
    openapi_tags=[
        {"name": "Status", "description": "Check status of API"},
        {"name": "Arrivals", "description": "Returns arrivals details"},
        {"name": "Codes", "description": "Returns counts for status codes"},
        {"name": "Flight", "description": "Flight number searches"},
    ],
)


@api.get("/status", name="Status", tags=["Status"])
def get_status():
    """Returns status of the API"""
    return {"Status": "API is OK - use /docs endpoint for more details"}


@api.get("/arrivals/", name="Get arrivals by IATA", tags=["Arrivals"])
def get_arrivals(IATA):
    """Returns a list of all arrivals for a specific IATA code \n
    Accepts an IATA code \n
    Returns list of all arrivals for specified IATA"""
    flights_db, client = mongo_connect()
    results = []

    IATA = IATA.upper()

    if (
        any(uk["IATA"] == IATA)
        or any(france["IATA"] == IATA)
        or any(italy["IATA"] == IATA)
    ):
        results = flights_db.find({"Arrival.AirportCode": IATA}, {"_id": False})

        if len(list(results.clone())) == 0:
            return {"No arrivals matching search criteria"}

        return list(results)
    else:
        return {"Error": "IATA code is invalid"}


@api.get("/arrivals/{country:str}", name="Get arrivals by country", tags=["Arrivals"])
def get_arrivals(country):
    """Returns a list of all arrivals for a country \n
    Accepts country (uk,france,italy) \n
    Returns list of all arrivals for country"""
    flights_db, client = mongo_connect()
    results = []

    arrival_country = country_selector(country.lower())

    if isinstance(arrival_country, str):
        return {"error": "country must be uk, france or italy"}

    results = flights_db.find(
        {"Arrival.AirportCode": {"$in": list(arrival_country["IATA"])}}, {"_id": False}
    )

    if len(list(results.clone())) == 0:
        return {"No arrivals matching search criteria"}

    return list(results)


@api.get(
    "/arrivals/{country:str}/{date:str}",
    name="Get arrivals by date by country",
    tags=["Arrivals"],
)
def get_arrivals(country, date):
    """Returns a list of arrivals on a specific date for a country \n
    Accepts country (uk,france,italy), date (YYYY-MM-DD) \n
    Returns list of arrivals on said date in country"""
    flights_db, client = mongo_connect()
    date = str(date)

    date_match = re.compile(r"(\d{4}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01]))")
    date_matched = date_match.search(date)

    if not date_matched:
        return {"Error": "Date does not match required format (YYYY-MM-DD)"}

    arrival_country = country_selector(country.lower())

    if isinstance(arrival_country, str):
        return {"error": "country must be uk, france or italy"}

    results = flights_db.find(
        {
            "Arrival.AirportCode": {"$in": list(arrival_country["IATA"])},
            "Arrival.Actual.Date": date_matched[0],
        },
        {"_id": False},
    )

    if len(list(results.clone())) == 0:
        return {"No arrivals matching search criteria"}

    return list(results)


@api.get(
    "/arrivals/{country:str}/{date:str}/{code:str}",
    name="Return arrivals by country by date and by status",
    tags=["Arrivals"],
)
def status_count(country, date, code):
    """Returns a count of arrival statuses for a country \n
    Accepts country (uk,france,italy), date(YYYY-MM-DD) and code (DV,FE,LD,CD,DL,OT) \n
    Returns list or arrivals by criteria
    """
    flights_db, client = mongo_connect()

    arrival_country = country_selector(country.lower())

    if isinstance(arrival_country, str):
        return {"error": "country must be uk, france or italy"}

    date = str(date)

    date_match = re.compile(r"(\d{4}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01]))")
    date_matched = date_match.search(date)

    if not date_matched:
        return {"Error": "Date does not match required format (YYYY-MM-DD)"}

    code = code_selector(code.upper())
    if code == "error":
        return {"error": "Arrival code invalid - must be DV,FE,LD,CD,DL,OT"}

    results = flights_db.find(
        {
            "Arrival.AirportCode": {"$in": list(arrival_country["IATA"])},
            "Arrival.Actual.Date": date_matched[0],
            "Status.Code": code,
        },
        {"_id": False},
    )

    if len(list(results.clone())) == 0:
        return {"No arrivals matching search criteria"}

    return list(results)


@api.get(
    "/codes",
    name="Return arrival code counts (uk, france, italy combined)",
    tags=["Codes"],
)
def get_status_codes():

    flights_db, client = mongo_connect()

    pipeline = [
        {"$group": {"_id": "$Status.Code", "count": {"$sum": 1}}},
        {"$project": {"_id": 1, "count": 1}},
    ]
    results = flights_db.aggregate(pipeline=pipeline)

    client.close()
    return list(results)


@api.get("/codes/all", name="Returns counts for all IATA codes", tags=["Codes"])
def status_count():
    """Returns a count of arrival status by all IATA codes"""
    flights_db, client = mongo_connect()

    pipeline = [
        {"$match": {"Arrival.AirportCode": {"$in": list(iata_codes["IATA"])}}},
        {
            "$group": {
                "_id": {"IATA": "$Arrival.AirportCode", "Status Code": "$Status.Code"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
        {
            "$project": {
                "_id": 0,
                "IATA": "$_id.IATA",
                "Status Code": "$_id.Status Code",
                "count": 1,
            }
        },
    ]

    results = flights_db.aggregate(pipeline=pipeline)
    client.close()
    return list(results)


@api.get(
    "/codes/",
    name="Return counts of arrivals by status by IATA location",
    tags=["Codes"],
)
def status_count(IATA: str):
    """Returns a count of arrival status by IATA code \n
    Accepts IATA code string \n
    Returns list of status counts for that location"""
    flights_db, client = mongo_connect()

    IATA = IATA.upper()

    pipeline = [
        {"$match": {"Arrival.AirportCode": IATA}},
        {
            "$group": {
                "_id": {"IATA": "$Arrival.AirportCode", "Status Code": "$Status.Code"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
        {
            "$project": {
                "_id": 0,
                "IATA": "$_id.IATA",
                "Status Code": "$_id.Status Code",
                "count": 1,
            }
        },
    ]
    if (
        any(uk["IATA"] == IATA)
        or any(france["IATA"] == IATA)
        or any(italy["IATA"] == IATA)
    ):
        results = flights_db.aggregate(pipeline=pipeline)
    else:
        return {"Error": "IATA code is invalid"}

    if len(list(results)) == 0:
        return {"No arrivals matching search criteria"}

    client.close()
    return list(results)


@api.get(
    "/codes/{country:str}",
    name="Return counts of arrivals by status by country",
    tags=["Codes"],
)
def status_count(country):
    """Returns a count of arrival statuses for a country \n
    Accepts country (uk,france,italy) \n
    Returns list of statuses and counts
    """
    flights_db, client = mongo_connect()

    status_country = country_selector(country.lower())

    if isinstance(status_country, str):
        return {"error": "country must be uk, france or italy"}

    pipeline = [
        {"$match": {"Arrival.AirportCode": {"$in": list(status_country["IATA"])}}},
        {
            "$group": {
                "_id": {"IATA": "$Arrival.AirportCode", "Status Code": "$Status.Code"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
        {
            "$project": {
                "_id": 0,
                "IATA": "$_id.IATA",
                "Status Code": "$_id.Status Code",
                "count": 1,
            }
        },
    ]
    results = flights_db.aggregate(pipeline=pipeline)
    client.close()
    return list(results)


@api.get(
    "/codes/{country:str}/{date:str}",
    name="Return counts of arrivals by status by country and date",
    tags=["Codes"],
)
def status_count(country, date):
    """Returns a count of arrival statuses for a country \n
    Accepts country (uk,france,italy) and date (YYYY-MM-DD) \n
    Returns list of statuses and counts
    """
    flights_db, client = mongo_connect()
    date = str(date)

    status_country = country_selector(country.lower())

    if isinstance(status_country, str):
        return {"error": "country must be uk, france or italy"}

    date_match = re.compile(r"(\d{4}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01]))")
    date_matched = date_match.search(date)

    if not date_matched:
        return {"Error": "Date does not match required format (YYYY-MM-DD)"}
    pipeline = [
        {
            "$match": {
                "Arrival.AirportCode": {"$in": list(status_country["IATA"])},
                "Arrival.Actual.Date": date_matched[0],
            }
        },
        {
            "$group": {
                "_id": {"IATA": "$Arrival.AirportCode", "Status Code": "$Status.Code"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
        {
            "$project": {
                "_id": 0,
                "IATA": "$_id.IATA",
                "Status Code": "$_id.Status Code",
                "count": 1,
            }
        },
    ]
    results = flights_db.aggregate(pipeline=pipeline)
    client.close()

    if len(list(results.clone())) == 0:
        return {"No arrivals matching search criteria"}

    return list(results)


@api.get("/flight/", name="Return arrivals by status code", tags=["Flight"])
def get_flight(code):
    """Returns arrivals by status code \n
    Accepts Status Code (DV,FE,LD,CD,DL,OT) \n
    Returns list of arrivals matching status code
    """

    flights_db, client = mongo_connect()

    code = code_selector(code.upper())
    if code == "error":
        return {"error": "Arrival code invalid - must be DV,FE,LD,CD,DL,OT"}

    results = flights_db.find(
        {
            "Status.Code": code,
        },
        {"_id": False},
    )

    if len(list(results.clone())) == 0:
        return {"No arrivals matching search criteria"}

    return list(results)


@api.get(
    "/flight/{flight_id:str}", name="Return arrivals by flight number", tags=["Flight"]
)
def get_flight(flight_id):
    """Returns arrivals for a specific flight number \n
    Accepts flight ID (integer) \n
    Returns list of arrivals
    """
    flights_db, client = mongo_connect()

    results = flights_db.find(
        {"OperatingCarrier.FlightNumber": flight_id}, {"_id": False}
    )

    if len(list(results.clone())) == 0:
        return {"No arrivals matching search criteria"}

    return list(results)


@api.get(
    "/flight/{flight_id:str}/{date:str}",
    name="Return arrivals by flight number on specific date",
    tags=["Flight"],
)
def get_flight(flight_id, date):
    """Returns arrivals for a specific flight number on a date \n
    Accepts flight ID (integer) and date (YYYY-MM-DD) \n
    Returns list of arrivals
    """
    flights_db, client = mongo_connect()
    date = str(date)

    date_match = re.compile(r"(\d{4}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01]))")
    date_matched = date_match.search(date)

    if not date_matched:
        return {"Error": "Date does not match required format (YYYY-MM-DD)"}

    results = flights_db.find(
        {
            "OperatingCarrier.FlightNumber": flight_id,
            "Arrival.Actual.Date": date_matched[0],
        },
        {"_id": False},
    )

    if len(list(results.clone())) == 0:
        return {"No arrivals matching search criteria"}

    return list(results)
