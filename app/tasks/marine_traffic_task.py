import logging

import httpx

from app.config import settings
from app.schemas.schema_marine_traffic import MarineTrafficPosition

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_marine_traffic_data() -> list[MarineTrafficPosition]:
    api_url = "https://api.kpler.com/v2/maritime/ais-latest?limit=3"
    headers = {
        "Authorization": f"Bearer {settings.marine_traffic_api_url}",
        "Accept": "application/json"
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(api_url, headers=headers)
            response.raise_for_status()

            raw = response.json()
            positions = raw.get("DATA", [])

            return [MarineTrafficPosition(**p) for p in positions]

    except httpx.HTTPError as e:
        logger.error(f"HTTP error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    return []
