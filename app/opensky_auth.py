import logging
import time
from typing import Dict, List, Optional

import httpx
from app.config import settings

logger = logging.getLogger(__name__)

_api_keys: List[Dict[str, str]] = []
_access_tokens: Dict[int, Optional[str]] = {}
_token_expiry: Dict[int, float] = {}
_current_key_index: int = 0


def load_api_keys() -> List[Dict[str, str]]:
    keys: List[Dict[str, str]] = []
    for i in range(1, 10):
        client_id = getattr(settings, f"opensky_client_id_{i}", None)
        client_secret = getattr(settings, f"opensky_client_secret_{i}", None)
        if client_id and client_secret:
            keys.append({"client_id": client_id, "client_secret": client_secret})
            logger.info(f"Loaded API key {i}: {client_id[:10]}...")
    if not keys:
        client_id = getattr(settings, "opensky_client_id", None)
        client_secret = getattr(settings, "opensky_client_secret", None)
        if client_id and client_secret:
            keys.append({"client_id": client_id, "client_secret": client_secret})
            logger.info("Loaded default API key (non-numbered)")
    if not keys:
        logger.error("NO API KEYS FOUND IN SETTINGS!")
    else:
        logger.info(f"Total API keys loaded: {len(keys)}")
    return keys


def is_token_valid(index: int) -> bool:
    token = _access_tokens.get(index)
    expiry = _token_expiry.get(index, 0)
    if not token:
        return False
    return time.time() < (expiry - 60)


def fetch_new_token(index: int) -> Optional[str]:
    key = _api_keys[index]

    data = {
        "grant_type": "client_credentials",
        "client_id": key["client_id"],
        "client_secret": key["client_secret"],
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(settings.opensky_token_url, data=data)
            response.raise_for_status()

            token_data = response.json()
            access_token: Optional[str] = token_data.get("access_token")
            expires_in: int = token_data.get("expires_in", 3600)

            if not access_token:
                logger.error(f"No access token found in response for key {index}")
                return None

            _access_tokens[index] = access_token
            _token_expiry[index] = time.time() + expires_in

            logger.info(f"Token fetched for key {index}, expires in {expires_in}s")
            return access_token
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching token for key {index}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching token for key {index}: {e}")
        return None


def get_access_token() -> Optional[str]:
    global _current_key_index
    if not _api_keys:
        logger.error("No API keys loaded")
        return None

    if not is_token_valid(_current_key_index):
        token = fetch_new_token(_current_key_index)
        if not token:
            logger.error(f"Failed to fetch token for key {_current_key_index}")
            return None
        return token

    return _access_tokens.get(_current_key_index)


def get_auth_headers() -> Dict[str, str]:
    token = get_access_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    else:
        logger.error("No valid access token available")
        return {}


# Initialize keys on import
_api_keys = load_api_keys()
for i in range(len(_api_keys)):
    _access_tokens[i] = None
    _token_expiry[i] = 0
