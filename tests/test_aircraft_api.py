import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

dummy_aircraft_data = [
    {
        "icao24": "abc123",
        "callsign": "TEST123",
        "time_position": 1698500000,
        "last_contact": 1698500100,
        "longitude": 24.93545,
        "latitude": 60.16952,
        "baro_altitude": 250,
        "velocity": 150,
        "true_track": 90,
        "origin_country": "Finland",
        "on_ground": False,
    },
    {
        "icao24": "def456",
        "callsign": "GROUND1",
        "longitude": 24.93545,
        "latitude": 60.16952,
        "baro_altitude": 50,
        "velocity": 10,
        "true_track": 180,
        "origin_country": "Finland",
        "on_ground": True,
    },
]

client = TestClient(app)


@patch("app.api.radar_api.fetch_aircraft_data")  # patch here!
def test_get_aircraft_data(mock_fetch):
    mock_fetch.return_value = dummy_aircraft_data

    response = client.get("/radar/aircraft")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1  # Only the aircraft not on the ground should be included

    aircraft = data[0]
    assert aircraft["id"] == "abc123"
    assert aircraft["aircraftId"] == "TEST123"
    assert aircraft["altitude"] == "surface"  # This depends on your classify_altitude logic
    assert aircraft["speed"] == "fast"
    assert aircraft["direction"] == 90
    assert "details" in aircraft
