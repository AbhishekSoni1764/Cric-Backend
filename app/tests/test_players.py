import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_players():
    response = client.get("/api/players/")
    assert response.status_code == 200
    assert "message" in response.json()
