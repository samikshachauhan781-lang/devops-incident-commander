# DevOps Incident Commander

An Agentic AI-based incident investigation and response platform designed to help teams track incidents, investigate potential root causes, and organize diagnostic recommendations.

## Project Overview

DevOps Incident Commander combines structured incident management with AI-assisted investigation capabilities.

### Current MVP Scope

- Incident CRUD operations, filtering, searching, sorting, and pagination
- Incident timeline and event tracking
- Analytics and dashboard views
- AI-powered incident investigation with built-in template guidance
- Investigation timeout validation and configuration
- Demo mode with protections against incident write operations
- Documentation-based dashboard guide chatbot
- Local AI provider support through Ollama

## Verification Status

**Last audited: October 27, 2026**

The following results were reported during the latest verification work. They describe local test runs, not a verified live production deployment.

| Verification | Reported result |
|---|---|
| Recommended backend pytest suite | 187 passed |
| All `test_*.py` tests | 187 passed, 19 skipped |
| Total pytest tests collected | 206 |
| Standalone demo-mode tests | 19 passed |
| Frontend TypeScript check | Passed |
| Full configured Playwright matrix | 54 passed, 0 failed |
| Guide chatbot Playwright (`qa-guide-chat*.spec.ts`) | 40 passed (reported; includes engine, UI, regression specs) |
| Guide chatbot evaluation dataset (120 cases) | 120/120 topic match, 120/120 behavior match (reported) |
| Live Render deployment | Not verified |
| Live Ollama runtime | Not verified |

The 19 demo-mode tests are executed separately because they are skipped during the normal pytest run. Historical reports referring to 185, 271, or 33 tests/protections do not represent the latest verification counts.

## Prerequisites

- Python 3.11 or newer
- Node.js and npm compatible with the frontend lockfile
- Git
- macOS, Linux, or Windows
- Optional: Ollama installed locally for AI-powered investigations

## Installation

Run these commands from the repository root.

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install backend dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Use `requirements.txt` as the source of truth for Python dependencies.

### 3. Install frontend dependencies

```bash
cd frontend
npm ci
cd ..
```

`npm ci` requires the frontend lockfile to be present and consistent with `package.json`.

## Running the Application

### Backend: normal development mode

From the repository root:

```bash
.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

On Windows, use the virtual environment's Python executable to launch Uvicorn:

```powershell
.venv\Scripts\python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The API is available at `http://127.0.0.1:8000`.

### Database configuration

The application uses SQLite. The `DB_PATH` environment variable selects the database path; the default is `incidents.db`.

macOS/Linux example:

```bash
export DB_PATH="$PWD/incidents.db"
.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
```

Use the appropriate environment variable syntax for your shell. Avoid committing private database files or credentials.

### Environment variables (reference)

| Variable | Purpose |
|----------|---------|
| `DB_PATH` | SQLite file when **not** in demo mode (default: `incidents.db` in repo root via `models.py`) |
| `DEMO_MODE` | `true` enables read-only API, mock investigation, disabled OpenAPI UI |
| `DEMO_DB_PATH` | SQLite file for demo data (e.g. `incidents_demo.db` or `/tmp/incidents_demo.db` on Render) |
| `DEMO_DB_SEED_PATH` | Seed file copied on startup (`demo_db_setup.py`; see `.env.example`) |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend URL(s) for demo CORS (`main.py`) |
| `AI_PROVIDER` | Selects provider (`mock`, `ollama`, etc.; see `ai_provider.py`) |

See `.env.example` and `project_memory/RENDER_DEPLOY.md` for Render-oriented settings.

### Frontend: development server

With the backend running on port 8000, open another terminal:

```bash
cd frontend
npm run dev
```

The Vite development server uses the project's configured proxy for API requests. Check the frontend configuration if you change the backend port.

## API Reference

The examples below illustrate the API's intended request and response shapes. Dynamic IDs and timestamps will differ between requests.

### Root and health endpoints

- `GET /` — service information
- `GET /health` — health and database status

Example root response:

```json
{
  "project_name": "DevOps Incident Commander",
  "status": "running",
  "version": "1.0.0",
  "welcome_message": "Agentic AI-based incident investigation and response platform",
  "demo_mode": false
}
```

Example healthy `/health` response (200 when the database is reachable):

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

