"""Unit tests of endpoint of the flask app"""
import requests

def test_version() -> None:
    """Unit test of /version endpoint"""
    expversion = "v0.0.1"
    assert requests.get("http://localhost:5000/version", timeout=600).text == expversion 

def test_temperature():
    """Unit test of /temperature endpoint"""
    expoutput = "Data older than 1 hour whitin 5000 meters"
    assert requests.get("http://localhost:5000/temperature", timeout=600).text == expoutput
