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
  "welcome_message": "Agentic AI-based incident investigation and response platform"
}
```

A healthy API returns a healthy status from `/health`. The timestamp and database details depend on the current runtime.

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
- `200` — successful retrieval or update
- `204` — successful deletion
- `404` — incident not found
- `422` — input validation error

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

## AI-Powered Investigation

### Start an investigation

```http
POST /incidents/{incident_id}/investigate
Content-Type: application/json
```

Example request:

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

## Investigation Timeout

The investigation endpoint supports an optional `investigation_timeout` query parameter in non-demo operation.

Example:

```http
POST /incidents/{incident_id}/investigate?investigation_timeout=30
```

A positive timeout value can be supplied. Invalid values such as zero, negative values, or non-numeric input should be rejected by request validation.

In demo mode, the investigation path uses the demo behavior and does not exercise the normal AI investigation timeout path. Do not interpret a successful demo investigation as verification of live provider timeout behavior.

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

The full matrix includes guide-chat, browser, final workflow, theme, and responsive tests. The reported 54/54 result was obtained with this API/build/preview configuration.

If a request unexpectedly fails with a CORS error, check the running API process. A stale server may not reflect the current `main.py` CORS configuration. Restart the API using the current project environment before diagnosing the frontend as the cause.

The browser QA result is a local test result. It does not verify a live Render deployment.

## Known Limitations

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
├── main.py
├── models.py
├── investigation_service.py
├── investigation_templates.py
├── template_engine.py
├── ai_provider.py
├── ollama_provider.py
├── requirements.txt
├── render.yaml
├── create_demo_db.py
├── test_*.py
├── frontend/
├── project_memory/
├── README.md
├── incidents.db
└── incidents_demo.db
```

This is a representative structure. Check the repository for the current complete file list. Local database files may be ignored by Git and should not be committed unless the deployment design explicitly requires a demo seed database.

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

Follow the Demo Mode section to start the API, then start the frontend with Vite for local development.

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
**Status:** MVP — local verification reported; live deployment not verified.

