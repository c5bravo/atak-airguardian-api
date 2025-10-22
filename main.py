from fastapi import FastAPI
from app.api import mock_api

app = FastAPI(
    title="AirGuardian Backend",
    version="1.0.0",
)

# APIs
app.include_router(mock_api.router)
