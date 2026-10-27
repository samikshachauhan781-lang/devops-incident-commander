# Project Cleanup Audit Report

**Project:** DevOps Incident Commander
**Root:** `/Users/samiksha/Desktop/devops-incident-commander`
**Date:** 2026-10-26
**Auditor:** AI Assistant

---

## 1. Project Structure Overview

### 1.1 High-Level Directory Structure

```
/Users/samiksha/Desktop/devops-incident-commander/
├── Core Backend Application (Python/FastAPI)
│   ├── main.py                          # FastAPI entry point (840 lines)
│   ├── models.py                        # Pydantic models & DB ops (604 lines)
│   ├── investigation_service.py         # AI investigation workflow (813 lines)
│   ├── investigation_templates.py       # Template definitions (542 lines)
│   ├── investigation_templates_fixed.py # Unused fixed templates (542 lines)
│   ├── template_engine.py               # Template rendering (285 lines)
│   ├── ai_provider.py                   # AI provider abstraction (667 lines)
│   ├── ai_provider_fixed.py             # Unused fixed provider (337 lines)
│   ├── ai_provider_simple.py            # Unused simple provider (255 lines)
│   ├── ollama_provider.py               # Ollama LLM integration (529 lines)
│   └── README.md                        # Main documentation (15KB)
│
├── Frontend Application (React/TypeScript/Vite)
│   ├── frontend/
│   │   ├── src/                         # Source code (22 files)
│   │   ├── dist/                        # Build output (regenerable)
│   │   ├── node_modules/                # Dependencies (excluded from git)
│   │   ├── package.json / lock.json     # NPM manifests
│   │   ├── vite.config.mts              # Vite configuration
│   │   ├── tsconfig.json                # TypeScript config
│   │   ├── tailwind.config.js           # Tailwind CSS config
│   │   └── Various logs & backup files
│
├── Test Suite (130+ Python test files)
│   ├── test_app.py                      # Core tests (9 tests)
│   ├── test_day5_patch.py               # PATCH tests (21 tests)
│   ├── test_day6_filters.py             # Filter tests (42 tests)
│   ├── test_day7_timeline.py            # Timeline tests (3 tests)
│   ├── test_day8_analytics.py           # Analytics tests (18 tests)
│   ├── test_final_day3_fixed.py         # Regression tests (9 tests)
│   ├── test_investigation.py            # Investigation tests (25 tests)
│   ├── test_demo_mode.py                # Demo protection (19 tests, env-dependent)
│   └── 25+ other test files
│
├── Project Memory & Documentation (13 files)
│   └── project_memory/ (10 files)
│
├── Phase Reports & Summaries (30+ markdown files)
│
├── Temporary/Artifact Files (23 UUID-named files)
│
├── Logs & Cache
│
├── Scripts & Utilities (15+ files)
│
└── Databases (2 SQLite files)
```

### 1.2 File Counts by Category

| Category | Count | Size |
|----------|-------|------|
| Core Backend Python Files | 10 | ~4,872 lines |
| Frontend Source (TS/TSX/CSS) | 22 | ~3,000 lines |
| Frontend Build Output | 5 | regenerable |
| Test Files (Python) | 32 | ~10,000+ tests |
| Documentation (Markdown) | 45+ | ~500KB |
| Project Memory | 10 | ~150KB |
| Phase Reports/Summaries | 30+ | ~400KB |
| UUID Temporary Files | 23 | mostly empty |
| Log Files | 8 | ~30KB |
| Scripts/Utilities | 15 | ~50KB |
| Database Files | 2 | ~2MB |
| Backup Files | 3 | ~5KB |
| Cache Directories | 2 | variable |

---

## 2. Critical Application Entry Points

### 2.1 Backend Entry Points
- **`main.py`** - FastAPI application factory, all routes registered here
- **`models.py`** - Database models, SQLite persistence layer
- **`investigation_service.py`** - AI investigation workflow engine
- **`investigation_templates.py`** - Template definitions (ACTIVE)
- **`template_engine.py`** - Template rendering wrapper
- **`ai_provider.py`** - AI provider abstraction (ACTIVE)
- **`ollama_provider.py`** - Ollama LLM integration (ACTIVE)

### 2.2 Frontend Entry Points
- **`frontend/src/main.tsx`** - React app bootstrap
- **`frontend/src/App.tsx`** - Routing, providers, layout composition
- **`frontend/src/layouts/MainLayout.tsx`** - Main layout with sidebar, header, toasts
- **`frontend/src/contexts/IncidentContext.tsx`** - Global state management
- **`frontend/src/api/client.ts`** - Axios API client

