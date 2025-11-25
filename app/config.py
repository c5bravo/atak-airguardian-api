from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Redis Configuration
    redis_host: str = ""
    redis_port: int = 0
    redis_db: int = 0

    # Mock Generiter aircraft API
    generater_api_url: str = ""

    # OpenSky API Configuration
    opensky_api_url: str = ""
    opensky_token_url: str = ""
    # Default/single key (fallback)
    opensky_client_id: Optional[str] = ""
    opensky_client_secret: Optional[str] = ""

    # Multi-key support
    opensky_client_id_1: Optional[str] = ""
    opensky_client_secret_1: Optional[str] = ""

    opensky_client_id_2: Optional[str] = ""
    opensky_client_secret_2: Optional[str] = ""

    opensky_client_id_3: Optional[str] = ""
    opensky_client_secret_3: Optional[str] = ""

    # Finland Bounding Box
    finland_lat_min: float = 0.0
    finland_lat_max: float = 0.0
    finland_lon_min: float = 0.0
    finland_lon_max: float = 0.0

    # API Server Configuration
    api_host: str = ""
    api_port: int = 0

    # Celery Configuration
    celery_broker_url: str = ""
    celery_result_backend: str = ""

    # mTLS Configuration
    mtls_enabled: bool = False
    mtls_ca_cert: Optional[str] = ""
    mtls_server_cert: Optional[str] = ""
    mtls_server_key: Optional[str] = ""
    mtls_client_cert: Optional[str] = ""
    mtls_client_key: Optional[str] = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
