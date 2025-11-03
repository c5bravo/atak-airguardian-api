# app/opensky_auth.py
import httpx
import time
import logging
from typing import Optional, Dict
from app.config import settings

logger = logging.getLogger(__name__)


class OpenSkyAuth:
    """Handle OpenSky API OAuth2 authentication"""

    def __init__(self):
        self.token_url = settings.opensky_token_url
        self.client_id = settings.opensky_client_id
        self.client_secret = settings.opensky_client_secret
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

    def _is_token_valid(self) -> bool:
        """Check if current token is still valid"""
        if not self._access_token:
            return False
        # Consider token expired 60 seconds before actual expiry
        return time.time() < (self._token_expires_at - 60)

    def _fetch_new_token(self) -> str:
        """Fetch a new access token using OAuth2 Client Credentials Flow"""
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.token_url, data=data)

                if response.status_code != 200:
                    logger.error(f"❌ Token request failed: {response.status_code}")
                    logger.error(f"Response: {response.text}")

                response.raise_for_status()
                token_data = response.json()

                self._access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self._token_expires_at = time.time() + expires_in

                logger.info(f"✅ OpenSky token obtained (expires in {expires_in}s)")
                return self._access_token

        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to fetch OpenSky access token: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error fetching access token: {e}")
            raise

    def get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary"""
        if not self._is_token_valid():
            logger.info("🔄 Access token expired or missing, fetching new token...")
            return self._fetch_new_token()
        return self._access_token

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests"""
        token = self.get_access_token()
        return {"Authorization": f"Bearer {token}"}


# Global instance
opensky_auth = OpenSkyAuth()