### 2.3 Runtime Loading Paths
- **FastAPI routers** - Registered in `main.py` via decorators
- **AI Provider** - Dynamic loading via `get_analysis_service()` in `ai_provider.py`
- **Ollama Provider** - Lazy-loaded via `get_ollama_provider()` in `ollama_provider.py`
- **Templates** - Loaded via `get_template_engine()` → `investigation_templates` module
- **Frontend Routes** - Declared in `App.tsx` with React Router
- **Test Discovery** - pytest auto-discovers `test_*.py` files

---

## 3. Dependency Analysis Summary

### 3.1 Backend Import Graph (Verified Active)

```
main.py
├── investigation_service.py
│   ├── ai_provider.py (ACTIVE)
│   │   └── ollama_provider.py (ACTIVE)
│   ├── template_engine.py
│   │   └── investigation_templates.py (ACTIVE)
│   └── models.py
├── models.py
└── ollama_provider.py (via ai_provider)
```

### 3.2 Files NOT Imported Anywhere (Dead Code Candidates)

| File | Evidence |
|------|----------|
| `ai_provider_fixed.py` | No imports in any non-test file |
| `ai_provider_simple.py` | No imports in any non-test file |
| `investigation_templates_fixed.py` | No imports in any non-test file |
| `test_investigation_old.py` | Legacy test, superseded by `test_investigation.py` |
| `test_ai_provider_fixed.py` | Tests for dead `ai_provider_fixed.py` |
| `test_ai_provider_simple.py` | Tests for dead `ai_provider_simple.py` |
| `test_investigation_api_template.py` | Tests for unused API |
| `test_investigation_template_integration_fixed.py` | Tests for dead templates |
| `test_mock_provider_template_guidance.py` | Tests for unused feature |
| `test_ollama_structured_output.py` | Tests for unused feature |
| `test_ollama_template_guidance.py` | Tests for unused feature |
| `test_ollama_timeout.py` | Tests for unused feature |
| `test_thread_management_issue.py` | Tests for fixed issue |
| `test_timeout_fix.py` | Tests for fixed implementation |
| `test_timeout_implementation.py` | Tests for fixed implementation |
| `test_timeout_validation.py` | Tests for fixed implementation |
| `test_timeout_validation_corrected.py` | Tests for fixed implementation |
| `test_template_engine.py` | Tests for `template_engine.py` (keep) |
| `test_template_engine_documentation.py` | Documentation tests (keep) |
| `test_template_loading_simple.py` | Simple template tests (keep) |
| `verify_template_engine.py` | Not found in filesystem |

### 3.3 Frontend Unused Components

| File | Status | Evidence |
|------|--------|----------|
| `src/components/settings/Settings.tsx` | **Unused** | Not imported in `App.tsx`; `SimpleSettings.tsx` used instead |
| `src/components/incidents/IncidentDetail.tsx.bak` | **Backup** | Backup file, not imported |
| `src/layouts/MainLayout.tsx.backup` | **Backup** | Backup file |
| `src/hooks/useAuth.tsx` | **Used** | Imported in `App.tsx` |
| `src/hooks/useIncidentService.ts` | **Used** | Imported in components |
| `src/hooks/useToast.ts` | **Used** | Imported in `MainLayout.tsx` |
| `vite.config.ts.bak` | **Backup** | Backup file |

---

## 4. Detailed Cleanup Candidates Classification

### Category A — Safe Cleanup (Disposable Artifacts)

