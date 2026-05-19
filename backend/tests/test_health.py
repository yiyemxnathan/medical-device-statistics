from fastapi.testclient import TestClient

from app.main import create_app


def test_health_returns_versions():
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app_version": "0.1.0",
        "algorithm_version": "sampling-statistics-0.1.0",
    }
