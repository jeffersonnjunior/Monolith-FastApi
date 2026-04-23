from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.health import HealthResponse
from app.services.health import get_health_status

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def healthcheck(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return get_health_status(settings)
from fastapi import APIRouter, Depends

from app.core.config.settings import Settings, get_settings
from app.schemas.health import HealthResponse
from app.services.health import get_health_status

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def healthcheck(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return get_health_status(settings)
