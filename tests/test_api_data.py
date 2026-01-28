from typing import List, Dict, Any
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

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
        MMSI="538003913",
        IMO="9470959",
        SHIP_ID="713139",
        LAT=60.1666,
        LON=24.9667,
        SPEED=12.5,
        HEADING=104,
        COURSE=41,
        STATUS="0",
        TIMESTAMP=datetime.now(),
        DSRC="TER",
        UTC_SECONDS=45,
        MARKET="SUPPORTING VESSELS",
        SHIPNAME="SUNNY STAR",
        SHIPTYPE="89",
        CALLSIGN="V7TZ6",
        FLAG="MH",
        LENGTH=184,
        WIDTH=27.43,
        GRT=23313,
        DWT=37857,
        DRAUGHT=95,
        YEAR_BUILT="2010",
        SHIP_COUNTRY="Marshall Is",
        SHIP_CLASS="HANDYSIZE",
        ROT=0,
        TYPE_NAME="Oil/Chemical Tanker",
        AIS_TYPE_SUMMARY="Tanker",
        DESTINATION="HELSINKI",
        L_FORE=5,
        W_LEFT=5,
        CURRENT_PORT="HELSINKI",
        LAST_PORT="AGIOI THEODOROI",
        CURRENT_PORT_ID="101",
        CURRENT_PORT_UNLOCODE="FIHEL",
        CURRENT_PORT_COUNTRY="FI",
        LAST_PORT_ID="29",
        LAST_PORT_UNLOCODE="GRAGT",
        LAST_PORT_COUNTRY="GR",
        NEXT_PORT_ID="",
        NEXT_PORT_UNLOCODE="",
        NEXT_PORT_NAME="",
        NEXT_PORT_COUNTRY="",
        DISTANCE_TO_GO=0,
        DISTANCE_TRAVELLED=74,
        AVG_SPEED=12.6,
        MAX_SPEED=13.2,
        ETA=None,
        LAST_PORT_TIME=None,
        ETA_CALC=None,
        ETA_UPDATED=None,
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
    assert aircraft["type"] == "practiceTool"

    # ---- Ship assertions ----
    ship: Dict[str, Any] = data[1]
    assert ship["aircraftId"] == "713139"
    assert ship["type"] == "marine"
    assert ship["speed"] == "slow"
    assert "SUNNY STAR" in ship["details"]
