import os

import pytest
from sqlalchemy import text

from app.core.config import get_settings
from app.core.db.engine import get_engine, get_session_factory


@pytest.mark.asyncio
async def test_session_can_execute_simple_query() -> None:
    os.environ["DB_URL"] = "sqlite+aiosqlite:///./test.db"
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()

    session_factory = get_session_factory()
    async with session_factory() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1