Previously summarized: a healthy API returns a healthy status from `/health`. The timestamp and database details depend on the current runtime.

### Incident management

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/incidents` | Create an incident |
| `GET` | `/incidents` | List incidents |
| `GET` | `/incidents/{incident_id}` | Retrieve an incident |
| `PATCH` | `/incidents/{incident_id}` | Update an incident |
| `DELETE` | `/incidents/{incident_id}` | Delete an incident |

Create an incident using `POST /incidents`:

```json
{
  "title": "Database connection timeout",
  "description": "The database connection pool is exhausted, causing timeouts across services.",
  "severity": "high",
  "status": "open",
  "service": "database"
}
```

Typical response codes include:

- `201` — incident created
- `200` — successful retrieval, update, or deletion (delete returns a JSON message body)
- `404` — incident not found
- `422` — input validation error
- `403` — write blocked in demo mode (`ReadOnlyMiddleware` in `main.py`)

In demo mode, write operations are restricted; see the Demo Mode section.

### Pagination, filtering, search, and sorting

Example:

```http
GET /incidents?page=1&page_size=10
```

Supported query parameters:

| Parameter | Description |
|---|---|
| `page` | Page number |
| `page_size` | Number of incidents per page |
| `service` | Filter by service |
| `severity` | Filter by severity |
| `status` | Filter by incident status |
| `created_after` | Filter by creation timestamp |
| `search` | Case-insensitive search in title and description |
| `sort_by` | `created_at`, `title`, `severity`, `status`, or `service` |
| `order` | `asc` or `desc` |

Supported severity values: `low`, `medium`, `high`, `critical`.

Supported status values: `open`, `investigating`, `resolved`, `closed`.

Example:

```http
GET /incidents?severity=high&status=open&search=database&sort_by=created_at&order=desc
```

A paginated response includes `incidents`, `page`, `page_size`, `total`, and `has_more`.

### Incident timeline

```http
GET /incidents/{incident_id}/timeline
```

The timeline exposes recorded incident events, including applicable changes and deletion events.

Example event:

```json
{
  "id": "event-1",
  "incident_id": "incident-1",
  "event_type": "severity_change",
  "description": "Severity changed from medium to high",
  "old_values": {
    "severity": "medium"
  },
  "new_values": {
    "severity": "high"
  },
  "created_at": "2026-10-23T06:35:44.143087+00:00"
}
```

The timeline may retain historical events after an incident is deleted. In that case, the timeline can contain events even when the parent incident record no longer exists.

### Analytics endpoints

- `GET /analytics/overview`
- `GET /analytics/severity`
- `GET /analytics/status`

The following examples use a consistent hypothetical dataset of five incidents. Actual results depend on the database contents.

#### Overview

```json
{
  "total_incidents": 5,
  "open_incidents": 3,
  "investigating_incidents": 1,
  "resolved_incidents": 1,
  "closed_incidents": 0,
  "critical_incidents": 1,
  "resolution_rate_percent": 20.0
}
```

#### Severity breakdown

```json
{
  "severity_breakdown": [
    {"severity": "low", "count": 1, "percentage": 20.0},
    {"severity": "medium", "count": 2, "percentage": 40.0},
    {"severity": "high", "count": 1, "percentage": 20.0},
    {"severity": "critical", "count": 1, "percentage": 20.0}
  ]
}
```

#### Status breakdown

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

These examples are illustrative, not live API output.

Analytics are **computed from the active SQLite database** (`models.py`); counts and percentages depend on your data. The severity breakdown always includes **four entries** in order: `low`, `medium`, `high`, `critical`. For each severity, `percentage` = `round((count / total_incidents) * 100, 2)` when `total_incidents > 0`, else `0.0`. Overview `resolution_rate_percent` = `round((resolved + closed) / total * 100, 2)` when `total > 0`.

## AI-Powered Investigation

### Start an investigation

```http
POST /incidents/{incident_id}/investigate?include_timeline=true&include_events=true&investigation_depth=detailed&template_id=api_failure_v1
```

**Query parameters** (`main.py`):

| Parameter | Description |
|-----------|-------------|
| `include_timeline` | bool, default `true` |
| `include_events` | bool, default `true` |
| `investigation_depth` | `basic`, `detailed`, or `full` (default `detailed`) |
| `template_id` | optional; e.g. `api_failure_v1`, `database_incident_v1`, `network_incident_v1` |
| `investigation_timeout` | optional positive number; invalid/zero/negative → **422** (`Query(..., gt=0)`) |

**Optional JSON body**: evidence fields (`log_text`, `system_events`, `error_messages`, `timestamps`, `source`) as `evidence_request`.

In **demo mode**, the handler returns a **fixed mock JSON** (HTTP 200) before the investigation service runs; the timeout query parameter has **no effect**. In non-demo mode, `investigation_timeout` is forwarded into `InvestigationRequest.constraints` (see `test_investigation_timeout_api.py`).

Example request body (optional evidence):

```json
{
  "include_timeline": true,
  "include_events": true,
  "investigation_depth": "detailed",
  "template_id": "database_incident_v1"
}
```

The incident must exist. The response may contain:

- Incident data and supplied evidence
- AI analysis and reasoning
- Root-cause hypotheses
- Supporting evidence
- Confidence scores
- Diagnostic steps and recommendations
- Urgency and investigation metadata

The exact fields and results depend on the request, selected provider, template applicability, and runtime configuration. Example AI responses in this document are illustrative and should not be treated as guaranteed output.

### Built-in investigation templates

The application includes three built-in templates:

| Template ID | Name |
|---|---|
| `api_failure_v1` | API Service Failure |
| `database_incident_v1` | Database Service Incident |
| `network_incident_v1` | Network Infrastructure Incident |

Templates provide investigation guidance for common incident categories. They are intended to be immutable and thread-safe. Applicability depends on the incident and the template's rules.

### AI providers

| Provider | Purpose | Requirement |
|---|---|---|
| `mock` | Development and deterministic testing | No external AI service required |
| `ollama` | Local model inference | Local Ollama service and configured model |
| `openai` | Cloud model inference | Valid API key and provider configuration |

The Ollama example model used in project documentation is `llama3.2:3b`. Its availability and runtime behavior must be verified in the target environment. The existence of the provider implementation does not prove that a live Ollama request has succeeded.

**Note on `openai`:** listed in configuration; this repository initializes OpenAI as **mock** in `AnalysisService._initialize_providers()` (no separate OpenAI client module).

## Investigation Timeout

The investigation endpoint supports an optional `investigation_timeout` query parameter in non-demo operation.

Example:

```http
POST /incidents/{incident_id}/investigate?investigation_timeout=30
```

A positive timeout value can be supplied. Invalid values such as zero, negative values, or non-numeric input should be rejected by request validation.

In demo mode, the investigation path uses the demo behavior and does not exercise the normal AI investigation timeout path. Do not interpret a successful demo investigation as verification of live provider timeout behavior.

| Mode | `investigation_timeout` on HTTP API |
|------|-------------------------------------|
| **Normal** (`DEMO_MODE` false) | Supported as query param; forwarded to `InvestigationRequest` |
| **Demo** (`DEMO_MODE` true) | Ignored (mock response returned immediately) |

## Demo Mode

Demo mode is intended for safe sharing and demonstration. It restricts incident write operations and disables the interactive API documentation route.

Example local setup:

```bash
python3 create_demo_db.py
DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db \
  .venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
