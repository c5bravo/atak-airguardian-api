from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AircraftState(BaseModel):
    """Schema for aircraft state data from OpenSky Network API"""
    
    icao24: str = Field(..., description="Unique ICAO 24-bit address")
    callsign: Optional[str] = Field(None, description="Callsign of the aircraft")
    origin_country: str = Field(..., description="Country of origin")
    time_position: Optional[int] = Field(None, description="Unix timestamp of position")
    last_contact: int = Field(..., description="Unix timestamp of last contact")
    longitude: Optional[float] = Field(None, description="Longitude in decimal degrees")
    latitude: Optional[float] = Field(None, description="Latitude in decimal degrees")
    baro_altitude: Optional[float] = Field(None, description="Barometric altitude in meters")
    on_ground: bool = Field(..., description="True if aircraft is on ground")
    velocity: Optional[float] = Field(None, description="Velocity in m/s")
    true_track: Optional[float] = Field(None, description="True track in degrees")
    vertical_rate: Optional[float] = Field(None, description="Vertical rate in m/s")
    sensors: Optional[list[int]] = Field(None, description="IDs of sensors")
    geo_altitude: Optional[float] = Field(None, description="Geometric altitude in meters")
    squawk: Optional[str] = Field(None, description="Transponder code")
    spi: bool = Field(..., description="Special purpose indicator")
    position_source: int = Field(..., description="Origin of position (0=ADS-B, 1=ASTERIX, 2=MLAT)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "icao24": "abc123",
                "callsign": "FIN123",
                "origin_country": "Finland",
                "time_position": 1698765432,
                "last_contact": 1698765432,
                "longitude": 25.0,
                "latitude": 60.0,
                "baro_altitude": 10000.0,
                "on_ground": False,
                "velocity": 250.0,
                "true_track": 180.0,
                "vertical_rate": 0.0,
                "sensors": None,
                "geo_altitude": 10100.0,
                "squawk": "1200",
                "spi": False,
                "position_source": 0
            }
        }


class AircraftResponse(BaseModel):
    """Response schema for filtered aircraft data"""
    
    total_aircraft: int = Field(..., description="Total number of aircraft in Finland")
    timestamp: datetime = Field(..., description="Timestamp of data retrieval")
    aircraft: list[AircraftState] = Field(..., description="List of aircraft states")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_aircraft": 5,
                "timestamp": "2024-10-26T12:00:00",
                "aircraft": []
            }
        }