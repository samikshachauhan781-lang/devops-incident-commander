#!/bin/bash
# start_tunnel_sharing.sh
# Starts backend + frontend + Cloudflare tunnels for temporary DEMO sharing
# Run from project root: /Users/samiksha/Desktop/devops-incident-commander

set -e

PROJECT_ROOT="/Users/samiksha/Desktop/devops-incident-commander"
BACKEND_PORT=8000
FRONTEND_PREVIEW_PORT=4173
TUNNEL_TIMEOUT=60  # seconds to wait for tunnel URL

echo "🚀 Starting DevOps Incident Commander DEMO Tunnel Sharing"
echo "========================================================="
echo ""

# Check cloudflared
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared not installed. Run: brew install cloudflared"
    exit 1
fi

# Check virtual environment
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "❌ Virtual environment not found at $PROJECT_ROOT/.venv"
    exit 1
fi

# Check demo database exists
if [ ! -f "$PROJECT_ROOT/incidents_demo.db" ]; then
    echo "❌ Demo database not found. Run: python3 create_demo_db.py"
    exit 1
fi

# Activate venv
source "$PROJECT_ROOT/.venv/bin/activate"

# Track PIDs for cleanup
BACKEND_PID=""
BACKEND_TUNNEL_PID=""
FRONTEND_PREVIEW_PID=""
FRONTEND_TUNNEL_PID=""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down demo..."

    # Kill specific tracked processes
    [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null && echo "  ✅ Backend stopped"
    [ -n "$BACKEND_TUNNEL_PID" ] && kill "$BACKEND_TUNNEL_PID" 2>/dev/null && echo "  ✅ Backend tunnel stopped"
    [ -n "$FRONTEND_PREVIEW_PID" ] && kill "$FRONTEND_PREVIEW_PID" 2>/dev/null && echo "  ✅ Frontend preview stopped"
    [ -n "$FRONTEND_TUNNEL_PID" ] && kill "$FRONTEND_TUNNEL_PID" 2>/dev/null && echo "  ✅ Frontend tunnel stopped"

    echo "✅ Cleanup complete"
}
trap cleanup EXIT INT TERM

# Function to extract tunnel URL from cloudflared log
# Waits for the actual URL line (not the "Requesting..." message)
wait_for_tunnel_url() {
    local log_file="$1"
    local label="$2"
    local timeout="$TUNNEL_TIMEOUT"
    local url=""

    echo "⏳ Waiting for $label tunnel URL (timeout: ${timeout}s)..."

    for ((i=1; i<=timeout; i++)); do
        # Check if cloudflared process is still alive (macOS compatible)
        if [ -n "$BACKEND_TUNNEL_PID" ] && ! ps -p "$BACKEND_TUNNEL_PID" >/dev/null 2>&1; then
            echo "❌ $label cloudflared process died unexpectedly"
            echo "--- Recent $label tunnel log ---"
            tail -30 "$log_file" 2>/dev/null || echo "(no log file)"
            return 1
        fi
        if [ -n "$FRONTEND_TUNNEL_PID" ] && ! ps -p "$FRONTEND_TUNNEL_PID" >/dev/null 2>&1; then
            echo "❌ $label cloudflared process died unexpectedly"
            echo "--- Recent $label tunnel log ---"
            tail -30 "$log_file" 2>/dev/null || echo "(no log file)"
            return 1
        fi

        # Look for the actual URL line pattern (inside the box drawing)
        if [ -f "$log_file" ]; then
            url=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$log_file" 2>/dev/null | head -1)
            if [ -n "$url" ]; then
                echo "✅ $label tunnel: $url"
                echo "$url"
                return 0
            fi
        fi

        sleep 1
    done

    echo "❌ Timeout waiting for $label tunnel URL after ${timeout}s"
    echo "--- Recent $label tunnel log ---"
    tail -50 "$log_file" 2>/dev/null || echo "(no log file)"
    return 1
}

# ------------------------------------------------------------------
# 1. Start Backend in DEMO MODE
# ------------------------------------------------------------------
echo "📦 Starting FastAPI backend in DEMO MODE on port $BACKEND_PORT..."
cd "$PROJECT_ROOT"
DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db .venv/bin/uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT > backend.log 2>&1 &
BACKEND_PID=$!
sleep 3

# Verify backend
if curl -s "http://localhost:$BACKEND_PORT/health" | grep -q "healthy"; then
    echo "✅ Backend healthy (demo mode)"
else
    echo "❌ Backend failed to start. Check backend.log"
    cat backend.log
    exit 1
fi

# ------------------------------------------------------------------
# 2. Start Cloudflare Tunnel for Backend
# ------------------------------------------------------------------
echo "🌐 Starting Cloudflare Tunnel for backend..."
rm -f backend_tunnel.log
cloudflared tunnel --url "http://localhost:$BACKEND_PORT" --no-autoupdate > backend_tunnel.log 2>&1 &
BACKEND_TUNNEL_PID=$!

