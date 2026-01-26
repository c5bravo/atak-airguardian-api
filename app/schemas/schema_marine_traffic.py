from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MarineTrafficPosition(BaseModel):
    MMSI: Optional[str]
    IMO: Optional[str]
    SHIP_ID: str
    LAT: float
    LON: float
    SPEED: float
    HEADING: int
    COURSE: Optional[str]
    TIMESTAMP: datetime
    UTC_SECONDS: Optional[str]
    SHIPNAME: str
    SHIP_COUNTRY: str
