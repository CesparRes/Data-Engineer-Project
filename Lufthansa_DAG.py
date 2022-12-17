from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.providers.mongo.hooks.mongo import MongoHook
from pymongo import MongoClient
import requests
from requests.auth import HTTPBasicAuth
import re
import json
from bson import json_util
import pandas as pd
import configparser
import time
import asyncio
from datetime import datetime, timedelta

client = MongoClient(host="Lufthansa_db", port=27017, authSource="admin")
db = client.flight_info
flights = db.flights

IATAs = [
    "AOI",
    "BDS",
    "BHX",
    "BLQ",
    "CAG",
    "CDG",
    "CTA",
    "FCO",
    "FLR",
    "GLA",
    "GOA",
    "LHR",
    "LIN",
    "LYS",
    "MAN",
    "MRS",
    "MXP",
    "NAP",
    "NCE",
    "OLB",
    "ORY",
    "SUF",
    "TLS",
    "TRN",
    "TRS",
    "VCE",
    "VRN",
]

my_lufthansa_dag = DAG(
    dag_id="Lufthansa_scrape_dag",
    tags=["Datascientest", "Lufthansa-Project"],
    schedule_interval="0 6 */1 * *",
    default_args={"owner": "airflow", "start_date": days_ago(0, 1)},
    catchup=False,
)


def get_bearer():
    data = {
        "client_id": "3xeucrdc57sceex6dnpdpm4j",
        "client_secret": "FZt7b9XES8XjwKGy3BNc",
        "grant_type": "client_credentials",
    }
    response = requests.post("https://api.lufthansa.com/v1/oauth/token", data=data)

    ## probably this can be done more tidily, but essentially we turn the response into readable JSON
    temp_json = json.dumps(response.json())
    temp_resp = json.loads(temp_json)
    bearer = temp_resp["access_token"]

    return bearer


def api_scrape():
    results = []
    result_out = []
    data_out = []

    day_arg = datetime.today() - timedelta(days=1)
    day_arg = day_arg.strftime("/%Y-%m-%dT")

    times = ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"]

    print(day_arg)

    bearer = get_bearer()
    print("Bearer created is: ", bearer)

    headers = {
        "accept": "application/json",
        "authorization": "Bearer " + bearer,
    }

    for code in IATAs:
        for dtime in times:
            response = requests.get(
                "https://api.lufthansa.com/v1/operations/customerflightinformation/arrivals/"
                + code
                + day_arg
                + dtime,
                headers=headers,
            )
            print(
                "requested with code: {0}, day_arg: {1}, dtime: {2}, bearer:{3}".format(
                    code, day_arg, dtime, headers["authorization"]
                )
            )
        time.sleep(0.2)

        ## if there are no arrivals within a window, we get the resource not found error, so we want to filter these out of the response
        ## we also want to filter out any "error" messages
        if "ResourceNotFound" and "Error" not in response.text:
            results.append(response)

    print("results is: ", results)
    for result in results:
        result_out.append(json.dumps(result.json(strict=False), ensure_ascii=True))

    print("result_out is: ", result_out)
    with open("/tmp/all_airports.txt", "w") as f:
        f.write(str(result_out))


def flatten_data():
    data_out = []

    with open("/tmp/all_airports.txt", "r", encoding="utf-8") as f:
        data = f.read()

    data = re.sub("}\n{", "},{", data)
    data = re.sub("\['\{", "[{", data)
    data = re.sub("', '", ",", data)
    data = re.sub("'\]", "]", data)

    data = json.loads(data)

    ## loop through the list of flight details and append just the flight departure information into our list
    for i in range(len(data)):
        ## if this json entry is a list (IE the request returned more than one flight) - loop through the list and append each individually
        if type(data[i]["FlightInformation"]["Flights"]["Flight"]) == list:
            for item in data[i]["FlightInformation"]["Flights"]["Flight"]:
                data_out.append(item)
        else:
            data_out.append(data[i]["FlightInformation"]["Flights"]["Flight"])

    print("flattened data is: ", data_out)
    with open("/tmp/airports_parsed.txt", "w") as f:
        json.dump(data_out, f)


def writetoMongo():

    with open("/tmp/airports_parsed.txt", "r") as f:
        data = json.load(f)

    print("data contains: ", data)
    print("data is type: ", type(data))

    if isinstance(data, list):
        flights.insert_many(data)
    else:
        flights.insert_one(data)


task1 = PythonOperator(
    task_id="API_calls", python_callable=api_scrape, retries=0, dag=my_lufthansa_dag
)

task2 = PythonOperator(
    task_id="Flatten_data", python_callable=flatten_data, dag=my_lufthansa_dag
)

task3 = PythonOperator(
    task_id="DB_insert", python_callable=writetoMongo, dag=my_lufthansa_dag
)

task1 >> task2
task2 >> task3
