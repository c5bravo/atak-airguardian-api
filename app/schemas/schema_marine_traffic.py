from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MarineTrafficPosition(BaseModel):
    SHIP_ID: str
    LAT: float
    LON: float
    SPEED: Optional[float]
    HEADING: Optional[int]
    COURSE: Optional[int]
    TIMESTAMP: Optional[datetime]
    UTC_SECONDS: Optional[int]
    SHIPNAME: Optional[str]
    SHIP_COUNTRY: Optional[str]
    type: Optional[str]
