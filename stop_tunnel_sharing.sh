#!/bin/bash
# stop_tunnel_sharing.sh
# Stops all demo tunnel sharing processes
# Does NOT modify main.py (no CORS patch to revert anymore)

set -e

echo "🛑 Stopping Demo Tunnel Sharing..."
echo "==============================="

# Kill cloudflared tunnels started by our script (more specific)
echo "Stopping cloudflared tunnels..."
pkill -f "cloudflared tunnel --url http://localhost:8000" 2>/dev/null && echo "  ✅ Backend tunnel stopped" || echo "  ℹ️  No backend tunnel found"
pkill -f "cloudflared tunnel --url http://localhost:4173" 2>/dev/null && echo "  ✅ Frontend tunnel stopped" || echo "  ℹ️  No frontend tunnel found"

# Kill uvicorn backend started by our script
echo "Stopping demo backend..."
pkill -f "uvicorn main:app --host 0.0.0.0 --port 8000" 2>/dev/null && echo "  ✅ Demo backend stopped" || echo "  ℹ️  No demo backend found"

# Kill vite preview
echo "Stopping frontend preview..."
pkill -f "vite preview --port 4173" 2>/dev/null && echo "  ✅ Frontend preview stopped" || echo "  ℹ️  No preview found"

# Clean up log files (optional)
echo ""
read -p "Delete log files? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f /Users/samiksha/Desktop/devops-incident-commander/backend.log
    rm -f /Users/samiksha/Desktop/devops-incident-commander/backend_tunnel.log
    rm -f /Users/samiksha/Desktop/devops-incident-commander/frontend/build.log
    rm -f /Users/samiksha/Desktop/devops-incident-commander/frontend/frontend_preview.log
    rm -f /Users/samiksha/Desktop/devops-incident-commander/frontend/frontend_tunnel.log
    echo "  ✅ Log files deleted"
fi

echo ""
echo "✅ Demo tunnel sharing stopped. Public access revoked."
echo "   Original local configuration unchanged."
echo "   Original database (incidents.db) was never modified."