"""Ilmavalvontaseloste schemas."""

from typing import Optional, Literal

from pydantic import Field, BaseModel

class AirSurveillanceLog(BaseModel):
    """Example of what the data from AirSurveillace could look like"""
    id: int = Field(description="Source id")
    identification_number: str = Field(description="Indentification number for the air. Str because id can start with 0")
    general_position: str = Field(description="Two Nato-alphabethical letters")
    accurate_poisition: str(max_length=2) = Field(description="Position defined within 10km")
    speed: Literal("slow" | "fast" | "supersonic") = Field(description="Speed of the air unit")
    direction: int = Field(description="Speed of the air unit")
    altitude: Literal("surface" | "low" | "high") = Field
    details: Optional[str] = Field(description="Additional info", default=None)