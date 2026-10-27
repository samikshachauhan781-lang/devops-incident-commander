# How to Check Your DevOps Incident Commander Application

## Method 1: Using FastAPI TestClient (Python)

This is the method we just used:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
response = client.get("/")
print(response.json())
```

**Pros:** Fast, no server needed, good for testing
**Cons:** Requires Python

## Method 2: Using curl (Command Line)

Install curl if not already installed:

```bash
# On macOS (already installed):
curl http://127.0.0.1:8000/

# Or with Python uvicorn server:
cd ~/Desktop/devops-incident-commander
.venv/bin/uvicorn main:app --reload &
curl http://127.0.0.1:8000/health
```

Example responses:

Root endpoint:
```bash
$ curl http://127.0.0.1:8000/
{"project_name":"DevOps Incident Commander","status":"running","welcome_message":"Welcome to the Agentic AI-based incident investigation and response platform!"}
```

Health endpoint:
```bash
$ curl http://127.0.0.1:8000/health
{"status":"healthy","timestamp":"2026-10-13T05:39:00.194990+00:00"}
```

## Method 3: Using Web Browser

Open your browser and go to:
- `http://127.0.0.1:8000/` - Main page
- `http://127.0.0.1:8000/health` - Health check
- `http://127.0.0.1:8000/docs` - Interactive API documentation

## Method 4: Python Requests (for external testing)

```python
import requests

base_url = "http://127.0.0.1:8000"

# Test root endpoint
response = requests.get(f"{base_url}/")
print(response.json())

# Test health endpoint
response = requests.get(f"{base_url}/health")
print(response.json())
```

## Method 5: Using Postman

Import the OpenAPI specification from `http://127.0.0.1:8000/docs/openapi.json`

## Quick Check Commands

Save this as `check_app.sh`:

```bash
#!/bin/bash

cd ~/Desktop/devops-incident-commander

echo "🔍 Checking DevOps Incident Commander API"
echo "=" * 50

# Test with curl
response1=$(curl -s http://127.0.0.1:8000/)
response2=$(curl -s http://127.0.0.1:8000/health)

echo "Root endpoint: $response1"
echo "Health endpoint: $response2"

echo "=" * 50
echo "✅ Application check complete!"
```

Then run: `bash check_app.sh`

## Expected Response Format

**Root endpoint (GET /):**
```json
{
  "project_name": "DevOps Incident Commander",
  "status": "running",
  "welcome_message": "Welcome to the Agentic AI-based incident investigation and response platform!"
}
```

**Health endpoint (GET /health):**
```json
{
  "status": "healthy",
  "timestamp": "2026-10-13T05:39:00.194990+00:00"
}
```

## Common Issues and Solutions

1. **Connection refused**: Make sure uvicorn server is running
2. **Wrong port**: Check if uvicorn is using port 8000
3. **CORS issues**: Check if requests are from same origin
4. **JSON parsing errors**: Verify API is returning valid JSON

## Automation Script

`test_application.py` (complete test suite):

```python
from fastapi.testclient import TestClient
from main import app
import json
from datetime import datetime

client = TestClient(app)

def test_all_endpoints():
    # Test each endpoint
    endpoints = [
        ("/", ["project_name", "status", "welcome_message"]),
        ("/health", ["status", "timestamp"])
    ]

    for endpoint, expected_fields in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200
        data = response.json()

        for field in expected_fields:
            assert field in data, f"Missing field {field} in {endpoint}"

        print(f"✅ {endpoint}: {len(data)} fields found")

    print("\n🎉 All application checks passed!")

if __name__ == "__main__":
    test_all_endpoints()
```

## Conclusion

You now have multiple ways to check your application:
- **Quick**: Use curl commands
- **Automated**: Use Python test scripts
- **Visual**: Use web browser for documentation
- **Comprehensive**: Use full test suites

Choose the method that best fits your testing needs!
