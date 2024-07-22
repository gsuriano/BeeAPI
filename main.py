"""Source code of the application"""
from datetime import datetime, timedelta
from typing import List
import os
import re
import ast
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
import pymemcache

load_dotenv()
app = flask.Flask(__name__)
memcached_client = pymemcache.client.Client(('memcached', 11211))

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

def validate(response: dict, key: str, stop: int) -> List[float]:
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
        if len(res) == stop:
            break
    if len(res) < stop:
        return None
    return res

def parse_datetime(match):
    """
    Function to parse datetime from a match
    """

    return datetime(
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3)),
        int(match.group(4)),
        int(match.group(5)),
        int(match.group(6)),
        int(match.group(7))
    )

def parse_cache(cached_data: str) -> dict:
    """
    Function to parse cache considering the value of avg temp and timestamp
    """
    datetime_regex = r"datetime\.datetime\((\d+), (\d+), (\d+), (\d+), (\d+), (\d+), (\d+)\)"
    match = re.search(datetime_regex, cached_data)

    if match:
        timestamp_str = match.group(0)
        timestamp = parse_datetime(match)
        
        # Replace the datetime part in the string with a placeholder
        cached_data = cached_data.replace(timestamp_str, '"TIMESTAMP_PLACEHOLDER"')

    # Step 3: Safely evaluate the modified string to a dictionary
    data = ast.literal_eval(cached_data)

    # Replace the placeholder with the actual datetime object
    data['timestamp'] = timestamp

    # `data` now contains the dictionary
    print(data)

    return data

@app.route("/temperature")
@REQUEST_TIME.time()
def temperature():
    """ 
    Return current average temperature based on all senseBox data.
    Ensure that the data is no older 1 hour.
    """
    start_time = datetime.now()
    cached_data = memcached_client.get("temperature")
    if cached_data:
        cached_data = cached_data.decode('utf-8')
        cached_data = parse_cache(cached_data)  # Convert string back to dictionary
        REQUEST_COUNTER.inc()
        latency = (datetime.now() - start_time).total_seconds()
        REQUEST_HISTOGRAM.observe(latency)
        return flask.jsonify({'data': cached_data['value'], 'source': 'cache'})

    central_id = os.getenv("senseBoxId")
    url = os.getenv("URL_API")

    response = requests.get(url + central_id, timeout=600).json()

    coordinates_list = response["loc"][0]['geometry']['coordinates']

    coordinates = f"{coordinates_list[0]},{coordinates_list[1]}"

    response = requests.get(url+"?near="+coordinates+"&maxDistance=5000", timeout=600).json()

    temperatures = validate(response,"Temperatur",3)

    if temperatures is None:
        REQUEST_COUNTER.inc()
        latency = (datetime.now() - start_time).total_seconds()
        REQUEST_HISTOGRAM.observe(latency)
        return "Data older than 1 hour whitin 5000 meters"
    avg = sum(temperatures) / len(temperatures)
    if avg <= 10:
        status = "Too cold"
    elif avg <= 36 :
        status = "Good"
    elif avg > 36:
        status = "Too hot"
    REQUEST_COUNTER.inc()
    timestamp = datetime.now()
    latency = (timestamp - start_time).total_seconds()
    REQUEST_HISTOGRAM.observe(latency)
    data = {
            "avg": avg,
            "status": status
            }
    
    memcached_client.set("temperature", {'value': data, 'timestamp': timestamp}, expire=60)
    return flask.jsonify({
        "data": data,
        "source": "api"})

@app.route("/metrics")
@REQUEST_TIME.time()
def metrics():
    """
    Returns default Prometheus metrics about the app.
    """
    return flask.Response(generate_latest(REGISTRY), mimetype=CONTENT_TYPE_LATEST)

@app.route("/readyz")
@REQUEST_TIME.time()
def readyz() -> str:
    """Function printing index."""
    REQUEST_COUNTER.inc()
    central_id = os.getenv("senseBoxId")
    url = os.getenv("URL_API")

    response = requests.get(url + central_id, timeout=600).json()

    coordinates_list = response["loc"][0]['geometry']['coordinates']

    coordinates = f"{coordinates_list[0]},{coordinates_list[1]}"

    response = requests.get(url+"?near="+coordinates+"&maxDistance=5000", timeout=600).json()

    stop = int(len(response)/2)+1
    temperatures = validate(response,"Temperatur",stop)

    if temperatures is None:
        REQUEST_COUNTER.inc()
        response = {
            'message': "More than half sensor are not accessible",
            'status': 400
        }
        return flask.Response(flask.jsonify(response), status=400)
    
    cached_data = memcached_client.get("temperature")
    
    if cached_data:
        cached_data = cached_data.decode('utf-8')
        cached_data = parse_cache(cached_data) # Convert string back to dictionary
        current_time = datetime.now()
        cache_time = cached_data['timestamp']
        if (current_time - cache_time).total_seconds() <= 300:
            REQUEST_COUNTER.inc()
            response = {
                'message': "Cache older than 5 minutes",
                'status': 400
            }
            return flask.Response(flask.jsonify(response), status=400)
    
    return flask.Response("OK")


@app.route("/")
@REQUEST_TIME.time()
def index() -> str:
    """Function printing index."""
    REQUEST_COUNTER.inc()
    return flask.Response("Hello World!")

if __name__ == "__main__":
    app.run(debug=True)