```

If `incidents_demo.db` is already seeded, follow the project's demo database setup instructions rather than unnecessarily overwriting existing data.

Reported demo verification: 19 standalone demo test functions passed. Normal pytest execution skips those 19 tests because the demo test file is designed to be run separately.

Run the standalone demo tests with:

```bash
DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db \
  python3 test_demo_mode.py
```

In demo mode, write operations such as `POST`, `PATCH`, and `DELETE` are blocked according to the demo protections. The API documentation route is disabled.

Demo mode is not a substitute for authentication or production access controls.

## Testing

Run the recommended backend suite from the repository root:

```bash
python3 -m pytest \
  test_app.py \
  test_day5_patch.py \
  test_day6_filters.py \
  test_day7_timeline.py \
  test_day8_analytics.py \
  test_final_day3_fixed.py \
  test_check.py \
  test_fixture.py \
  test_ai_provider.py \
  test_investigation.py \
  test_investigation_timeout_api.py \
  test_template_engine.py \
  test_template_engine_documentation.py \
  test_template_loading_simple.py \
  test_demo_db_setup.py \
  -q
```

Reported result during the October 27 audit: **187 passed**.

#### Test count reconciliation

| What | Count | Notes |
|------|------:|-------|
| **Recommended pytest suite** | **187** pass | Explicit file list above (includes `test_demo_db_setup.py`) |
| **Same list without `test_demo_db_setup.py`** | **185** collected | Historical docs often cite **185** |
| **`pytest test_*.py`** | **206** collected; **187** pass, **19** skipped | Skipped: entire `test_demo_mode.py` (run as script) |
| **Demo script** | **19** functions | `DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db python3 test_demo_mode.py` |
| **Legacy “271 tests” / “33 demo checks”** | — | Obsolete; do not use |

Run all matching pytest files:

```bash
python3 -m pytest test_*.py -q
```

Reported result: **187 passed, 19 skipped; 206 tests collected**. The skipped demo tests are run separately using the standalone command above.

Run the frontend TypeScript check:

```bash
cd frontend
npx tsc --noEmit
```

The October 27 audit reported this check passing.

```bash
npm run build
# Guide chatbot only (mocked API; preview port 4188 default — see playwright.config.ts):
PLAYWRIGHT_FORCE_NEW_SERVER=1 npx playwright test qa-guide-chat*.spec.ts
```

### Full Playwright browser QA

The configured Playwright suite matches:

- `qa-*.spec.ts`
- `browser-test.spec.ts`

Debug DOM specs are excluded by the current Playwright configuration.

The reported final result was **54 passed, 0 failed** after correcting the local API setup and mobile timeline layout.

For the full local matrix, the frontend must be built with the API base URL embedded in the production bundle. Start the demo API first on port `8000`, then run:

Terminal 1 — API:

```bash
DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db \
  .venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
