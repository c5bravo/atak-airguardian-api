from fastapi import APIRouter
from schemas import AirSurveillanceLog
import random

router = APIRouter()

def aircraft_log(i: int) -> AirSurveillanceLog:
    return AirSurveillanceLog(
        id=i,
        aircraft_id=f"{random.randint(10000, 99999)}",
        general_position=random.choice(["DP52", "EQ45", "FR01", "GS85"]),
        accurate_position=f"{random.randint(1, 99)}km",
        speed=random.choice(["slow", "fast", "supersonic"]),  # lowercase
        direction=random.randint(0, 360),
        altitude=random.choice(["surface", "low", "high"]),  # lowercase
        details=random.choice(["Jet", "Propeller", "Helicopter"])
    )

@router.get("/api", response_model=list[AirSurveillanceLog])
async def get_aircrafts():
    num_aircrafts = random.randint(1, 10)
    return [aircraft_log(i) for i in range(1, num_aircrafts + 1)]
