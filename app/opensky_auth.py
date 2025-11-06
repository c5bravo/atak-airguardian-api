# app/opensky_auth.py
import httpx
import time
import logging
import redis
import json
from typing import Optional, Dict, List
from app.config import settings

logger = logging.getLogger(__name__)


class OpenSkyAuth:
    """Handle OpenSky API OAuth2 authentication with optional multi-key rotation."""

    def __init__(self):
        # Token endpoint
        self.token_url = settings.opensky_token_url

        # Single-key mode (default)
        self.client_id = settings.opensky_client_id
        self.client_secret = settings.opensky_client_secret

        # Multi-key configuration
        self.multi_key_mode = False
        self.max_requests_per_key = 4000

        # Load optional multiple keys
        self.keys = self._load_keys()

        # Redis for usage tracking
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,
        )

        # Token cache
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

    # -------------------------------------------------------------------------
    # 🔧 Multi-key management
    # -------------------------------------------------------------------------
    def _load_keys(self) -> List[Dict[str, str]]:
        keys = []
        for i in range(1, 4):
            cid = getattr(settings, f"opensky_client_id_{i}", None)
            csec = getattr(settings, f"opensky_client_secret_{i}", None)
            if cid and csec:
                keys.append({"id": cid, "secret": csec})
        return keys

    def enable_multi_key_mode(self, enabled: bool):
        """Toggle multi-key rotation mode."""
        self.multi_key_mode = enabled
        logger.info(f"🔁 Multi-key mode set to {enabled}")

    def _get_usage(self) -> Dict[str, Dict[str, int]]:
        if not self.redis_client.exists("opensky:key_usage"):
            usage = {str(i): {"used": 0} for i in range(len(self.keys))}
            self.redis_client.set("opensky:key_usage", json.dumps(usage))
        return json.loads(self.redis_client.get("opensky:key_usage"))

    def _save_usage(self, data: Dict[str, Dict[str, int]]):
        self.redis_client.set("opensky:key_usage", json.dumps(data))

    def _select_next_key(self) -> Dict[str, str]:
        """Rotate between keys based on usage count."""
        usage = self._get_usage()
        for i, stats in usage.items():
            if stats["used"] < self.max_requests_per_key:
                usage[i]["used"] += 1
                self._save_usage(usage)
                return self.keys[int(i)]

        # All keys used up -> reset
        logger.warning("⚠️ All OpenSky API keys reached 4000 requests — resetting counters.")
        for k in usage:
            usage[k]["used"] = 0
        self._save_usage(usage)
        return self.keys[0]

    def _get_credentials(self) -> Dict[str, str]:
        """Return credentials for current mode."""
        if not self.multi_key_mode:
            return {"id": self.client_id, "secret": self.client_secret}
        return self._select_next_key()

    # -------------------------------------------------------------------------
    # 🔐 Token management
    # -------------------------------------------------------------------------
    def _is_token_valid(self) -> bool:
        if not self._access_token:
            return False
        return time.time() < (self._token_expires_at - 60)

    def _fetch_new_token(self) -> str:
        """Fetch new access token via OAuth2 Client Credentials flow."""
        creds = self._get_credentials()
        data = {
            "grant_type": "client_credentials",
            "client_id": creds["id"],
            "client_secret": creds["secret"],
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.token_url, data=data)
                response.raise_for_status()
                token_data = response.json()
                self._access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self._token_expires_at = time.time() + expires_in
                logger.info(f"✅ Token obtained for {creds['id']} (expires in {expires_in}s)")
                return self._access_token
        except httpx.HTTPError as e:
            logger.error(f"❌ Failed to fetch token for {creds['id']}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected token fetch error: {e}")
            raise

    def get_access_token(self) -> str:
        """Get valid access token."""
        if not self._is_token_valid():
            logger.info("🔄 Token missing/expired — fetching new one...")
            return self._fetch_new_token()
        return self._access_token

    def get_auth_headers(self) -> Dict[str, str]:
        """Return bearer token headers for API calls."""
        token = self.get_access_token()
        return {"Authorization": f"Bearer {token}"}


# Global instance
opensky_auth = OpenSkyAuth()
