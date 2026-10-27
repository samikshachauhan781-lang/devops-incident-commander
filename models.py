# Incident Data Model for DevOps Incident Commander
# This module defines Pydantic models for representing incidents in the system
# SQLite persistence layer added in Day 4

from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Literal, Optional, List
from uuid import uuid4
import os
import sqlite3
import json
from contextlib import contextmanager

# Define literal types for validation
SEVERITY_LEVELS = Literal["low", "medium", "high", "critical"]
STATUS_LEVELS = Literal["open", "investigating", "resolved", "closed"]

class Incident(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique incident identifier")
    title: str = Field(..., min_length=1, max_length=200, description="Incident title")
    description: str = Field(..., min_length=10, description="Incident description")
    severity: SEVERITY_LEVELS = Field("medium", description="Incident severity")
    status: STATUS_LEVELS = Field("open", description="Incident status")
    service: str = Field(..., min_length=1, description="Affected service")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Creation timestamp")
    resolved_at: Optional[str] = Field(None, description="Resolution timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Last update timestamp")

    @field_validator('severity')
    def validate_severity(cls, v):
        if v not in ["low", "medium", "high", "critical"]:
            raise ValueError(f"Invalid severity: {v}")
        return v

    @field_validator('status')
    def validate_status(cls, v):
        if v not in ["open", "investigating", "resolved", "closed"]:
            raise ValueError(f"Invalid status: {v}")
        return v

class IncidentCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Incident title")
    description: str = Field(..., min_length=10, description="Incident description")
    severity: SEVERITY_LEVELS = Field("medium", description="Incident severity")
    status: STATUS_LEVELS = Field("open", description="Incident status")
    service: str = Field(..., min_length=1, description="Affected service")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Creation timestamp")
    resolved_at: Optional[str] = Field(None, description="Resolution timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Last update timestamp")

class IncidentUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Incident title")
    description: Optional[str] = Field(None, min_length=10, description="Incident description")
    severity: Optional[SEVERITY_LEVELS] = Field(None, description="Incident severity")
    status: Optional[STATUS_LEVELS] = Field(None, description="Incident status")
    service: Optional[str] = Field(None, min_length=1, description="Affected service")
    resolved_at: Optional[str] = Field(None, description="Resolution timestamp")
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Last update timestamp")

class IncidentResponse(BaseModel):
    id: str = Field(..., description="Incident unique identifier")
    title: str = Field(..., description="Incident title")
    description: str = Field(..., description="Incident description")
    severity: SEVERITY_LEVELS = Field(..., description="Incident severity")
    status: STATUS_LEVELS = Field(..., description="Incident status")
    service: str = Field(..., description="Affected service")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    resolved_at: Optional[str] = Field(None, description="Resolution timestamp")

class IncidentListResponse(BaseModel):
    incidents: List[IncidentResponse] = Field(..., description="List of incidents")
    page: int = Field(..., description="Page number")
    page_size: int = Field(..., description="Page size")
    total: int = Field(..., description="Total number of incidents")

class IncidentEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()), description="Event unique identifier")
    incident_id: str = Field(..., description="Associated incident ID")
    event_type: str = Field(..., description="Event type")
    description: str = Field(..., description="Event description")
    old_values: Optional[str] = Field(None, description="Old values JSON")
    new_values: Optional[str] = Field(None, description="New values JSON")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Event creation timestamp")

# Database functions

# Global variables for database configuration (overridden by main.py in demo mode)
_db_path = os.getenv(
    "DB_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "incidents.db"),
)
_test_db_path_override = None

# Database initialization
def set_test_database_path(path: str):
    global _test_db_path_override
    _test_db_path_override = path


def clear_test_database_path():
    global _test_db_path_override
    _test_db_path_override = None


def _get_db_path():
    if _test_db_path_override is not None:
        return _test_db_path_override
    return _db_path

@contextmanager
def get_db_connection(db_path=None):
    if db_path is None:
        db_path = _get_db_path()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Initialize production database with sample data
