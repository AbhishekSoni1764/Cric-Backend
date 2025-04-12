import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_matches():
    response = client.get("/api/matches/")
    assert response.status_code == 200
    assert "message" in response.json()
