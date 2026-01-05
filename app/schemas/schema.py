from typing import Optional, TypedDict


class TransformedAircraft(TypedDict, total=False):
    id: int
    aircraftId: Optional[str]
    position: Optional[str]
    altitude: Optional[str]
    speed: Optional[str]
    direction: int
    details: Optional[str]
    isExited: bool
