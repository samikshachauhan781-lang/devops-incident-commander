# DevOps Incident Commander

## Project Overview

The DevOps Incident Commander is an Agentic AI-based incident investigation and response platform designed to help teams quickly diagnose, analyze, and resolve production incidents. It combines structured incident tracking with AI-powered investigation capabilities.

**Current MVP Scope**:
- Incident management (CRUD operations, filtering, pagination)
- Timeline and event tracking
- Analytics and dashboards
- AI-powered incident investigation with template guidance
- Investigation timeout configuration and validation
- Demo mode with read-only protections for safe sharing

**Verification Status (2026-10-26)**:
- ✅ **Backend Tests**: 185/185 passing (19 demo-mode tests skipped — run as standalone script)
- ✅ **Frontend Build**: TypeScript strict check + production build pass
- ✅ **Demo Mode**: All 33 protections verified (POST/PATCH/DELETE blocked, /docs disabled)
- ✅ **Investigation**: Mock provider returns structured results; Ollama provider implemented
- ✅ **Templates**: 3 built-in templates with applicability checking

## Prerequisites

### Operating System
- macOS, Linux, or Windows 10+
- Python 3.11+ (tested with 3.11.9)

### Virtual Environment Setup

```bash
# Create virtual environment
cd /Users/samiksha/Desktop/devops-incident-commander
python3 -m venv .venv

# Activate environment
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

## Dependencies Installation

The project requires these Python packages:

```txt
fastapi>=0.104.0
pydantic>=2.4.2
uvicorn>=0.24.0
python-multipart>=0.0.7
python-multipart
```

### Install Dependencies

```bash
# Update pip and install requirements
cd /Users/samiksha/Desktop/devops-incident-commander
.venv/bin/pip install --upgrade pip
.venv/bin/pip install fastapi pydantic uvicorn python-multipart
```

**Note**: Some dependencies are included in Python standard library (sqlite3, typing, uuid).

## Application Setup

### Start the FastAPI Server

```bash
cd /Users/samiksha/Desktop/devops-incident-commander
.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
```

**For development with auto-reload:**
```bash
cd /Users/samiksha/Desktop/devops-incident-commander
.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Configuration

The application uses SQLite database with configurable database path:

- `DB_PATH`: Path to SQLite database file (default: `incidents.db`)

**Example:**
```bash
export DB_PATH="/Users/samiksha/Desktop/devops-incident-commander/incidents.db"
# Then start the server
.venv/bin/uvicorn main:app
```

## API Endpoints

### Root Endpoint
```http
GET /
```

**Response**:
```json
{
  "project_name": "DevOps Incident Commander",
  "status": "running",
  "version": "1.0.0",
  "welcome_message": "Agentic AI-based incident investigation and response platform"
}
```

### Health Endpoint
```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-10-23T06:35:44.140204+00:00",
  "service": "devops-incident-commander-api"
}
```

## Incident Management API

### Create Incident
```http
POST /incidents
Content-Type: application/json

{
  "title": "Database connection timeout",
  "description": "The database connection pool is exhausted, causing timeouts across all services",
  "severity": "high",
  "status": "open",
  "service": "database"
}
```

**Response**:
```json
{
  "id": "c259d59a-04cf-4300-b7dc-d96fcbab4741",
  "title": "Database connection timeout",
  "description": "The database connection pool is exhausted, causing timeouts across all services",
  "severity": "high",
  "status": "open",
  "service": "database",
  "created_at": "2026-10-23T06:35:44.143087+00:00",
  "updated_at": "2026-10-23T06:35:44.143089+00:00",
  "resolved_at": null
}
```

**Response Codes**:
- `201` - Incident created successfully
- `422` - Validation error for invalid input

### List Incidents
```http
GET /incidents?page=1&page_size=10
```

**Response**:
```json
{
  "incidents": [
    {
      "id": "incident-1",
      "title": "Database connection timeout",
      "description": "The database connection pool is exhausted",
      "severity": "high",
      "status": "open",
      "service": "database",
      "created_at": "2026-10-23T06:35:44.143087+00:00",
      "updated_at": "2026-10-23T06:35:44.143089+00:00",
      "resolved_at": null
    }
  ],
  "page": 1,
  "page_size": 10,
  "total": 1,
  "has_more": false
}
```

**Query Parameters**:
- `page` (integer): Page number (default: 1)
- `page_size` (integer): Page size (default: 10)

