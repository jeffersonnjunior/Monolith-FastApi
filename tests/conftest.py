import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.deps import get_bank_service
from app.dao import BankAccountDAO, BankTransferDAO
from app.core.config import get_settings
from app.core.db.engine import get_engine, get_session_factory
from app.main import app
from app.models import Base
from app.services.bank import BankService


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    os.environ["DB_URL"] = "sqlite+aiosqlite:///./test.db"
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()

    engine: AsyncEngine = get_engine()
    service = BankService(account_dao=BankAccountDAO(), transfer_dao=BankTransferDAO())
    app.dependency_overrides[get_bank_service] = lambda: service
    with TestClient(app) as test_client:
        with engine.sync_engine.begin() as connection:
            Base.metadata.create_all(bind=connection)
        yield test_client
        with engine.sync_engine.begin() as connection:
            Base.metadata.drop_all(bind=connection)
    app.dependency_overrides.clear()
