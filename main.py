from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import sqlite3
import json
import os
import uuid
from contextlib import contextmanager
import re

from demo_db_setup import ensure_demo_database

# Import investigation service
from investigation_service import InvestigationService, InvestigationEvidence, InvestigationRequest, InvestigationResult

# ─── Demo Mode Configuration ───
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
DEMO_DB_PATH = os.getenv("DEMO_DB_PATH", "incidents_demo.db")
PROD_DB_PATH = os.getenv("DB_PATH", "incidents.db")

def get_active_db_path() -> str:
    """Return the database path based on demo mode."""
    return DEMO_DB_PATH if DEMO_MODE else PROD_DB_PATH

# Import Pydantic models from models.py
from models import (
    Incident, IncidentCreateRequest, IncidentUpdateRequest, IncidentResponse, IncidentListResponse,
    IncidentEvent, save_incident, get_incident as get_incident_from_db, list_incidents,
    save_event, get_event, list_events, save_incident_with_events, get_db_connection as models_get_db_connection
)

# ─── Global Database Path Override for Demo Mode ───
# This must be done after importing models, so models._db_path exists
import models

models._db_path = get_active_db_path()
if DEMO_MODE:
    models._test_db_path_override = None
    print(f"✅ Demo mode: Using database {get_active_db_path()}")


def _parse_cors_origins() -> List[str]:
    """Comma-separated origins from CORS_ALLOWED_ORIGINS or DEMO_FRONTEND_ORIGIN."""
    raw = os.getenv("CORS_ALLOWED_ORIGINS") or os.getenv("DEMO_FRONTEND_ORIGIN", "")
    if raw.strip():
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    return []


def _local_demo_cors_origins() -> List[str]:
    return [
        "http://localhost:3000",
        "http://localhost:4173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4173",
    ]


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    ensure_demo_database(demo_mode=DEMO_MODE, active_db_path=get_active_db_path())
    yield

# Additional Pydantic models for endpoints
class EventResponse(BaseModel):
    id: str
    incident_id: str
    event_type: str
    description: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    created_at: str

class TimelineResponse(BaseModel):
    incident_id: str
    events: List[EventResponse]

# ─── Read-Only Middleware for Demo Mode ───
class ReadOnlyMiddleware:
    """
    Middleware that blocks mutating HTTP methods in demo mode.
    Allows: GET, HEAD, OPTIONS
    Blocks: POST, PUT, PATCH, DELETE
    Allows POST to /investigate endpoints (returns mock data in demo mode)
    Disables API docs (/docs, /redoc, /openapi.json) in demo mode.
    """
    def __init__(self, app, enabled: bool = False):
        self.app = app
        self.enabled = enabled
        self.read_only_methods = {"GET", "HEAD", "OPTIONS"}
        # Paths that are always allowed (health, root)
        self.always_allowed_paths = {"/", "/health"}
        # Paths blocked in demo mode even for GET
        self.blocked_in_demo_paths = {"/docs", "/redoc", "/openapi.json"}
        # Paths that allow POST in demo mode (investigation with mock response)
        self.demo_allowed_post_paths = {"/investigate"}

    async def __call__(self, scope, receive, send):
        if self.enabled and scope["type"] == "http":
            method = scope["method"]
            path = scope["path"]

            # Block API documentation in demo mode
            if path in self.blocked_in_demo_paths:
                await send({
                    "type": "http.response.start",
                    "status": 403,
                    "headers": [(b"content-type", b"application/json")]
                })
                await send({
                    "type": "http.response.body",
                    "body": b'{"detail": "Demo mode: API documentation disabled"}'
                })
                return

            # Allow health and root always
            if path in self.always_allowed_paths:
                pass  # Continue to app
            # Allow POST to investigation endpoints in demo mode (returns mock)
            elif method == "POST" and any(path.endswith(p) for p in self.demo_allowed_post_paths):
                pass  # Continue to app - endpoint will return mock data
            # Block mutating methods
            elif method not in self.read_only_methods:
                await send({
                    "type": "http.response.start",
                    "status": 403,
                    "headers": [(b"content-type", b"application/json")]
                })
                await send({
                    "type": "http.response.body",
                    "body": b'{"detail": "Demo mode: read-only access, write operations disabled"}'
                })
                return

        await self.app(scope, receive, send)

