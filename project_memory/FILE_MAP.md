# Project File Map

## Core Application Files

### `main.py`
- **Type**: Core Application
- **Responsibility**: FastAPI application with all API endpoints
- **Key Components**:
  - Root endpoint (`/`)
  - Health endpoint (`/health`)
  - Incident CRUD endpoints (`/incidents`, `/incidents/{id}`)
  - Timeline endpoint (`/incidents/{id}/timeline`)
  - Analytics overview endpoint
- **Dependencies**: `models.py`, `fastapi`, `sqlite3`
- **Location**: Database operations for incidents and events

### `models.py`
- **Type**: Core Application
- **Responsibility**: Pydantic models, database initialization, and CRUD operations
- **Key Components**:
  - Incident model with validation
  - IncidentEvent model for timeline tracking
  - Database connection management and test isolation
  - All SQLite persistence functions
- **Dependencies**: `pydantic`, `sqlite3`, `uuid`, `datetime`
- **Location**: Business logic and data persistence

### `conftest.py`
- **Type**: Test Infrastructure
- **Responsibility**: Pytest fixtures for test database isolation
- **Key Components**:
  - `function_test_isolation` fixture (autouse)
  - `test_client` fixture
  - Sample incident data for testing
- **Dependencies**: `pytest`, `fastapi.testclient`, `models.py`
- **Location**: Test setup and cleanup

## Test Files

### `test_app.py`
- **Type**: Test
- **Responsibility**: Core API functionality tests
- **Key Tests**:
  - Root endpoint functionality
  - Health endpoint
  - Incident creation
  - Incident listing
  - Incident retrieval by ID
  - Incident deletion
  - Validation error handling
- **Dependencies**: `main.py`, `conftest.py`

### `test_day5_patch.py`
- **Type**: Test
- **Responsibility**: PATCH endpoint comprehensive tests
- **Key Tests**:
  - Single field updates
  - Multiple field updates
  - Empty updates (422 validation)
  - Null value validation (422 validation)
  - Status transitions
  - Resolution timestamps
- **Dependencies**: `main.py`, `conftest.py`

### `test_day6_filters.py`
- **Type**: Test
- **Responsibility**: Filtering and query tests
- **Key Tests**:
  - Service-based filtering
  - Status-based filtering
  - Severity-based filtering
  - Pagination
  - Date-based filtering
- **Dependencies**: `main.py`, `conftest.py`

### `test_day7_timeline.py`
- **Type**: Test
- **Responsibility**: Timeline and event tests
- **Key Tests**:
  - Timeline retrieval
  - Event creation
  - Event filtering
  - Timeline validation
- **Dependencies**: `main.py`, `conftest.py`

### `test_day8_analytics.py`
- **Type**: Test
- **Responsibility**: Analytics overview tests
- **Key Tests**:
  - Severity breakdown
  - Status breakdown
  - Resolution rate calculations
  - Analytics endpoint response
- **Dependencies**: `main.py`, `conftest.py`

### `test_final_day3_fixed.py`
- **Type**: Test
- **Responsibility**: Regression tests for Day 3 functionality
- **Dependencies**: `main.py`, `models.py`

### `test_check.py`
- **Type**: Test
- **Responsibility**: Basic application validation tests
- **Dependencies**: `main.py`

## Development Tools & Scripts

### `check_application.py`
- **Type**: Development Tool
- **Responsibility**: Application validation script
- **Dependencies**: `main.py`

### `fix_test_day6_filters.py`
- **Type**: Development Tool
- **Responsibility**: Test fixes script
- **Dependencies**: `main.py`, `test_day6_filters.py`

### `minimal_test_day6_filters.py`
- **Type**: Development Tool
- **Responsibility**: Minimal test script
- **Dependencies**: `main.py`

## Documentation Files

### `CHECK_APPLICATION_GUIDE.md`
- **Type**: Documentation
- **Responsibility**: Application validation guide

### `DAY_*_CHANGES_SUMMARY.md`
- **Type**: Documentation
- **Responsibility**: Development phase documentation
- **Each file documents changes for a specific development phase**

### `test_check_methods.md`
- **Type**: Documentation
- **Responsibility**: Testing methods guide

## Database & Cache

### `incidents.db`
- **Type**: Database
- **Responsibility**: SQLite database for production incidents
- **Size**: ~196 KB
- **Notes**: Test fixtures create temporary databases in `/tmp/`

## Temporary/Debug Files

### `temp_*.py`
- **Type**: Temporary Files
- **Responsibility**: Temporary utilities (to be cleaned up)

### `conftest.py.backup`
- **Type**: Backup File
- **Responsibility**: Backup of conftest.py

## UUID-named Temporary Files

- **Location**: Project root directory
- **Pattern**: Various UUID-named files
- **Usage**: Temporary files (to be cleaned up)

## Directory Structure

```
/devops-incident-commander
├── main.py                    # Core FastAPI application
├── models.py                  # Pydantic models and database
├── conftest.py                # Pytest fixtures
├── test_*.py                  # Test files
├── CHECK_APPLICATION_GUIDE.md # Application validation guide
├── DAY_*_CHANGES_SUMMARY.md   # Development phase documentation
├── temp_*.py                  # Temporary utilities
├── .venv/                     # Python virtual environment
├── __pycache__/              # Python bytecode cache
├── incidents.db               # SQLite database
├── project_memory/            # Project memory files (new)
└── Various UUID-named temp files
```

## Key File Responsibilities Summary

| File | Responsibility | Dependencies |
|------|----------------|--------------|
| `main.py` | API endpoints and request handling | `models.py`, `fastapi` |
| `models.py` | Data models and database operations | `pydantic`, `sqlite3` |
| `conftest.py` | Test fixtures and isolation | `pytest`, `fastapi.testclient` |
| `test_app.py` | Core API functionality tests | `main.py`, `conftest.py` |
| `test_day5_patch.py` | PATCH endpoint tests | `main.py`, `conftest.py` |
| `test_day6_filters.py` | Filtering tests | `main.py`, `conftest.py` |
| `test_day7_timeline.py` | Timeline tests | `main.py`, `conftest.py` |
| `test_day8_analytics.py` | Analytics tests | `main.py`, `conftest.py` |

## Current Verified State

As of 2026-10-19 14:54:00:
- All 39 tests are passing
- Test database isolation is working correctly
- Transaction management is fixed with explicit commits
- Service filtering is implemented
- Null value validation is working (422 errors)
- Empty update validation is working (422 errors)
- Resolution timestamps are being set correctly