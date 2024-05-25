"""Source code of the application"""
from datetime import datetime, timedelta
from typing import List
import os
import flask
import requests

app = flask.Flask(__name__)

@app.route("/version")
def version() -> str:
    """Function printing BeeAPI version."""
    with open("version.txt", encoding="utf-8") as f:
        return f.read()

def validate(response: dict, key: str) -> List[float]:
    """
    Validate that the data is no older 1 hour.
    Referencing to key attribute in json response.
    """
    url = os.getenv("URL_API")
    now = datetime.now()
    res = []
    for sensebox in response:
        for sensor in sensebox["sensors"]:
            if sensor["title"] == key:
                measurement = requests.get(url + sensebox["_id"]+"/sensors/"+sensor["_id"],timeout=600).json()
                if measurement['lastMeasurement'] is not None:
                    measurement_time_str = measurement['lastMeasurement']['createdAt']
                    measument_time = datetime.strptime(measurement_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    if measument_time > now - timedelta(hours=1) :
                        res.append(measurement['lastMeasurement']['value'])
        if len(res) == 3:
            break
    if len(res) < 3:
        return None
    return res

@app.route("/temperature")
def temperature():
    """ 
    Return current average temperature based on all senseBox data.
    Ensure that the data is no older 1 hour.
    """
    with open("ids.txt", encoding="utf-8") as f:
        central_id = f.readline().strip()
    url = os.getenv("URL_API")

    response = requests.get(url + central_id, timeout=600).json()

    coordinates_list = response["loc"][0]['geometry']['coordinates']

    coordinates = f"{coordinates_list[0]},{coordinates_list[1]}"

    response = requests.get(url+"?near="+coordinates+"&maxDistance=5000", timeout=600).json()

    temperatures = validate(response,"Temperatur")

    if temperatures is None:
        return "Data older than 1 hour whitin 5000 meters"
    return sum(temperatures) / len(temperatures)

@app.route("/")
def index() -> str:
    """Function printing index."""
    return "Hello World!"

if __name__ == "__main__":
    app.run()
