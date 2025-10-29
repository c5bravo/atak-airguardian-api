# app/api/radar_api.py
from fastapi import APIRouter
import redis
import json
from app.config import settings
import logging
import ssl

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/radar", tags=["radar"])


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
            "aircraft": aircraft_list,
        }
    except Exception as e:
        logger.error(f"Error retrieving aircraft data: {e}")
        return {"error": str(e), "aircraft_count": 0, "aircraft": []}
