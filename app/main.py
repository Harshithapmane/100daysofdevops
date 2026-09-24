"""Incident Copilot API, v0 (in-memory data, no database yet)."""
from fastapi import Depends, FastAPI, HTTPException, status

from app.models import Incident, IncidentCreate, Severity
from app.store import InMemoryIncidentStore

app = FastAPI(
    title="Incident Copilot",
    version="0.1.0",
    description="Log and search ops incidents. v0: in-memory storage.",
)

_store = InMemoryIncidentStore()


def get_store() -> InMemoryIncidentStore:
    return _store


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check (used later by Docker HEALTHCHECK and K8s probes)."""
    return {"status": "ok"}


@app.post("/incidents", response_model=Incident, status_code=status.HTTP_201_CREATED)
def create_incident(
    data: IncidentCreate, store: InMemoryIncidentStore = Depends(get_store)
) -> Incident:
    return store.add(data)


@app.get("/incidents", response_model=list[Incident])
def list_incidents(
    severity: Severity | None = None,
    store: InMemoryIncidentStore = Depends(get_store),
) -> list[Incident]:
    """List incidents, optionally filtered: /incidents?severity=high"""
    return store.list(severity)


@app.get("/incidents/{incident_id}", response_model=Incident)
def get_incident(
    incident_id: int, store: InMemoryIncidentStore = Depends(get_store)
) -> Incident:
    incident = store.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incident
