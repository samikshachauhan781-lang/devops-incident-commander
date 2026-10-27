"""
Day 7 Test Suite for DevOps Incident Commander - Timeline Testing.
Tests incident timeline and event history functionality.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
import time

# Use pytest fixtures from conftest.py for consistent test database setup
from conftest import test_client


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


def test_timeline_endpoint(test_client):
    """Test timeline endpoint functionality."""
    client = test_client

    # Create an incident for testing
    incident = create_test_incident(client)

    # Test the timeline endpoint with the incident we just created
    # The timeline endpoint should return at least the incident_created event
    response = client.get(f"/incidents/{incident['id']}/timeline")
    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"] == incident["id"]
    assert "events" in data
    assert len(data["events"]) == 1  # Should have exactly the incident_created event
    assert data["events"][0]["event_type"] == "incident_created"
    print("✅ test_timeline_endpoint passed - timeline endpoint returns incident_created event")


def test_timeline_endpoint_missing_incident(test_client):
    """Test timeline endpoint with non-existent incident."""
    client = test_client
    incident_id = "nonexistent-id"
    response = client.get(f"/incidents/{incident_id}/timeline")
    assert response.status_code == 404
    print("✅ test_timeline_endpoint_missing_incident passed")


def test_timeline_event_details(test_client):
    """Test timeline event details endpoint."""
    client = test_client

    # Create an incident and get its events
    incident = create_test_incident(client)
    response = client.get(f"/incidents/{incident['id']}/timeline")
    assert response.status_code == 200
    timeline_data = response.json()
    assert len(timeline_data["events"]) == 1  # incident_created event is automatically created
    assert timeline_data["events"][0]["event_type"] == "incident_created"

    print("✅ test_timeline_event_details passed")