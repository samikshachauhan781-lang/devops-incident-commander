"""
Day 5 Test Suite for DevOps Incident Commander - PATCH /incidents/{id} Endpoint
Tests partial update functionality, validation, error handling, and resolved_at lifecycle.
Uses pytest fixtures from conftest.py for proper test database isolation.
"""

from fastapi.testclient import TestClient
from main import app
import time
import pytest

# Use pytest fixtures from conftest.py for consistent test database setup
from conftest import test_client


def create_test_incident(client, **overrides):
    """Helper to create a test incident with default values."""
    default_data = {
        "title": "Test Incident",
        "description": "This is a test incident for PATCH testing",
        "severity": "medium",
        "status": "open",
        "service": "test-service"
    }
    default_data.update(overrides)
    response = client.post("/incidents", json=default_data)
    assert response.status_code == 201
    return response.json()


def test_patch_update_single_field_severity(test_client):
    """Test 1: Update only severity field."""
    client = test_client
    incident = create_test_incident(client, severity="low", status="open")
    incident_id = incident["id"]
    original_title = incident["title"]
    original_description = incident["description"]
    original_status = incident["status"]
    original_service = incident["service"]
    original_created_at = incident["created_at"]

    # Update only severity
    response = client.patch(f"/incidents/{incident_id}", json={"severity": "critical"})
    assert response.status_code == 200
    data = response.json()

    # Verify updated field
    assert data["severity"] == "critical"

    # Verify all other fields unchanged
    assert data["id"] == incident_id
    assert data["title"] == original_title
    assert data["description"] == original_description
    assert data["status"] == original_status
    assert data["service"] == original_service
    assert data["created_at"] == original_created_at
    assert data["resolved_at"] is None

    print("✅ test_patch_update_single_field_severity passed")


def test_patch_update_single_field_status(test_client):
    """Test 2: Update only status field."""
    client = test_client
    incident = create_test_incident(client, status="open")
    incident_id = incident["id"]
    original_severity = incident["severity"]

    # Update only status
    response = client.patch(f"/incidents/{incident_id}", json={"status": "investigating"})
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "investigating"
    assert data["severity"] == original_severity
    assert data["id"] == incident_id
    assert data["resolved_at"] is None  # Not resolved yet

    print("✅ test_patch_update_single_field_status passed")


def test_patch_update_multiple_fields(test_client):
    """Test 3: Update multiple fields in one request."""
    client = test_client
    incident = create_test_incident(client, severity="low", status="open", service="old-service")
    incident_id = incident["id"]
    original_title = incident["title"]
    original_description = incident["description"]
    original_created_at = incident["created_at"]

    # Update multiple fields
    response = client.patch(f"/incidents/{incident_id}", json={
        "status": "investigating",
        "severity": "high",
        "service": "new-service"
    })
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "investigating"
    assert data["severity"] == "high"
    assert data["service"] == "new-service"
    assert data["id"] == incident_id
    assert data["title"] == original_title
    assert data["description"] == original_description
    assert data["created_at"] == original_created_at
    assert data["resolved_at"] is None

    print("✅ test_patch_update_multiple_fields passed")


def test_patch_partial_update_preserves_omitted_fields(test_client):
    """Test 4: PATCH preserves fields that are not updated."""
    client = test_client
    incident = create_test_incident(client, title="Original Title", description="Original Description", severity="critical")
    incident_id = incident["id"]

    # Update only title
    response = client.patch(f"/incidents/{incident_id}", json={"title": "Updated Title"})
    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Updated Title"
    assert data["description"] == "Original Description"
    assert data["severity"] == "critical"
    assert data["id"] == incident_id

    print("✅ test_patch_partial_update_preserves_omitted_fields passed")


def test_patch_nonexistent_incident(test_client):
    """Test 5: PATCH on non-existent incident returns 404."""
    client = test_client
    incident_id = "nonexistent-id"

    response = client.patch(f"/incidents/{incident_id}", json={"severity": "high"})
    assert response.status_code == 404

    print("✅ test_patch_nonexistent_incident passed")


