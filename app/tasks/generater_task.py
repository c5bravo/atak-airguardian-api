import httpx
import redis
import json
import logging
from typing import Optional, List, Dict

from app.celery_app import celery_app
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_redis_client():
    """Create Redis client"""
    return redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True,
    )


redis_client = create_redis_client()


def fetch_generater_data() -> Dict:
    """Fetch from Generater API"""

    api_url = settings.generater_api_url

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(api_url)

            response.raise_for_status()
            logger.info("✅ Successfully fetched data from Generater API")
            return response.json()

    except Exception as e:
        logger.error(f"Unexpected error fetching Generater data: {e}!!!!")
        return {}


def extract_required_fields(states: List[Dict]) -> List[Dict]:
    """Extract only the relevant aircraft fields from API states"""
    aircraft_list = []
    for state in states:
        aircraft_list.append(
            {
                "aircraft_id": state[0],
                "time_position": state[1],
                "speed": state[2],
                "altitude": state[3],
                "longitude": state[4],
                "latitude": state[5],
                "heading": state[6],
                "additionalInfo": state[7],
                "is_exited": state[8],
            }
        )
    return aircraft_list


def store_in_redis(aircraft_list: List[Dict], timestamp: int):
    """Store aircraft data and timestamp in Redis"""
    redis_client.set("generater_aircraft", json.dumps(aircraft_list))
    redis_client.set("generater_last_update_time", timestamp)
    logger.info(f"Stored generater {len(aircraft_list)} aircraft in Redis.")


@celery_app.task(name="app.tasks.generater_task.fetch_generater_aircraft_data")
def fetch_aircraft_data():
    """Main Celery task: Fetch aircraft data and store filtered results in Redis"""
    logger.info("Starting fetch_generater_aircraft_data task...")
    data = fetch_generater_data()

    if not data or "states" not in data:
        logger.warning("No data received from generater API!!")
        store_in_redis([], 0)
        return {"aircraft_count": 0, "timestamp": 0}

    states = data.get("states", [])
    aircraft_list = extract_required_fields(states)
    store_in_redis(aircraft_list, data.get("time", 0))

    logger.info(f"Processed {len(aircraft_list)} aircraft out of {len(states)} total.")

    return {
        "aircraft_count": len(aircraft_list),
        "timestamp": data.get("time", 0),
        "total_states": len(states),
    }
