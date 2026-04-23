from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.lifespan.shutdown import shutdown
from app.core.lifespan.startup import startup


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await startup(app)
    try:
        yield
    finally:
        await shutdown(app)
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.lifespan.shutdown import shutdown
from app.core.lifespan.startup import startup


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await startup(app)
    try:
        yield
    finally:
        await shutdown(app)
