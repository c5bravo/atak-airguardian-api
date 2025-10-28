from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_host: str
    redis_port: int
    redis_db: int

    opensky_api_url: str

    finland_lat_min: float
    finland_lat_max: float
    finland_lon_min: float
    finland_lon_max: float

    api_host: str
    api_port: int

    celery_broker_url: str
    celery_result_backend: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        fields = {
            "redis_host": {"env": "REDIS_HOST"},
            "redis_port": {"env": "REDIS_PORT"},
            "redis_db": {"env": "REDIS_DB"},
            "opensky_api_url": {"env": "OPENSKY_API_URL"},
            "finland_lat_min": {"env": "FINLAND_LAT_MIN"},
            "finland_lat_max": {"env": "FINLAND_LAT_MAX"},
            "finland_lon_min": {"env": "FINLAND_LON_MIN"},
            "finland_lon_max": {"env": "FINLAND_LON_MAX"},
            "api_host": {"env": "API_HOST"},
            "api_port": {"env": "API_PORT"},
            "celery_broker_url": {"env": "CELERY_BROKER_URL"},
            "celery_result_backend": {"env": "CELERY_RESULT_BACKEND"},
        }

settings = Settings()
