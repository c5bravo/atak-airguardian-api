from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenSky API Configuration
    opensky_api_url: Optional[str] = None
    opensky_token_url: Optional[str] = None
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
    lat_min: Optional[float] = 59.5
    lat_max: Optional[float] = 70.0
    lon_min: Optional[float] = 19.5
    lon_max: Optional[float] = 31.5

    # API Server Configuration
    api_host: Optional[str] = "0.0.0.0"
    api_port: Optional[int] = 8002

    practool_host: Optional[str] = None
    practool_port: Optional[int] = None


settings = Settings()
