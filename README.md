# Lufthansa_Project
The Lufthansa data engineering project for Data Scientest

Use:

The Lufthansa API is first scraped with the "new_test.py" via command "python3 new_test.py > all_airports.txt" - this will then take around 5 minutes to make the API calls and produce the all_airports.txt file. Following this, "python3 flatten_data.py" flattens all the list of JSON objects in the all_airports.txt file into a list of singular (valid) JSON objects. The data is then inserted into the mongoDb database with "mongoimport --db flight_info --collection flights --file airports_parsed.txt --jsonArray".

There are several ways the above could be handled in automation - either via a cronjob running each task sequentially, an airflow DAG running the bash commands for the scripts, or the python scripts as airflow code tasks directly within the DAG . Included in the project files is a DAG file for running them as bash tasks, but as this project does not contain the airflow container these have all been handled manually over multiple days during the project. The cadence for the Lufthansa API scrape in this case is daily, but it could just as easily be setup to be every several hours to lighten the burden of the API calls.

To deploy the Dashboard, API and MongoDb download the included docker-compose.yml and run "docker-compose up" in the terminal. After some delay and downloading 3 containers will be running. One will be the MongoDb database for the project, one will be the Dash dashboard, one the FastAPI API.

By visiting localhost:8000/docs you will find the API documentation, alternatively you can simply visit localhost:8000/status for confirmation that the API is active, however to ensure the MongoDb is accessible you can use the API tests at localhost:8000/docs. (http://localhost:8000/codes should return counts of all flight arrival codes if the MongoDB is available for the API)

The dashboard can be found at localhost:5000. The dashboard will load with global totals for arrival codes at each airport, but you can enter individual dates in the input box on the left (For example 2022-10-29) - upon pressing return the map will update with the new totals.


Business cases

For the 3 major countries: - UK, France, Italy (This already gives us a huge load of Airports)

List flight arrivals for airports. Display status of flights arriving at airports by country/IATA code.
Count the total statuses of arrivals per country/IATA

Using MongDb - update daily but remain within the API limits (5 per second, 1000 per hour)


Project files:

The primary Dashboard and API files are in the subfolders and are the versions used for the docker containers. 

docker-compose.yml - the docker compose file to deploy the project on other machines via containers
  This docker-compose spins up 2 containers, one for the FastAPI app that queries the database, and the second being the mongo DB containing the flight information.
  Ordinarily, the database would not be within the container itself, but for ease of use with this project the mongodb container also contains all the scraped flights.
 
new_test.py - the python script that makes the calls to Lufthansa API. This outputs a file (all_airports.txt).
flatten_data.py - python script that takes the all_airports.txt file and "flattens" it to return just a single list of all individual arrivals. This is because new_test.py returns a list that can contain a list of JSON objects as well as individual JSON objects. Outputs "airports_parsed.txt" file for insertion into mongo DB

main.py - the FastAPI app. 

lufthansa_dash.py - The source code for the Dash dashboard app

lufthansa_DAG.py - the DAG file that would be used to automate the API scrape and database insertion if we were running Airflow.

check_request.py - external function used to ensure that the bearer token for the Lufthansa API is valid, returns the valid bearer token. Requests new bearer token if existing is invalid

Additional files:
addlatlon.py - script used to combine the latitude and longitude to the IATA list in order to be able to use locations for the dashboard map.
IATA_scrape.py - script used to scrape the IATA codes from external website
GlobalAirportDatabase.csv - file of IATA codes and lat/lon - found later in the project when the lat/lon coords were required.

