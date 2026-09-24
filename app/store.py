"""In-memory incident store (v0).

Deliberately tiny and behind a class so Day 4 can swap in SQLite/JSON
without touching the API layer.
"""
from datetime import datetime, timezone
from threading import Lock

from app.models import Incident, IncidentCreate, Severity, Status


class InMemoryIncidentStore:
    def __init__(self) -> None:
        self._items: dict[int, Incident] = {}
        self._next_id = 1
        self._lock = Lock()

    def add(self, data: IncidentCreate) -> Incident:
        with self._lock:
            incident = Incident(
                **data.model_dump(),
                id=self._next_id,
                # An incident with a recorded fix counts as resolved.
                status=Status.resolved if data.fix else Status.open,
                created_at=datetime.now(timezone.utc),
            )
            self._items[incident.id] = incident
            self._next_id += 1
            return incident

    def list(self, severity: Severity | None = None) -> list[Incident]:
        items = list(self._items.values())
        if severity is not None:
            items = [i for i in items if i.severity == severity]
        return items

    def get(self, incident_id: int) -> Incident | None:
        return self._items.get(incident_id)
