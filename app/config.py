# app/config.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Redis Configuration
    redis_host: str
    redis_port: int
    redis_db: int

    # OpenSky API Configuration
    opensky_api_url: str
    opensky_token_url: str
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

    # Optional additional OpenSky API credentials (for multi-key rotation)
    opensky_client_id_1: Optional[str] = None
    opensky_client_secret_1: Optional[str] = None
    opensky_client_id_2: Optional[str] = None
    opensky_client_secret_2: Optional[str] = None
    opensky_client_id_3: Optional[str] = None
    opensky_client_secret_3: Optional[str] = None

    # Finland Bounding Box
    finland_lat_min: float
    finland_lat_max: float
    finland_lon_min: float
    finland_lon_max: float

    # API Server Configuration
    api_host: str
    api_port: int

    # Celery Configuration
    celery_broker_url: str
    celery_result_backend: str

    # mTLS Configuration
    mtls_enabled: bool
    mtls_ca_cert: Optional[str] = None
    mtls_server_cert: Optional[str] = None
    mtls_server_key: Optional[str] = None
    mtls_client_cert: Optional[str] = None
    mtls_client_key: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
