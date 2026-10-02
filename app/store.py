"""Incident stores.

Two implementations, same shape (add/list/get), so main.py doesn't care
which one is in use:
  - SQLiteIncidentStore: a single local file. Good for running the app
    directly on a laptop/VM with no extra setup.
  - PostgresIncidentStore: a real database server. Used when running via
    docker-compose, where a separate Postgres container is available.
main.py picks one automatically based on whether DATABASE_URL is set.
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


class PostgresIncidentStore:
    """Same interface as SQLiteIncidentStore, backed by a real Postgres server."""

    def __init__(self, dsn: str) -> None:
        import psycopg  # imported here so psycopg is only required when this store is used

        self._psycopg = psycopg
        self.dsn = dsn
        self._init_schema()

    def _connect(self):
        return self._psycopg.connect(self.dsn)

    def _init_schema(self) -> None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    symptoms TEXT NOT NULL,
                    root_cause TEXT,
                    fix TEXT,
                    status TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            conn.commit()

    @staticmethod
    def _row_to_incident(row) -> Incident:
        (id_, title, severity, symptoms, root_cause, fix, status_, created_at) = row
        return Incident(
            id=id_,
            title=title,
            severity=Severity(severity),
            symptoms=symptoms,
            root_cause=root_cause,
            fix=fix,
            status=Status(status_),
            created_at=created_at,
        )

    def add(self, data: IncidentCreate) -> Incident:
        status_value = Status.resolved if data.fix else Status.open
        created_at = datetime.now(timezone.utc)
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO incidents
                    (title, severity, symptoms, root_cause, fix, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    data.title,
                    data.severity.value,
                    data.symptoms,
                    data.root_cause,
                    data.fix,
                    status_value.value,
                    created_at,
                ),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
        return Incident(
            **data.model_dump(), id=new_id, status=status_value, created_at=created_at
        )

    def list(self, severity: Severity | None = None) -> list[Incident]:
        with self._connect() as conn, conn.cursor() as cur:
            if severity is not None:
                cur.execute(
                    "SELECT * FROM incidents WHERE severity = %s ORDER BY id",
                    (severity.value,),
                )
            else:
                cur.execute("SELECT * FROM incidents ORDER BY id")
            return [self._row_to_incident(r) for r in cur.fetchall()]

    def get(self, incident_id: int) -> Incident | None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM incidents WHERE id = %s", (incident_id,))
            row = cur.fetchone()
            return self._row_to_incident(row) if row else None
