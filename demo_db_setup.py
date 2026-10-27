"""
Demo database bootstrap for ephemeral hosts (e.g. Render).

Copies the committed seed SQLite file to a writable runtime path on startup
so restarts do not depend on persistent disk. Never touches incidents.db.
"""
from __future__ import annotations

import os
import shutil
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_SEED = REPO_ROOT / "incidents_demo.db"
PROD_DB_BASENAME = "incidents.db"


def default_demo_runtime_path() -> Path:
    """Writable path for demo SQLite (ephemeral disk friendly)."""
    explicit = os.getenv("DEMO_DB_PATH")
    if explicit:
        return Path(explicit)
    return Path("/tmp/incidents_demo.db")


def resolve_seed_path() -> Path:
    raw = os.getenv("DEMO_DB_SEED_PATH")
    if raw:
        return Path(raw).expanduser().resolve()
    return DEFAULT_SEED.resolve()


def _is_production_db_path(path: Path) -> bool:
    return path.name == PROD_DB_BASENAME


def validate_demo_db_config(demo_mode: bool, active_db_path: str) -> None:
    if not demo_mode:
        return
    active = Path(active_db_path).resolve()
    if _is_production_db_path(active):
        raise RuntimeError(
            "Demo mode must not use incidents.db. Set DEMO_DB_PATH to a demo runtime file "
            "(e.g. /tmp/incidents_demo.db)."
        )


def validate_render_public_deploy(demo_mode: bool) -> None:
    if os.getenv("RENDER", "").lower() != "true":
        return
    if not demo_mode:
        raise RuntimeError(
            "Render deployment requires DEMO_MODE=true so the public API stays read-only."
        )


def _verify_demo_seed(seed: Path) -> None:
    if not seed.is_file():
        raise FileNotFoundError(
            f"Demo seed database not found at {seed}. "
            "Run `python3 create_demo_db.py` before deploy or set DEMO_DB_SEED_PATH."
        )
    with sqlite3.connect(seed) as conn:
        count = conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
    if count < 1:
        raise RuntimeError(f"Demo seed at {seed} has no incidents.")


def ensure_demo_database(
    *,
    demo_mode: bool,
    active_db_path: str,
    refresh_from_seed: bool | None = None,
) -> None:
    """
    Prepare demo SQLite for the running process.

    When seed and runtime paths differ, copies seed → runtime on each startup
    (unless DEMO_DB_REFRESH_ON_START=false and runtime already exists).
    """
    if not demo_mode:
        return

    validate_render_public_deploy(demo_mode)
    validate_demo_db_config(demo_mode, active_db_path)

    seed = resolve_seed_path()
    runtime = Path(active_db_path).expanduser().resolve()
    _verify_demo_seed(seed)

    if seed == runtime:
        return

    if refresh_from_seed is None:
        refresh = os.getenv("DEMO_DB_REFRESH_ON_START", "true").lower() != "false"
    else:
        refresh = refresh_from_seed

    runtime.parent.mkdir(parents=True, exist_ok=True)
    if refresh or not runtime.is_file():
        shutil.copy2(seed, runtime)
