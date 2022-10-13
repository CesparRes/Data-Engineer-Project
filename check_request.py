import requests
from requests.auth import HTTPBasicAuth
import configparser
import json

conf = configparser.ConfigParser()
conf.read("config.ini")


def check_request(bearer_token):
    try:
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer " + bearer_token,
        }

        response = requests.get(
            "https://api.lufthansa.com/v1/mds-references/airports/FRA", headers=headers
        )

        ### if the response is 401 (not authorised) we'll request a new token
        if response.status_code == 401:
            # print('401 failure - getting new auth token')
            data = {
                "client_id": conf["lufthansa"]["clientId"],
                "client_secret": conf["lufthansa"]["clientSecret"],
                "grant_type": "client_credentials",
            }
            response = requests.post(
                "https://api.lufthansa.com/v1/oauth/token", data=data
            )

            ## probably this can be done more tidily, but essentially we turn the response into readable JSON
            temp_json = json.dumps(response.json())
            temp_resp = json.loads(temp_json)

            ## save the received bearer token into the bearer variable, and update config.ini with the updated bearer
            bearer = temp_resp["access_token"]
            conf["lufthansa"]["bearer"] = bearer
            with open("config.ini", "w") as configfile:
                conf.write(configfile)

    except:
        pass
    return conf["lufthansa"]["bearer"]
