from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.deps import get_session
from app.schemas.health import HealthResponse
from app.services.health import get_health_status

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def healthcheck(
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> HealthResponse:
    return await get_health_status(settings=settings, session=session)
