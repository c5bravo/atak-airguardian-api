import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import mgrs  # type: ignore
from fastapi import APIRouter, HTTPException

from app.schemas.schema import TransformedAircraft
from app.schemas.schema_marine_traffic import ShipFeature
from app.tasks.radar_task import fetch_aircraft_data
from app.tasks.marine_traffic_task import fetch_fin_marine_traffic_data

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/radar", tags=["radar"])

mgrs_converter = mgrs.MGRS()


def to_mgrs_typed(latitude: float, longitude: float) -> str:
    mgrs_string: str = mgrs_converter.toMGRS(latitude, longitude, True, 1)  # pyright: ignore[reportUnknownMemberType]
    return mgrs_string


def convert_timestamp_to_datetime(timestamp: Optional[int]) -> Optional[str]:
    """Convert UNIX timestamp to formatted datetime string."""
    if timestamp is None:
        return None
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except Exception as e:
        logger.error(f"Error converting timestamp {timestamp}: {e}")
        return None


def convert_to_mgrs(longitude: Optional[float], latitude: Optional[float]) -> Optional[str]:
    if longitude is None or latitude is None:
        return None
    try:
        mgrs_string: str = to_mgrs_typed(latitude, longitude)
        return mgrs_string.strip().replace(" ", "")
    except Exception as e:
        logger.error(f"Error converting coordinates ({latitude}, {longitude}) to MGRS: {e}")
        return None


def classify_altitude(altitude: Optional[float]) -> Optional[str]:
    if altitude is None:
        return None
    if altitude < 300:
        return "surface"
    elif altitude < 3000:
        return "low"
    else:
        return "high"


def classify_speed(velocity: Optional[float]) -> Optional[str]:
    if velocity is None:
        return None
    if velocity < 140:
        return "slow"
    elif velocity < 280:
        return "fast"
    else:
        return "supersonic"


def more_details(aircraft: Optional[Dict[str, Any]]) -> Optional[str]:
    if not aircraft:
        return None

    callsign = aircraft.get("callsign")
    origin_country = aircraft.get("origin_country")

    if not isinstance(callsign, str) or not isinstance(origin_country, str):
        return None

    return f"This aircraft[{callsign}] from [{origin_country}] and it is civilian aircraft."


def transform_aircraft(aircraft: Dict[str, Any]) -> TransformedAircraft:
    true_track_raw = aircraft.get("true_track")
    try:
        true_track = int(true_track_raw) if true_track_raw is not None else 0
    except (ValueError, TypeError):
        true_track = 0

    transformed: TransformedAircraft = {
        "id": 0,
        "aircraftId": aircraft.get("callsign"),
        "position": convert_to_mgrs(aircraft.get("longitude"), aircraft.get("latitude")),
        "altitude": classify_altitude(aircraft.get("baro_altitude")),
        "speed": classify_speed(aircraft.get("velocity")),
        "direction": true_track,
        "details": more_details(aircraft),
        "isExited": bool(aircraft.get("isExited")),
        "type": "openSky",
    }
    return transformed


def filter_on_ground(aircraft: Dict[str, Any]) -> bool:
    # Only aircraft not on ground
    return not bool(aircraft.get("on_ground"))


def transform_finTraffic_ship(feature: ShipFeature) -> TransformedAircraft:
    coords = feature.geometry.coordinates
    props = feature.properties

    lon = coords[0] if len(coords) > 0 else None
    lat = coords[1] if len(coords) > 1 else None

    direction_val: int = int(props.heading) if props.heading is not None else 0

    return {
        "id": feature.mmsi,
        "aircraftId": str(feature.mmsi),
        "position": convert_to_mgrs(lon, lat),
        "altitude": "surface",
        "speed": classify_speed(props.sog),
        "direction": direction_val,
        "details": f"MMSI: {feature.mmsi} | Status: {props.navStat}",
        "isExited": False,
        "type": "marineTraffic",
    }


@router.get("/aircraft")
def get_aircraft_data() -> List[TransformedAircraft]:
    try:
        data = fetch_aircraft_data()
        raw_fin_marine_data = fetch_fin_marine_traffic_data()

        # Transform OpenSky data
        filtered_data = list(filter(filter_on_ground, data))
        transformed_aircraft = [transform_aircraft(ac) for ac in filtered_data]

        # Transform FinMarine data
        transformed_FinMarine = [transform_finTraffic_ship(ship) for ship in raw_fin_marine_data]

        return [
            *transformed_aircraft,
            *transformed_FinMarine,
        ]

    except Exception as e:
        logger.error(f"Error retrieving aircraft data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
