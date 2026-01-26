from typing import List, Dict, Any
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.main import app
from app.schemas.schema_marine_traffic import MarineTrafficPosition

client = TestClient(app)

# Dummy practice aircraft data
dummy_aircraft_data: List[Dict[str, Any]] = [
    {
        "id": 0,
        "aircraftId": "FIN321",
        "position": "35VMS12",
        "altitude": "surface",
        "speed": "fast",
        "direction": 90,
        "details": "4 Jet",
        "isExited": False,
        "type": "practiceTool",
    }
]

# Dummy marine traffic ship data
dummy_marine_data = [
    MarineTrafficPosition(
        SHIP_ID="713139",
        LAT=37.38843,
        LON=23.87123,
        SPEED=6,
        HEADING=104,
        COURSE=41,
        TIMESTAMP=datetime.now(timezone.utc),
        UTC_SECONDS=45,
        SHIPNAME="SUNNY STAR",
        SHIP_COUNTRY="Marshall Is",
        type="marine"
    )
]


@patch("app.api.radar_api.fetch_marine_traffic_data")
@patch("app.api.radar_api.fetch_practice_data")
def test_get_aircraft_data(
    mock_fetch_practice: MagicMock,
    mock_fetch_marine: MagicMock,
) -> None:
    mock_fetch_practice.return_value = dummy_aircraft_data
    mock_fetch_marine.return_value = dummy_marine_data

    response = client.get("/radar/aircraft")
    assert response.status_code == 200

    data: List[Dict[str, Any]] = response.json()
    assert len(data) == 2

    # ---- Aircraft assertions ----
    aircraft: Dict[str, Any] = data[0]
    assert aircraft["aircraftId"] == "FIN321"
    assert aircraft["position"] == "35VMS12"
    assert aircraft["altitude"] == "surface"
    assert aircraft["speed"] == "fast"
    assert aircraft["direction"] == 90
    assert aircraft["details"] == "4 Jet"
    assert aircraft["type"] == "practiceTool"

    # ---- Ship assertions ----
    ship: Dict[str, Any] = data[1]
    assert ship["aircraftId"] == "713139"
    assert ship["altitude"] == "surface"
    assert ship["speed"] == "slow"
    assert ship["direction"] == 104
    assert "SUNNY STAR" in ship["details"]
    assert ship["type"] == "marine"
