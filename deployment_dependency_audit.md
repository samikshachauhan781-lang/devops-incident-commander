# Deployment Dependency Audit: `cors_patch.py`, `demo_server.py`, `demo_asgi_server.py`

**Project:** DevOps Incident Commander
**Root:** `/Users/samiksha/Desktop/devops-incident-commander`
**Date:** 2026-10-26
**Audit Type:** Verification-only (no deletions)

---

## Executive Summary

| File | Classification | Rationale |
|------|----------------|-----------|
| `cors_patch.py` | **OBSOLETE** | Superseded by native CORS handling in `main.py` (lines 162-185). The `start_tunnel_sharing.sh` uses `DEMO_FRONTEND_ORIGIN` env var instead. |
| `demo_server.py` | **OBSOLETE** | Not used in current demo pipeline. `start_tunnel_sharing.sh` uses `npx vite preview` (Vite's built-in preview server) with proxy config. |
| `demo_asgi_server.py` | **OBSOLETE** | Not used in current demo pipeline. Same as above - `vite preview` + cloudflared is the actual deployment path. |

**All three files are conclusively obsolete.** None are referenced by any tracked/untracked project file, startup script, package.json script, or documentation.

---

## 1. Reference Search Results

### Global Search Across Entire Project

```bash
grep -r "cors_patch\|demo_server\|demo_asgi" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=__pycache__ --exclude-dir=.venv
```

**Results: ZERO references** in any:
- Python source files (`*.py`)
- Shell scripts (`*.sh`)
- Markdown documentation (`*.md`)
- Package manifests (`package.json`, `package-lock.json`)
- TypeScript/React source (`*.ts`, `*.tsx`)
- Configuration files (`vite.config.mts`, `tsconfig.json`, `tailwind.config.js`)

### Specific File Checks

| Check | Result |
|-------|--------|
| `start_tunnel_sharing.sh` references | Only `create_demo_db.py` (for DB creation) |
| `package.json` scripts | `dev`, `build`, `lint`, `preview` — no demo server scripts |
| `README.md` | Documents `uvicorn main:app` + `npm run dev` / `npm run build` only |
| `QUICK_REFERENCE_GUIDE.md` | Same as README |
| `vite.config.mts` | Proxy config for `/api` → `http://127.0.0.1:8000` in both `dev` and `preview` |
| `frontend/src/api/client.ts` | Uses `/api` base URL (proxied by Vite) |
| Project memory docs | No references to these three files |

---

## 2. Current Demo Deployment Pipeline (`start_tunnel_sharing.sh`)

### Actual Command Sequence Used Today

```bash
# 1. Start FastAPI backend in DEMO MODE
DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db .venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

# 2. Cloudflare tunnel for backend
cloudflared tunnel --url "http://localhost:8000"

# 3. Build frontend WITH backend tunnel URL as VITE_API_BASE_URL
VITE_API_BASE_URL="$BACKEND_TUNNEL_URL" npm run build

# 4. Start Vite preview server (serves frontend/dist + proxies /api)
npx vite preview --port 4173 --host 0.0.0.0

# 5. Cloudflare tunnel for frontend
cloudflared tunnel --url "http://localhost:4173"

# 6. Restart backend with DEMO_FRONTEND_ORIGIN=$FRONTEND_TUNNEL_URL
DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db DEMO_FRONTEND_ORIGIN="$FRONTEND_TUNNEL_URL" .venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
```

### Key Observations

1. **Frontend served by `vite preview`** — not `demo_server.py` or `demo_asgi_server.py`
2. **API proxying handled by Vite** — configured in `vite.config.mts` for both `dev` and `preview` modes
3. **CORS handled natively in `main.py`** — uses `DEMO_FRONTEND_ORIGIN` env var (lines 162-185)
4. **No Python HTTP server involved** — the entire demo stack is uvicorn + vite preview + cloudflared

---

## 3. Comparison: `demo_asgi_server.py` vs Current Approach

| Feature | `demo_asgi_server.py` | Current (`vite preview` + `uvicorn`) |
|---------|----------------------|--------------------------------------|
| **Static file serving** | Starlette `FileResponse` + manual MIME detection | Vite's optimized static server (esbuild/rolldown) |
| **SPA fallback (index.html)** | Manual path check → `FileResponse(index.html)` | Vite built-in SPA fallback |
| **`/api/*` proxying** | Custom `httpx.AsyncClient` proxy to `http://127.0.0.1:8000` | Vite dev server proxy (same config for dev & preview) |
| **Path rewriting** | Manual: `path[4:]` strips `/api` | Vite: `rewrite: (path) => path.replace(/^\/api/, '')` |
| **Error handling** | Custom 502/500/403 responses | Vite proxy error handling + FastAPI responses |
| **CORS** | Starlette `CORSMiddleware(allow_origins=['*'])` | FastAPI `CORSMiddleware` with `DEMO_FRONTEND_ORIGIN` |
| **HTTP/2 support** | Via uvicorn | Via uvicorn (FastAPI) |
| **Dependencies** | `httpx`, `starlette` (extra deps) | Zero extra deps (uses Vite + uvicorn already in project) |
| **Maintenance** | Custom code to maintain | Standard Vite feature |

### Critical Differences

1. **`demo_asgi_server.py` allows ALL methods in CORS** (`allow_methods=['*']`) — **incompatible with demo read-only protection** which blocks POST/PATCH/DELETE at FastAPI middleware level
2. **`demo_asgi_server.py` serves frontend AND proxies API** — current architecture separates concerns: Vite serves frontend, FastAPI serves API
3. **Current approach uses `DEMO_FRONTEND_ORIGIN` for precise CORS** — `demo_asgi_server.py` uses wildcard `*`

---

## 4. Frontend → Backend Connection in Current Deployment

### Development Mode (`npm run dev`)
- Vite dev server on port 3000
- Proxy: `/api` → `http://127.0.0.1:8000` (rewrites `/api` → `/`)
- Frontend axios client uses baseURL `/api`
- CORS: FastAPI allows `localhost:3000`, `localhost:3001`, `127.0.0.1:3000`, `127.0.0.1:3001`

### Production Preview (`npm run preview`)
- Vite preview server on port 4173
- Same proxy config as dev
- Frontend axios client uses baseURL `/api`
- CORS: FastAPI allows `localhost:3000`, `localhost:4173`, `127.0.0.1:3000`, `127.0.0.1:4173`

### Demo Mode with Tunnels
- Frontend built with `VITE_API_BASE_URL=$BACKEND_TUNNEL_URL` (but `src/api/client.ts` ignores it — uses `/api`)
- Vite preview serves built `dist/` on port 4173
- Cloudflare tunnel for frontend → `https://xxx.trycloudflare.com`
- Cloudflare tunnel for backend → `https://yyy.trycloudflare.com`
- Backend restarted with `DEMO_FRONTEND_ORIGIN=https://xxx.trycloudflare.com`
- FastAPI CORS allows only that specific origin, with `allow_methods=["GET", "HEAD", "OPTIONS"]`

### Key Finding: `VITE_API_BASE_URL` is NOT USED

```typescript
// frontend/src/api/client.ts
const API_BASE_URL = '/api';  // Hardcoded, ignores import.meta.env.VITE_API_BASE_URL
```

The `VITE_API_BASE_URL` injected during build is **unused**. The frontend relies entirely on Vite's proxy (`/api` → backend) in both dev and preview modes. In demo mode, the tunnel URLs handle the cross-origin routing.

---

## 5. CORS Configuration Analysis: `main.py` vs `cors_patch.py`

### Current `main.py` CORS (Lines 162-185)

```python
if DEMO_MODE:
    DEMO_FRONTEND_ORIGIN = os.getenv("DEMO_FRONTEND_ORIGIN", "")
    if DEMO_FRONTEND_ORIGIN:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[DEMO_FRONTEND_ORIGIN],  # Single specific origin
            allow_credentials=True,
            allow_methods=["GET", "HEAD", "OPTIONS"],  # Read-only!
            allow_headers=["*"],
        )
    else:
        # Localhost fallback for local demo testing
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://localhost:4173", "http://127.0.0.1:3000", "http://127.0.0.1:4173"],
            allow_credentials=True,
            allow_methods=["GET", "HEAD", "OPTIONS"],
            allow_headers=["*"],
        )
else:
    # Production: full methods allowed
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
        allow_credentials=True,
        allow_methods=["*"],  # All methods
        allow_headers=["*"],
    )
```

### `cors_patch.py` Behavior

```python
# Patches main.py to replace CORS with DynamicCORSMiddleware that:
# 1. Allows ANY localhost origin (http://localhost:*, http://127.0.0.1:*)
# 2. Allows ANY *.trycloudflare.com origin via regex
# 3. Allows ALL methods (GET, POST, PATCH, DELETE, etc.)
# 4. Injects CORS headers dynamically per-request
```

### Comparison

| Aspect | `main.py` (Current) | `cors_patch.py` (Obsolete) |
|--------|---------------------|----------------------------|
| **Origin matching** | Exact match via env var (`DEMO_FRONTEND_ORIGIN`) | Wildcard regex for `*.trycloudflare.com` + all localhost |
| **Methods in demo** | Read-only: `["GET", "HEAD", "OPTIONS"]` | **All methods: `["*"]`** |
| **Security** | ✅ Enforces read-only demo | ❌ **Breaks read-only protection** |
| **Maintenance** | Native, no source modification | Modifies `main.py` source at runtime |
| **Used by** | `start_tunnel_sharing.sh` (via env var) | **Nothing** |

### Verdict

`cors_patch.py` is **not only obsolete but actively harmful** if used — it would bypass the read-only middleware by allowing mutating methods through CORS. The current `main.py` implementation is superior: precise origin control + method restriction aligned with `ReadOnlyMiddleware`.

---

## 5. Development/Testing/Recovery Workflow Check

| Workflow | Uses `cors_patch.py`? | Uses `demo_server.py`? | Uses `demo_asgi_server.py`? |
|----------|----------------------|------------------------|----------------------------|
| Local dev (`npm run dev` + `uvicorn`) | No | No | No |
| Local preview (`npm run preview` + `uvicorn`) | No | No | No |
| Demo tunnel sharing (`start_tunnel_sharing.sh`) | No | No | No |
| CI/CD (pytest) | No | No | No |
| Database creation (`create_demo_db.py`) | No | No | No |
| Application validation (`check_application.py`) | No | No | No |
| Documentation references | No | No | No |

**Result:** Zero workflows depend on these files.

---

## 6. `/incidents` Blank Screen Status

### Current State: **UNVERIFIED** (Requires Browser Test)

**Evidence against regression:**
- All 184 backend tests pass, including `/incidents` endpoint returning demo data
- Frontend TypeScript strict check: PASS
- Frontend production build: PASS
- No frontend source files modified during cleanup
- `IncidentList.tsx` has proper loading/error/empty states
- `IncidentContext` correctly calls `incidentService.getIncidents()`
- `incidentService` uses `/api` base URL with axios
- Vite proxy config correct for both dev and preview

**Root cause hypothesis for blank screen (if it exists):**
1. Backend not running on port 8000 when frontend accessed
2. Vite proxy not working in production preview (but it's configured identically to dev)
3. CORS blocking requests (but demo mode sets precise `DEMO_FRONTEND_ORIGIN`)
4. Network timing issue between tunnel URLs

**Cannot claim fixed without manual browser verification.** The build succeeds and API tests pass, but blank-screen is a runtime integration issue requiring browser confirmation.

---

## 7. Deletion Proposals (For Future Approval)

### `cors_patch.py` — **DELETE**

**Recovery method:** `git checkout HEAD -- cors_patch.py` (tracked in git)
**Risk:** None — superseded by superior native implementation
**Impact:** Removes dangerous code that would break read-only demo if executed

### `demo_server.py` — **DELETE**

**Recovery method:** `git checkout HEAD -- demo_server.py` (tracked in git)
**Risk:** None — not used by any script
**Impact:** Removes ~150 lines of stdlib HTTP server code that duplicates `vite preview`

### `demo_asgi_server.py` — **DELETE**

**Recovery method:** `git checkout HEAD -- demo_asgi_server.py` (tracked in git)
**Risk:** None — not used by any script
**Impact:** Removes ~180 lines of Starlette/httpx code that duplicates `vite preview` + introduces security risk (wildcard CORS)

---

## 8. Final Classification

| File | Classification | Confidence | Action |
|------|----------------|------------|--------|
| `cors_patch.py` | **OBSOLETE** | 100% | Delete (with git recovery) |
| `demo_server.py` | **OBSOLETE** | 100% | Delete (with git recovery) |
| `demo_asgi_server.py` | **OBSOLETE** | 100% | Delete (with git recovery) |

**All three files are conclusively obsolete.** No references exist anywhere in the project. The current deployment uses `uvicorn main:app` + `vite preview` + `cloudflared` exclusively.

---

## 9. Verification Checklist

- [x] Searched all tracked files (git ls-files) — no references
- [x] Searched all untracked files (git status) — no references
- [x] Inspected `start_tunnel_sharing.sh` — uses `vite preview`, not demo servers
- [x] Inspected `package.json` — no demo server scripts
- [x] Inspected `README.md` / `QUICK_REFERENCE_GUIDE.md` — documents uvicorn + vite only
- [x] Compared `demo_asgi_server.py` vs `vite preview` proxy behavior — current approach superior
- [x] Verified frontend→backend connection via Vite proxy in dev/preview/demo modes
- [x] Analyzed CORS in `main.py` — native implementation superior to `cors_patch.py`
- [x] Checked all workflows — zero dependencies on these files
- [x] Confirmed `/incidents` blank screen status — UNVERIFIED (requires browser test)

---

**Report Status:** Complete — Ready for explicit approval to delete the three obsolete files.