from typing import Optional, Any, Dict, cast
from pydantic_settings import BaseSettings
from pathlib import Path
import json
import functools


class Settings(BaseSettings):
    # OpenSky API Configuration
    opensky_api_url: str = "https://opensky-network.org/api/states/all"
    opensky_token_url: str = (
        "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
    )
    # Default/single key (fallback)
    opensky_client_id: Optional[str] = None
    opensky_client_secret: Optional[str] = None

    # Multi-key support
    opensky_client_id_1: Optional[str] = None
    opensky_client_secret_1: Optional[str] = None

    opensky_client_id_2: Optional[str] = None
    opensky_client_secret_2: Optional[str] = None

    opensky_client_id_3: Optional[str] = None
    opensky_client_secret_3: Optional[str] = None

    # Finland Bounding Box
    lat_min: float = 59.5
    lat_max: float = 70.0
    lon_min: float = 19.5
    lon_max: float = 31.5

    # API Server Configuration
    api_host: str = "0.0.0.0"  # nosec
    api_port: int = 8010

    practool_host: Optional[str] = None
    practool_port: Optional[int] = None

    fin_marine_traffic_api_url: Optional[str] = None


settings = Settings()


@functools.cache
def load_manifest(filepth: Path = Path("/pvarki/kraftwerk-init.json")) -> Dict[str, Any]:
    """Load the manifest"""
    if not filepth.exists():
        rm_uri = "https://localmaeher.dev.pvarki.fi"
        mtls_uri = rm_uri.replace("https://", "https://mtls.")
        tool_uri = rm_uri.replace("airguardian", "agpractice")
        return {
            "deployment": "localmaeher",
            "rasenmaeher": {
                "init": {"base_uri": tool_uri, "csr_jwt": "LOL, no"},
                "mtls": {"base_uri": mtls_uri},
                "certcn": "rasenmaeher",
            },
            "product": {"dns": "agpractice.localmaeher.dev.pvarki.fi"},
        }
    return cast(Dict[str, Any], json.loads(filepth.read_text(encoding="utf-8")))


def read_ag_uri() -> str:
    """Read the uri from manifest"""
    return str(load_manifest()["product"]["uri"])
