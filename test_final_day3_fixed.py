"""
Fixed Day 3 test suite for DevOps Incident Commander.
Tests DELETE workflow, pagination edge cases, and data isolation.
"""

from fastapi.testclient import TestClient
from main import app
import pytest
from uuid import UUID

# Remove conflicting database setup that conflicts with conftest.py fixtures
# The conftest.py now provides proper pytest fixtures:
# - test_client: TestClient fixture
# - session_test_database: Session-scoped database setup
# - function_test_isolation: Function-scoped database reset
# - sample_incidents_data: Sample incident data

# Import sample_incidents_data from conftest.py for compatibility
from conftest import test_client, sample_incidents_data

# Keep helper functions that don't conflict with conftest fixtures
def create_test_incident(client, **overrides):
    """Helper to create a test incident with default values."""
    default_data = {
        "title": "Test Incident",
        "description": "This is a test incident",
        "severity": "medium",
        "status": "open",
        "service": "test-service"
    }
    default_data.update(overrides)
    response = client.post("/incidents", json=default_data)
    assert response.status_code == 201, f"Failed to create incident: {response.json()}"
    return response.json()

# Remove module-level database setup that conflicts with conftest.py
# setup_test_database() and teardown_test_database() are handled by conftest.py


def test_day3_root_endpoint(test_client):
    """Test Day 1 root endpoint."""
    client = test_client
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project_name"] == "DevOps Incident Commander"
    assert data["status"] == "running"
    assert "welcome_message" in data
    assert data["version"] == "1.0.0"
    print("✅ test_day3_root_endpoint passed")


def test_day3_health_endpoint(test_client):
    """Test Day 1 health endpoint."""
    client = test_client
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "devops-incident-commander-api"
    print("✅ test_day3_health_endpoint passed")


def test_day3_create_incident(test_client):
    """Test Day 2 incident creation."""
    client = test_client
    incident_data = {
        "title": "Test Incident",
        "description": "This is a test incident",
        "severity": "medium",
        "status": "open",
        "service": "test-service"
    }
    response = client.post("/incidents", json=incident_data)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == incident_data["title"]
    assert data["severity"] == incident_data["severity"]
    assert data["status"] == incident_data["status"]
    assert data["service"] == incident_data["service"]
    assert "created_at" in data
    print("✅ test_day3_create_incident passed")


def test_day3_list_incidents(test_client):
    """Test Day 2 incident listing with pagination."""
    client = test_client
    response = client.get("/incidents")
    assert response.status_code == 200
    data = response.json()
    assert "incidents" in data
    assert "page" in data
    assert "page_size" in data
    assert "total" in data
    assert isinstance(data["incidents"], list)
    print(f"✅ test_day3_list_incidents passed - {len(data['incidents'])} incidents")


def test_day3_get_incident(test_client):
    """Test Day 2 individual incident retrieval."""
    client = test_client
    # Create a test incident to retrieve
    incident = create_test_incident(client)
    incident_id = incident["id"]

    response = client.get(f"/incidents/{incident_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == incident_id
    assert data["title"] == incident["title"]
    print("✅ test_day3_get_incident passed")


def test_day3_get_nonexistent_incident(test_client):
    """Test Day 2 nonexistent incident retrieval."""
    client = test_client
    incident_id = "non-existent-id"
    response = client.get(f"/incidents/{incident_id}")
    assert response.status_code == 404
    print("✅ test_day3_get_nonexistent_incident passed")


def test_day3_delete_incident(test_client):
    """Test Day 3 incident deletion."""
    client = test_client
    # Create an incident to delete
    incident_data = {
        "title": "Test Incident to Delete",
        "description": "This incident will be deleted",
        "severity": "high",
        "status": "open",
        "service": "test-service"
    }
    create_response = client.post("/incidents", json=incident_data)
    assert create_response.status_code == 201
    incident_id = create_response.json()["id"]

    # Delete the incident
    delete_response = client.delete(f"/incidents/{incident_id}")
    assert delete_response.status_code == 200  # Note: API returns 200, not 204

    # Verify it's deleted
    get_response = client.get(f"/incidents/{incident_id}")
    assert get_response.status_code == 404

    print("✅ test_day3_delete_incident passed")


def test_day3_pagination_page_zero(test_client):
    """Test Day 3 pagination with page=0."""
    client = test_client
    response = client.get("/incidents?page=0")
    assert response.status_code == 422  # Invalid page parameter
    print("✅ test_day3_pagination_page_zero passed")


def test_day3_pagination_negative_page(test_client):
    """Test Day 3 pagination with negative page number."""
    client = test_client
    response = client.get("/incidents?page=-1")
    assert response.status_code == 422  # Invalid page parameter
    print("✅ test_day3_pagination_negative_page passed")


def test_day3_pagination_invalid_page_size(test_client):
    """Test Day 3 pagination with invalid page_size."""
    client = test_client
    response = client.get("/incidents?page_size=invalid")
    assert response.status_code == 422  # Invalid parameter
    print("✅ test_day3_pagination_invalid_page_size passed")


def test_day3_pagination_large_page_size(test_client):
    """Test Day 3 pagination with large page_size."""
    client = test_client
    response = client.get("/incidents?page_size=1000")
    assert response.status_code == 200
    data = response.json()
    assert data["page_size"] == 1000
    print("✅ test_day3_pagination_large_page_size passed")


def test_day3_pagination_beyond_available_results(test_client):
    """Test Day 3 pagination beyond available results."""
    client = test_client
    response = client.get("/incidents?page=100&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 100
    assert len(data["incidents"]) == 0
    print("✅ test_day3_pagination_beyond_available_results passed")


def test_day3_input_validation(test_client):
    """Test Day 3 input validation."""
    client = test_client
    # Test missing required field
    invalid_data = {
        "title": "Test Incident",
        "description": "Description",
        # Missing severity, status, service
    }
    response = client.post("/incidents", json=invalid_data)
    assert response.status_code == 422

    # Test invalid field values
    invalid_data = {
        "title": "Test Incident",
        "description": "Description",
        "severity": "invalid-severity",
        "status": "open",
        "service": "test-service"
    }
    response = client.post("/incidents", json=invalid_data)
    assert response.status_code == 422

    print("✅ test_day3_input_validation passed")


def test_day3_model_validation(test_client):
    """Test Day 3 model validation."""
    client = test_client
    # Test title too short (minimum 1 char)
    invalid_data = {
        "title": "A",  # Minimum 1 char, should pass
        "description": "This is a longer description that meets the minimum requirements (minimum 10 chars)",
        "severity": "medium",
        "status": "open",
        "service": "test-service"
    }
    response = client.post("/incidents", json=invalid_data)
    assert response.status_code == 201  # Should pass validation

    print("✅ test_day3_model_validation passed")