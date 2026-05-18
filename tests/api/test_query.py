from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.query import QueryResponse

client = TestClient(app)


def test_query_valid_request():
    # GIVEN
    input_payload = {"question": "Combien de clients ?"}
    expected = QueryResponse(
        question="Combien de clients ?",
        sql="SELECT COUNT(*) FROM clients",
        result=[{"count": 42}],
        explanation="Il y a 42 clients dans la base.",
    )

    # WHEN
    with patch("app.api.query.run_agent", new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = expected
        actual = client.post("/api/v1/query", json=input_payload)

    # THEN
    assert actual.status_code == 200
    assert actual.json()["sql"] == expected.sql
    assert actual.json()["result"] == expected.result
    assert actual.json()["explanation"] == expected.explanation


def test_query_returns_question_in_response():
    # GIVEN
    input_payload = {"question": "Combien de clients ?"}
    expected_question = "Combien de clients ?"
    mock_response = QueryResponse(
        question=expected_question,
        sql="SELECT COUNT(*) FROM clients",
        result=[{"count": 42}],
        explanation="Il y a 42 clients dans la base.",
    )

    # WHEN
    with patch("app.api.query.run_agent", new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = mock_response
        actual = client.post("/api/v1/query", json=input_payload)

    # THEN
    assert actual.json()["question"] == expected_question


def test_query_empty_question_returns_422():
    # GIVEN / WHEN
    actual = client.post("/api/v1/query", json={"question": ""})

    # THEN
    assert actual.status_code == 422


def test_query_missing_question_returns_422():
    # GIVEN / WHEN
    actual = client.post("/api/v1/query", json={})

    # THEN
    assert actual.status_code == 422


def test_query_question_too_long_returns_422():
    # GIVEN / WHEN
    actual = client.post("/api/v1/query", json={"question": "a" * 1001})

    # THEN
    assert actual.status_code == 422


def test_query_agent_failure_returns_500():
    # GIVEN / WHEN
    with patch("app.api.query.run_agent", new_callable=AsyncMock) as mock_agent:
        mock_agent.side_effect = Exception("Athena connection failed")
        actual = client.post("/api/v1/query", json={"question": "Combien de clients ?"})

    # THEN
    assert actual.status_code == 500
    assert "Athena connection failed" in actual.json()["detail"]
