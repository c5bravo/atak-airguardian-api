from fastapi import APIRouter
import redis
from redis.client import Redis
import json
from app.config import settings
import logging
from datetime import datetime
from typing import Dict, Optional, Any
import mgrs

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/radar", tags=["radar"])

mgrs_converter = mgrs.MGRS()


def create_redis_client() -> Redis:
    return redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True,
    )


redis_client = create_redis_client()


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
        mgrs_string = mgrs_converter.toMGRS(latitude, longitude)
        return mgrs_string.strip().replace(" ", "")
    except Exception as e:
        logger.error(f"Error converting coordinates ({latitude}, {longitude}) to MGRS: {e}!!!")
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
        return "super sonic"


def more_details(aircraft: Dict[str, Any]) -> str:
    callsign = aircraft.get("callsign", "unknown")
    country = aircraft.get("origin_country", "unknown")
    return f"This aircraft[{callsign}] from [{country}] is a civilian aircraft."


def transform_aircraft(aircraft: Dict) -> Dict:
    """Transform a single aircraft object to the new format"""
    full_mgrs = convert_to_mgrs(aircraft.get("longitude"), aircraft.get("latitude"))

    transformed = {
        "is_from_opensky": aircraft.get("open_sky"),
        "icao24": aircraft.get("icao24"),
        "callsign": aircraft.get("callsign"),
        "origin_country": aircraft.get("origin_country"),
        "time_position": convert_timestamp_to_datetime(aircraft.get("time_position")),
        "last_contact": convert_timestamp_to_datetime(aircraft.get("last_contact")),
        "position": shorten_mgrs(str(full_mgrs)),
        "altitude": classify_altitude(aircraft.get("baro_altitude")),
        "velocity": classify_speed(aircraft.get("velocity")),
        "track": aircraft.get("true_track"),
        "on_ground": aircraft.get("on_ground"),
        "details": more_details(aircraft),
    }

    return transformed


@router.get("/aircraft")
def get_aircraft_data():
    """Retrieve aircraft data in Finland from Redis"""
    try:
        aircraft_json = redis_client.get("finland_aircraft")
        generater_aircraft_json = redis_client.get("generater_aircraft")
        last_update_time = redis_client.get("last_update_time")

        aircraft_list = json.loads(str(aircraft_json)) if aircraft_json else []
        generater_aircraft_json = (
            json.loads(str(generater_aircraft_json)) if generater_aircraft_json else []
        )

        timestamp = int(last_update_time) if last_update_time else 0

        # Transform each aircraft
        transformed_aircraft = [transform_aircraft(aircraft) for aircraft in aircraft_list]
        combined_airckraft_list = transformed_aircraft + generater_aircraft_json

        return {
            "aircraft_count": len(combined_airckraft_list),
            "timestamp": convert_timestamp_to_datetime(timestamp),
            "aircraft": combined_airckraft_list,
        }
    except Exception as e:
        logger.error(f"Error retrieving aircraft data: {e}")
        return {"error": str(e), "aircraft_count": 0, "aircraft": []}


@router.get("/aircraft/raw")
def get_raw_aircraft_data():
    """Retrieve raw aircraft data in Finland from Redis without transformation"""
    try:
        aircraft_json = redis_client.get("finland_aircraft")
        last_update_time = redis_client.get("last_update_time")

        aircraft_list = json.loads(str(aircraft_json)) if aircraft_json else []
        timestamp = last_update_time if last_update_time else 0

        return {
            "aircraft_count": len(aircraft_list),
            "timestamp": timestamp,
            "aircraft": aircraft_list,
        }
    except Exception as e:
        logger.error(f"Error retrieving aircraft data: {e}")
        return {"error": str(e), "aircraft_count": 0, "aircraft": []}