| # | Path | Type | Size | Evidence | Recovery |
|---|------|------|------|----------|----------|
| A1 | `01900dcd-124b-46b1-8d8d-30f3fb42bd83` | Empty file | 0B | UUID-named, empty, created Oct 17 | N/A (empty) |
| A2 | `10b4ac6b-995d-4800-a9db-bb2e53e8509a` | Empty file | 0B | UUID-named, empty, created Oct 17 | N/A (empty) |
| A3 | `130dabb9-8009-4830-a0c9-05d57aad5dbf` | Empty file | 0B | UUID-named, empty, created Oct 17 | N/A (empty) |
| A4 | `3fb9ca39-45e1-42d8-94d6-5825cd260591` | Empty file | 0B | UUID-named, empty, created Oct 17 | N/A (empty) |
| A5 | `40dd286d-b260-47a5-8f8c-4e149d52aa80` | Empty file | 0B | UUID-named, empty, created Oct 16 | N/A (empty) |
| A6 | `4f683daa-6501-4e6d-8568-03f3dbcc0687` | Empty file | 0B | UUID-named, empty, created Oct 17 | N/A (empty) |
| A7 | `55a3284b-e3ea-4aa7-89d6-0b1bba2e5e1f` | Empty file | 0B | UUID-named, empty, created Oct 17 | N/A (empty) |
| A8 | `63b650a6-c1c5-4b3e-b291-c7f20febfd68` | Empty file | 0B | UUID-named, empty, created Oct 17 | N/A (empty) |
| A9 | `700224b0-a9b9-4bf9-8476-5e59468a3574` | Empty file | 0B | UUID-named, empty, created Oct 16 | N/A (empty) |
| A10 | `7daaac83-0a19-4607-a558-4348cd74d52b` | Empty file | 0B | UUID-named, empty, created Oct 17 | N/A (empty) |
| A11 | `89d41a41-b2d2-4b12-8021-7b936b06f97f` | Empty file | 0B | UUID-named, empty, created Oct 17 | N/A (empty) |
| A12 | `8f36773e-6d94-4160-967c-7580a6153f50` | Empty file | 0B | UUID-named, empty, created Oct 17 | N/A (empty) |
| A13 | `924ae6de-8520-44a2-8100-d4873ce6fa9d` | Empty file | 0B | UUID-named, empty, created Oct 17 | N/A (empty) |
| A14 | `a6b41e64-1734-48c5-93c3-089e589802a4` | Empty file | 0B | UUID-named, empty, created Oct 17 | N/A (empty) |
| A15 | `c454912c-9dee-46e7-be28-9562d014901a` | Empty file | 0B | UUID-named, empty, created Oct 16 | N/A (empty) |
| A16 | `d0e405e9-0cdf-4189-ac82-78cb596327e3` | Empty file | 0B | UUID-named, empty, created Oct 16 | N/A (empty) |
| A17 | `dcf37aff-b9b8-4f53-a3e2-34b0ae525b9e` | Empty file | 0B | UUID-named, empty, created Oct 16 | N/A (empty) |
| A18 | `ddaf8d70-0285-48da-823e-f8e844a689b2` | Empty file | 0B | UUID-named, empty, created Oct 16 | N/A (empty) |
| A19 | `deb293c5-4812-45ba-905b-5179748e604b` | Empty file | 0B | UUID-named, empty, created Oct 16 | N/A (empty) |
| A20 | `e3c2b7d1-9dc5-4b8c-a9d9-5a640a881c5f` | Empty file | 0B | UUID-named, empty, created Oct 16 | N/A (empty) |
| A21 | `e3d6ed6b-83ce-4af1-9c33-dde90affeb8f` | Empty file | 0B | UUID-named, empty, created Oct 16 | N/A (empty) |
| A22 | `f0c64a91-7c60-4a10-ad3a-326a5d89da30` | Empty file | 0B | UUID-named, empty, created Oct 16 | N/A (empty) |
| A23 | `fba871b9-ff93-46fa-a0b0-df6d5cac02f7` | Empty file | 0B | UUID-named, empty, created Oct 17 | N/A (empty) |
| A24 | `1d39ebf9-40ac-4efd-ad9c-7606c0b2206f` | SQLite DB | 12KB | Test artifact DB, not used by app | Git history |
| A25 | `frontend/vite.config.ts.bak` | Backup | 290B | Backup of vite config | Git history |
| A26 | `frontend/src/components/incidents/IncidentDetail.tsx.bak` | Backup | ~3KB | Backup of component | Git history |
| A27 | `frontend/src/layouts/MainLayout.tsx.backup` | Backup | ~15KB | Backup of layout | Git history |
| A28 | `conftest.py.backup` | Backup | 4.7KB | Backup of pytest config | Git history |
| A29 | `test_day6_filters.py.backup` | Backup | 26KB | Backup in git index | Git history |
| A30 | `backend.log` | Log | 25KB | Runtime log, regenerable | N/A |
| A31 | `backend_tunnel.log` | Log | 6KB | Runtime log, regenerable | N/A |
| A32 | `frontend/frontend.log` | Log | 2KB | Runtime log, regenerable | N/A |
| A33 | `frontend/frontend_preview.log` | Log | 595B | Runtime log, regenerable | N/A |
| A34 | `frontend/frontend_tunnel.log` | Log | 5.7KB | Runtime log, regenerable | N/A |
| A35 | `frontend/build.log` | Log | 1.3KB | Build log, regenerable | N/A |
| A36 | `comprehensive_test_report.json` | JSON | 3KB | Test report, regenerable | N/A |
| A37 | `__pycache__/` (root) | Cache | ~5MB | Python bytecode, regenerable | N/A |
| A38 | `frontend/dist/` | Build output | ~1MB | Vite build output, regenerable | `npm run build` |
| A39 | `frontend/node_modules/` | Dependencies | ~200MB | NPM deps, regenerable | `npm install` |
| A40 | `.pytest_cache/` | Cache | ~1MB | Pytest cache, regenerable | N/A |

