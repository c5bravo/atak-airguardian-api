# app/config.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    redis_host: str
    redis_port: int
    redis_db: int

    opensky_api_url: str
    opensky_token_url: str
    opensky_client_id: str
    opensky_client_secret: str

    finland_lat_min: float
    finland_lat_max: float
    finland_lon_min: float
    finland_lon_max: float

    api_host: str
    api_port: int

    celery_broker_url: str
    celery_result_backend: str

    # mTLS settings
    mtls_enabled: bool = False
    mtls_ca_cert: Optional[str] = None
    mtls_server_cert: Optional[str] = None
    mtls_server_key: Optional[str] = None
    mtls_client_cert: Optional[str] = None
    mtls_client_key: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
