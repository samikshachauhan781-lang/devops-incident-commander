#!/bin/bash

# Start the React frontend
backend_url="http://localhost:8000"

# Check if backend is running
if curl -s "$backend_url/health" > /dev/null; then
    echo "✅ Backend is running at $backend_url"
else
    echo "❌ Backend is not running at $backend_url"
    echo "Please start the backend using:"
    echo "cd /Users/samiksha/Desktop/devops-incident-commander"
    echo "npm run dev"
    exit 1
fi

# Start the frontend in development mode
npx vite dev