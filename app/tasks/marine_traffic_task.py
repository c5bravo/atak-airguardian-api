import logging
import httpx
from app.config import settings
from app.schemas.schema_marine_traffic import ShipFeature

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_fin_marine_traffic_data() -> list[ShipFeature]:
    api_url = settings.fin_marine_traffic_api_url
    if not api_url:
        logger.warning("FinMarine API URL is not configured.")
        return []

    lamin: float = settings.lat_min
    lamax: float = settings.lat_max
    lomin: float = settings.lon_min
    lomax: float = settings.lon_max

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.get(api_url)
            response.raise_for_status()
            raw = response.json()
            features = raw.get("features", [])

            filtered_features: list[ShipFeature] = []

            for f in features:
                try:
                    coords = f.get("geometry", {}).get("coordinates", [])
                    if len(coords) < 2:
                        continue

                    lon: float = coords[0]
                    lat: float = coords[1]

                    if lamin <= lat <= lamax and lomin <= lon <= lomax:
                        filtered_features.append(ShipFeature(**f))
                except (KeyError, TypeError, ValueError) as e:
                    logger.debug(f"Skipping malformed feature: {e}")
                    continue

            logger.info(f"Filtered {len(filtered_features)} ships from {len(features)} total.")
            return filtered_features

    except httpx.HTTPStatusError as e:
        logger.error(f"FinMarine API returned error {e.response.status_code}: {e}")
    except httpx.RequestError as e:
        logger.error(f"Network error connecting to FinMarine: {e}")
    except Exception as e:
        logger.error(f"Unexpected error parsing FinMarine data: {e}")

    return []
