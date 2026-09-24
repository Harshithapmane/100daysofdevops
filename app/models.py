"""Pydantic models: the shape of an incident on the way in and out of the API."""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Status(str, Enum):
    open = "open"
    resolved = "resolved"


class IncidentCreate(BaseModel):
    """What a client sends to POST /incidents."""

    title: str = Field(min_length=3, max_length=120, examples=["AKS node NotReady"])
    severity: Severity
    symptoms: str = Field(min_length=1, examples=["Pods stuck Pending after node drain"])
    root_cause: str | None = None
    fix: str | None = None


class Incident(IncidentCreate):
    """What the API returns: the input plus server-generated fields."""

    id: int
    status: Status
    created_at: datetime