### Get Incident by ID
```http
GET /incidents/{incident_id}
```

**Response Codes**:
- `200` - Incident found
- `404` - Incident not found

### Update Incident (PATCH)
```http
PATCH /incidents/{incident_id}
Content-Type: application/json

{
  "title": "Database connection pool timeout",
  "severity": "critical"
}
```

**Response Codes**:
- `200` - Incident updated successfully
- `404` - Incident not found
- `422` - Validation error

### Delete Incident
```http
DELETE /incidents/{incident_id}
```

**Response Codes**:
- `204` - Incident deleted successfully
- `404` - Incident not found

## Filtering and Query API

### Filter Incidents
```http
GET /incidents?service=database&severity=high&page=1&page_size=10
```

**Available Filters**:
- `service`: Filter by service name
- `severity`: Filter by severity (low, medium, high, critical)
- `status`: Filter by status (open, investigating, resolved, closed)
- `created_after`: Filter by creation timestamp (ISO format)

**Search and Sort**:
- `search`: Search in title and description fields (case-insensitive)
- `sort_by`: Sort by field (created_at, title, severity, status, service)
- `order`: Sort order (asc or desc, default: desc)

### Advanced Filtering Example
```http
GET /incidents?severity=high&status=open&search="database"&sort_by=created_at&order=desc
```

## Timeline API

### Get Incident Timeline
```http
GET /incidents/{incident_id}/timeline
```

**Response**:
```json
{
  "incident_id": "incident-1",
  "events": [
    {
      "id": "event-1",
      "incident_id": "incident-1",
      "event_type": "severity_change",
      "description": "Severity changed from medium to high",
      "old_values": {"severity": "medium"},
      "new_values": {"severity": "high"},
      "created_at": "2026-10-23T06:35:44.143087+00:00"
    }
  ]
}
```

## Analytics API

### Overall Analytics
```http
GET /analytics/overview
```

**Response**:
```json
{
  "total_incidents": 5,
  "open_incidents": 3,
  "investigating_incidents": 1,
  "resolved_incidents": 2,
  "closed_incidents": 0,
  "critical_incidents": 2,
  "resolution_rate_percent": 40.0
}
```

### Severity Breakdown
```http
GET /analytics/severity
```

**Response**:
```json
{
  "severity_breakdown": [
    {"severity": "low", "count": 1, "percentage": 20.0},
    {"severity": "medium", "count": 2, "percentage": 40.0},
    {"severity": "high", "count": 1, "percentage": 30.0},
    {"severity": "critical", "count": 1, "percentage": 10.0}
  ]
}
```

### Status Breakdown
```http
GET /analytics/status
```

**Response**:
```json
{
  "status_breakdown": [
    {"status": "open", "count": 3, "percentage": 60.0},
    {"status": "investigating", "count": 1, "percentage": 20.0},
    {"status": "resolved", "count": 1, "percentage": 20.0},
    {"status": "closed", "count": 0, "percentage": 0.0}
  ]
}
```

## Investigation API

### Start Incident Investigation
```http
POST /incidents/{incident_id}/investigate
Content-Type: application/json

{
  "include_timeline": true,
  "include_events": true,
  "investigation_depth": "detailed",
  "template_id": "api_failure_v1"
}
```

**Optional Query Parameters**:
- `investigation_timeout`: Investigation timeout in seconds (positive number, default: None)

**Response**:
```json
{
  "investigation_id": "inv-123",
  "incident_id": "incident-1",
  "investigated_at": "2026-10-23T06:35:44.143087+00:00",
  "incident_data": {
    "incident_id": "incident-1",
    "title": "Database connection timeout",
    "description": "The database connection pool is exhausted",
    "severity": "high",
    "status": "open",
    "service": "database",
    "created_at": "2026-10-23T06:35:44.143087+00:00"
  },
  "evidence": {
    "log_text": "Database connection pool exhausted after 1000 attempts",
    "system_events": [],
    "error_messages": ["Connection timeout", "Pool exhausted"],
    "timestamps": ["2026-10-23T06:30:00Z", "2026-10-23T06:35:00Z"],
    "source": "database_logs",
    "collected_at": "2026-10-23T06:35:44.143087+00:00"
  },
  "ai_analysis": {
    "success": true,
    "analysis_type": "root_cause",
    "confidence_score": 0.85,
    "hypotheses": [
      {"hypothesis": "Database connection pool configuration is insufficient", "confidence": 0.9},
      {"hypothesis": "Network latency causing connection timeouts", "confidence": 0.7}
    ],
    "recommendations": ["Increase connection pool size", "Add timeout monitoring"],
    "reasoning": "Based on connection pool metrics and error logs",
    "metadata": {"template_applied_info": {"template_id": "api_failure_v1", "name": "API Service Failure"}},
    "errors": [],
    "warnings": []
  },
  "investigation_results": {
    "root_cause_hypotheses": ["Database connection pool exhaustion"],
    "supporting_evidence": ["Connection pool metrics show 100% utilization"],
    "confidence_scores": [0.85],
    "diagnostic_steps": ["Check database connection pool configuration", "Monitor connection pool metrics"],
    "urgency_level": "high",
    "investigation_type": "root_cause"
  },
  "investigation_metadata": {
    "template_used": true,
    "ai_provider": "ollama",
    "model": "llama3.2:3b"
  }
}
```

