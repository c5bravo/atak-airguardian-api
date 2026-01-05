from typing import Optional

from pydantic import BaseModel, Field


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
