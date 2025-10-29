# app/main.py
import ssl
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import radar_api 
from app.config import settings


app = FastAPI(
    title="Finland Aircraft Tracker API",
    description="API to track aircraft currently flying over Finland",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

##### Include routers #####
app.include_router(radar_api.router)


if __name__ == "__main__":
    import uvicorn

    if settings.mtls_enabled:
        print("🔒 Starting server with mTLS enabled")
        uvicorn.run(
            "app.main:app",  # Changed from "main:app"
            host=settings.api_host,
            port=settings.api_port,
            ssl_keyfile=settings.mtls_server_key,
            ssl_certfile=settings.mtls_server_cert,
            ssl_ca_certs=settings.mtls_ca_cert,
            ssl_cert_reqs=ssl.CERT_REQUIRED,
            reload=True
        )
    else:
        print("⚠️  Starting server without mTLS")
        uvicorn.run(
            "app.main:app",  # Changed from "main:app"
            host=settings.api_host,
            port=settings.api_port,
            reload=True
        )