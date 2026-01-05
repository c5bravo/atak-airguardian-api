from typing import List, Dict, Any
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app

dummy_aircraft_data: List[Dict[str, Any]] = [
    {
        "aircraftId": "FIN321",
        "position": "35VMS12",
        "altitude": "surface",
        "speed": "fast",
        "direction": 90,
        "details": "4 Jet",
        "isExited": False,
    },
]

client = TestClient(app)


@patch("app.api.radar_api.fetch_practice_data")
def test_get_aircraft_data(mock_fetch: MagicMock) -> None:
    mock_fetch.return_value = dummy_aircraft_data

    response = client.get("/radar/aircraft")
    assert response.status_code == 200

    data = response.json()

    aircraft = data[0]
    assert aircraft["aircraftId"] == "FIN321"
    assert aircraft["position"] == "35VMS12"
    assert aircraft["altitude"] == "surface"
    assert aircraft["speed"] == "fast"
    assert aircraft["direction"] == 90
    assert aircraft["details"] == "4 Jet"
