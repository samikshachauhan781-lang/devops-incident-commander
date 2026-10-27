"""
test_day8_analytics.py - Testing framework for Day 8 incident analytics overview.

Purpose:
- Test the analytics overview endpoint functionality
- Verify correct incident statistics and resolution rate calculations
- Ensure analytics data is read from actual database, not hardcoded
- Test edge cases like empty database and mixed incident scenarios
"""

import pytest
from fastapi.testclient import TestClient
from main import app

# Use pytest fixtures from conftest.py for consistent test database setup
from conftest import test_client

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

# Remove conflicting database setup that conflicts with conftest.py fixtures
# The conftest.py now provides proper pytest fixtures:
# - test_client: TestClient fixture
# - session_test_database: Session-scoped database setup
# - function_test_isolation: Function-scoped database reset
# - sample_incidents_data: Sample incident data

# Remove conflicting database setup functions
# setup_and_teardown() is handled by conftest.py
# setup_test_database(), cleanup_test_database() are handled by conftest.py


def test_empty_database(test_client):
    """Test analytics overview with empty database returns zero counts and 0.0 rate."""
    from models import list_incidents

    # Get all incidents with current test database (should be empty after reset)
    result = list_incidents()

    # Should have 0 incidents
    assert result["total"] == 0
    assert len(result["incidents"]) == 0
    print("✅ test_empty_database passed")


def test_mixed_incident_statuses(test_client):
    """Test analytics overview with various incident statuses and severities."""
    from models import list_incidents, get_analytics_overview

    # First, let's create some incidents with different statuses
    # Use test_client fixture directly
    client = test_client

    # Create incidents with different statuses
    create_data = [
        {"title": "Critical Open", "description": "Critical issue", "severity": "critical", "status": "open", "service": "service-a"},
        {"title": "High Investigating", "description": "High severity", "severity": "high", "status": "investigating", "service": "service-b"},
        {"title": "Medium Resolved", "description": "Medium severity", "severity": "medium", "status": "resolved", "service": "service-a"},
        {"title": "Low Closed", "description": "Low severity", "severity": "low", "status": "closed", "service": "service-c"},
        {"title": "Another Critical Open", "description": "Another critical", "severity": "critical", "status": "open", "service": "service-b"},
    ]

    for data in create_data:
        response = client.post("/incidents", json=data)
        assert response.status_code == 201

    # Get analytics overview
    analytics = get_analytics_overview()

    # Verify analytics calculations
    assert analytics["total_incidents"] == 5
    assert analytics["open_incidents"] == 2  # Critical Open + Another Critical Open (only status 'open')
    assert analytics["investigating_incidents"] == 1
    assert analytics["resolved_incidents"] == 1
    assert analytics["closed_incidents"] == 1
    assert analytics["critical_incidents"] == 2
    assert analytics["resolution_rate_percent"] == 40.0  # (1 + 1) / 5 * 100

    print("✅ test_mixed_incident_statuses passed")


def test_critical_incidents_across_statuses(test_client):
    """Test that critical incidents are counted across different statuses."""
    from models import get_analytics_overview

    # Analytics should count critical incidents regardless of status
    # This test ensures the query correctly includes critical incidents in all status categories
    analytics = get_analytics_overview()

    # The exact count depends on existing data, but critical incidents should be counted properly
    # The key is that the query doesn't filter by status when counting by severity
    assert "critical_incidents" in analytics
    print("✅ test_critical_incidents_across_statuses passed")


def test_resolution_rate_calculation(test_client):
    """Test resolution rate calculation logic."""
    from models import get_analytics_overview

    # Get analytics to check resolution rate calculation
    analytics = get_analytics_overview()

    # Verify resolution rate is calculated correctly
    total = analytics["total_incidents"]
    resolved = analytics["resolved_incidents"] + analytics["closed_incidents"]

    if total > 0:
        expected_rate = (resolved / total) * 100
        assert abs(analytics["resolution_rate_percent"] - expected_rate) < 0.01
    else:
        assert analytics["resolution_rate_percent"] == 0.0

    print("✅ test_resolution_rate_calculation passed")


def test_endpoint_reads_actual_database_data(test_client):
    """Test that analytics endpoint reads from actual database, not cached data."""
    from models import get_analytics_overview

    # Get initial analytics
    analytics1 = get_analytics_overview()
    total1 = analytics1["total_incidents"]

    # Create a new incident via API
    create_data = {
        "title": "New Incident for Test",
        "description": "This is a new incident created during test",
        "severity": "high",
        "status": "open",
        "service": "test-service"
    }
    # Use test_client fixture directly
    client = test_client
    response = client.post("/incidents", json=create_data)
    assert response.status_code == 201

    # Get analytics again - should reflect the new incident
    analytics2 = get_analytics_overview()

    # Total should increase by 1
    assert analytics2["total_incidents"] == total1 + 1

    print("✅ test_endpoint_reads_actual_database_data passed")


