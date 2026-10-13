"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_root_endpoint(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "operational"
    assert "GlucoTwin" in data["project"]


def test_patients_endpoints(client):
    res = client.get("/api/patients")
    assert res.status_code == 200
    patients = res.json()
    assert len(patients) >= 6
    assert patients[0]["patient_id"] == "PT-101"
    
    # Single patient
    res_single = client.get("/api/patients/PT-101")
    assert res_single.status_code == 200
    assert res_single.json()["name"] == "Rajesh Patel"


def test_forecast_step_and_inject(client):
    res = client.post("/api/forecast/PT-101/step")
    assert res.status_code == 200
    data = res.json()
    assert "twin_state" in data
    assert "recent_history" in data
    assert len(data["recent_history"]) > 0
    
    # Inject meal
    inj_res = client.post("/api/forecast/inject", json={
        "patient_id": "PT-101",
        "event_type": "meal",
        "carbs": 50.0,
        "exercise_minutes": 0.0,
        "description": "Lunch Roti & Dal"
    })
    assert inj_res.status_code == 200
    assert inj_res.json()["status"] == "ok"
