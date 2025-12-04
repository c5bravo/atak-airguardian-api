from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import radar_api
from app.config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(radar_api.router)


if __name__ == "__main__":
    import uvicorn

    print("Starting server")
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