BACKEND_TUNNEL_URL=$(wait_for_tunnel_url "backend_tunnel.log" "backend") || exit 1

# ------------------------------------------------------------------
# 3. Build Frontend with Backend Tunnel URL
# ------------------------------------------------------------------
echo "🏗️  Building frontend with API URL: $BACKEND_TUNNEL_URL"
cd "$PROJECT_ROOT/frontend"
VITE_API_BASE_URL="$BACKEND_TUNNEL_URL" npm run build > build.log 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed. Check build.log"
    cat build.log
    exit 1
fi
echo "✅ Frontend built successfully"

# ------------------------------------------------------------------
# 4. Start Preview Server for Built Frontend
# ------------------------------------------------------------------
echo "📦 Starting frontend preview server on port $FRONTEND_PREVIEW_PORT..."
npx vite preview --port $FRONTEND_PREVIEW_PORT --host 0.0.0.0 > frontend_preview.log 2>&1 &
FRONTEND_PREVIEW_PID=$!
sleep 3

# Verify frontend preview
if curl -s "http://localhost:$FRONTEND_PREVIEW_PORT" | grep -q "DevOps Incident Commander"; then
    echo "✅ Frontend preview running"
else
    echo "❌ Frontend preview failed. Check frontend_preview.log"
    cat frontend_preview.log
    exit 1
fi

# ------------------------------------------------------------------
# 5. Start Cloudflare Tunnel for Frontend
# ------------------------------------------------------------------
echo "🌐 Starting Cloudflare Tunnel for frontend..."
rm -f frontend_tunnel.log
cloudflared tunnel --url "http://localhost:$FRONTEND_PREVIEW_PORT" --no-autoupdate > frontend_tunnel.log 2>&1 &
FRONTEND_TUNNEL_PID=$!

FRONTEND_TUNNEL_URL=$(wait_for_tunnel_url "frontend_tunnel.log" "frontend") || exit 1

# ------------------------------------------------------------------
# 6. Restart Backend with Correct CORS Origin (DEMO_FRONTEND_ORIGIN)
# ------------------------------------------------------------------
echo "🔄 Restarting backend with DEMO_FRONTEND_ORIGIN=$FRONTEND_TUNNEL_URL..."
kill "$BACKEND_PID" 2>/dev/null
sleep 1
DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db DEMO_FRONTEND_ORIGIN="$FRONTEND_TUNNEL_URL" .venv/bin/uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT > backend.log 2>&1 &
BACKEND_PID=$!
sleep 2

# Verify backend still healthy
if curl -s "http://localhost:$BACKEND_PORT/health" | grep -q "healthy"; then
    echo "✅ Backend restarted with correct CORS"
else
    echo "❌ Backend failed to restart. Check backend.log"
    cat backend.log
    exit 1
fi

# ------------------------------------------------------------------
# 7. Display Final URLs
# ------------------------------------------------------------------
echo ""
echo "══════════════════════════════════════════════════════════════"
echo "🎉 DEMO SHARING READY - Send this URL to your reviewer:"
echo "══════════════════════════════════════════════════════════════"
echo ""
echo "📱 FRONTEND (Reviewer Dashboard - READ ONLY):"
echo "   $FRONTEND_TUNNEL_URL"
echo ""
echo "🔧 BACKEND API (Direct API Access - READ ONLY):"
echo "   $BACKEND_TUNNEL_URL"
echo "   API Docs: DISABLED in demo mode"
echo ""
echo "══════════════════════════════════════════════════════════════"
echo "⚠️  DEMO MODE PROTECTIONS ACTIVE:"
echo "   • Separate synthetic database (10 demo incidents)"
echo "   • Read-only: POST/PUT/PATCH/DELETE blocked with 403"
echo "   • API docs (/docs, /redoc) disabled"
echo "   • Investigation returns mock data (no external AI calls)"
echo "   • CORS restricted to: $FRONTEND_TUNNEL_URL"
echo "   • Original database (incidents.db) untouched"
echo "══════════════════════════════════════════════════════════════"
echo ""
echo "📋 Logs:"
echo "   Backend:        tail -f $PROJECT_ROOT/backend.log"
echo "   Backend Tunnel: tail -f $PROJECT_ROOT/backend_tunnel.log"
echo "   Frontend Build: cat $PROJECT_ROOT/frontend/build.log"
echo "   Frontend Preview: tail -f $PROJECT_ROOT/frontend/frontend_preview.log"
echo "   Frontend Tunnel: tail -f $PROJECT_ROOT/frontend/frontend_tunnel.log"
echo ""
echo "Press Ctrl+C to STOP sharing and revoke access"
echo "══════════════════════════════════════════════════════════════"

# Keep script running
wait