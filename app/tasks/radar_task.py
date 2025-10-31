# app/tasks/radar_task.py
import httpx
import redis
import json
import logging
import ssl
from typing import Optional, List, Dict

from app.celery_app import celery_app
from app.config import settings
from app.opensky_auth import opensky_auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Redis client with SSL support
def create_redis_client():
    """Create Redis client with SSL if using rediss://"""
    if settings.celery_broker_url.startswith("rediss://"):
        ssl_context = ssl.create_default_context(cafile=settings.mtls_ca_cert)
        ssl_context.load_cert_chain(
            certfile=settings.mtls_client_cert, keyfile=settings.mtls_client_key
        )
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
        )
    else:
        return redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,
        )


redis_client = create_redis_client()


def fetch_opensky_data() -> Dict:
    """Fetch from OpenSky API with OAuth2 authentication"""
    try:
        # Get authentication headers
        auth_headers = opensky_auth.get_auth_headers()

        with httpx.Client(timeout=10.0) as client:
            response = client.get(settings.opensky_api_url, headers=auth_headers)
            response.raise_for_status()
            logger.info("Successfully fetched data from OpenSky API")
            return response.json()

    except httpx.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        if hasattr(e, "response") and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error fetching OpenSky data: {e}")
        return {}


def is_in_finland(latitude: Optional[float], longitude: Optional[float]) -> bool:
    if latitude is None or longitude is None:
        return False
    return (
        settings.finland_lat_min <= latitude <= settings.finland_lat_max
        and settings.finland_lon_min <= longitude <= settings.finland_lon_max
    )


def filter_aircraft_in_finland(states: List[List]) -> List[Dict]:
    filtered = []
    for state in states:
        lat, lon = state[6], state[5]
        if is_in_finland(lat, lon):
            filtered.append(state)
    return filtered


def extract_required_fields(states: List[List]) -> List[Dict]:
    aircraft_list = []
    for state in states:
        aircraft_list.append(
            {
                "icao24": state[0],
                "callsign": state[1].strip() if state[1] else None,
                "origin_country": state[2],
                "time_position": state[3],
                "last_contact": state[4],
                "longitude": state[5],
                "latitude": state[6],
                "baro_altitude": state[7],
                "velocity": state[9],
                "true_track": state[10],
                "on_ground": state[8],
            }
        )
    return aircraft_list


def store_in_redis(aircraft_list: List[Dict], timestamp: int):
    redis_client.set("finland_aircraft", json.dumps(aircraft_list))
    redis_client.set("last_update_time", timestamp)
    logger.info(f"Stored {len(aircraft_list)} aircraft in Redis")


@celery_app.task(name="app.tasks.radar_task.fetch_aircraft_data")
def fetch_aircraft_data():
    logger.info("Starting fetch_aircraft_data task...")
    data = fetch_opensky_data()

    if not data or "states" not in data:
        logger.warning("No data received from OpenSky API")
        store_in_redis([], 0)
        return {"aircraft_count": 0, "timestamp": 0}

    states = data.get("states", [])
    filtered_states = filter_aircraft_in_finland(states)
    aircraft_list = extract_required_fields(filtered_states)
    store_in_redis(aircraft_list, data.get("time", 0))

    logger.info(f"Processed {len(aircraft_list)} aircraft in Finland out of {len(states)} total")

    return {
        "aircraft_count": len(aircraft_list),
        "timestamp": data.get("time", 0),
        "total_states": len(states),
    }
