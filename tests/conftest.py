import pytest
from fastapi.testclient import TestClient

from app.core.deps import get_bank_service
from app.dao import BankAccountDAO, BankTransferDAO
from app.main import app
from app.services.bank import BankService


@pytest.fixture
def client() -> TestClient:
    service = BankService(account_dao=BankAccountDAO(), transfer_dao=BankTransferDAO())
    app.dependency_overrides[get_bank_service] = lambda: service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
