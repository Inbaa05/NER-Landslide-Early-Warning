from fastapi.testclient import TestClient
from main import app, risk_from_inputs

client = TestClient(app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_zones():
    r = client.get("/api/zones")
    assert r.status_code == 200
    assert len(r.json()["zones"]) >= 5

def test_risk_levels():
    low = risk_from_inputs(0, 0, 0, 10, 0.1)
    high = risk_from_inputs(120, 180, 120, 50, 1.0)
    assert low[1] == "Low"
    assert high[1] == "Severe"

def test_report():
    payload = {
        "latitude": 26.14,
        "longitude": 91.74,
        "category": "blocked-road",
        "description": "Road blocked after slope movement."
    }
    r = client.post("/api/reports", json=payload)
    assert r.status_code == 201
    assert r.json()["accepted"] is True