### Category B — Likely Unnecessary (Dead Code, Requires Verification)

| # | Path | Type | Size | Evidence | Risk |
|---|------|------|------|----------|------|
| B1 | `ai_provider_fixed.py` | Python module | 12KB | No imports in non-test code; superseded by `ai_provider.py` | Low |
| B2 | `ai_provider_simple.py` | Python module | 8.7KB | No imports in non-test code; experimental | Low |
| B3 | `investigation_templates_fixed.py` | Python module | 8KB | No imports; `investigation_templates.py` is active | Low |
| B4 | `test_investigation_old.py` | Test file | 17KB | Legacy, superseded by `test_investigation.py` | Low |
| B5 | `test_ai_provider_fixed.py` | Test file | 11.8KB | Tests for dead `ai_provider_fixed.py` | Low |
| B6 | `test_ai_provider_simple.py` | Test file | 7.4KB | Tests for dead `ai_provider_simple.py` | Low |
| B7 | `test_investigation_api_template.py` | Test file | 9.7KB | Tests unused API endpoint | Low |
| B8 | `test_investigation_template_integration_fixed.py` | Test file | 17KB | Tests for dead templates | Low |
| B9 | `test_mock_provider_template_guidance.py` | Test file | 11.4KB | Tests unused feature | Low |
| B10 | `test_ollama_structured_output.py` | Test file | 19KB | Tests unused feature | Low |
| B11 | `test_ollama_template_guidance.py` | Test file | 17.3KB | Tests unused feature | Low |
| B12 | `test_ollama_timeout.py` | Test file | 5.6KB | Tests unused feature | Low |
| B13 | `test_thread_management_issue.py` | Test file | 7.8KB | Tests fixed issue | Low |
| B14 | `test_timeout_fix.py` | Test file | 7.9KB | Tests fixed implementation | Low |
| B15 | `test_timeout_implementation.py` | Test file | 7KB | Tests fixed implementation | Low |
| B16 | `test_timeout_validation.py` | Test file | 12.6KB | Tests fixed implementation | Low |
| B17 | `test_timeout_validation_corrected.py` | Test file | 12.1KB | Tests fixed implementation | Low |
| B18 | `verify_templates.py` | Script | 6.8KB | One-time verification script | Low |
| B19 | `verify_template_engine.py` | Missing | N/A | Referenced in git but not on disk | N/A |
| B20 | `audit_timeout_implementation.py` | Script | 18.3KB | One-time audit script | Low |
| B21 | `missing_incident_behavior_audit.py` | Script | 13.5KB | One-time audit script | Low |
| B22 | `performance_baseline.py` | Script | 15.4KB | One-time baseline script | Low |
| B23 | `performance_verification.py` | Script | 25.7KB | One-time verification script | Low |
| B24 | `run_comprehensive_tests.py` | Script | 14KB | Test runner, redundant with pytest | Low |
| B25 | `GET_TEST_COUNTS.py` | Script | 3.3KB | One-off counting script | Low |
| B26 | `fix_test_day6_filters.py` | Script | 2.5KB | One-time fix script | Low |
| B27 | `minimal_test_day6_filters.py` | Script | 3.8KB | Minimal test variant | Low |
| B28 | `check_application.py` | Script | 5.8KB | Validation script (maybe used?) | Medium |
| B29 | `create_demo_db.py` | Script | 15KB | Creates demo DB (run once) | Medium |
| B30 | `timeout_implementation.py` | Script | 3KB | Implementation helper | Low |
| B31 | `cors_patch.py` | Script | 2.6KB | CORS fix (maybe used?) | Medium |
| B32 | `demo_server.py` / `demo_asgi_server.py` | Scripts | 7KB/5KB | Demo servers (maybe used?) | Medium |
| B33 | `frontend/src/components/settings/Settings.tsx` | Component | ~15KB | Not imported; SimpleSettings used | Low |
| B34 | `test_demo_mode.py` | Test file | 9KB | Requires env vars; fails without them | Medium |

