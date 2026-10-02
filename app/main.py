"""Incident Copilot API, v0 (in-memory data, no database yet)."""
from fastapi import Depends, FastAPI, HTTPException, status

import os

from app.models import Incident, IncidentCreate, Severity
from app.store import PostgresIncidentStore, SQLiteIncidentStore

app = FastAPI(
    title="Incident Copilot",
    version="0.3.0",
    description="Log and search ops incidents. Persisted to SQLite or Postgres.",
)

# If DATABASE_URL is set (docker-compose sets it), use the real Postgres
# container. Otherwise fall back to the local SQLite file, so the app still
# runs with zero extra setup (e.g. `uvicorn app.main:app` on a bare laptop/VM).
_database_url = os.environ.get("DATABASE_URL")
_store = PostgresIncidentStore(_database_url) if _database_url else SQLiteIncidentStore()


def get_store() -> PostgresIncidentStore | SQLiteIncidentStore:
    return _store


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check (used later by Docker HEALTHCHECK and K8s probes)."""
    return {"status": "ok"}


@app.post("/incidents", response_model=Incident, status_code=status.HTTP_201_CREATED)
def create_incident(
    data: IncidentCreate, store: PostgresIncidentStore | SQLiteIncidentStore = Depends(get_store)
) -> Incident:
    return store.add(data)


@app.get("/incidents", response_model=list[Incident])
def list_incidents(
    severity: Severity | None = None,
    store: PostgresIncidentStore | SQLiteIncidentStore = Depends(get_store),
) -> list[Incident]:
    """List incidents, optionally filtered: /incidents?severity=high"""
    return store.list(severity)


@app.get("/incidents/{incident_id}", response_model=Incident)
def get_incident(
    incident_id: int, store: PostgresIncidentStore | SQLiteIncidentStore = Depends(get_store)
) -> Incident:
    incident = store.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident
