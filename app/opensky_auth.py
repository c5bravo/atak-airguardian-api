# app/opensky_auth.py
import logging
import time
from typing import Dict, List, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class OpenSkyAuth:
    """Handle OpenSky API OAuth2 authentication with multi-key support"""

    def __init__(self):
        # Token endpoint
        self.token_url = settings.opensky_token_url

        # Support multiple API keys
        self.api_keys = self._parse_api_keys()
        self.current_key_index = 0

        self._access_tokens: Dict[str, Optional[str]] = {}
        self._token_expires_at: Dict[str, float] = {}

        # Initialize tracking for each key
        for i, key in enumerate(self.api_keys):
            self._access_tokens[i] = None
            self._token_expires_at[i] = 0

    def _parse_api_keys(self) -> List[Dict]:
        """Parse API keys from settings

        Expected format in .env:
        OPENSKY_CLIENT_ID_1=xxx
        OPENSKY_CLIENT_SECRET_1=yyy
        OPENSKY_CLIENT_ID_2=xxx
        OPENSKY_CLIENT_SECRET_2=yyy
        etc...
        """
        keys = []

        # Try to load numbered keys (1, 2, 3, ...)
        for i in range(1, 10):  # Support up to 9 keys
            try:
                client_id = getattr(settings, f"opensky_client_id_{i}", None)
                client_secret = getattr(settings, f"opensky_client_secret_{i}", None)

                if client_id and client_secret:
                    keys.append({"client_id": client_id, "client_secret": client_secret})
                    logger.info(f"✅ Loaded API key {i}: {client_id[:10]}...")
            except Exception as e:
                logger.error(f"Error loading key {i}: {e}")
                continue

        # If no numbered keys found, try default (non-numbered)
        if not keys:
            try:
                if hasattr(settings, "opensky_client_id") and hasattr(
                    settings, "opensky_client_secret"
                ):
                    if settings.opensky_client_id and settings.opensky_client_secret:
                        keys.append(
                            {
                                "client_id": settings.opensky_client_id,
                                "client_secret": settings.opensky_client_secret,
                            }
                        )
                        logger.info("✅ Loaded default API key (non-numbered)")
            except Exception as e:
                logger.error(f"Error loading default key: {e}")

        if not keys:
            logger.error("❌ NO API KEYS FOUND IN SETTINGS!")
        else:
            logger.info(f"✅ Total API keys loaded: {len(keys)}")
            for i, key in enumerate(keys):
                logger.info(f"   Key {i}: {key['client_id'][:10]}...")

        return keys

    def _is_token_valid(self, key_index: int) -> bool:
        """Check if current token is still valid"""
        if not self._access_tokens.get(key_index):
            return False
        # Consider token expired 60 seconds before actual expiry
        return time.time() < (self._token_expires_at.get(key_index, 0) - 60)

    def _fetch_new_token(self, key_index: int) -> str:
        """Fetch a new access token using OAuth2 Client Credentials Flow"""
        key = self.api_keys[key_index]

        data = {
            "grant_type": "client_credentials",
            "client_id": key["client_id"],
            "client_secret": key["client_secret"],
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.token_url, data=data)

                if response.status_code != 200:
                    logger.error(
                        f"❌ Token request failed for key {key_index}: {response.status_code}"
                    )
                    logger.error(f"Response: {response.text}")
                    return None

                response.raise_for_status()
                token_data = response.json()

                access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)

                self._access_tokens[key_index] = access_token
                self._token_expires_at[key_index] = time.time() + expires_in

                logger.info(
                    f"✅ OpenSky token obtained for key {key_index} (expires in {expires_in}s)"
                )
                return access_token

        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to fetch OpenSky access token (key {key_index}): {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching access token (key {key_index}): {e}")
            return None

    def get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary"""
        key_index = self.current_key_index

        if not self._is_token_valid(key_index):
            logger.info(f"🔄 Fetching new token for key {key_index}...")
            token = self._fetch_new_token(key_index)

            if not token:
                # Try next key if current one failed
                self._rotate_to_next_key()
                return self.get_access_token()

            return token

        return self._access_tokens[key_index]

    def rotate_key(self):
        """Manually rotate to next API key (when limit reached)"""
        logger.warning(f"⚠️  Rotating from key {self.current_key_index} to next key...")
        self._rotate_to_next_key()

    def _rotate_to_next_key(self):
        """Rotate to next available key"""
        old_index = self.current_key_index
        next_index = (self.current_key_index + 1) % len(self.api_keys)

        self.current_key_index = next_index

        logger.warning(f"🔄 Rotated from key {old_index} → key {next_index}")
        logger.info(f"ℹ️  Now using: {self.api_keys[next_index]['client_id'][:10]}...")

    def get_auth_headers(self) -> Dict[str, str]:
        """Return bearer token headers for API calls."""
        token = self.get_access_token()
        return {"Authorization": f"Bearer {token}"}

    def get_current_key_info(self) -> Dict:
        """Get info about current key"""
        return {
            "key_index": self.current_key_index,
            "total_keys": len(self.api_keys),
            "has_token": bool(self._access_tokens.get(self.current_key_index)),
        }


# Global instance
opensky_auth = OpenSkyAuth()
