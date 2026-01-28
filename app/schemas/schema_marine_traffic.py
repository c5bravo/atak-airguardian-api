from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MarineTrafficPosition(BaseModel):
    # Identification
    mmsi: str = Field(..., alias="MMSI")
    imo: str = Field(..., alias="IMO")
    ship_id: str = Field(..., alias="SHIP_ID")
    shipname: str = Field(..., alias="SHIPNAME")
    callsign: str = Field(..., alias="CALLSIGN")
    
    # Movement & Position
    lat: float = Field(..., alias="LAT")
    lon: float = Field(..., alias="LON")
    speed: float = Field(..., alias="SPEED")
    heading: int = Field(..., alias="HEADING")
    course: int = Field(..., alias="COURSE")
    rot: int = Field(..., alias="ROT")
    
    # Status & Time
    status: str = Field(..., alias="STATUS")
    timestamp: datetime = Field(..., alias="TIMESTAMP")
    dsrc: str = Field(..., alias="DSRC")
    utc_seconds: int = Field(..., alias="UTC_SECONDS")
    
    # Vessel Specifications
    market: str = Field(..., alias="MARKET")
    shiptype: str = Field(..., alias="SHIPTYPE")
    type_name: str = Field(..., alias="TYPE_NAME")
    ais_type_summary: str = Field(..., alias="AIS_TYPE_SUMMARY")
    flag: str = Field(..., alias="FLAG")
    ship_country: str = Field(..., alias="SHIP_COUNTRY")
    ship_class: str = Field(..., alias="SHIP_CLASS")
    length: float = Field(..., alias="LENGTH")
    width: float = Field(..., alias="WIDTH")
    grt: int = Field(..., alias="GRT")
    dwt: int = Field(..., alias="DWT")
    draught: int = Field(..., alias="DRAUGHT")
    year_built: str = Field(..., alias="YEAR_BUILT")
    
    # Dimensions relative to AIS antenna
    l_fore: int = Field(..., alias="L_FORE")
    w_left: int = Field(..., alias="W_LEFT")
    
    # Voyage Info
    destination: str = Field(..., alias="DESTINATION")
    eta: Optional[datetime] = Field(None, alias="ETA")
    current_port: str = Field(..., alias="CURRENT_PORT")
    current_port_id: str = Field(..., alias="CURRENT_PORT_ID")
    current_port_unlocode: str = Field(..., alias="CURRENT_PORT_UNLOCODE")
    current_port_country: str = Field(..., alias="CURRENT_PORT_COUNTRY")
    
    last_port: str = Field(..., alias="LAST_PORT")
    last_port_time: Optional[datetime] = Field(None, alias="LAST_PORT_TIME")
    last_port_id: str = Field(..., alias="LAST_PORT_ID")
    last_port_unlocode: str = Field(..., alias="LAST_PORT_UNLOCODE")
    last_port_country: str = Field(..., alias="LAST_PORT_COUNTRY")
    
    next_port_id: str = Field(..., alias="NEXT_PORT_ID")
    next_port_unlocode: str = Field(..., alias="NEXT_PORT_UNLOCODE")
    next_port_name: str = Field(..., alias="NEXT_PORT_NAME")
    next_port_country: str = Field(..., alias="NEXT_PORT_COUNTRY")
    
    # Performance Metrics
    distance_to_go: int = Field(..., alias="DISTANCE_TO_GO")
    distance_travelled: int = Field(..., alias="DISTANCE_TRAVELLED")
    avg_speed: float = Field(..., alias="AVG_SPEED")
    max_speed: float = Field(..., alias="MAX_SPEED")
    
    # Calculated Fields (Optional)
    eta_calc: Optional[str] = Field(None, alias="ETA_CALC")
    eta_updated: Optional[str] = Field(None, alias="ETA_UPDATED")

    class Config:
        populate_by_name = True

class Metadata(BaseModel):
    cursor: str = Field(..., alias="CURSOR")
    date_from: str = Field(..., alias="DATE_FROM")
    date_to: str = Field(..., alias="DATE_TO")

class MarineTrafficResponse(BaseModel):
    data: List[MarineTrafficPosition] = Field(..., alias="DATA")
    metadata: Metadata = Field(..., alias="METADATA")
