from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MarineTrafficPosition(BaseModel):
    ship_id: str
    lat: float
    lon: float
    speed: Optional[float]
    heading: Optional[int]
    course: Optional[int]
    times_tamp: Optional[datetime]
    utc_seconds: Optional[int]
    ship_name: Optional[str]
    ship_country: Optional[str]
    type: Optional[str]
