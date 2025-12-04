from typing import Dict, List, Optional, Any, cast
import logging
import httpx
from app.config import settings
from app.opensky_auth import get_auth_headers

logger = logging.getLogger(__name__)


def build_opensky_url() -> str:
    base_url = settings.opensky_api_url.rstrip("/")
    return (
        f"{base_url}?"
        f"lamin={settings.lat_min}&"
        f"lamax={settings.lat_max}&"
        f"lomin={settings.lon_min}&"
        f"lomax={settings.lon_max}"
    )


def fetch_opensky_data() -> Dict[str, Any]:
    url = build_opensky_url()
    headers = get_auth_headers()
    if not headers:
        logger.error("No auth headers, cannot fetch OpenSky data")
        return {}

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, dict):
                logger.error("OpenSky API returned unexpected data (not a dict)")
                return {}
            # Cast to Dict[str, Any] after runtime check
            return cast(Dict[str, Any], data)
    except Exception as e:
        logger.error(f"Error fetching OpenSky data: {e}")
        return {}


def extract_required_fields(states: List[List[Optional[Any]]]) -> List[Dict[str, Any]]:
    aircraft_list: List[Dict[str, Any]] = []
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
                "on_ground": state[8],
                "velocity": state[9],
                "true_track": state[10],
                "vertical_rate": state[11],
                "squawk": state[14],
                "position_source": state[16],
            }
        )
    return aircraft_list


def fetch_aircraft_data() -> List[Dict[str, Any]]:
    logger.info("Starting fetch_aircraft_data task...")
    data: Dict[str, Any] = fetch_opensky_data()

    if not data or "states" not in data:
        logger.warning("No data received from OpenSky API")
        return []

    states = data.get("states", [])
    aircraft_list = extract_required_fields(states)

    logger.info(f"Processed {len(aircraft_list)} aircraft in Finland out of {len(states)} total")

    return aircraft_list
