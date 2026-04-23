import logging

from fastapi import FastAPI

logger = logging.getLogger(__name__)


async def shutdown(app: FastAPI) -> None:
    logger.info("Application shutdown completed: %s", app.title)
