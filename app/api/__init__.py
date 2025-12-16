"""Api endpoints"""

from fastapi.routing import APIRouter

#from .usercrud import router as usercrud_router
from .healthcheck import router as healthcheck_router
from .description import router as description_router

from .description import router_v2 as description_router_v2


all_routers = APIRouter()
#all_routers.include_router(usercrud_router, prefix="/users", tags=["users"])
all_routers.include_router(healthcheck_router, prefix="/healthcheck", tags=["healthcheck"])
all_routers.include_router(description_router, prefix="/description", tags=["description"])

all_routers_v2 = APIRouter()
all_routers_v2.include_router(description_router_v2, prefix="/description", tags=["description"])
