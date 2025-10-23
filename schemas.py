from typing import Optional, Literal, List
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


class flightradar24Log(BaseModel):
    """This data schema from flightradar24 api"""
    icao24: str = Field(..., description="Unique ICAO 24-bit address of the aircraft like == 39de4f")
    callsign: Optional[str] = Field(None, description="Callsign of the aircraft, may be null or have trailing spaces like == TVF23TK")
    origin_country: str = Field(..., description="Country where the aircraft’s transponder is registered like == France")
    time_position: Optional[int] = Field(None, description="Unix timestamp (seconds) when position was last reported like == 1761126595")
    last_contact: int = Field(..., description="Unix timestamp of the last received message like == 1761126595")
    longitude: Optional[float] = Field(None, description="Aircraft longitude in decimal degrees like == 5.7155")
    latitude: Optional[float] = Field(None, description="Aircraft latitude in decimal degrees like == 46.8238")
    baro_altitude: Optional[float] = Field(None, description="Barometric altitude (m) like == 11574.78")
    on_ground: bool = Field(..., description="True if aircraft is on ground like == false")
    velocity: Optional[float] = Field(None, description="Ground speed (m/s) like == 206.76")
    heading: Optional[float] = Field(None, description="Direction of motion, degrees clockwise from north like == 309.75")
    vertical_rate: Optional[float] = Field(None, description="Climb or descent rate (m/s) like == -0.33")
    sensors: Optional[List[int]] = Field(None, description="List of sensor IDs receiving the signal (if known) like == null")
    geo_altitude: Optional[float] = Field(None, description="Geometric (GPS) altitude (m) like == 11689.08")
    squawk: Optional[str] = Field(None, description="Transponder squawk code like == 1000")
    spi: bool = Field(..., description="Special Position Identification flag like == false")
    position_source: int = Field(..., description="Position source: 0=ADS-B, 1=ASTERIX, 2=MLAT like == 0")


class OpenSkyResponse(BaseModel):
    """Represents the full OpenSky API response"""
    time: int = Field(..., description="Unix timestamp of the snapshot (UTC)")
    states: List[flightradar24Log] = Field(..., description="List of aircraft states")
