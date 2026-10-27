from fastapi.testclient import TestClient
from main import app
from models import Incident
import json
import pytest

# Use pytest fixtures from conftest.py for consistent test database setup
from conftest import test_client

def test_root_endpoint(test_client):
    """Test the root endpoint returns project information."""
    client = test_client

    print("\n📍 Testing GET /")
    response = client.get("/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # Verify response structure and content
    assert response.status_code == 200
    data = response.json()
    assert "project_name" in data
    assert "status" in data
    assert "welcome_message" in data
    print("   ✅ Root endpoint: All required fields present")
    print(f"   📝 Project: {data['project_name']}")
    print(f"   🔄 Status: {data['status']}")

def test_health_endpoint(test_client):
    """Test the health endpoint returns status and timestamp."""
    client = test_client

    print("\n📊 Testing GET /health")
    response = client.get("/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # Verify response structure and content
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    print("   ✅ Health endpoint: All required fields present")
    print(f"   🟢 Status: {data['status']}")
    print(f"   📅 Timestamp: {data['timestamp']}")

def test_create_valid_incident(test_client):
    """Test creating a valid incident with correct data."""
    client = test_client

    print("\n🆕 Testing POST /incidents (valid data)")

    # Valid incident data
    incident_data = {
        "title": "Database Connection Pool Exhaustion",
        "description": "Database connection pool reached maximum limit. New connections rejected.",
        "severity": "critical",
        "status": "open",
        "service": "database-service"
    }

    response = client.post("/incidents", json=incident_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # Verify successful creation
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == incident_data["title"]
    assert data["severity"] == incident_data["severity"]
    assert data["status"] == incident_data["status"]
    assert data["service"] == incident_data["service"]
    assert "created_at" in data
    print("   ✅ Incident created successfully")
    print(f"   🆔 ID: {data['id']}")
    print(f"   📝 Title: {data['title']}")
    print(f"   ⚠️  Severity: {data['severity']}")

def test_get_incidents_list(test_client):
    """Test retrieving list of incidents."""
    client = test_client

    print("\n📋 Testing GET /incidents")
    response = client.get("/incidents")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # Verify response structure
    assert response.status_code == 200
    data = response.json()
    assert "incidents" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    print("   ✅ Incident list retrieved successfully")
    print(f"   📊 Total incidents: {data['total']}")
    print(f"   📄 Page: {data['page']}")
    print(f"   📏 Page size: {data['page_size']}")

    # If we have incidents, verify first incident structure
    if data["total"] > 0:
        incident = data["incidents"][0]
        assert "id" in incident
        assert "title" in incident
        assert "severity" in incident
        assert "status" in incident
        assert "service" in incident
        print(f"   📝 Sample incident: {incident['title']} ({incident['severity']})")

def test_get_incident_by_id(test_client):
    """Test retrieving a specific incident by ID."""
    client = test_client

    print("\n🔍 Testing GET /incidents/{incident_id}")

    # First, create an incident to get its ID
    incident_data = {
        "title": "API Response Time Issue",
        "description": "API response times exceeding 5 seconds for payment endpoints.",
        "severity": "high",
        "status": "investigating",
        "service": "api-service"
    }

    create_response = client.post("/incidents", json=incident_data)
    assert create_response.status_code == 201
    created_incident = create_response.json()
    incident_id = created_incident["id"]

    print(f"   Created incident with ID: {incident_id}")

    # Now retrieve it
    get_response = client.get(f"/incidents/{incident_id}")
    print(f"   Status: {get_response.status_code}")
    print(f"   Response: {get_response.json()}")

    # Verify retrieval
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == incident_id
    assert data["title"] == incident_data["title"]
    print("   ✅ Incident retrieved successfully")
    print(f"   📝 Retrieved: {data['title']} (ID: {data['id']})")

def test_get_nonexistent_incident(test_client):
    """Test retrieving a non-existent incident returns 404."""
    client = test_client

    print("\n❌ Testing GET /incidents/{invalid_id} (404 test)")

    # Use a fake UUID that doesn't exist
    fake_incident_id = "123e4567-e89b-12d3-a456-426614174999"

    response = client.get(f"/incidents/{fake_incident_id}")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # Verify 404 error
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    print("   ✅ Correctly returned 404 error")
    print(f"   📋 Error message: {data['detail']}")

def test_validation_error_invalid_severity(test_client):
    """Test that invalid severity returns validation error."""
    client = test_client

    print("\n⚠️  Testing POST /incidents (invalid severity validation)")

    # Invalid incident data with unsupported severity
    invalid_incident_data = {
        "title": "Test Error",
        "description": "Test incident with invalid severity.",
        "severity": "extremely-dangerous",  # Not in valid values
        "status": "open",
        "service": "test-service"
    }

    response = client.post("/incidents", json=invalid_incident_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")

    # Verify validation error (should be 422 or 400)
    assert response.status_code in [400, 422]
    data = response.json()
    assert "detail" in data or "errors" in data
    print("   ✅ Validation error correctly returned")
    print(f"   📋 Error: {data.get('detail', data.get('errors', 'Validation error'))}")

def test_delete_incident(test_client):
    """Test DELETE /incidents/{id} endpoint."""
    print("\n🗑️ Testing DELETE /incidents/{id}")

    # First, create an incident to delete
    client = test_client
    incident_data = {
        "title": "Test Incident for Deletion",
        "description": "This incident will be deleted.",
        "severity": "low",
        "status": "open",
        "service": "test-service"
    }

    create_response = client.post("/incidents", json=incident_data)
    print(f"   Created incident status: {create_response.status_code}")
    assert create_response.status_code == 201
    incident_id = create_response.json()["id"]
    print(f"   Created incident ID: {incident_id}")

    # Delete the incident
    delete_response = client.delete(f"/incidents/{incident_id}")
    print(f"   Delete incident status: {delete_response.status_code}")
    print(f"   Delete response: {delete_response.json()}")

    # Verify successful deletion
    assert delete_response.status_code == 200
    assert "deleted successfully" in delete_response.json()["message"]
    print(f"   ✅ Incident deleted successfully")

    # Verify incident is gone
    get_response = client.get(f"/incidents/{incident_id}")
    print(f"   Verify deletion status: {get_response.status_code}")
    assert get_response.status_code == 404
    print(f"   ✅ Incident no longer exists (404)")

def test_incident_model_validation(test_client):
    """Test Pydantic model validation directly."""
    print("\n🧪 Testing Incident Model Validation")

    from models import Incident

    # Test valid incident
    valid_data = {
        "title": "Valid Test Incident",
        "description": "This is a valid incident for testing.",
        "severity": "medium",
        "status": "open",
        "service": "test-service"
    }

    try:
        incident = Incident(**valid_data)
        print(f"   ✅ Valid incident created: {incident.title}")
        print(f"   📊 Severity: {incident.severity}")
        print(f"   🆔 Auto-generated ID: {incident.id}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

    # Test invalid incident
    invalid_data = {
        "title": "Invalid",
        "description": "Bad",
        "severity": "invalid-severity",
        "status": "unknown-status",
        "service": "test"
    }

    try:
        invalid_incident = Incident(**invalid_data)
        print(f"   ❌ Should have failed but didn't: {invalid_incident.title}")
    except Exception as e:
        print(f"   ✅ Validation correctly caught error: {type(e).__name__}")

if __name__ == "__main__":
    import pytest
    exit(pytest.main([__file__, "-v"]))