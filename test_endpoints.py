from main import version
import requests

def test_version():
    expVersion = "v0.0.1"
    assert expVersion == version()

def test_temperature():
    expOutput = "Data older than 1 hour whitin 5000 meters"
    assert requests.get("http://localhost:5000/temperature").text == expOutput

