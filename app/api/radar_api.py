import logging
from datetime import datetime
from typing import Dict, Optional, List, Any, TypedDict
from fastapi import HTTPException, APIRouter

import mgrs  # type: ignore

from app.tasks.radar_task import fetch_aircraft_data

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/radar", tags=["radar"])

mgrs_converter = mgrs.MGRS()


class TransformedAircraft(TypedDict, total=False):
    id: int
    aircraftId: Optional[str]
    position: Optional[str]
    altitude: Optional[str]
    speed: Optional[str]
    direction: int
    details: Optional[str]


def to_mgrs_typed(latitude: float, longitude: float) -> str:
    mgrs_string: str = mgrs_converter.toMGRS(latitude, longitude, True, 5)  # type: ignore[attr-defined]
    return mgrs_string


def convert_timestamp_to_datetime(timestamp: Optional[int]) -> Optional[str]:
    if timestamp is None:
        return None
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except Exception as e:
        logger.error(f"Error converting timestamp {timestamp}: {e}")
        return None


def convert_to_mgrs(longitude: Optional[float], latitude: Optional[float]) -> Optional[str]:
    if longitude is None or latitude is None:
        return None
    try:
        mgrs_string: str = to_mgrs_typed(latitude, longitude)
        return mgrs_string.strip().replace(" ", "")
    except Exception as e:
        logger.error(f"Error converting coordinates ({latitude}, {longitude}) to MGRS: {e}")
        return None


def shorten_mgrs(mgrs_full: str) -> str:
    if not mgrs_full or len(mgrs_full) < 5:
        return mgrs_full

    grid_zone = mgrs_full[:5]  # e.g. "36WVT"
    rest = mgrs_full[5:]

    mid = len(rest) // 2
    easting = rest[:mid]
    northing = rest[mid:]

    short = f"{grid_zone}{easting[0]}{northing[0]}"
    return short


def classify_altitude(altitude: Optional[float]) -> Optional[str]:
    if altitude is None:
        return None
    if altitude < 300:
        return "surface"
    elif altitude < 3000:
        return "low"
    else:
        return "high"


def classify_speed(velocity: Optional[float]) -> Optional[str]:
    if velocity is None:
        return None
    if velocity < 140:
        return "slow"
    elif velocity < 280:
        return "fast"
    else:
        return "supersonic"


def more_details(aircraft: Optional[Dict[str, Any]]) -> Optional[str]:
    if not aircraft:
        return None

    callsign = aircraft.get("callsign")
    origin_country = aircraft.get("origin_country")

    if not isinstance(callsign, str) or not isinstance(origin_country, str):
        return None

    return f"This aircraft[{callsign}] from [{origin_country}] and it is civilian aircraft."


def transform_aircraft(aircraft: Dict[str, Any]) -> TransformedAircraft:
    true_track_raw = aircraft.get("true_track")
    try:
        true_track = int(true_track_raw) if true_track_raw is not None else 0
    except (ValueError, TypeError):
        true_track = 0

    transformed: TransformedAircraft = {
        "id": 0,
        "aircraftId": aircraft.get("callsign"),
        "position": convert_to_mgrs(aircraft.get("longitude"), aircraft.get("latitude")),
        "altitude": classify_altitude(aircraft.get("baro_altitude")),
        "speed": classify_speed(aircraft.get("velocity")),
        "direction": true_track,
        "details": more_details(aircraft),
    }
    return transformed


def filter_on_ground(aircraft: Dict[str, Any]) -> bool:
    # Only aircraft not on ground
    return not bool(aircraft.get("on_ground"))


@router.get("/aircraft")
def get_aircraft_data() -> List[TransformedAircraft]:
    try:
        data = fetch_aircraft_data()
        filtered_data = list(filter(filter_on_ground, data))
        transformed_aircraft = [transform_aircraft(ac) for ac in filtered_data]

        if not transformed_aircraft:
            raise HTTPException(status_code=404, detail="No aircraft found")

        return transformed_aircraft
    except Exception as e:
        logger.error(f"Error retrieving aircraft data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
