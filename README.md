# Lufthansa_Project
The Lufthansa data engineering project for Data Scientest

## Use:

First create the following folders in your home folder:
*dags*  - Airflow Dags folder
*plugins* - Airflow plugins folder
*logs* - Airflow logs folder

Then using chmod ensure they have full access (777)

Next using docker create the volume "mongo_data_volume". This is used to persist the mongoDB for when the containers are shut down.

Once this is done run:
docker-compose up airflow-init

This will take some time to initialise all the parts of airflow but once done we're ready to use:
docker-compose up

This will launcher the docker containers for
Airflow (and it's supporting workers/redis/server)
The project Dashboard
The project API
The project MongoDB database

You next need to copy the Lufthansa_DAG.py file into your "dags" folder.

Airflow can be found by visiting localhost:8080. The default login credentials of "airflow" are used for both username and password.
Once you've logged in, you can filter the DAG's for Datascientest or Lufthansa-Project to find the project DAG

The DAG is set to run at 6am everyday, but for project testing it can be manually triggered.
Upon triggering, three tasks are executed:

***API_calls*** - this runs the multiple requests to Lufthansa's provided API. The API returns flights for a specified time/IATA code, these can be individual flights or a list of flights. The task appends them all and saves them in a tempory file within the airflow container (all_airports.txt)

***Flatten_data*** - This task takes the all_airports file and converts it to a correctly represented JSON before "flattening" any lists of flights to individual flights so that the entire file now only consists of a single list of all flight arrivals. This is then stored in the temporary file "airports_parsed.txt"

***DB_insert*** - This simply loads the parsed flight data, checks if it is a single flight or many flights and inserts into the project mongodb database with the relevant insert command.

By visiting localhost:8000/docs you will find the project API documentation, alternatively you can simply visit localhost:8000/status for confirmation that the API is active, however to ensure the MongoDb is accessible you can use the API tests at localhost:8000/docs. (http://localhost:8000/codes should return counts of all flight arrival codes if the MongoDB is available for the API). There are a range of different endpoints to be used ranging from returning all flight codes from individual airports or countries, to checking total arrivals by country or by airport or date.

The dashboard can be found at localhost:5000. The dashboard will load with global totals for arrival codes at each airport, but you can enter individual dates in the input box on the left (For example 2022-10-29) - upon pressing return the map will update with the new totals. Entering 0 or All will display the dashboard data for the entire range of arrivals.

Note that should their be any configuration issues with Airflow, the API scrape/flatten and DB insert can all still be executed manually with the project files:
new_test.py (API scrape - requires download of check_request.py and the config.ini files. Python will also require configparser library installing)
flatten_data.py (Flatten the data)
db_insert.py (insertion into mongodb)
These 3 scripts are simply executed as is, and will produce "all_airports.txt" and "airports_parsed.txt" to process themselves.

These will all still work correctly with the docker containers once running, even if airflow fails.

## Business cases

For the 3 major countries: - UK, France, Italy (This already gives us a huge load of Airports)

List flight arrivals for airports. Display status of flights arriving at airports by country/IATA code.
Count the total statuses of arrivals per country/IATA

Using MongDb - update daily but remain within the API limits (5 per second, 1000 per hour)


## Project files:

The primary Dashboard and API files are in the subfolders and are the versions used for the docker containers. 

**docker-compose.yaml** - the docker compose file to deploy the project on other machines via containers
   This docker-compose spins up multiple containers, one for the FastAPI app that queries the database, one for the Dashboard container displaying flight arrivals visually, and the third being the mongo DB containing the flight information. The rest are containers for the Airflow automation/orchestration of DAG for database insertion
Ordinarily, the database would not be within the container itself, but for ease of use with this project the mongodb container also contains all the scraped flights. The database is persisted within the "mongo_data_volume" volume created with docker.

**Lufthansa_DAG.py** - the python file for automation of the API requests and database insertion. This file needs to be placed in your dags folder once airflow is running.

**main.py** - the source code for the FastAPI app. 

**lufthansa_dash.py** - The source code for the Dash dashboard app

### Legacy files:
This folder basically contains old legacy test files and working files from the project

**new_test.py** - the python script that makes the calls to Lufthansa API. This outputs a file (all_airports.txt).

**flatten_data.py** - python script that takes the all_airports.txt file and "flattens" it to return just a single list of all individual arrivals. This is because new_test.py - returns a list that can contain a list of JSON objects as well as individual JSON objects. Outputs "airports_parsed.txt" file for insertion into mongo DB

**check_request.py** - external function used to ensure that the bearer token for the Lufthansa API is valid, returns the valid bearer token. Requests new bearer token if existing is invalid

**IATA_codes.csv** - list of airport IATA codes imported by the scrape script in order to make the requests based on IATA - (only used by new_test.py)
**addlatlon.py** - script used to combine the latitude and longitude to the IATA list in order to be able to use locations for the dashboard map.
**IATA_scrape.py** - script used to scrape the IATA codes from external website
**GlobalAirportDatabase.csv** - file of IATA codes and lat/lon - found later in the project when the lat/lon coords were required.
**main.py** - local version of the API app for testing (localhost instead of container address)
**lufthansa_dash.py** - local version of the dashboard app for testing (localhost instead of container address)

