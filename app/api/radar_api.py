# app/api/radar_api.py
from fastapi import APIRouter
import redis
import json
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/radar", tags=["radar"])

# Redis client
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True
)

@router.get("/aircraft")
def get_aircraft_data():
    """
    Retrieve aircraft data in Finland from Redis.
    """
    try:
        aircraft_json = redis_client.get("finland_aircraft")
        last_update_time = redis_client.get("last_update_time")

        aircraft_list = json.loads(aircraft_json) if aircraft_json else []
        timestamp = int(last_update_time) if last_update_time else 0

        return {
            "aircraft_count": len(aircraft_list),
            "timestamp": timestamp,
            "aircraft": aircraft_list
        }
    except Exception as e:
        logger.error(f"Error retrieving aircraft data: {e}")
        return {"error": str(e), "aircraft_count": 0, "aircraft": []}
