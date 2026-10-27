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

**Verification Status (2026-10-27)** — run commands in [Testing](#testing) to reproduce:
- ✅ **Backend (pytest)**: **187** tests in the standard suite (`test_demo_db_setup.py` included); `test_demo_mode.py` is **skipped** under pytest (run as a script)
- ✅ **Demo mode (script)**: **19** checks in `test_demo_mode.py` when run standalone
- ✅ **Frontend**: TypeScript check + production build; Playwright specs under `frontend/qa-*.spec.ts` (see `frontend/playwright.config.ts`)
- ✅ **Investigation**: Mock provider + Ollama provider in code; demo mode returns mock investigation JSON (no external AI)
- ✅ **Templates**: `api_failure_v1`, `database_incident_v1`, `network_incident_v1` (`investigation_templates.py`)

## Prerequisites

### Operating System
- macOS, Linux, or Windows 10+
- Python 3.11+ (tested with 3.11.9)

### Virtual Environment Setup

```bash
# Create virtual environment (from repository root)
python3 -m venv .venv

# Activate environment
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

## Dependencies Installation

Python dependencies are pinned in `requirements.txt` (FastAPI, Pydantic, Uvicorn, `python-multipart`, `httpx`).

### Install Dependencies

```bash
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

**Note**: `sqlite3` is part of the Python standard library.

## Application Setup

### Start the FastAPI Server

```bash
.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
```

**For development with auto-reload:**
```bash
.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Demo mode (recommended for UI / public-style behavior):**
```bash
python3 create_demo_db.py   # creates/updates incidents_demo.db seed
DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db .venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
```

### Configuration

| Variable | Purpose |
|----------|---------|
| `DB_PATH` | SQLite file when **not** in demo mode (default: `incidents.db` in repo root via `models.py`) |
| `DEMO_MODE` | `true` enables read-only API, mock investigation, disabled OpenAPI UI |
| `DEMO_DB_PATH` | SQLite file for demo data (e.g. `incidents_demo.db` or `/tmp/incidents_demo.db` on Render) |
| `DEMO_DB_SEED_PATH` | Seed file copied on startup (`demo_db_setup.py`; see `.env.example`) |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend URL(s) for demo CORS (`main.py`) |
| `AI_PROVIDER` | Selects provider (`mock`, `ollama`, etc.; see `ai_provider.py`) |

See `.env.example` and `project_memory/RENDER_DEPLOY.md` for Render-oriented settings.

## API Endpoints

### Root Endpoint
```http
GET /
```

**Response** (includes `demo_mode` when configured):
```json
{
  "project_name": "DevOps Incident Commander",
  "status": "running",
  "version": "1.0.0",
  "welcome_message": "Agentic AI-based incident investigation and response platform",
  "demo_mode": false
}
```

### Health Endpoint
```http
GET /health
```

**Response** (200 when DB is reachable):
```json
{
  "status": "healthy",
  "timestamp": "2026-10-23T06:35:44.140204+00:00",
  "service": "devops-incident-commander-api",
  "demo_mode": false,
  "database": "incidents.db"
}
```

Returns **503** with `"status": "unhealthy"` if the database check fails (`main.py`).

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
- `200` - Incident deleted successfully (JSON message body)
- `404` - Incident not found

In **demo mode**, `POST`, `PATCH`, and `DELETE` on incidents return **403** (`ReadOnlyMiddleware` in `main.py`).

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

Analytics are **computed from the active SQLite database** (`models.py`); counts and percentages depend on your data, not fixed demo numbers.

### Overall Analytics
```http
GET /analytics/overview
```

**Response shape**:
```json
{
  "total_incidents": 0,
  "open_incidents": 0,
  "investigating_incidents": 0,
  "resolved_incidents": 0,
  "closed_incidents": 0,
  "critical_incidents": 0,
  "resolution_rate_percent": 0.0
}
```

`resolution_rate_percent` = `round((resolved + closed) / total * 100, 2)` when `total > 0`.

### Severity Breakdown
```http
GET /analytics/severity
```

Returns `severity_breakdown`: **four entries**, always in this order: `low`, `medium`, `high`, `critical` (`models.py` → `get_severity_breakdown()`).

For each severity:

- `count` = number of incidents with that severity (0 if none)
- `percentage` = `round((count / total_incidents) * 100, 2)` when `total_incidents > 0`, else `0.0`

**Example** (not fixed demo data): if the database has 1 `low`, 1 `medium`, and 2 incidents total, the API returns `low` → 50%, `medium` → 50%, `high` → 0%, `critical` → 0%. Percentages sum to **100** only when every incident is counted across those four buckets (each incident has exactly one severity).

### Status Breakdown
```http
GET /analytics/status
```

Returns `status_breakdown`: array of `{ "status", "count", "percentage" }` for `open`, `investigating`, `resolved`, `closed`.

## Investigation API

### Start Incident Investigation
```http
POST /incidents/{incident_id}/investigate?include_timeline=true&include_events=true&investigation_depth=detailed&template_id=api_failure_v1&investigation_timeout=30
```

**Query parameters** (`main.py`):
- `include_timeline` (bool, default `true`)
- `include_events` (bool, default `true`)
- `investigation_depth` (`basic` | `detailed` | `full`, default `detailed`)
- `template_id` (optional; e.g. `api_failure_v1`, `database_incident_v1`, `network_incident_v1`)
- `investigation_timeout` (optional positive number; invalid/zero/negative values → **422** via FastAPI `Query(..., gt=0)`)

**Optional JSON body**: evidence fields (`log_text`, `system_events`, `error_messages`, `timestamps`, `source`) passed as `evidence_request`.

**HTTP API `investigation_timeout` (non–demo mode only):** When `DEMO_MODE` is not enabled, `investigation_timeout` is passed into `InvestigationRequest` and `constraints` (`main.py`; covered by `test_investigation_timeout_api.py`). In **demo mode**, the handler returns a **fixed mock payload** (HTTP 200) **before** the investigation service runs, so the timeout query parameter has **no effect** on behavior.

**Response** (illustrative — non-demo investigation; **demo mode JSON differs**, see `main.py` demo branch):

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

**AI providers** (see `ai_provider.py`, `ollama_provider.py`):
- **`mock`**: Default-style provider for tests and demo-style responses
- **`ollama`**: Local Ollama integration when installed and available
- **`openai`**: Listed in config; initialization currently falls back to **mock** (no separate OpenAI client module in this repo)

### Investigation Timeout Configuration

| Mode | `investigation_timeout` on HTTP API |
|------|-------------------------------------|
| **Normal** (`DEMO_MODE` false) | Supported as query param; forwarded to `InvestigationRequest` |
| **Demo** (`DEMO_MODE` true) | Ignored (mock response returned immediately) |

Service-layer validation (booleans, zero, negatives, non-numeric) is covered in `test_investigation.py` and provider tests; API query validation uses `gt=0` in `main.py`.

## Testing

### Backend (pytest)

Recommended explicit suite (matches project verification docs):

```bash
python3 -m pytest \
  test_app.py test_day5_patch.py test_day6_filters.py test_day7_timeline.py \
  test_day8_analytics.py test_final_day3_fixed.py test_check.py test_fixture.py \
  test_ai_provider.py test_investigation.py test_investigation_timeout_api.py \
  test_template_engine.py test_template_engine_documentation.py \
  test_template_loading_simple.py test_demo_db_setup.py \
  -q
```

**Last verified**: **187 passed** in ~3.5s (2026-10-27, this repository).

#### Test count reconciliation

| What | Count | Command / notes |
|------|------:|-----------------|
| **Recommended pytest suite** | **187** run, **187** pass | Explicit file list above (includes `test_demo_db_setup.py` → 2 tests) |
| **Pytest without `test_demo_db_setup.py`** | **185** collected | Same list omitting `test_demo_db_setup.py` (historical docs often cite **185**) |
| **`pytest test_*.py`** | **206** collected; **187** pass, **19** skipped | Skipped: entire `test_demo_mode.py` (`pytestmark` skip — run as script) |
| **Demo script** | **19** functions | `test_demo_mode.py` `__main__` (not pytest) |
| **Legacy “271 tests”** | — | **Obsolete** in older reports; not the current pytest total. Do not use. |

`206` = `187` executed + `19` skipped (not `187 + 19` “passing” tests).

### Demo mode (standalone script)

```bash
DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db python3 test_demo_mode.py
```

**Last verified**: **19** test functions, all passing when run as above.

### Frontend

```bash
cd frontend
npm ci
npx tsc --noEmit
npm run build
# Optional E2E (starts preview on port 4188 by default — see playwright.config.ts):
PLAYWRIGHT_FORCE_NEW_SERVER=1 npx playwright test qa-guide-chat.spec.ts
```

**Representative pytest modules**:
- `test_app.py` — core API
- `test_day6_filters.py` — filtering, search, sort, pagination
- `test_day8_analytics.py` — analytics from DB
- `test_investigation.py` / `test_investigation_timeout_api.py` — investigation + timeout
- `test_template_engine.py` — templates

### Test Structure

The test suite includes:
- **Unit tests**: Test individual components
- **Integration tests**: Test API endpoints
- **E2E tests**: Test full workflows
- **Validation tests**: Test input validation

**Test Database**: Each test runs in an isolated temporary database to prevent data contamination.

## Current Limitations and Known Issues

### Current Limitations (Pre-existing, Non-Regression)
1. **Investigation constraints**: Only `investigation_timeout` is wired from the HTTP API into `InvestigationRequest.constraints`; other constraint keys are not exposed on the endpoint (`main.py`).
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
├── main.py                     # FastAPI application
├── models.py                   # Pydantic models and SQLite access
├── demo_db_setup.py            # Demo DB seed copy for ephemeral hosts
├── create_demo_db.py           # Regenerate incidents_demo.db
├── investigation_service.py
├── investigation_templates.py  # api_failure_v1, database_incident_v1, network_incident_v1
├── template_engine.py
├── ai_provider.py
├── ollama_provider.py
├── conftest.py                 # Pytest DB isolation
├── requirements.txt
├── render.yaml                 # Render blueprint (demo API + static frontend)
├── incidents_demo.db           # Demo seed (public deploy)
├── incidents.db                # Local production DB (gitignored; not used on public demo)
├── test_*.py                   # Pytest + demo script
├── frontend/                   # React + Vite UI (see frontend/package.json)
├── project_memory/             # Architecture, Render deploy, workflow docs
└── README.md
```

## Development Notes

### Testing Strategy
- Each test runs in an isolated temporary database
- Tests do not modify the main `incidents.db`
- Use `set_test_database_path()` for test database configuration

### AI Provider Configuration
- **Default / tests**: `mock` (`ai_provider.py`)
- **Local**: `ollama` when Ollama is available (`ollama_provider.py`)
- **`openai`**: Config entry only; initializes as **mock** in `AnalysisService._initialize_providers()` (no dedicated OpenAI client in this repo)

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

-- incident_events table (application init in main.py / models; pytest uses FK in conftest.py)
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

**Event history and deletion** (`main.py`):

- Creating/updating/deleting incidents appends rows to `incident_events` (e.g. `incident_created`, `incident_deleted`).
- **Delete does not remove event rows**: `DELETE /incidents/{id}` inserts an `incident_deleted` event, then deletes the incident row only.
- `GET /incidents/{id}/timeline` can still return **orphaned events** for that `incident_id` if the incident row is gone but events remain (404 only when both incident and events are missing).
- There is **no** `ON DELETE CASCADE` on `incident_events` in the runtime schema created by `main.py` (test DB in `conftest.py` documents `ON DELETE NO ACTION`).

### Template System
Built-in templates (`investigation_templates.py` — exactly **three** IDs, asserted at import):

| ID | Name |
|----|------|
| `api_failure_v1` | API Service Failure |
| `database_incident_v1` | Database Service Incident |
| `network_incident_v1` | Network Infrastructure Incident |

Extend by adding new templates in that module (and updating the module’s length guard if you add more).

### Frontend (summary)
- **Stack**: React 18, Vite, TypeScript, Tailwind (`frontend/`)
- **Routes**: `/`, `/incidents`, `/incidents/:id`, `/analytics`, `/timeline`, `/settings`
- **API URL**: local dev uses Vite proxy `/api`; production builds use `VITE_API_BASE_URL` (`frontend/src/lib/apiConfig.ts`)
- **Homepage guide chat**: documentation-based chatbot on `/` only (`GuideChatbot` in `MainLayout`)

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

**Backend (demo mode — recommended for UI work), from repo root:**
```bash
python3 create_demo_db.py
DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db .venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
```

**Frontend** (Vite proxies `/api` → backend; no `VITE_API_BASE_URL` needed in dev):
```bash
cd frontend && npm ci && npm run dev
```

### Public demo on Render (two services)

Use **two Render services**: a Python **Web Service** (API) and a **Static Site** (React SPA). The repo includes `render.yaml` as a Blueprint template. **Do not commit secrets** — use Render environment variables only.

| Concern | Approach |
|--------|----------|
| API URL in production | `VITE_API_BASE_URL` at **frontend build time** (see `frontend/.env.example`) |
| CORS | `CORS_ALLOWED_ORIGINS` on the API (comma-separated frontend URL(s)) |
| Demo safety | `DEMO_MODE=true`, read-only middleware, `/docs` disabled |
| Database | Seed `incidents_demo.db`; Render sets `DEMO_DB_PATH=/tmp/incidents_demo.db` and `DEMO_DB_SEED_PATH=incidents_demo.db` (`render.yaml`, `demo_db_setup.py`) |
| API build/start | `pip install -r requirements.txt && python3 create_demo_db.py` / `uvicorn main:app --host 0.0.0.0 --port $PORT` (`render.yaml`) |
| Frontend build | `cd frontend && npm ci && npm run build`; publish `frontend/dist` (`render.yaml`) |
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
# Terminal 1 — API (repo root)
DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db .venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000

# Terminal 2 — frontend against real API origin (production bundle)
cd frontend
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run build && npm run preview
```

### Production considerations (non-demo)

For a private, writable deployment you would disable demo mode, use `DB_PATH` with a persistent database, add authentication, and restrict CORS. **The Render blueprint in this repo is intentionally demo-only.**

## License

This project is part of the DevOps Incident Commander initiative.
See project documentation for licensing information.

---

**Last Updated**: 2026-10-27 (README audit: pytest 187/187, demo script 19/19, `tsc --noEmit` OK)  
**Version**: 1.0.0 (API root `/` field)  
**Status**: MVP — backend tests verified in-repo; **Render production URLs unverified**; full Playwright matrix not re-run in this audit