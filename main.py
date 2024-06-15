"""Source code of the application"""
from datetime import datetime, timedelta
from typing import List
import os
from prometheus_client import (generate_latest,
                               REGISTRY,
                               CONTENT_TYPE_LATEST,
                               Counter,
                               Summary,
                               Histogram
                        )
from dotenv import load_dotenv
import flask
import requests

load_dotenv()
app = flask.Flask(__name__)

# Create a metric to track time spent and requests made.
# These are custom metrics defined by you.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
REQUEST_COUNTER = Counter('request_count', 'Total number of requests')
REQUEST_HISTOGRAM = Histogram('request_latency_seconds',
                              'Request latency',
                              buckets=[0.3, 1.5, 3.0, 10.5])

@app.route("/version")
@REQUEST_TIME.time()
def version() -> str:
    """Function printing BeeAPI version."""
    REQUEST_COUNTER.inc()
    return flask.Response(os.getenv("version"))

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
                sensor_url = url + sensebox["_id"]+"/sensors/"+sensor["_id"]
                measurement = requests.get(sensor_url,timeout=600).json()
                if measurement.get('lastMeasurement') is not None:
                    measurement_time_str = measurement['lastMeasurement']['createdAt']
                    measument_time = datetime.strptime(
                        measurement_time_str,
                        "%Y-%m-%dT%H:%M:%S.%fZ"
                    )

                    # Sensor save the time of recording with another timezone
                    # so we need to transpose by two hours
                    measument_time = measument_time + timedelta(hours=2)
                    if measument_time > now - timedelta(hours=1) :
                        res.append(float(measurement['lastMeasurement']['value']))
        if len(res) == 3:
            break
    if len(res) < 3:
        return None
    return res

@app.route("/temperature")
@REQUEST_TIME.time()
def temperature():
    """ 
    Return current average temperature based on all senseBox data.
    Ensure that the data is no older 1 hour.
    """
    start_time = datetime.now()
    central_id = os.getenv("senseBoxId")
    url = os.getenv("URL_API")

    response = requests.get(url + central_id, timeout=600).json()

    coordinates_list = response["loc"][0]['geometry']['coordinates']

    coordinates = f"{coordinates_list[0]},{coordinates_list[1]}"

    response = requests.get(url+"?near="+coordinates+"&maxDistance=5000", timeout=600).json()

    temperatures = validate(response,"Temperatur")

    if temperatures is None:
        REQUEST_COUNTER.inc()
        latency = (datetime.now() - start_time).total_seconds()
        REQUEST_HISTOGRAM.observe(latency)
        return "Data older than 1 hour whitin 5000 meters"
    avg = sum(temperatures) / len(temperatures)
    if avg <= 10:
        status = "Too cold"
    elif avg <= 36 and avg > 10:
        status = "Good"
    elif avg > 36:
        status = "Too hot"
    REQUEST_COUNTER.inc()
    latency = (datetime.now() - start_time).total_seconds()
    REQUEST_HISTOGRAM.observe(latency)
    return flask.jsonify({
        "avg": avg,
        "status": status
        })

@app.route("/metrics")
@REQUEST_TIME.time()
def metrics():
    """
    Returns default Prometheus metrics about the app.
    """
    return flask.Response(generate_latest(REGISTRY), mimetype=CONTENT_TYPE_LATEST)

@app.route("/")
@REQUEST_TIME.time()
def index() -> str:
    """Function printing index."""
    REQUEST_COUNTER.inc()
    return flask.Response("Hello World!")

if __name__ == "__main__":
    app.run()
