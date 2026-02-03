from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Geometry(BaseModel):
    type: str = "Point"
    # GeoJSON coordinates are [longitude, latitude]
    coordinates: List[float]


class ShipProperties(BaseModel):
    mmsi: int
    sog: Optional[float] = None  # Speed Over Ground
    cog: Optional[float] = None # Course Over Ground
    navStat: int
    rot: Optional[int] = None  # Rate of Turn
    posAcc: bool
    raim: bool
    heading: Optional[float] = None
    timestamp: int
    timestampExternal: int  # Unix timestamp in milliseconds


class ShipFeature(BaseModel):
    mmsi: int
    type: str = "Feature"
    geometry: Geometry
    properties: ShipProperties


class GeoJSONShipResponse(BaseModel):
    type: str = "FeatureCollection"
    dataUpdatedTime: datetime
    features: List[ShipFeature]