@contextmanager
def get_db_connection():
    """Get database connection using the active database path."""
    # Database path is already set globally in models module
    with models_get_db_connection() as conn:
        yield conn

def init_db():
    with get_db_connection() as conn:
        conn.execute("""
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
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incident_events (
                id TEXT PRIMARY KEY,
                incident_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                old_values TEXT,
                new_values TEXT,
                created_at TEXT NOT NULL
            )
        """)

# ─── FastAPI App Initialization ───
# Disable docs in demo mode
app = FastAPI(
    docs_url=None if DEMO_MODE else "/docs",
    redoc_url=None if DEMO_MODE else "/redoc",
    openapi_url=None if DEMO_MODE else "/openapi.json",
    lifespan=app_lifespan,
)

# ─── Middleware Stack (Order Matters!) ───
# 1. Read-only middleware FIRST (blocks before CORS)
app.add_middleware(ReadOnlyMiddleware, enabled=DEMO_MODE)

# 2. CORS middleware
if DEMO_MODE:
    demo_origins = _parse_cors_origins() or _local_demo_cors_origins()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=demo_origins,
        allow_credentials=True,
        # GET/HEAD/OPTIONS for read-only API; POST for /investigate mock in demo mode
        allow_methods=["GET", "HEAD", "OPTIONS", "POST"],
        allow_headers=["*"],
    )
else:
    # Production/local development: original CORS settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ─── Root & Health Endpoints ───
@app.get("/")
async def root():
    return {
        "project_name": "DevOps Incident Commander",
        "status": "running",
        "version": "1.0.0",
        "welcome_message": "Agentic AI-based incident investigation and response platform",
        "demo_mode": DEMO_MODE
    }

@app.get("/health")
async def health():
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1")
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "devops-incident-commander-api",
            "demo_mode": DEMO_MODE,
            "database": get_active_db_path()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": "devops-incident-commander-api",
                "demo_mode": DEMO_MODE
            }
        )

# ─── Incident CRUD Endpoints ───
@app.post("/incidents")
async def create_incident(incident: IncidentCreateRequest):
    # This endpoint is blocked by ReadOnlyMiddleware in demo mode
    incident_data = incident.model_dump()
    incident_data['id'] = str(uuid.uuid4())
    incident_data['created_at'] = datetime.now(timezone.utc).isoformat()
    incident_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    incident_data['resolved_at'] = None

    with get_db_connection() as conn:
        try:
            conn.execute(
                """
                INSERT INTO incidents (id, title, severity, status, service, description, created_at, updated_at, resolved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    incident_data['id'], incident_data['title'], incident_data['severity'],
                    incident_data['status'], incident_data['service'], incident_data['description'],
                    incident_data['created_at'], incident_data['updated_at'], incident_data['resolved_at']
                )
            )
            conn.commit()

            event_id = str(uuid.uuid4())
            event_data = {
                'id': event_id,
                'incident_id': incident_data['id'],
                'event_type': 'incident_created',
                'description': 'Incident created',
                'old_values': None,
                'new_values': {
                    'title': incident_data['title'],
                    'severity': incident_data['severity'],
                    'status': incident_data['status'],
                    'service': incident_data['service'],
                    'description': incident_data['description']
                },
                'created_at': datetime.now(timezone.utc).isoformat()
            }

            conn.execute(
                """
                INSERT INTO incident_events (id, incident_id, event_type, description, old_values, new_values, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id, event_data['incident_id'], event_data['event_type'],
                    event_data['description'], json.dumps(event_data['old_values']) if event_data['old_values'] else None,
                    json.dumps(event_data['new_values']) if event_data['new_values'] else None,
                    event_data['created_at']
                )
            )
            conn.commit()

            return JSONResponse(content=IncidentResponse(**incident_data).model_dump(), status_code=201)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create incident: {str(e)}")

