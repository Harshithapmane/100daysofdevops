"""SQLite-backed incident store.

Same shape as the v0 in-memory store (add/list/get), so main.py barely
changes. Data now survives an app restart because it lives in a .sqlite3
file on disk instead of only in RAM.
"""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from app.models import Incident, IncidentCreate, Severity, Status

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "incidents.db"


class SQLiteIncidentStore:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        # check_same_thread=False: FastAPI may use this store from different
        # request threads; our own _lock still serializes writes.
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    symptoms TEXT NOT NULL,
                    root_cause TEXT,
                    fix TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def _row_to_incident(row: sqlite3.Row) -> Incident:
        return Incident(
            id=row["id"],
            title=row["title"],
            severity=Severity(row["severity"]),
            symptoms=row["symptoms"],
            root_cause=row["root_cause"],
            fix=row["fix"],
            status=Status(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def add(self, data: IncidentCreate) -> Incident:
        with self._lock, self._connect() as conn:
            status_value = Status.resolved if data.fix else Status.open
            created_at = datetime.now(timezone.utc)
            cursor = conn.execute(
                """
                INSERT INTO incidents
                    (title, severity, symptoms, root_cause, fix, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data.title,
                    data.severity.value,
                    data.symptoms,
                    data.root_cause,
                    data.fix,
                    status_value.value,
                    created_at.isoformat(),
                ),
            )
            return Incident(
                **data.model_dump(),
                id=cursor.lastrowid,
                status=status_value,
                created_at=created_at,
            )

    def list(self, severity: Severity | None = None) -> list[Incident]:
        with self._connect() as conn:
            if severity is not None:
                rows = conn.execute(
                    "SELECT * FROM incidents WHERE severity = ? ORDER BY id",
                    (severity.value,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM incidents ORDER BY id").fetchall()
            return [self._row_to_incident(r) for r in rows]

    def get(self, incident_id: int) -> Incident | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM incidents WHERE id = ?", (incident_id,)
            ).fetchone()
            return self._row_to_incident(row) if row else None