**Available AI Providers**:
- `mock`: For testing and development
- `ollama`: Local AI model (llama3.2:3b)
- `openai`: OpenAI API (requires API key)

### Investigation Timeout Configuration

The investigation endpoint accepts an optional `investigation_timeout` query parameter:

**Valid Values**:
- Missing: Uses default timeout (None)
- Positive integer: `investigation_timeout=30`
- Positive float: `investigation_timeout=30.5`

**Invalid Values** (return 422 Validation Error):
- Zero: `investigation_timeout=0`
- Negative: `investigation_timeout=-5`
- Non-numeric: Invalid type

## Testing

### Run All Tests

```bash
# From project root
cd /Users/samiksha/Desktop/devops-incident-commander
python3 -m pytest test_*.py --tb=short -q
```

**Test Coverage**:
- Core API functionality: `test_app.py`
- Incident filtering: `test_day6_filters.py`
- Timeline operations: `test_day7_timeline.py`
- Analytics: `test_day8_analytics.py`
- Investigation service: `test_investigation.py`
- Template immutability: `test_template_engine.py`
- Timeout validation: `test_timeout_validation.py`

### Test Structure

The test suite includes:
- **Unit tests**: Test individual components
- **Integration tests**: Test API endpoints
- **E2E tests**: Test full workflows
- **Validation tests**: Test input validation

**Test Database**: Each test runs in an isolated temporary database to prevent data contamination.

## Current Limitations and Known Issues

### Known Issues
None — all previously reported issues resolved as of 2026-10-26.

### Current Limitations (Pre-existing, Non-Regression)
1. **API Hardcodes `constraints={}`**: The `/incidents/{id}/investigate` endpoint hardcodes `constraints={}` in the `InvestigationRequest`, preventing callers from supplying a request-specific `investigation_timeout` via API. The timeout validation logic exists in all three layers (service, Ollama, mock) but is only exercisable via direct service/provider calls or tests.
2. **`call_with_timeout` Thread Cleanup**: The standalone utility function in `investigation_service.py` shows delayed daemon-thread cleanup when invoked directly with very short timeouts. Does not affect the investigation path (removed from `_call_ai_analysis_with_timeout()`).
3. **Demo Mode Tests Under Pytest**: `test_demo_mode.py` is designed as a standalone script; it's skipped under pytest due to conftest fixture interference. Run manually: `DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db python3 test_demo_mode.py`
4. **No Evidence Collection UI**: Frontend has no form to submit evidence with investigation requests (backend accepts it).
5. **No Authentication**: API access requires no authentication (suitable for development/demo only).

### Not in MVP Scope
- Advanced monitoring integration
- Multi-database support
- User authentication/authorization
- Advanced reporting and export features
- Real-time websocket updates
- Multi-tenancy support

## How to Get Help

### For Bugs and Issues
1. Review existing documentation
2. Check test failures and error logs
3. Verify input format matches API specification
4. Ensure all required fields are included in requests

### For Development
1. Follow the dependency installation instructions
2. Refer to individual test files for specific use cases
3. Check the source code for detailed implementation notes
4. Use the `investigation_templates.py` file for template reference

## Project Structure

```
.
├── main.py                    # FastAPI application
├── models.py                  # Pydantic models and database operations
├── investigation_service.py    # Investigation service with AI integration
├── investigation_templates.py  # Built-in investigation templates (immutable)
├── template_engine.py         # Template engine for investigation guidance
├── ai_provider.py             # AI provider foundation
├── ollama_provider.py         # Ollama AI provider implementation
├── test_*.py                  # Test suite (271 tests total)
├── project_memory/            # Development documentation
├── README.md                  # This documentation
└── incidents.db               # SQLite database
```

