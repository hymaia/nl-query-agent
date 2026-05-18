from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_returns_200():
    # WHEN
    actual = client.get("/health")

    # THEN
    assert actual.status_code == 200


def test_health_returns_ok():
    # GIVEN
    expected = {"status": "ok"}

    # WHEN
    actual = client.get("/health")

    # THEN
    assert actual.json() == expected