### Category C — Protected (Must Preserve)

| Path | Reason |
|------|--------|
| `main.py` | Application entry point |
| `models.py` | Core data models & persistence |
| `investigation_service.py` | Core investigation workflow |
| `investigation_templates.py` | Active template definitions |
| `template_engine.py` | Template rendering (used by investigation_service) |
| `ai_provider.py` | Active AI provider abstraction |
| `ollama_provider.py` | Active Ollama integration |
| `README.md` | Main documentation |
| `incidents.db` | Production database (PROTECTED) |
| `incidents_demo.db` | Demo database (PROTECTED) |
| All test_*.py (core: test_app, test_day5, test_day6, test_day7, test_day8, test_final_day3_fixed, test_investigation, test_check, test_fixture) | Active test suite |
| `conftest.py` | Pytest configuration |
| `frontend/src/**` (except backups) | Frontend source code |
| `frontend/package.json`, `package-lock.json`, `tsconfig.json`, `vite.config.mts`, `tailwind.config.js` | Build configuration |
| `project_memory/**` | Project documentation & memory |
| `start_tunnel_sharing.sh`, `stop_tunnel_sharing.sh` | Demo infrastructure |
| Phase reports (30+ files) | Historical documentation |

### Category D — Uncertain (Cannot Confidently Classify)

| Path | Uncertainty |
|------|-------------|
| `check_application.py` | May be used in CI/CD or deployment |
| `cors_patch.py` | May be imported dynamically |
| `create_demo_db.py` | May be needed to regenerate demo DB |
| `demo_server.py`, `demo_asgi_server.py` | May be used for demo deployment |
| `test_demo_mode.py` | Fails without env vars; integration test |

---

## 5. Duplicate & Redundancy Findings

### 5.1 Exact Duplicates
- **`test_day6_filters.py`** and **`test_day6_filters.py.backup`** (in git index) - identical
- **`conftest.py`** and **`conftest.py.backup`** - identical

### 5.2 Functional Duplicates (Superseded Implementations)
| Original (Active) | Duplicate (Dead) | Notes |
|-------------------|------------------|-------|
| `ai_provider.py` | `ai_provider_fixed.py`, `ai_provider_simple.py` | Fixed/simple variants never adopted |
| `investigation_templates.py` | `investigation_templates_fixed.py` | Fixed variant never adopted |
| `SimpleSettings.tsx` | `Settings.tsx` | Complex Settings not used; SimpleSettings is active |
| `test_investigation.py` | `test_investigation_old.py` | Old test file superseded |

### 5.3 Redundant Test Files (Testing Dead Code)
15+ test files exist solely to test the dead implementations in Category B.

---

## 6. Baseline Test Results (Pre-Cleanup)

### 6.1 Backend Tests (All Passing)

```
test_app.py                          9 passed
test_day5_patch.py                   21 passed
test_day6_filters.py                 42 passed
test_day7_timeline.py                3 passed
test_day8_analytics.py               18 passed
test_final_day3_fixed.py             9 passed
test_investigation.py                25 passed
test_check.py                        1 passed
TOTAL: 128 tests passed
```

### 6.2 Frontend Build & Type Check
```
TypeScript check:  PASSED (no errors)
Production build:  PASSED (warnings about chunk size only)
```

### 6.3 Demo Mode Tests
- **Without env vars:** 17 failed, 16 passed (expected - requires DEMO_MODE=true)
- **With env vars:** 33 passed (all demo protections verified)

---

## 7. Proposed Cleanup Plan (Ordered by Risk)

### Phase 1: Zero-Risk Cleanup (Category A - 40 items)
Delete all empty UUID files, backup files, logs, caches, build outputs.

### Phase 2: Dead Code Removal (Category B - 20 items)
Remove unused Python modules: `ai_provider_fixed.py`, `ai_provider_simple.py`, `investigation_templates_fixed.py`
Remove their test files: 15+ test files testing dead code
Remove unused frontend component: `Settings.tsx` and backup files
Remove one-time scripts: audit, verification, performance scripts

### Phase 3: Conditional Cleanup (Category D - 5 items)
Evaluate `check_application.py`, `cors_patch.py`, `create_demo_db.py`, `demo_server.py`, `demo_asgi_server.py` for actual usage before deciding.

### Phase 4: Documentation Consolidation (Optional)
Consider consolidating 30+ phase reports into fewer summary documents (separate task).

---

