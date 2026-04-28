from decimal import Decimal

from fastapi.testclient import TestClient


def _create_account(
    client: TestClient,
    owner_name: str,
    document: str,
    agency: str,
    account_number: str,
    initial_balance: str = "0",
) -> dict[str, str]:
    response = client.post(
        "/api/v1/bank/accounts",
        json={
            "owner_name": owner_name,
            "document": document,
            "agency": agency,
            "account_number": account_number,
            "initial_balance": initial_balance,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_account_rejects_duplicate_active_account(client: TestClient) -> None:
    _create_account(client, "Alice", "11111111111", "0001", "12345")
    response = client.post(
        "/api/v1/bank/accounts",
        json={
            "owner_name": "Alice 2",
            "document": "22222222222",
            "agency": "0001",
            "account_number": "12345",
            "initial_balance": "0",
        },
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_deposit_and_withdraw_success(client: TestClient) -> None:
    account = _create_account(client, "Bob", "33333333333", "0001", "99999")

    deposit_response = client.post(
        f"/api/v1/bank/accounts/{account['id']}/deposit",
        json={"amount": "500.00"},
    )
    assert deposit_response.status_code == 200
    assert Decimal(deposit_response.json()["balance"]) == Decimal("500.00")

    withdraw_response = client.post(
        f"/api/v1/bank/accounts/{account['id']}/withdraw",
        json={"amount": "300.00"},
    )
    assert withdraw_response.status_code == 200
    assert Decimal(withdraw_response.json()["balance"]) == Decimal("200.00")


def test_withdraw_rejects_insufficient_funds(client: TestClient) -> None:
    account = _create_account(client, "Carol", "44444444444", "0001", "88888", "100.00")
    response = client.post(
        f"/api/v1/bank/accounts/{account['id']}/withdraw",
        json={"amount": "200.00"},
    )

    assert response.status_code == 422
    assert "Insufficient funds" in response.json()["detail"]


def test_transfer_updates_balances_and_statement(client: TestClient) -> None:
    from_account = _create_account(client, "Dan", "55555555555", "0001", "77777", "1000.00")
    to_account = _create_account(client, "Eve", "66666666666", "0001", "66666", "100.00")

    transfer_response = client.post(
        "/api/v1/bank/transfers",
        json={
            "from_account_id": from_account["id"],
            "to_account_id": to_account["id"],
            "amount": "250.00",
        },
    )
    assert transfer_response.status_code == 201

    from_statement = client.get(f"/api/v1/bank/accounts/{from_account['id']}/statement")
    to_statement = client.get(f"/api/v1/bank/accounts/{to_account['id']}/statement")
    assert from_statement.status_code == 200
    assert to_statement.status_code == 200

    from_payload = from_statement.json()
    to_payload = to_statement.json()
    assert Decimal(from_payload["balance"]) == Decimal("750.00")
    assert Decimal(from_payload["total_transferred_today"]) == Decimal("250.00")
    assert Decimal(to_payload["balance"]) == Decimal("350.00")
    assert Decimal(to_payload["total_transferred_today"]) == Decimal("0")


def test_transfer_rejects_daily_limit_exceeded(client: TestClient) -> None:
    from_account = _create_account(client, "Frank", "77777777777", "0002", "11111", "20000.00")
    to_account = _create_account(client, "Grace", "88888888888", "0002", "22222", "0")

    first_transfer = client.post(
        "/api/v1/bank/transfers",
        json={
            "from_account_id": from_account["id"],
            "to_account_id": to_account["id"],
            "amount": "9000.00",
        },
    )
    assert first_transfer.status_code == 201

    second_transfer = client.post(
        "/api/v1/bank/transfers",
        json={
            "from_account_id": from_account["id"],
            "to_account_id": to_account["id"],
            "amount": "1500.00",
        },
    )
    assert second_transfer.status_code == 422
    assert "Daily transfer limit exceeded" in second_transfer.json()["detail"]
