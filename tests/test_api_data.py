from typing import Any, Dict, List
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.schema_marine_traffic import ShipFeature, Geometry, ShipProperties

client = TestClient(app)


def create_dummy_ship_feature() -> ShipFeature:
    return ShipFeature(
        mmsi=219598000,
        type="Feature",
        geometry=Geometry(
            type="Point",
            coordinates=[24.9667, 60.1666],  # [Lon, Lat]
        ),
        properties=ShipProperties(
            mmsi=219598000,
            sog=15.5,
            cog=346.5,
            navStat=1,
            rot=4,
            posAcc=True,
            raim=True,
            heading=79,
            timestamp=59,
            timestampExternal=1659212938646,
        ),
    )


dummy_practice_data: List[Dict[str, Any]] = [
    {
        "id": 1,
        "aircraftId": "TEST-PRACTICE",
        "position": "35VMS12",
        "altitude": "low",
        "speed": "slow",
        "direction": 90,
        "details": "Practice Data",
        "isExited": False,
        "type": "practiceTool",
    }
]

dummy_opensky_data: List[Dict[str, Any]] = [
    {
        "callsign": "FIN123",
        "longitude": 24.0,
        "latitude": 60.0,
        "baro_altitude": 5000,
        "velocity": 200,
        "true_track": 180,
        "on_ground": False,
        "origin_country": "Finland",
        "isExited": False,
    }
]


@patch("app.api.radar_api.fetch_fin_marine_traffic_data")
@patch("app.api.radar_api.fetch_practice_data")
@patch("app.api.radar_api.fetch_aircraft_data")
def test_get_aircraft_data_combined(
    mock_fetch_opensky: MagicMock,
    mock_fetch_practice: MagicMock,
    mock_fetch_fin_marine: MagicMock,
) -> None:
    mock_fetch_practice.return_value = dummy_practice_data
    mock_fetch_opensky.return_value = dummy_opensky_data
    mock_fetch_fin_marine.return_value = [create_dummy_ship_feature()]

    response = client.get("/radar/aircraft")

    assert response.status_code == 200
    data: List[Dict[str, Any]] = response.json()

    assert len(data) == 3

    practice = next(item for item in data if item["type"] == "practiceTool")
    assert practice["aircraftId"] == "TEST-PRACTICE"

    aircraft = next(item for item in data if item["type"] == "openSky")
    assert aircraft["aircraftId"] == "FIN123"
    assert aircraft["altitude"] == "high"

    ship = next(item for item in data if item["type"] == "marineTraffic")
    assert ship["aircraftId"] == "219598000"
    assert ship["altitude"] == "surface"
    assert ship["speed"] == "slow"
    assert "MMSI: 219598000" in ship["details"]
