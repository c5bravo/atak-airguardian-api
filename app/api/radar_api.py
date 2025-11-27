import logging
from datetime import datetime
from typing import Dict, Optional

import mgrs
from fastapi import APIRouter

from app.tasks.radar_task import fetch_aircraft_data

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/radar", tags=["radar"])

# Initialize MGRS converter
mgrs_converter = mgrs.MGRS()


def convert_timestamp_to_datetime(timestamp: Optional[int]) -> Optional[str]:
    """Convert Unix timestamp to dd.mm.yyyy hh:mm:ss format"""
    if timestamp is None:
        return None
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except Exception as e:
        logger.error(f"Error converting timestamp {timestamp}: {e}")
        return None


def convert_to_mgrs(longitude: Optional[float], latitude: Optional[float]) -> Optional[str]:
    """Convert longitude/latitude to full-precision MGRS format"""
    if longitude is None or latitude is None:
        return None

    try:
        mgrs_string = mgrs_converter.toMGRS(latitude, longitude, True, 1)
        return mgrs_string.strip().replace(" ", "")
    except Exception as e:
        logger.error(f"Error converting coordinates ({latitude}, {longitude}) to MGRS: {e}")
        return None


def shorten_mgrs(mgrs_full: str) -> str:
    """Return a readable shortened MGRS (auto-adjust precision)."""
    if not mgrs_full or len(mgrs_full) < 5:
        return mgrs_full

    grid_zone = mgrs_full[:5]  # e.g. "36WVT"
    rest = mgrs_full[5:]

    mid = len(rest) // 2
    easting = rest[:mid]
    northing = rest[mid:]

    short = f"{grid_zone}{easting[1]}{northing[1]}"
    return short


def classify_altitude(altitude: Optional[float]) -> Optional[str]:
    """Classify altitude in meters"""
    if altitude is None:
        return None

    if altitude < 300:
        return "surface"
    elif altitude < 3000:
        return "low"
    else:
        return "high"


def classify_speed(velocity: Optional[float]) -> Optional[str]:
    """Classify speed in m/s"""
    if velocity is None:
        return None

    if velocity < 140:
        return "slow"
    elif velocity < 280:
        return "fast"
    else:
        return "supersonic"


def more_details(aircraft: Optional[Dict]) -> Optional[str]:
    return f"This aircraft[{aircraft.get('callsign')}] from [{aircraft.get('origin_country')}] and it is civilian aircraft."


def transform_aircraft(aircraft: Dict) -> Dict:
    """Transform a single aircraft object to the new format"""

    transformed = {
        "id": 0,
        "aircraftId": aircraft.get("callsign"),
        # "time_position": convert_timestamp_to_datetime(aircraft.get("time_position")),
        # "last_contact": convert_timestamp_to_datetime(aircraft.get("last_contact")),
        "position": convert_to_mgrs(aircraft.get("longitude"), aircraft.get("latitude")),
        "altitude": classify_altitude(aircraft.get("baro_altitude")),
        "speed": classify_speed(aircraft.get("velocity")),
        "direction": int(aircraft.get("true_track")),
        "details": more_details(aircraft),
    }

    return transformed


def filter_on_ground(aircraft: Dict) -> bool:
    return not aircraft.get("on_ground")


@router.get("/aircraft")
def get_aircraft_data():
    """Retrieve aircraft data in Finland from Redis"""
    try:
        data = fetch_aircraft_data()
        filtered_data = filter(filter_on_ground, data)
        transformed_aircraft = [transform_aircraft(aircraft) for aircraft in filtered_data]

        return transformed_aircraft
    except Exception as e:
        logger.error(f"Error retrieving aircraft data: {e}")
        return {"error": str(e)}
