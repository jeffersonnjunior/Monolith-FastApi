from decimal import Decimal
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.deps import get_idempotency_cache
from app.core.deps.cache import IdempotencyCacheEntry
from app.core.db.engine import get_engine


def _seed_balance(user_id: str, amount: str, version_id: int = 1) -> None:
    engine = get_engine()
    with engine.sync_engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO user_balances (user_id, balance, version_id, updated_at)
                VALUES (:user_id, :balance, :version_id, CURRENT_TIMESTAMP)
                """
            ),
            {"user_id": user_id, "balance": amount, "version_id": version_id},
        )


def _seed_checkout(idempotency_key: str, user_id: str, amount: str, status: str) -> None:
    engine = get_engine()
    with engine.sync_engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO payment_checkouts (
                    id, user_id, idempotency_key, amount, status, failure_reason, created_at, updated_at
                )
                VALUES (
                    :id, :user_id, :idempotency_key, :amount, :status, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
                """
            ),
            {
                "id": str(uuid4()),
                "user_id": user_id,
                "idempotency_key": idempotency_key,
                "amount": amount,
                "status": status,
            },
        )


def test_checkout_requires_idempotency_key(client: TestClient) -> None:
    response = client.post(
        "/api/v1/checkout/payments/checkout",
        json={"user_id": str(uuid4()), "order_amount": "10.00"},
    )
    assert response.status_code == 400
    assert "X-Idempotency-Key" in response.json()["detail"]


def test_checkout_success_and_idempotent_replay(client: TestClient) -> None:
    user_id = str(uuid4())
    _seed_balance(user_id=user_id, amount="150.00")

    first = client.post(
        "/api/v1/checkout/payments/checkout",
        headers={"X-Idempotency-Key": "idem-success-1"},
        json={"user_id": user_id, "order_amount": "100.00"},
    )
    assert first.status_code == 200

    second = client.post(
        "/api/v1/checkout/payments/checkout",
        headers={"X-Idempotency-Key": "idem-success-1"},
        json={"user_id": user_id, "order_amount": "100.00"},
    )
    assert second.status_code == 200
    assert second.json()["checkout_id"] == first.json()["checkout_id"]
    assert second.json()["status"] == "completed"


def test_checkout_returns_conflict_when_processing_cache_exists(client: TestClient) -> None:
    cache = get_idempotency_cache()
    import anyio

    anyio.run(cache.set, "idem-processing", IdempotencyCacheEntry(status="processing", payload={}))
    response = client.post(
        "/api/v1/checkout/payments/checkout",
        headers={"X-Idempotency-Key": "idem-processing"},
        json={"user_id": str(uuid4()), "order_amount": "10.00"},
    )
    assert response.status_code == 409


def test_checkout_returns_conflict_when_processing_exists_in_database(client: TestClient) -> None:
    user_id = str(uuid4())
    _seed_checkout(idempotency_key="idem-db-processing", user_id=user_id, amount="25.00", status="processing")

    response = client.post(
        "/api/v1/checkout/payments/checkout",
        headers={"X-Idempotency-Key": "idem-db-processing"},
        json={"user_id": user_id, "order_amount": "25.00"},
    )
    assert response.status_code == 409


def test_checkout_insufficient_balance_marks_failed_and_returns_400(client: TestClient) -> None:
    user_id = str(uuid4())
    _seed_balance(user_id=user_id, amount="20.00")

    response = client.post(
        "/api/v1/checkout/payments/checkout",
        headers={"X-Idempotency-Key": "idem-fail-1"},
        json={"user_id": user_id, "order_amount": "90.00"},
    )
    assert response.status_code == 400

    replay = client.post(
        "/api/v1/checkout/payments/checkout",
        headers={"X-Idempotency-Key": "idem-fail-1"},
        json={"user_id": user_id, "order_amount": "90.00"},
    )
    assert replay.status_code == 200
    assert replay.json()["status"] == "failed"


def test_checkout_concurrency_conflict_returns_409(client: TestClient) -> None:
    user_id = str(uuid4())
    _seed_balance(user_id=user_id, amount="100.00")
    with patch(
        "app.dao.repositories.checkout.UserBalanceRepository.discount_with_version",
        new=AsyncMock(return_value=False),
    ):
        response = client.post(
            "/api/v1/checkout/payments/checkout",
            headers={"X-Idempotency-Key": "idem-conflict-1"},
            json={"user_id": user_id, "order_amount": str(Decimal("10.00"))},
        )
    assert response.status_code == 409
