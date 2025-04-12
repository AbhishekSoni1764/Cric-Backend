import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_collapses():
    response = client.get("/api/analytics/collapses/test_match")
    assert response.status_code == 200
    assert "message" in response.json()