def test_patch_invalid_severity(test_client):
    """Test 6: PATCH with invalid severity returns 422."""
    client = test_client
    # First create a valid incident
    incident = create_test_incident(client)
    incident_id = incident["id"]

    # Try to update with invalid severity
    response = client.patch(f"/incidents/{incident_id}", json={"severity": "invalid-severity"})
    assert response.status_code == 422

    print("✅ test_patch_invalid_severity passed")


def test_patch_invalid_status(test_client):
    """Test 7: PATCH with invalid status returns 422."""
    client = test_client
    incident = create_test_incident(client)
    incident_id = incident["id"]

    response = client.patch(f"/incidents/{incident_id}", json={"status": "invalid-status"})
    assert response.status_code == 422

    print("✅ test_patch_invalid_status passed")


def test_patch_invalid_title(test_client):
    """Test 8: PATCH with invalid title (empty) returns 422."""
    client = test_client
    incident = create_test_incident(client)
    incident_id = incident["id"]

    response = client.patch(f"/incidents/{incident_id}", json={"title": ""})
    assert response.status_code == 422

    print("✅ test_patch_invalid_title passed")


def test_patch_invalid_description(test_client):
    """Test 9: PATCH with invalid description (too short) returns 422."""
    client = test_client
    incident = create_test_incident(client)
    incident_id = incident["id"]

    response = client.patch(f"/incidents/{incident_id}", json={"description": "Short"})
    assert response.status_code == 422

    print("✅ test_patch_invalid_description passed")


def test_patch_invalid_service(test_client):
    """Test 10: PATCH with invalid service (empty) returns 422."""
    client = test_client
    incident = create_test_incident(client)
    incident_id = incident["id"]

    response = client.patch(f"/incidents/{incident_id}", json={"service": ""})
    assert response.status_code == 422

    print("✅ test_patch_invalid_service passed")


def test_patch_empty_update(test_client):
    """Test 11: PATCH with empty update returns 422."""
    client = test_client
    incident = create_test_incident(client)
    incident_id = incident["id"]

    response = client.patch(f"/incidents/{incident_id}", json={})
    assert response.status_code == 422

    print("✅ test_patch_empty_update passed")


def test_patch_explicit_null_severity(test_client):
    """Test 12: PATCH with explicit null severity returns 422."""
    client = test_client
    incident = create_test_incident(client)
    incident_id = incident["id"]

    response = client.patch(f"/incidents/{incident_id}", json={"severity": None})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    # The error detail is now a list of validation errors
    if isinstance(data["detail"], list):
        # Check if any error message contains "cannot be set to null" or similar
        error_messages = [error.get("msg", "") for error in data["detail"]]
        assert any("cannot be set to null" in msg.lower() or "cannot be null" in msg.lower() for msg in error_messages)
    else:
        # Fallback for string error messages
        assert "cannot be set to null" in data["detail"].lower()

    print("✅ test_patch_explicit_null_severity passed")


def test_patch_explicit_null_status(test_client):
    """Test 13: PATCH with explicit null status returns 422."""
    client = test_client
    incident = create_test_incident(client)
    incident_id = incident["id"]

    response = client.patch(f"/incidents/{incident_id}", json={"status": None})
    assert response.status_code == 422

    print("✅ test_patch_explicit_null_status passed")


def test_patch_explicit_null_title(test_client):
    """Test 14: PATCH with explicit null title returns 422."""
    client = test_client
    incident = create_test_incident(client)
    incident_id = incident["id"]

    response = client.patch(f"/incidents/{incident_id}", json={"title": None})
    assert response.status_code == 422

    print("✅ test_patch_explicit_null_title passed")


def test_patch_preserves_id_and_created_at(test_client):
    """Test 15: PATCH preserves id and created_at fields."""
    client = test_client
    incident = create_test_incident(client, title="Test Title")
    incident_id = incident["id"]
    original_created_at = incident["created_at"]

    response = client.patch(f"/incidents/{incident_id}", json={"severity": "high"})
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == incident_id
    assert data["created_at"] == original_created_at
    assert data["severity"] == "high"

    print("✅ test_patch_preserves_id_and_created_at passed")


