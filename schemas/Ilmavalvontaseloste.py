"""Ilmavalvontaseloste schemas."""

from typing import Optional

from pydantic import BaseModel

class AirSurvellianceLog(BaseModel):
    """Example of what the data from AirSurvelliace could look like"""
    id: int
    identification_number: str 
    general_position: str
    accurate_poisition: int(max_length=2)
    speed: str("slow" | "fast" | "supersonic")
    direction: int
    altitude: str("surface" | "low" | "high")
    details: Optional[str]