@app.get("/incidents")
async def list_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=10000),
    service: Optional[str] = Query(None, description="Filter by service name"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    created_after: Optional[str] = Query(None, description="Filter by creation date (ISO format)"),
    sort_by: Optional[str] = Query(None, description="Sort by field"),
    order: Optional[str] = Query("desc", description="Sort order (asc or desc)")
):
    # Validate filter parameters
    valid_severities = ["low", "medium", "high", "critical"]
    valid_statuses = ["open", "investigating", "resolved", "closed"]

    if severity and severity not in valid_severities:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "type": "value_error",
                    "loc": ["query", "severity"],
                    "msg": f"Invalid severity. Must be one of: {valid_severities}",
                    "input": severity
                }
            ]
        )

    if status and status not in valid_statuses:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "type": "value_error",
                    "loc": ["query", "status"],
                    "msg": f"Invalid status. Must be one of: {valid_statuses}",
                    "input": status
                }
            ]
        )

    if created_after:
        import re
        iso_date_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?$'

        if not re.match(iso_date_pattern, created_after):
            raise HTTPException(
                status_code=422,
                detail=[
                    {
                        "type": "value_error",
                        "loc": ["query", "created_after"],
                        "msg": "Invalid date format. Must be ISO 8601 format (e.g., 2026-10-15T12:00:00Z)",
                        "input": created_after
                    }
                ]
            )

    valid_sort_fields = ["created_at", "title", "severity", "status", "service"]
    valid_order_values = ["asc", "desc"]

    if sort_by and sort_by not in valid_sort_fields:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "type": "value_error",
                    "loc": ["query", "sort_by"],
                    "msg": f"Invalid sort field. Must be one of: {valid_sort_fields}",
                    "input": sort_by
                }
            ]
        )

    if order and order not in valid_order_values:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "type": "value_error",
                    "loc": ["query", "order"],
                    "msg": f"Invalid order value. Must be one of: {valid_order_values}",
                    "input": order
                }
            ]
        )

    with get_db_connection() as conn:
        offset = (page - 1) * page_size

        where_clauses = []
        params = []

        if service:
            where_clauses.append("service = ?")
            params.append(service)

        if severity:
            where_clauses.append("severity = ?")
            params.append(severity)

        if status:
            where_clauses.append("status = ?")
            params.append(status)

        if search and search.strip():
            where_clauses.append("LOWER(title) LIKE ? OR LOWER(description) LIKE ?")
            search_term = f"%{search.lower()}%"
            params.append(search_term)
            params.append(search_term)

        if created_after:
            where_clauses.append("created_at >= ?")
            params.append(created_after)

        where_clause = ""
        if where_clauses:
            where_clause = "WHERE " + " AND ".join(where_clauses)

        order_by_clause = "created_at DESC"
        if sort_by:
            if sort_by in ["title", "service"]:
                order_by_clause = f"{sort_by} {order.upper() if order in valid_order_values else 'DESC'}"
            elif sort_by in ["severity", "status"]:
                order_by_clause = f"{sort_by} {order.upper() if order in valid_order_values else 'DESC'}"
            else:
                order_by_clause = f"created_at {order.upper() if order in valid_order_values else 'DESC'}"

        total_query = f"SELECT COUNT(*) as count FROM incidents {where_clause}"
        total_result = conn.execute(total_query, params)
        total = total_result.fetchone()['count']

        incidents_query = f"""
        SELECT * FROM incidents
        {where_clause}
        ORDER BY {order_by_clause}
        LIMIT ? OFFSET ?
        """
        query_params = params + [page_size, offset]

        incidents_result = conn.execute(incidents_query, query_params)

        incidents = []
        for row in incidents_result.fetchall():
            incident = dict(row)
            incidents.append(IncidentResponse(**incident))

        has_more = (page * page_size) < total

        return {
            "incidents": incidents,
            "page": page,
            "page_size": page_size,
            "total": total,
            "has_more": has_more
        }

@app.get("/incidents/{incident_id}")
async def get_incident(incident_id: str = Path(...)):
    with get_db_connection() as conn:
        incident_result = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
        incident = incident_result.fetchone()

        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")

        return IncidentResponse(**dict(incident))