```

Terminal 2 — frontend build and browser tests:

```bash
cd frontend
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run build
PLAYWRIGHT_PREVIEW_PORT=4173 \
PLAYWRIGHT_FORCE_NEW_SERVER=1 \
npx playwright test --reporter=list
```

The full matrix includes guide-chat, browser, final workflow, theme, and responsive tests. The reported 54/54 result was obtained with this API/build/preview configuration. With the advanced guide chatbot specs on this branch, the reported **`qa-guide-chat*.spec.ts`** result is **40/40** and the **120-case** guide evaluation is **120/120** topic and behavior match (see `qa-guide-chat-engine.spec.ts`).

If a request unexpectedly fails with a CORS error, check the running API process. A stale server may not reflect the current `main.py` CORS configuration (demo mode must allow **POST** for `/investigate`). Restart the API using the current project environment before diagnosing the frontend as the cause.

The browser QA result is a local test result. It does not verify a live Render deployment.

## Known Limitations

- **Investigation constraints:** Only `investigation_timeout` is wired from the HTTP investigate endpoint into `InvestigationRequest.constraints` when not in demo mode; other constraint keys are not exposed on the API.
- **No authentication:** API authentication and authorization are not implemented. Do not expose a writable, non-demo instance publicly without appropriate access controls.
- **No evidence collection UI:** The backend supports investigation evidence, but the frontend does not provide a dedicated evidence-submission form.
- **External AI dependencies:** Ollama requires a working local service and model; OpenAI requires valid credentials and provider configuration.
- **Deployment not verified:** A successful local build or test run does not establish that the live Render services are healthy.
- **Browser coverage is configuration-specific:** The reported 54-test result covers the specs matched by the current Playwright configuration, not excluded debug specs or every possible browser/environment.
- **SQLite:** The application uses SQLite by default. Production deployments require deliberate choices around persistent storage, backups, access permissions, and concurrency.

### Out of MVP scope

- Advanced monitoring integrations
- Multi-database support
- User authentication and authorization
- Advanced reporting and export
- Real-time WebSocket updates
- Multi-tenancy

## Project Structure

Key files and directories include:

```text
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
├── test_*.py                   # Pytest + demo script
├── frontend/                   # React + Vite UI; guide chatbot on `/` only
├── project_memory/             # Architecture, Render deploy, workflow docs
└── README.md
```

Local `incidents.db` is gitignored and not used on the public demo deploy.

This is a representative structure. Check the repository for the current complete file list. Local database files may be ignored by Git and should not be committed unless the deployment design explicitly requires a demo seed database.

## Development Notes

### Homepage guide chatbot

- **UI:** floating **Guide** on the dashboard (`/` only) — `GuideChatbot` in `MainLayout`
- **Engine:** documentation-based local assistant (`guideChatEngine.ts`, `guideChatKnowledge.ts`); optional LLM provider hook (`guideChatProvider.ts`) with **no external API by default**
- **Tests:** `frontend/qa-guide-chat*.spec.ts`, `frontend/playwright.config.ts`

### Frontend (summary)

- **Stack:** React 18, Vite, TypeScript, Tailwind (`frontend/`)
- **Routes:** `/`, `/incidents`, `/incidents/:id`, `/analytics`, `/timeline`, `/settings`
- **API URL:** local dev uses Vite proxy `/api`; production builds use `VITE_API_BASE_URL` (`frontend/src/lib/apiConfig.ts`)

### Event history and deletion

- **Delete does not remove event rows:** `DELETE /incidents/{id}` records an `incident_deleted` event, then deletes the incident row only.
- `GET /incidents/{id}/timeline` may return **orphaned events** when the incident row is gone (404 only when both incident and events are missing).

## Security Considerations

The application uses Pydantic validation and SQLite storage, but input validation alone is not a complete security boundary.

Before deploying a writable instance publicly:

- Add authentication and authorization.
- Restrict CORS to trusted origins.
- Implement rate limiting.
- Store credentials in environment variables or a secrets manager.
- Configure persistent database storage and backups.
- Review logging and sensitive-data handling.
- Test the deployment's write protections and health checks.

The supplied Render configuration is intended for a demo deployment, not a fully secured production service.

## Deployment

### Local demo

Follow the Demo Mode section to start the API, then start the frontend with Vite for local development (`cd frontend && npm ci && npm run dev` — Vite proxies `/api`; no `VITE_API_BASE_URL` needed in dev).

For a production-style local frontend preview, build with:

```bash
cd frontend
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run build
npm run preview
```

Ensure the API is running and its CORS configuration permits the frontend origin.

### Render demo deployment

The repository includes `render.yaml` for a two-service setup:

1. A Python Web Service for the FastAPI backend.
2. A Static Site for the React frontend.

Configure the environment variables and build/start commands according to `render.yaml` and `project_memory/RENDER_DEPLOY.md`.

**Pre-deploy checklist:**

1. Seed demo data (`python3 create_demo_db.py` or commit `incidents_demo.db` if your deploy design requires it).
2. Ensure `.env`, `frontend/.env.production`, and local `incidents.db` are **not** in Git (see root `.gitignore`).
3. After first deploy, set `CORS_ALLOWED_ORIGINS` to your static site URL and redeploy the API.
4. Set `VITE_API_BASE_URL` to your API URL (no trailing slash) and **redeploy the frontend** so Vite bakes it into the bundle.

**Verify after deploy:**

- `curl https://<api-host>/health` → `"status":"healthy"`, `"demo_mode":true`
- Dashboard loads; deep links and refresh work; `POST /incidents` → `403` in demo mode

| Concern | Deployment requirement |
|---|---|
| Frontend API URL | Set `VITE_API_BASE_URL` to the deployed API URL at frontend build time |
| API CORS | Set `CORS_ALLOWED_ORIGINS` to the trusted frontend origin(s) |
| Demo safety | Enable `DEMO_MODE=true` and configure the demo database path |
| Health check | Configure the API health check to use `/health` |
| SPA routing | Configure the static site rewrite to serve `index.html` for frontend routes |
| Secrets | Use platform environment variables; do not commit secrets |

After deployment, verify the API health endpoint, open the frontend, check dashboard/API connectivity, test frontend deep links, and confirm demo write requests are rejected.

**Live deployment status:** Render deployment was not verified during the October 27 local QA audit.

## License

This project is part of the DevOps Incident Commander initiative. Refer to the repository's licensing files and project documentation for applicable license terms.

---

**Last updated:** October 27, 2026  
**Version:** 1.0.0  
**Status:** MVP — local verification reported (pytest 187/187, demo script 19/19, Playwright 54/54 matrix, guide chatbot specs/eval as reported above); **live Render deployment not verified**.

