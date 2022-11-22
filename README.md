# Lufthansa_Project
The Lufthansa data engineering project for Data Scientest

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