@app.patch("/incidents/{incident_id}")
async def update_incident(
    incident_id: str = Path(...),
    incident_update: IncidentUpdateRequest = None
):
    # Blocked by ReadOnlyMiddleware in demo mode
    with get_db_connection() as conn:
        incident_result = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
        incident = incident_result.fetchone()

        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")

        old_incident = dict(incident)

        if incident_update is None:
            raise HTTPException(status_code=422, detail="Invalid request body")

        update_data = incident_update.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=422, detail=[{"type": "validation_error", "loc": ["body"], "msg": "No fields to update", "input": {}}])

        for field, value in update_data.items():
            if value is None and field not in ['id', 'created_at', 'resolved_at']:
                raise HTTPException(
                    status_code=422,
                    detail=[{
                        'type': 'null_value',
                        'loc': ['body', field],
                        'msg': f'Field {field} cannot be null',
                        'input': None
                    }]
                )

        for field, value in update_data.items():
            old_incident[field] = incident[field]

        fields = []
        params = []
        for field, value in update_data.items():
            if field not in ['id', 'created_at']:
                fields.append(f"{field} = ?")
                params.append(value)

        if "status" in update_data and update_data["status"] == "resolved":
            fields.append("resolved_at = ?")
            params.append(datetime.now(timezone.utc).isoformat())

        params.append(incident_id)

        if fields:
            query = f"UPDATE incidents SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, params)

            incident_result = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
            updated_incident = incident_result.fetchone()
            updated_incident_dict = dict(updated_incident)

            if updated_incident_dict.get('status') != old_incident.get('status'):
                event_id = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO incident_events (id, incident_id, event_type, description, old_values, new_values, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event_id, incident_id, 'incident_status_changed',
                        'Incident status changed', json.dumps({'status': old_incident.get('status')}),
                        json.dumps({'status': updated_incident_dict.get('status')}),
                        datetime.now(timezone.utc).isoformat()
                    )
                )

            if old_incident.get('status') == 'resolved' and updated_incident_dict.get('status') != 'resolved':
                event_id = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO incident_events (id, incident_id, event_type, description, old_values, new_values, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event_id, incident_id, 'incident_reopened',
                        'Incident reopened', None,
                        json.dumps({'status': updated_incident_dict.get('status')}),
                        datetime.now(timezone.utc).isoformat()
                    )
                )

            if old_incident.get('status') != 'resolved' and updated_incident_dict.get('status') == 'resolved':
                event_id = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO incident_events (id, incident_id, event_type, description, old_values, new_values, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event_id, incident_id, 'incident_resolved',
                        'Incident resolved', json.dumps({'status': old_incident.get('status')}),
                        json.dumps({'status': updated_incident_dict.get('status'), 'resolved_at': updated_incident_dict.get('resolved_at')}),
                        datetime.now(timezone.utc).isoformat()
                    )
                )

            if len(fields) > 1 or (len(fields) == 1 and 'status' not in fields):
                event_id = str(uuid.uuid4())
                changed_fields = {k: v for k, v in update_data.items() if k in fields and k != 'status'}
                old_fields_data = {k: old_incident.get(k) for k in changed_fields.keys()}
                conn.execute(
                    """
                    INSERT INTO incident_events (id, incident_id, event_type, description, old_values, new_values, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event_id, incident_id, 'incident_updated',
                        'Incident details updated', json.dumps(old_fields_data),
                        json.dumps(changed_fields), datetime.now(timezone.utc).isoformat()
                    )
                )
            conn.commit()

        return IncidentResponse(**dict(updated_incident))

@app.delete("/incidents/{incident_id}")
async def delete_incident(incident_id: str = Path(...)):
    # Blocked by ReadOnlyMiddleware in demo mode
    with get_db_connection() as conn:
        incident_result = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
        incident = incident_result.fetchone()

        if incident is None:
            raise HTTPException(status_code=404, detail="Incident not found")

        event_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO incident_events (id, incident_id, event_type, description, old_values, new_values, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id, incident_id, 'incident_deleted',
                'Incident deleted', json.dumps(dict(incident)), None,
                datetime.now(timezone.utc).isoformat()
            )
        )
        conn.commit()

        conn.execute("DELETE FROM incidents WHERE id = ?", (incident_id,))
        conn.commit()

        return {"message": "Incident deleted successfully", "incident_id": incident_id}

# ─── Analytics Endpoints ───
@app.get("/analytics/overview")
async def get_analytics_overview():
    from models import get_analytics_overview as get_analytics_overview_func
    return get_analytics_overview_func()

@app.get("/analytics/severity")
async def get_severity_breakdown():
    from models import get_severity_breakdown as get_severity_breakdown_func
    return get_severity_breakdown_func()

@app.get("/analytics/status")
async def get_status_breakdown():
    from models import get_status_breakdown as get_status_breakdown_func
    return get_status_breakdown_func()

# ─── Timeline Endpoint ───
@app.get("/incidents/{incident_id}/timeline", response_model=TimelineResponse)
async def get_incident_timeline(incident_id: str = Path(...)):
    with get_db_connection() as conn:
        incident_exists = conn.execute("SELECT id FROM incidents WHERE id = ?", (incident_id,)).fetchone()

        events_result = conn.execute(
            """
            SELECT * FROM incident_events
            WHERE incident_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (incident_id,)
        )

        events = []
        for row in events_result.fetchall():
            event = dict(row)
            if event['old_values']:
                event['old_values'] = json.loads(event['old_values'])
            if event['new_values']:
                event['new_values'] = json.loads(event['new_values'])

            events.append(EventResponse(**event))

        if not incident_exists and not events:
            raise HTTPException(status_code=404, detail="Incident not found")

        return {
            "incident_id": incident_id,
            "events": events
        }

