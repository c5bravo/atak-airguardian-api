import logging
from typing import Dict, List

import httpx

from app.config import settings
from app.opensky_auth import opensky_auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_opensky_url() -> str:
    """Build OpenSky API URL with bounding box for Finland

    This saves API credits by only fetching data for Finland
    Area: ~400,000 sq km = 4 credits per request
    """
    base_url = settings.opensky_api_url

    # Add bounding box parameters
    url = (
        f"{base_url}?"
        f"lamin={settings.finland_lat_min}&"
        f"lamax={settings.finland_lat_max}&"
        f"lomin={settings.finland_lon_min}&"
        f"lomax={settings.finland_lon_max}"
    )

    logger.info(
        f"Using bounding box: Finland ({settings.finland_lat_min}°N to {settings.finland_lat_max}°N)"
    )
    return url


def fetch_opensky_data() -> Dict:
    """Fetch from OpenSky API with OAuth2 authentication

    Retries with all available API keys on 429 rate limit
    Uses bounding box to save credits
    """
    max_retries = len(opensky_auth.api_keys)
    attempt = 0

    api_url = build_opensky_url()

    while attempt < max_retries:
        try:
            attempt += 1
            key_info = opensky_auth.get_current_key_info()
            logger.info(
                f"📍 Attempt {attempt}/{max_retries} using key {key_info['key_index']} of {key_info['total_keys']}"
            )

            auth_headers = opensky_auth.get_auth_headers()

            with httpx.Client(timeout=10.0) as client:
                response = client.get(api_url, headers=auth_headers)

                # Check for rate limit (HTTP 429)
                if response.status_code == 429:
                    logger.warning(
                        f"⚠️  Rate limit 429 on key {key_info['key_index']}! Trying next key..."
                    )
                    opensky_auth.rotate_key()
                    continue  # Try next key

                response.raise_for_status()
                logger.info("✅ Successfully fetched data from OpenSky API")
                return response.json()

        except httpx.HTTPError as e:
            if "429" in str(e):
                logger.warning(f"⚠️  HTTP 429 error on attempt {attempt}! Rotating key...")
                opensky_auth.rotate_key()
                continue
            else:
                logger.error(f"❌ HTTP error occurred: {e}")
                return {}
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching OpenSky data: {e}")
            return {}

    logger.error(f"❌ All {max_retries} API keys exhausted - still getting 429!")
    return {}


def extract_required_fields(states: List[List]) -> List[Dict]:
    """Extract only the relevant aircraft fields from API states"""
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
                "on_ground": state[8],
                "velocity": state[9],
                "true_track": state[10],
                "vertical rate": state[11],
                "squawk": state[14],
                "position source": state[16],
            }
        )
    return aircraft_list


def fetch_aircraft_data():
    """Fetch aircraft data and store filtered results in Redis"""
    logger.info("🚀 Starting fetch_aircraft_data task...")
    data = fetch_opensky_data()

    if not data or "states" not in data:
        logger.warning("⚠️  No data received from OpenSky API")
        return []

    states = data.get("states", [])
    aircraft_list = extract_required_fields(states)

    logger.info(f"✅ Processed {len(aircraft_list)} aircraft in Finland out of {len(states)} total")

    return aircraft_list
