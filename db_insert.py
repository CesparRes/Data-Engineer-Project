from pymongo import MongoClient
from pprint import pprint
import pandas as pd
import json
from bson import json_util

## The db is local - this may need to change once we create a docker container running it
client = MongoClient(
    host='127.0.0.1',
    port=27017,
    authSource='admin'
)

db = client.flight_info
flights = db.flights

with open("airports_parsed.txt","r") as f:
        data = json.load(f)

if isinstance(data, list):
    flights.insert_many(data) 
else:
    flights.insert_one(data)
