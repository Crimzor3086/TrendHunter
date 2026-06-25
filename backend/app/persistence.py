import json
import sqlite3
from pathlib import Path

from backend.app.schemas import RegistryRecord


class RegistryPersistence:
    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS registry_records (
                    trend_id TEXT PRIMARY KEY,
                    record_json TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def save(self, record: RegistryRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO registry_records (trend_id, record_json) VALUES (?, ?)",
                (record.trend_id, record.model_dump_json()),
            )

    def load_all(self) -> list[RegistryRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT record_json FROM registry_records ORDER BY created_at DESC"
            ).fetchall()
        return [RegistryRecord.model_validate_json(row["record_json"]) for row in rows]