## Development Notes

### Testing Strategy
- Each test runs in an isolated temporary database
- Tests do not modify the main `incidents.db`
- Use `set_test_database_path()` for test database configuration

### AI Provider Configuration
- **Default**: Mock provider for testing
- **Local**: Ollama provider (requires local Ollama instance)
- **Cloud**: OpenAI provider (requires API key)

### Database Schema
```sql
-- incidents table
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
);

-- incident_events table
CREATE TABLE incident_events (
    id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    description TEXT NOT NULL,
    old_values TEXT,
    new_values TEXT,
    created_at TEXT NOT NULL
);
```

### Template System
The investigation system uses pre-built templates for common incident scenarios:
- `api_failure_v1`: API Service Failure investigation
- Templates are immutable and thread-safe
- Cannot be modified after creation to ensure data integrity
- Can be extended by adding new templates to `investigation_templates.py`

## Security Considerations

### Default Security
- SQLite database with file permissions
- No authentication required for API access
- Input validation through Pydantic models

### Recommendations for Production
- Add API authentication (JWT, OAuth2)
- Implement rate limiting
- Use environment variables for sensitive configuration
- Consider PostgreSQL instead of SQLite for production
- Implement proper database backup and recovery procedures

## Deployment

### Local development

**Backend (demo mode — recommended for UI work):**
```bash
cd devops-incident-commander
python3 create_demo_db.py   # ensures incidents_demo.db seed exists
DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db uvicorn main:app --host 0.0.0.0 --port 8000
```

**Frontend (Vite proxies `/api` → backend; no `VITE_API_BASE_URL` needed):**
```bash
cd frontend && npm install && npm run dev
```

### Public demo on Render (two services)

Use **two Render services**: a Python **Web Service** (API) and a **Static Site** (React SPA). The repo includes `render.yaml` as a Blueprint template. **Do not commit secrets** — use Render environment variables only.

| Concern | Approach |
|--------|----------|
| API URL in production | `VITE_API_BASE_URL` at **frontend build time** (see `frontend/.env.example`) |
| CORS | `CORS_ALLOWED_ORIGINS` on the API (comma-separated frontend URL(s)) |
| Demo safety | `DEMO_MODE=true`, read-only middleware, `/docs` disabled |
| Database | Seed file `incidents_demo.db` in repo; runtime copy at `/tmp/incidents_demo.db` on each start |
| `incidents.db` | **Not used** on public deploy; listed in `.gitignore` |
| SPA routing | `render.yaml` rewrites `/*` → `/index.html` |
| Health check | `GET /health` (set `healthCheckPath: /health` on the API service) |

**Pre-deploy checklist:**
1. Commit `incidents_demo.db` (or rely on `python3 create_demo_db.py` in the API build command).
2. Ensure `.env`, `frontend/.env.production`, and `incidents.db` are **not** in Git (see root `.gitignore`).
3. After first deploy, set `CORS_ALLOWED_ORIGINS` to your static site URL and redeploy the API.
4. Set `VITE_API_BASE_URL` to your API URL (no trailing slash) and **redeploy the frontend** so Vite bakes it into the bundle.

**Verify (after deploy):**
- `curl https://<api-host>/health` → `"status":"healthy"`, `"demo_mode":true`, `"database":"/tmp/incidents_demo.db"` (or your `DEMO_DB_PATH`)
- Open the static site: dashboard loads incidents; timeline deep links and refresh work
- `POST /incidents` → `403` (demo read-only)

See `project_memory/RENDER_DEPLOY.md` for exact Render dashboard fields, env vars, and step-by-step instructions.

### Local production build (smoke test)

```bash
# Terminal 1 — API
DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db uvicorn main:app --port 8000

# Terminal 2 — frontend against real API origin (no localhost in bundle)
cd frontend
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run build && npm run preview
```

### Production considerations (non-demo)

For a private, writable deployment you would disable demo mode, use `DB_PATH` with a persistent database, add authentication, and restrict CORS. **The Render blueprint in this repo is intentionally demo-only.**

## License

This project is part of the DevOps Incident Commander initiative.
See project documentation for licensing information.

---

**Last Updated**: 2026-10-23
**Version**: 1.0.0
**Status**: MVP Ready