"""One automated test covering the API end to end against a real SQLite file.

Uses a temporary database (not the app's real data/incidents.db) so running
tests never touches or clutters real incident data.
"""
from fastapi.testclient import TestClient

from app.main import app, get_store
from app.store import SQLiteIncidentStore


def test_create_list_and_get_incident(tmp_path):
    # Point the app at a throwaway SQLite file just for this test.
    test_store = SQLiteIncidentStore(db_path=tmp_path / "test_incidents.db")
    app.dependency_overrides[get_store] = lambda: test_store
    client = TestClient(app)

    # Health check responds.
    assert client.get("/health").json() == {"status": "ok"}

    # Creating an incident returns 201 with server-assigned fields.
    payload = {"title": "AKS node NotReady", "severity": "high", "symptoms": "Pods Pending"}
    create_resp = client.post("/incidents", json=payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["id"] == 1
    assert created["status"] == "open"  # no fix given

    # It shows up in the list.
    list_resp = client.get("/incidents")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # It can be fetched by id.
    get_resp = client.get(f"/incidents/{created['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "AKS node NotReady"

    # A missing id returns 404.
    assert client.get("/incidents/999").status_code == 404

    # Bad input (title too short) is rejected before it reaches storage.
    bad_resp = client.post("/incidents", json={"title": "x", "severity": "high", "symptoms": "y"})
    assert bad_resp.status_code == 422

    app.dependency_overrides.clear()
