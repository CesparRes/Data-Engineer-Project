FROM debian:latest
RUN apt-get update && apt-get install python3-pip -y && pip install fastapi uvicorn && pip install pandas
RUN pip install pymongo
ADD main.py /files/main.py
ADD iata_codes.csv /files/iata_codes.csv
WORKDIR /files
EXPOSE 8000
CMD uvicorn main:api --host 0.0.0.0 --proxy-headers --reload 
