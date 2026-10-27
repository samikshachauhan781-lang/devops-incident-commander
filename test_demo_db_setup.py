"""Tests for demo database bootstrap (Render / ephemeral disk)."""
import os
import sqlite3
import tempfile
from pathlib import Path

import pytest

from demo_db_setup import ensure_demo_database, validate_demo_db_config


@pytest.fixture
def seed_db(tmp_path: Path) -> Path:
    path = tmp_path / "incidents_demo.db"
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE incidents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL,
            service TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            resolved_at TEXT
        )
        """
    )
    conn.execute(
        """
        INSERT INTO incidents VALUES (
            'demo-1', 't', 'description long enough', 'low', 'open', 'svc',
            '2026-08-01T00:00:00+00:00', '2026-08-01T00:00:00+00:00', NULL
        )
        """
    )
    conn.commit()
    conn.close()
    return path


def test_rejects_incidents_db_in_demo_mode():
    with pytest.raises(RuntimeError, match="must not use incidents.db"):
        validate_demo_db_config(True, "/data/incidents.db")


def test_copies_seed_to_runtime(seed_db: Path, tmp_path: Path):
    runtime = tmp_path / "runtime" / "incidents_demo.db"
    os.environ["DEMO_DB_SEED_PATH"] = str(seed_db)
    os.environ["DEMO_DB_REFRESH_ON_START"] = "true"
    try:
        ensure_demo_database(
            demo_mode=True,
            active_db_path=str(runtime),
            refresh_from_seed=True,
        )
        assert runtime.is_file()
        with sqlite3.connect(runtime) as conn:
            assert conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0] == 1
    finally:
        os.environ.pop("DEMO_DB_SEED_PATH", None)
        os.environ.pop("DEMO_DB_REFRESH_ON_START", None)