def test_patch_database_persistence(test_client):
    """Test 16: PATCH updates database correctly."""
    client = test_client
    incident = create_test_incident(client, title="Original", severity="low")
    incident_id = incident["id"]

    # Update incident
    response = client.patch(f"/incidents/{incident_id}", json={"severity": "critical", "title": "Updated"})
    assert response.status_code == 200

    # Get the incident again to verify changes persisted
    get_response = client.get(f"/incidents/{incident_id}")
    assert get_response.status_code == 200
    data = get_response.json()

    assert data["severity"] == "critical"
    assert data["title"] == "Updated"

    print("✅ test_patch_database_persistence passed")


def test_patch_resolved_at_transition_to_resolved(test_client):
    """Test 17: PATCH status changes to 'resolved' sets resolved_at timestamp."""
    client = test_client
    incident = create_test_incident(client, status="open")
    incident_id = incident["id"]

    response = client.patch(f"/incidents/{incident_id}", json={"status": "resolved"})
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "resolved"
    assert data["resolved_at"] is not None
    # resolved_at should be a valid timestamp format
    assert isinstance(data["resolved_at"], str)

    print("✅ test_patch_resolved_at_transition_to_resolved passed")


def test_patch_resolved_at_preserved_on_other_updates(test_client):
    """Test 18: PATCH other fields when status is already resolved preserves resolved_at."""
    client = test_client
    incident = create_test_incident(client, status="resolved")
    incident_id = incident["id"]
    original_resolved_at = incident["resolved_at"]

    response = client.patch(f"/incidents/{incident_id}", json={"severity": "high"})
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "resolved"
    assert data["resolved_at"] == original_resolved_at
    assert data["severity"] == "high"

    print("✅ test_patch_resolved_at_preserved_on_other_updates passed")


def test_patch_resolved_at_cleared_on_reopen(test_client):
    """Test 19: PATCH status changes from resolved back to open clears resolved_at."""
    client = test_client
    incident = create_test_incident(client, status="resolved")
    incident_id = incident["id"]

    response = client.patch(f"/incidents/{incident_id}", json={"status": "open"})
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "open"
    assert data["resolved_at"] is None

    print("✅ test_patch_resolved_at_cleared_on_reopen passed")


def test_patch_resolved_at_new_timestamp_on_re_resolve(test_client):
    """Test 20: PATCH status changes to resolved again sets new resolved_at."""
    client = test_client
    incident = create_test_incident(client, status="open")
    incident_id = incident["id"]

    # First resolution
    response = client.patch(f"/incidents/{incident_id}", json={"status": "resolved"})
    assert response.status_code == 200
    data1 = response.json()
    first_resolved_at = data1["resolved_at"]

    # Re-open
    response = client.patch(f"/incidents/{incident_id}", json={"status": "open"})
    assert response.status_code == 200

    # Resolve again
    response = client.patch(f"/incidents/{incident_id}", json={"status": "resolved"})
    assert response.status_code == 200
    data2 = response.json()

    assert data2["status"] == "resolved"
    assert data2["resolved_at"] is not None
    assert data2["resolved_at"] != first_resolved_at  # Should be a new timestamp

    print("✅ test_patch_resolved_at_new_timestamp_on_re_resolve passed")


def test_patch_status_transitions(test_client):
    """Test 21: PATCH supports various status transitions."""
    client = test_client
    incident = create_test_incident(client, status="open")
    incident_id = incident["id"]

    # Test multiple status transitions
    transitions = [
        ("open", "investigating"),
        ("investigating", "resolved"),
        ("resolved", "closed")
    ]

    for from_status, to_status in transitions:
        # Update status
        response = client.patch(f"/incidents/{incident_id}", json={"status": to_status})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == to_status

        # Verify resolved_at is set for resolved status
        if to_status == "resolved":
            assert data["resolved_at"] is not None
        elif to_status == "closed":
            # closed status should keep resolved_at from when it was resolved
            assert data["resolved_at"] is not None

    print("✅ test_patch_status_transitions passed")