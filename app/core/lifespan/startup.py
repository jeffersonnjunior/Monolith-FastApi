import logging

from fastapi import FastAPI

from app.core.db import check_database_connection

logger = logging.getLogger(__name__)


async def startup(app: FastAPI) -> None:
    await check_database_connection()
    logger.info("Application startup completed: %s", app.title)