# ─── Investigation Endpoint ───
@app.post("/incidents/{incident_id}/investigate")
async def investigate_incident(
    incident_id: str = Path(...),
    evidence_request: Optional[Dict[str, Any]] = None,
    include_timeline: bool = Query(True, description="Include timeline analysis in investigation"),
    include_events: bool = Query(True, description="Include event analysis in investigation"),
    investigation_depth: str = Query("detailed", description="Depth of investigation (basic/detailed/full)"),
    template_id: Optional[str] = Query(None, description="Optional template ID for investigation guidance"),
    investigation_timeout: Optional[float] = Query(None, gt=0, description="Optional investigation timeout in seconds (positive number)")
):
    """
    Investigate an incident using AI-powered analysis.

    In demo mode: returns a mock investigation result without calling external AI providers.
    """
    # Validate incident exists
    existing_incident = get_incident_from_db(incident_id)
    if not existing_incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    if DEMO_MODE:
        # Return mock investigation result in demo mode - no external AI calls
        from datetime import datetime, timezone
        mock_investigation_id = f"demo-inv-{uuid.uuid4().hex[:8]}"

        return JSONResponse(content={
            "investigation_id": mock_investigation_id,
            "incident_id": incident_id,
            "investigated_at": datetime.now(timezone.utc).isoformat(),
            "incident_data": existing_incident,
            "evidence": {
                "log_text": evidence_request.get("log_text", "") if evidence_request else "",
                "system_events": evidence_request.get("system_events", []) if evidence_request else [],
                "error_messages": evidence_request.get("error_messages", []) if evidence_request else [],
                "timestamps": evidence_request.get("timestamps", []) if evidence_request else [],
                "source": evidence_request.get("source", "demo") if evidence_request else "demo",
                "collected_at": datetime.now(timezone.utc).isoformat(),
            },
            "ai_analysis": {
                "success": True,
                "analysis_type": "root_cause",
                "confidence_score": 0.85,
                "hypotheses": [
                    {
                        "hypothesis": "Demo hypothesis: Configuration drift detected in service mesh",
                        "confidence": 0.75,
                        "category": "configuration"
                    },
                    {
                        "hypothesis": "Demo hypothesis: Resource exhaustion due to traffic spike",
                        "confidence": 0.65,
                        "category": "resource"
                    }
                ],
                "recommendations": [
                    "Review recent configuration changes in demo mode",
                    "Check resource utilization metrics",
                    "Verify circuit breaker settings"
                ],
                "reasoning": "This is a mock investigation result for demo purposes. No external AI provider was called.",
                "metadata": {"demo_mode": True, "provider": "mock"},
                "errors": [],
                "warnings": ["Demo mode: investigation used mock provider, no external AI called"]
            },
            "investigation_results": {
                "root_cause_hypotheses": [
                    "Configuration drift in service mesh",
                    "Resource exhaustion from traffic spike"
                ],
                "supporting_evidence": [
                    "Recent config deployment correlates with error rate increase",
                    "CPU/memory metrics show sustained high utilization"
                ],
                "confidence_scores": {"configuration": 0.75, "resource": 0.65},
                "diagnostic_steps": [
                    "Verify config version in control plane",
                    "Check resource quotas and limits",
                    "Review circuit breaker thresholds"
                ],
                "urgency_level": "medium",
                "investigation_type": "root_cause"
            },
            "investigation_metadata": {
                "demo_mode": True,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "demo_mode": True
        }, status_code=200)

    # Production mode: actual investigation
    try:
        investigation_service = InvestigationService()

        evidence = None
        if evidence_request:
            evidence = InvestigationEvidence(
                log_text=evidence_request.get("log_text", ""),
                system_events=evidence_request.get("system_events", []),
                error_messages=evidence_request.get("error_messages", []),
                timestamps=evidence_request.get("timestamps", []),
                source=evidence_request.get("source", "manual")
            )

        constraints = {}
        if investigation_timeout is not None:
            constraints['investigation_timeout'] = investigation_timeout

        investigation_request = InvestigationRequest(
            incident_id=incident_id,
            evidence=evidence,
            analysis_type="root_cause",
            investigation_depth=investigation_depth,
            constraints=constraints,
            include_timeline=include_timeline,
            include_events=include_events,
            template_id=template_id,
            investigation_timeout=investigation_timeout
        )

        investigation_result = investigation_service.investigate_incident(investigation_request)

        response = {
            "investigation_id": investigation_result.investigation_id,
            "incident_id": investigation_result.incident_id,
            "investigated_at": investigation_result.investigated_at,
            "incident_data": {
                "id": investigation_result.incident_data.incident_id,
                "title": investigation_result.incident_data.title,
                "description": investigation_result.incident_data.description,
                "severity": investigation_result.incident_data.severity,
                "status": investigation_result.incident_data.status,
                "service": investigation_result.incident_data.service,
                "created_at": investigation_result.incident_data.created_at,
            },
            "evidence": {
                "log_text": investigation_result.evidence.log_text,
                "system_events": investigation_result.evidence.system_events,
                "error_messages": investigation_result.evidence.error_messages,
                "timestamps": investigation_result.evidence.timestamps,
                "source": investigation_result.evidence.source,
                "collected_at": investigation_result.evidence.collected_at,
            },
            "ai_analysis": {
                "success": investigation_result.ai_analysis.success,
                "analysis_type": investigation_result.ai_analysis.analysis_type,
                "confidence_score": investigation_result.ai_analysis.confidence_score,
                "hypotheses": investigation_result.ai_analysis.hypotheses,
                "recommendations": investigation_result.ai_analysis.recommendations,
                "reasoning": investigation_result.ai_analysis.reasoning,
                "metadata": investigation_result.ai_analysis.metadata,
                "errors": investigation_result.ai_analysis.errors,
                "warnings": investigation_result.ai_analysis.warnings,
            },
            "investigation_results": {
                "root_cause_hypotheses": investigation_result.root_cause_hypotheses,
                "supporting_evidence": investigation_result.supporting_evidence,
                "confidence_scores": investigation_result.confidence_scores,
                "diagnostic_steps": investigation_result.diagnostic_steps,
                "urgency_level": investigation_result.urgency_level,
                "investigation_type": investigation_result.investigation_type,
            },
            "investigation_metadata": investigation_result.investigation_metadata,
        }

        template_applied_info = investigation_result.ai_analysis.metadata.get('template_applied_info')
        if template_applied_info:
            response["template_applied"] = True
            response["template_id"] = template_applied_info.get('template_id')
            response["template_name"] = template_applied_info.get('name')
            response["template_applicability"] = template_applied_info.get('applicability')

        return JSONResponse(content=response, status_code=200)

    except ValueError as e:
        error_message = str(e)
        if "Template" in error_message and "not found" in error_message:
            raise HTTPException(status_code=400, detail=error_message)
        else:
            raise HTTPException(status_code=404, detail=error_message)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error during investigation: {str(e)}")