import logging

import httpx

from app.api.radar_api import TransformedAircraft
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_practice_data() -> list[TransformedAircraft]:
    if not settings.practool_host or not settings.practool_port:
        return []

    api_url = f"http://{settings.practool_host}:{settings.practool_port}/api/craft"

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(api_url)

            response.raise_for_status()
            logger.info("✅ Successfully fetched data from Practice API")
            data: list[TransformedAircraft] = response.json()
            return data

    except httpx.HTTPError as e:
        logger.error(f"❌ HTTP error occurred: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Unexpected error fetching Practice data: {e}")
        return []
