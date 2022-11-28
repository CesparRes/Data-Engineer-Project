# Lufthansa_Project
The Lufthansa data engineering project for Data Scientest

Use:

To deploy the Dashboard, API and MongoDb download the docker-compose.yml and run "docker-compose up" in the terminal. After some delay and downloading 3 containers will be running. One will be the MongoDb database for the project, one will be the Dash dashboard, one the FastAPI API.

By visiting localhost:8000/docs you will find the API documentation, alternatively you can simply visit localhost:8000/status.
The dashboard can be found at localhost:5000

While the project includes the python DAG for airflow, the docker compose does not include airflow. To "scrape" the Lufthansa API you may use the new_test.py file with the command "python3 new_test > all_airports.txt" - this will take several minutes while it queries the Lufthansa API, and will output the "all_airports.txt" file which is a list of JSON objects. Next, you'll need to use the command "python3 flatten_data.py". This script changes the list of JSON objects into a single level list of individual JSON objects.

Finally, the command to insert into the MongoDB "mongoimport --db flight_info --collection flights --file airports_parsed.txt --jsonArray"

Ordinarily these would be executed via the DAG - or a cronjob on a daily schedule


Business cases

For the 3 major countries: - UK, France, Italy (This already gives us a huge load of Airports)

List flight arrivals for airports. Display status of flights arriving at airports by country/IATA code.
Count the total statuses of arrivals per country/IATA

Using MongDb - update daily but remain within the API limits (5 per second, 1000 per hour)


Project files:

docker-compose.yml - the docker compose file to deploy the project on other machines via containers
  This docker-compose spins up 2 containers, one for the FastAPI app that queries the database, and the second being the mongo DB containing the flight information.
  Ordinarily, the database would not be within the container itself, but for ease of use with this project the mongodb container also contains all the scraped flights.
 
new_test.py - the python script that makes the calls to Lufthansa API. This outputs a file (all_airports.txt).
flatten_data.py - python script that takes the all_airports.txt file and "flattens" it to return just a single list of all individual arrivals. This is because new_test.py returns a list that can contain a list of JSON objects as well as individual JSON objects. Outputs "airports_parsed.txt" file for insertion into mongo DB

main.py - the FastAPI app. 

check_request.py - external function used to ensure that the bearer token for the Lufthansa API is valid, returns the valid bearer token. Requests new bearer token if existing is invalid