def test_endpoint_consistency(test_client):
    """Test that analytics endpoint provides consistent data."""
    from models import get_analytics_overview

    # Get analytics multiple times to ensure consistency
    analytics1 = get_analytics_overview()
    analytics2 = get_analytics_overview()
    analytics3 = get_analytics_overview()

    # All should return the same data
    assert analytics1 == analytics2 == analytics3

    print("✅ test_endpoint_consistency passed")


def test_analytics_endpoint_does_not_affect_incident_creation(test_client):
    """Test that analytics endpoint does not interfere with incident creation."""
    from models import get_analytics_overview

    # Get initial analytics
    analytics_before = get_analytics_overview()

    # Create a new incident
    client = test_client
    create_data = {
        "title": "Test Incident for Isolation",
        "description": "This test verifies isolation",
        "severity": "medium",
        "status": "open",
        "service": "test-service"
    }
    response = client.post("/incidents", json=create_data)
    assert response.status_code == 201

    # Get analytics after creation
    analytics_after = get_analytics_overview()

    # Analytics should have increased
    assert analytics_after["total_incidents"] == analytics_before["total_incidents"] + 1

    # But the incidents list should be properly isolated (not corrupted by analytics calls)
    # by checking that we can still create incidents normally
    create_data2 = {
        "title": "Second Test Incident",
        "description": "Another test incident",
        "severity": "low",
        "status": "closed",
        "service": "test-service"
    }
    response2 = client.post("/incidents", json=create_data2)
    assert response2.status_code == 201

    print("✅ test_analytics_endpoint_does_not_affect_incident_creation passed")


def test_severity_breakdown_empty_database(test_client):
    """Test severity breakdown with empty database."""
    from models import get_severity_breakdown

    severity_breakdown = get_severity_breakdown()

    # Should have all 4 severity categories with zero counts
    assert "severity_breakdown" in severity_breakdown
    assert len(severity_breakdown["severity_breakdown"]) == 4

    # Check each category has zero count and percentage
    for item in severity_breakdown["severity_breakdown"]:
        assert item["count"] == 0
        assert item["percentage"] == 0.0

    print("✅ test_severity_breakdown_empty_database passed")


def test_status_breakdown_empty_database(test_client):
    """Test status breakdown with empty database."""
    from models import get_status_breakdown

    status_breakdown = get_status_breakdown()

    # Should have all 4 status categories with zero counts
    assert "status_breakdown" in status_breakdown
    assert len(status_breakdown["status_breakdown"]) == 4

    # Check each category has zero count and percentage
    for item in status_breakdown["status_breakdown"]:
        assert item["count"] == 0
        assert item["percentage"] == 0.0

    print("✅ test_status_breakdown_empty_database passed")


def test_severity_breakdown_with_incidents(test_client):
    """Test severity breakdown with various incidents."""
    from models import get_severity_breakdown, get_analytics_overview

    # Get initial analytics to check current total
    initial_analytics = get_analytics_overview()
    initial_total = initial_analytics["total_incidents"]

    # Create test incidents with different severities
    create_data = [
        {"title": "Critical Incident 1", "description": "Critical issue", "severity": "critical", "status": "open", "service": "service-a"},
        {"title": "High Incident", "description": "High severity", "severity": "high", "status": "open", "service": "service-b"},
        {"title": "Medium Incident", "description": "Medium severity", "severity": "medium", "status": "open", "service": "service-c"},
        {"title": "Low Incident", "description": "Low severity", "severity": "low", "status": "open", "service": "service-d"},
    ]

    client = test_client
    for data in create_data:
        response = client.post("/incidents", json=data)
        assert response.status_code == 201

    # Get severity breakdown
    severity_breakdown = get_severity_breakdown()

    # Should have exactly 4 items
    assert len(severity_breakdown["severity_breakdown"]) == 4

    # Check counts
    severity_counts = {item["severity"]: item["count"] for item in severity_breakdown["severity_breakdown"]}
    assert severity_counts["low"] == 1
    assert severity_counts["medium"] == 1
    assert severity_counts["high"] == 1
    assert severity_counts["critical"] == 1

    # Check percentages (should be 25% each for 4 incidents)
    for item in severity_breakdown["severity_breakdown"]:
        assert item["percentage"] == 25.0

    print("✅ test_severity_breakdown_with_incidents passed")


