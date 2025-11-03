# app/api/radar_api.py
from fastapi import APIRouter
import redis
import json
from app.config import settings
import logging
import ssl
from datetime import datetime
from typing import Dict, Optional
import mgrs

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/radar", tags=["radar"])

# Initialize MGRS converter
mgrs_converter = mgrs.MGRS()


# Redis client with SSL support
def create_redis_client():
    """Create Redis client with SSL if using rediss://"""
    if settings.celery_broker_url.startswith("rediss://"):
        return redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,
            ssl=True,
            ssl_cert_reqs=ssl.CERT_REQUIRED,
            ssl_ca_certs=settings.mtls_ca_cert,
            ssl_certfile=settings.mtls_client_cert,
            ssl_keyfile=settings.mtls_client_key,
            ssl_check_hostname=False,  # Disable hostname verification for Docker network
        )
    else:
        return redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,
        )


redis_client = create_redis_client()


def convert_timestamp_to_datetime(timestamp: Optional[int]) -> Optional[str]:
    """
    Convert Unix timestamp to dd.mm.yyyy hh:mm:ss format.
    """
    if timestamp is None:
        return None
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except Exception as e:
        logger.error(f"Error converting timestamp {timestamp}: {e}")
        return None


def convert_to_mgrs(longitude: Optional[float], latitude: Optional[float]) -> Optional[str]:
    """
    Convert longitude/latitude to MGRS format.

    Args:
        longitude: Longitude in decimal degrees
        latitude: Latitude in decimal degrees

    Returns:
        MGRS string in format "35VMH23" or None
        Example: MGRS "35VMH2625532571" -> "35VMH26"
    """
    if longitude is None or latitude is None:
        return None

    try:
        # Convert to MGRS string with precision 5 (10m precision)
        # Example output: "35VMH2625532571"
        mgrs_string = mgrs_converter.toMGRS(latitude, longitude, MGRSPrecision=5)

        if len(mgrs_string) >= 5:
            # Extract grid zone (3 or 4 characters)
            if len(mgrs_string) > 2 and mgrs_string[2].isdigit():
                # 4-character grid zone (e.g., "31UBQ")
                grid_zone = mgrs_string[:4]
                square_id = mgrs_string[4:6]
                rest = mgrs_string[6:]
            else:
                # 3-character grid zone (e.g., "35VMH")
                grid_zone = mgrs_string[:3]
                square_id = mgrs_string[3:5]
                rest = mgrs_string[5:]

            # Get first 2 digits of easting (first half of remaining digits)
            if len(rest) > 0:
                mid = len(rest) // 2
                easting = rest[:mid]
                # Take first 2 digits of easting
                precision = easting[:2] if len(easting) >= 2 else easting.ljust(2, "0")
            else:
                precision = "00"

            # Format as "GridZone-SquareID-Precision"
            return f"{grid_zone}{square_id}{precision}"

        return None
    except Exception as e:
        logger.error(f"Error converting coordinates ({latitude}, {longitude}) to MGRS: {e}")
        return None


def classify_altitude(altitude: Optional[float]) -> Optional[str]:
    if altitude is None:
        return None

    if altitude < 300:
        return "pinnassa"
    elif altitude < 3000:
        return "matalalla"
    else:
        return "korkealla"


def classify_speed(velocity: Optional[float]) -> Optional[str]:
    if velocity is None:
        return None

    if velocity < 140:
        return "hidas"
    elif velocity < 280:
        return "nopea"
    else:
        return "erittäin nopea"


def transform_aircraft(aircraft: Dict) -> Dict:
    """
    Transform a single aircraft object to the new format.
    """
    transformed = {
        "icao24": aircraft.get("icao24"),
        "callsign": aircraft.get("callsign"),
        "origin_country": aircraft.get("origin_country"),
        "time_position": convert_timestamp_to_datetime(aircraft.get("time_position")),
        "last_contact": convert_timestamp_to_datetime(aircraft.get("last_contact")),
        "position": convert_to_mgrs(aircraft.get("longitude"), aircraft.get("latitude")),
        "altitude": classify_altitude(aircraft.get("baro_altitude")),
        "velocity": classify_speed(aircraft.get("velocity")),
        "track": aircraft.get("true_track"),
        "on_ground": aircraft.get("on_ground"),
    }

    return transformed


@router.get("/aircraft")
def get_aircraft_data():
    try:
        aircraft_json = redis_client.get("finland_aircraft")
        last_update_time = redis_client.get("last_update_time")

        aircraft_list = json.loads(aircraft_json) if aircraft_json else []
        timestamp = int(last_update_time) if last_update_time else 0

        # Transform each aircraft
        transformed_aircraft = [transform_aircraft(aircraft) for aircraft in aircraft_list]

        return {
            "aircraft_count": len(transformed_aircraft),
            "timestamp": convert_timestamp_to_datetime(timestamp),
            "aircraft": transformed_aircraft,
        }
    except Exception as e:
        logger.error(f"Error retrieving aircraft data: {e}")
        return {"error": str(e), "aircraft_count": 0, "aircraft": []}


@router.get("/aircraft/raw")
def get_raw_aircraft_data():
    """
    Retrieve raw aircraft data in Finland from Redis without transformation.
    """
    try:
        aircraft_json = redis_client.get("finland_aircraft")
        last_update_time = redis_client.get("last_update_time")

        aircraft_list = json.loads(aircraft_json) if aircraft_json else []
        timestamp = int(last_update_time) if last_update_time else 0

        return {
            "aircraft_count": len(aircraft_list),
            "timestamp": timestamp,
            "aircraft": aircraft_list,
        }
    except Exception as e:
        logger.error(f"Error retrieving aircraft data: {e}")
        return {"error": str(e), "aircraft_count": 0, "aircraft": []}
