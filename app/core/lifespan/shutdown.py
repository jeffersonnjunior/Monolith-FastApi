import logging

from fastapi import FastAPI

from app.core.db import close_engine

logger = logging.getLogger(__name__)


async def shutdown(app: FastAPI) -> None:
    await close_engine()
    logger.info("Application shutdown completed: %s", app.title)
