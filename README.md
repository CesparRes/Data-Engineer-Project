# Lufthansa_Project
The Lufthansa data engineering project for Data Scientest

Business cases

For the 5 major countries: - UK, France, Spain, Germany, Italy (This already gives us a huge load of Airports)

Given an airport can we calculate the latency/delayed flights - over a period of time? - how much delay?
List flights between airports? What flights are available between select airports?

Using MongDb - update daily but remain within the API limits (5 per second, 1000 per hour)


Project files:

check_request.py - this is an external library function which simply makes a request to ensure bearer token is valid. If not, it returns the new bearer
