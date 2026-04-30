import os

import pytest
from fastapi.testclient import TestClient

from app.core.deps import get_bank_service
from app.dao import BankAccountDAO, BankTransferDAO
from app.core.config import get_settings
from app.core.db.engine import get_engine, get_session_factory
from app.main import app
from app.services.bank import BankService


@pytest.fixture
def client() -> TestClient:
    os.environ["DB_URL"] = "sqlite+aiosqlite:///./test.db"
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()

    service = BankService(account_dao=BankAccountDAO(), transfer_dao=BankTransferDAO())
    app.dependency_overrides[get_bank_service] = lambda: service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
