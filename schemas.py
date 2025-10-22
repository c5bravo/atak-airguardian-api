from typing import Optional, Literal
from pydantic import Field, BaseModel

class AirSurveillanceLog(BaseModel):
    """Example of what the data from AirSurveillance could look like"""
    id: int = Field(description="Source id")
    aircraft_id: str = Field(description="Identification number from the aircraft. String because id can start with 0")
    general_position: str = Field(description="Two NATO-alphabetical letters")
    accurate_position: str = Field(description="Position defined within 10km")
    speed: Literal["slow", "fast", "supersonic"] = Field(description="Speed of the aircraft")
    direction: int = Field(description="Direction of aircraft")
    altitude: Literal["surface", "low", "high"] = Field(description="Altitude of aircraft")
    details: Optional[str] = Field(description="Additional info", default=None)
