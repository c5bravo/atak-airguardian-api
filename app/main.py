# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import radar_api 


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
    from app.config import settings

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
