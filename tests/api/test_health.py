from fastapi.testclient import TestClient

from app.core.config import get_settings


def test_healthcheck_returns_expected_payload(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    settings = get_settings()

    assert payload["status"] == "ok"
    assert payload["service"] == settings.app_name
    assert payload["version"] == settings.app_version
    assert payload["environment"] == settings.app_env
    assert payload["database"] == "up"