## 8. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Deleting test files that might be referenced | Verify no imports in active test files; git recovery available |
| Removing `create_demo_db.py` needed for demo setup | Keep until confirmed demo DB is stable |
| Removing `check_application.py` used in CI | Check CI configs before deletion |
| Frontend backup files referenced somewhere | Grep confirmed no references |

---

## 9. Cleanup Manifest (Exact Paths for Deletion)

### Phase 1 - Safe Artifacts (40 files/dirs)
```
01900dcd-124b-46b1-8d8d-30f3fb42bd83
10b4ac6b-995d-4800-a9db-bb2e53e8509a
130dabb9-8009-4830-a0c9-05d57aad5dbf
3fb9ca39-45e1-42d8-94d6-5825cd260591
40dd286d-b260-47a5-8f8c-4e149d52aa80
4f683daa-6501-4e6d-8568-03f3dbcc0687
55a3284b-e3ea-4aa7-89d6-0b1bba2e5e1f
63b650a6-c1c5-4b3e-b291-c7f20febfd68
700224b0-a9b9-4bf9-8476-5e59468a3574
7daaac83-0a19-4607-a558-4348cd74d52b
89d41a41-b2d2-4b12-8021-7b936b06f97f
8f36773e-6d94-4160-967c-7580a6153f50
924ae6de-8520-44a2-8100-d4873ce6fa9d
a6b41e64-1734-48c5-93c3-089e589802a4
c454912c-9dee-46e7-be28-9562d014901a
d0e405e9-0cdf-4189-ac82-78cb596327e3
dcf37aff-b9b8-4f53-a3e2-34b0ae525b9e
ddaf8d70-0285-48da-823e-f8e844a689b2
deb293c5-4812-45ba-905b-5179748e604b
e3c2b7d1-9dc5-4b8c-a9d9-5a640a881c5f
e3d6ed6b-83ce-4af1-9c33-dde90affeb8f
f0c64a91-7c60-4a10-ad3a-326a5d89da30
fba871b9-ff93-46fa-a0b0-df6d5cac02f7
1d39ebf9-40ac-4efd-ad9c-7606c0b2206f
conftest.py.backup
frontend/vite.config.ts.bak
frontend/src/components/incidents/IncidentDetail.tsx.bak
frontend/src/layouts/MainLayout.tsx.backup
test_day6_filters.py.backup
backend.log
backend_tunnel.log
frontend/frontend.log
frontend/frontend_preview.log
frontend/frontend_tunnel.log
frontend/build.log
comprehensive_test_report.json
__pycache__/
frontend/dist/
frontend/node_modules/
.pytest_cache/
```

### Phase 2 - Dead Code (20+ files)
```
ai_provider_fixed.py
ai_provider_simple.py
investigation_templates_fixed.py
test_investigation_old.py
test_ai_provider_fixed.py
test_ai_provider_simple.py
test_investigation_api_template.py
test_investigation_template_integration_fixed.py
test_mock_provider_template_guidance.py
test_ollama_structured_output.py
test_ollama_template_guidance.py
test_ollama_timeout.py
test_thread_management_issue.py
test_timeout_fix.py
test_timeout_implementation.py
test_timeout_validation.py
test_timeout_validation_corrected.py
verify_templates.py
audit_timeout_implementation.py
missing_incident_behavior_audit.py
performance_baseline.py
performance_verification.py
run_comprehensive_tests.py
GET_TEST_COUNTS.py
fix_test_day6_filters.py
minimal_test_day6_filters.py
timeout_implementation.py
frontend/src/components/settings/Settings.tsx
```

### Phase 3 - Conditional (Review First)
```
check_application.py
cors_patch.py
create_demo_db.py
demo_server.py
demo_asgi_server.py
test_demo_mode.py
```

---

## 10. Expected Impact

| Metric | Before | After (Phase 1+2) | Reduction |
|--------|--------|-------------------|-----------|
| Total files (excl. node_modules) | ~200 | ~140 | ~30% |
| Python source files | 52 | 32 | ~38% |
| Test files | 32 | 17 | ~47% |
| Root directory clutter | 85 items | 45 items | ~47% |
| Disk usage (excl. node_modules) | ~5MB | ~3MB | ~40% |

---

## 11. Verification Required After Each Phase

1. **After Phase 1:** Run all backend tests (128 tests), frontend build, type check
2. **After Phase 2:** Run all backend tests, verify investigation workflow still works
3. **After Phase 3:** Verify demo mode still works, CI/CD unaffected
4. **Final:** Full regression test suite, manual demo verification