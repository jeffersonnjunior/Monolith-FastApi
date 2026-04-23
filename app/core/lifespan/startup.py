import logging

from fastapi import FastAPI

logger = logging.getLogger(__name__)


async def startup(app: FastAPI) -> None:
    logger.info("Application startup completed: %s", app.title)