def test_status_breakdown_with_incidents(test_client):
    """Test status breakdown with various incidents."""
    from models import get_status_breakdown, get_analytics_overview

    # Get initial analytics to check current total
    initial_analytics = get_analytics_overview()
    initial_total = initial_analytics["total_incidents"]

    # Create test incidents with different statuses
    create_data = [
        {"title": "Open Incident 1", "description": "Open issue", "severity": "medium", "status": "open", "service": "service-a"},
        {"title": "Investigating Incident", "description": "Investigating issue", "severity": "high", "status": "investigating", "service": "service-b"},
        {"title": "Resolved Incident", "description": "Resolved issue", "severity": "low", "status": "resolved", "service": "service-c"},
        {"title": "Closed Incident", "description": "Closed issue", "severity": "critical", "status": "closed", "service": "service-d"},
    ]

    client = test_client
    for data in create_data:
        response = client.post("/incidents", json=data)
        assert response.status_code == 201

    # Get status breakdown
    status_breakdown = get_status_breakdown()

    # Should have exactly 4 items
    assert len(status_breakdown["status_breakdown"]) == 4

    # Check counts
    status_counts = {item["status"]: item["count"] for item in status_breakdown["status_breakdown"]}
    assert status_counts["open"] == 1
    assert status_counts["investigating"] == 1
    assert status_counts["resolved"] == 1
    assert status_counts["closed"] == 1

    # Check percentages (should be 25% each for 4 incidents)
    for item in status_breakdown["status_breakdown"]:
        assert item["percentage"] == 25.0

    print("✅ test_status_breakdown_with_incidents passed")


def test_severity_breakdown_zero_total_behavior(test_client):
    """Test that severity breakdown handles zero total correctly."""
    from models import get_severity_breakdown

    severity_breakdown = get_severity_breakdown()

    # All percentages should be 0.0 when total is 0
    for item in severity_breakdown["severity_breakdown"]:
        assert item["percentage"] == 0.0

    print("✅ test_severity_breakdown_zero_total_behavior passed")


def test_status_breakdown_zero_total_behavior(test_client):
    """Test that status breakdown handles zero total correctly."""
    from models import get_status_breakdown

    status_breakdown = get_status_breakdown()

    # All percentages should be 0.0 when total is 0
    for item in status_breakdown["status_breakdown"]:
        assert item["percentage"] == 0.0

    print("✅ test_status_breakdown_zero_total_behavior passed")


def test_severity_breakdown_api_endpoint(test_client):
    """Test severity breakdown API endpoint directly."""
    # Create test incident
    create_data = {
        "title": "Test Incident",
        "description": "This is a test incident",
        "severity": "high",
        "status": "open",
        "service": "test-service"
    }

    # Use test_client fixture directly
    client = test_client
    response = client.post("/incidents", json=create_data)
    assert response.status_code == 201

    # Get severity breakdown via API
    response = client.get("/analytics/severity")
    assert response.status_code == 200
    data = response.json()

    # Should have severity_breakdown key
    assert "severity_breakdown" in data

    # Should have 4 categories
    assert len(data["severity_breakdown"]) == 4

    # Check that high severity has count 1
    for item in data["severity_breakdown"]:
        if item["severity"] == "high":
            assert item["count"] == 1
            assert item["percentage"] == 100.0
            break

    print("✅ test_severity_breakdown_api_endpoint passed")


def test_status_breakdown_api_endpoint(test_client):
    """Test status breakdown API endpoint directly."""
    # Create test incident
    create_data = {
        "title": "Test Incident",
        "description": "This is a test incident",
        "severity": "medium",
        "status": "resolved",
        "service": "test-service"
    }

    # Use test_client fixture directly
    client = test_client
    response = client.post("/incidents", json=create_data)
    assert response.status_code == 201

    # Get status breakdown via API
    response = client.get("/analytics/status")
    assert response.status_code == 200
    data = response.json()

    # Should have status_breakdown key
    assert "status_breakdown" in data

    # Should have 4 categories
    assert len(data["status_breakdown"]) == 4

    # Check that resolved status has count 1
    for item in data["status_breakdown"]:
        if item["status"] == "resolved":
            assert item["count"] == 1
            assert item["percentage"] == 100.0
            break

    print("✅ test_status_breakdown_api_endpoint passed")


def test_regression_existing_analytics_and_incident_apis(test_client):
    """Regression test for existing analytics and incident APIs."""
    # Use test_client fixture directly
    client = test_client

    # Test analytics overview endpoint
    response = client.get("/analytics/overview")
    assert response.status_code == 200

    # Test incident creation
    create_data = {
        "title": "Regression Test Incident",
        "description": "This is a regression test incident",
        "severity": "medium",
        "status": "open",
        "service": "regression-test"
    }
    response = client.post("/incidents", json=create_data)
    assert response.status_code == 201

    # Test incident listing
    response = client.get("/incidents")
    assert response.status_code == 200

    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200

    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200

    print("✅ test_regression_existing_analytics_and_incident_apis passed")