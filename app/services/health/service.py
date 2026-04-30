from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.schemas.health import HealthResponse


async def get_health_status(settings: Settings, session: AsyncSession) -> HealthResponse:
    db_status = "down"
    try:
        await session.execute(text("SELECT 1"))
        db_status = "up"
    except Exception:
        db_status = "down"

    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        database=db_status,
    )