def init_database(db_path=None):
    if db_path is None:
        db_path = _get_db_path()

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
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
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incident_events (
                id TEXT PRIMARY KEY,
                incident_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                old_values TEXT,
                new_values TEXT,
                created_at TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_incident_events_incident_id ON incident_events(incident_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_incident_events_created_at ON incident_events(created_at)
        ''')

        conn.commit()
        print(f"✅ Database initialized at {db_path}")


def init_production_sample_data():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM incidents")

        sample_incidents = [
            {
                "id": "3c240ff9-ee44-44ab-ba68-0a3ed92b9c06",
                "title": "API Service High Response Time",
                "description": "API response times exceeding 5 seconds for payment endpoints. Users experiencing slow performance.",
                "severity": "high",
                "status": "investigating",
                "service": "api-service"
            },
            {
                "id": "4d8cfa76-195e-44ce-9f85-e9524189ce9d",
                "title": "Database Connection Pool Exhaustion",
                "description": "Database connection pool reached maximum limit. New connections rejected.",
                "severity": "critical",
                "status": "open",
                "service": "database-service"
            }
        ]

        for incident in sample_incidents:
            cursor.execute('''
                INSERT INTO incidents (id, title, description, severity, status, service, created_at, resolved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                incident["id"],
                incident["title"],
                incident["description"],
                incident["severity"],
                incident["status"],
                incident["service"],
                incident.get("created_at", "2024-01-13T14:30:00.000Z"),
                None
            ))

        conn.commit()
        print(f"✅ Production database initialized with sample incidents")

# Incident model initialized without automatic database setup
# Database will be initialized on-demand when needed

print(f"✅ Incident model initialized with SQLite persistence")
print(f"✅ Database path: {_db_path}")

# Analytics functions

def get_analytics_overview():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            query = """
            SELECT
                COUNT(*) as total_incidents,
                COUNT(CASE WHEN status = 'open' THEN 1 END) as open_incidents,
                COUNT(CASE WHEN status = 'investigating' THEN 1 END) as investigating_incidents,
                COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_incidents,
                COUNT(CASE WHEN status = 'closed' THEN 1 END) as closed_incidents,
                COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_incidents
            FROM incidents
            """
            cursor.execute(query)
            result = cursor.fetchone()

            total = result[0] if result[0] is not None else 0
            open_count = result[1] if result[1] is not None else 0
            investigating_count = result[2] if result[2] is not None else 0
            resolved_count = result[3] if result[3] is not None else 0
            closed_count = result[4] if result[4] is not None else 0
            critical_count = result[5] if result[5] is not None else 0

            resolution_rate = 0.0
            if total > 0:
                resolution_rate = round((resolved_count + closed_count) / total * 100, 2)

            return {
                "total_incidents": total,
                "open_incidents": open_count,
                "investigating_incidents": investigating_count,
                "resolved_incidents": resolved_count,
                "closed_incidents": closed_count,
                "critical_incidents": critical_count,
                "resolution_rate_percent": resolution_rate
            }

    except Exception as e:
        return {
            "total_incidents": 0,
            "open_incidents": 0,
            "investigating_incidents": 0,
            "resolved_incidents": 0,
            "closed_incidents": 0,
            "critical_incidents": 0,
            "resolution_rate_percent": 0.0
        }


def get_severity_breakdown():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            query = """
            SELECT
                severity,
                COUNT(*) as count
            FROM incidents
            GROUP BY severity
            """
            cursor.execute(query)
            results = cursor.fetchall()

            total_query = "SELECT COUNT(*) as total FROM incidents"
            cursor.execute(total_query)
            total_result = cursor.fetchone()
            total = total_result[0] if total_result and total_result[0] is not None else 0

            severity_breakdown = []
            severity_categories = ["low", "medium", "high", "critical"]

            for category in severity_categories:
                count = 0
                for row in results:
                    if row[0] == category:
                        count = row[1] if row[1] is not None else 0
                        break

                percentage = 0.0
                if total > 0:
                    percentage = round((count / total) * 100, 2)

                severity_breakdown.append({
                    "severity": category,
                    "count": count,
                    "percentage": percentage
                })

            return {
                "severity_breakdown": severity_breakdown
            }

    except Exception as e:
        return {
            "severity_breakdown": [
                {"severity": "low", "count": 0, "percentage": 0.0},
                {"severity": "medium", "count": 0, "percentage": 0.0},
                {"severity": "high", "count": 0, "percentage": 0.0},
                {"severity": "critical", "count": 0, "percentage": 0.0}
            ]
        }


def get_status_breakdown():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            query = """
            SELECT
                status,
                COUNT(*) as count
            FROM incidents
            GROUP BY status
            """
            cursor.execute(query)
            results = cursor.fetchall()

            total_query = "SELECT COUNT(*) as total FROM incidents"
            cursor.execute(total_query)
            total_result = cursor.fetchone()
            total = total_result[0] if total_result and total_result[0] is not None else 0

            status_breakdown = []
            status_categories = ["open", "investigating", "resolved", "closed"]

            for category in status_categories:
                count = 0
                for row in results:
                    if row[0] == category:
                        count = row[1] if row[1] is not None else 0
                        break

                percentage = 0.0
                if total > 0:
                    percentage = round((count / total) * 100, 2)

                status_breakdown.append({
                    "status": category,
                    "count": count,
                    "percentage": percentage
                })

            return {
                "status_breakdown": status_breakdown
            }

    except Exception as e:
        return {
            "status_breakdown": [
                {"status": "open", "count": 0, "percentage": 0.0},
                {"status": "investigating", "count": 0, "percentage": 0.0},
                {"status": "resolved", "count": 0, "percentage": 0.0},
                {"status": "closed", "count": 0, "percentage": 0.0}
            ]
        }

# Database CRUD functions
def save_incident(incident_data):
    """Save a new incident to the database."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            query = """
            INSERT INTO incidents (id, title, description, severity, status, service, created_at, updated_at, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, (
                incident_data.get('id'),
                incident_data.get('title'),
                incident_data.get('description'),
                incident_data.get('severity'),
                incident_data.get('status'),
                incident_data.get('service'),
                incident_data.get('created_at'),
                incident_data.get('created_at'),  # updated_at should be same as created_at for new incidents
                incident_data.get('resolved_at')
            ))

            conn.commit()
            return True
    except Exception as e:
        print(f"Error saving incident: {e}")
        return False

def get_incident(incident_id):
    """Get a single incident by ID."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM incidents WHERE id = ?"
            cursor.execute(query, (incident_id,))

            result = cursor.fetchone()
            if result:
                return dict(result)
            return None
    except Exception as e:
        print(f"Error getting incident {incident_id}: {e}")
        return None

def list_incidents(page=1, page_size=10):
    """List incidents with pagination."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get total count
            total_query = "SELECT COUNT(*) as count FROM incidents"
            cursor.execute(total_query)
            total_result = cursor.fetchone()
            total = total_result[0] if total_result else 0

            # Get incidents with pagination
            offset = (page - 1) * page_size
            incidents_query = """
            SELECT * FROM incidents
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """
            cursor.execute(incidents_query, (page_size, offset))

            incidents = []
            for row in cursor.fetchall():
                incident = dict(row)
                incidents.append(incident)

            return {
                "incidents": incidents,
                "page": page,
                "page_size": page_size,
                "total": total,
                "has_more": (page * page_size) < total
            }
    except Exception as e:
        print(f"Error listing incidents: {e}")
        return {
            "incidents": [],
            "page": page,
            "page_size": page_size,
            "total": 0,
            "has_more": False
        }

def save_event(event_data):
    """Save a new event to the database."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            query = """
            INSERT INTO incident_events (id, incident_id, event_type, description, old_values, new_values, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, (
                event_data.get('id'),
                event_data.get('incident_id'),
                event_data.get('event_type'),
                event_data.get('description'),
                event_data.get('old_values'),
                event_data.get('new_values'),
                event_data.get('created_at')
            ))

            conn.commit()
            return True
    except Exception as e:
        print(f"Error saving event: {e}")
        return False

def get_event(event_id):
    """Get a single event by ID."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM incident_events WHERE id = ?"
            cursor.execute(query, (event_id,))

            result = cursor.fetchone()
            if result:
                return dict(result)
            return None
    except Exception as e:
        print(f"Error getting event {event_id}: {e}")
        return None

def list_events(incident_id=None, page=1, page_size=10):
    """List events with optional incident filtering and pagination."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Build query based on whether incident_id is provided
            if incident_id:
                base_query = "SELECT * FROM incident_events WHERE incident_id = ?"
                params = (incident_id,)
            else:
                base_query = "SELECT * FROM incident_events"
                params = ()

            # Get total count
            count_query = f"SELECT COUNT(*) as count FROM ({base_query})"
            cursor.execute(count_query, params)
            total_result = cursor.fetchone()
            total = total_result[0] if total_result else 0

            # Get events with pagination
            offset = (page - 1) * page_size
            paginated_query = f"{base_query} ORDER BY created_at DESC LIMIT ? OFFSET ?"
            cursor.execute(paginated_query, params + (page_size, offset))

            events = []
            for row in cursor.fetchall():
                event = dict(row)
                events.append(event)

            return {
                "events": events,
                "page": page,
                "page_size": page_size,
                "total": total,
                "has_more": (page * page_size) < total
            }
    except Exception as e:
        print(f"Error listing events: {e}")
        return {
            "events": [],
            "page": page,
            "page_size": page_size,
            "total": 0,
            "has_more": False
        }

def save_incident_with_events(incident_data, events_data):
    """Save an incident and its associated events in a transaction."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Start transaction
            conn.execute("BEGIN TRANSACTION")

            # Save incident
            incident_query = """
            INSERT INTO incidents (id, title, description, severity, status, service, created_at, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(incident_query, (
                incident_data.get('id'),
                incident_data.get('title'),
                incident_data.get('description'),
                incident_data.get('severity'),
                incident_data.get('status'),
                incident_data.get('service'),
                incident_data.get('created_at'),
                incident_data.get('resolved_at')
            ))

            # Save events
            for event in events_data:
                event_query = """
                INSERT INTO incident_events (id, incident_id, event_type, description, old_values, new_values, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(event_query, (
                    event.get('id'),
                    event.get('incident_id'),
                    event.get('event_type'),
                    event.get('description'),
                    event.get('old_values'),
                    event.get('new_values'),
                    event.get('created_at')
                ))

            # Commit transaction
            conn.commit()
            return True
    except Exception as e:
        # Rollback transaction on error
        conn.execute("ROLLBACK")
        print(f"Error saving incident with events: {e}")
        return False