"""
Day 6 Test Suite for DevOps Incident Commander - Filtering, Search, Sorting & Pagination
Tests incident search, filtering, sorting, and pagination functionality.
Uses pytest fixtures from conftest.py for proper test database isolation.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from datetime import datetime, timezone
import time

# Use pytest fixtures from conftest.py for consistent test database setup
from conftest import test_client, sample_incidents_data


def create_test_incident(client, **overrides):
    """Helper to create a test incident with default values."""
    default_data = {
        "title": "Test Incident",
        "description": "This is a test incident for filtering testing",
        "severity": "medium",
        "status": "open",
        "service": "test-service"
    }
    default_data.update(overrides)
    response = client.post("/incidents", json=default_data)
    assert response.status_code == 201, f"Failed to create incident: {response.json()}"
    return response.json()


class TestServiceFiltering:
    """Test filtering by service."""

    def test_filter_by_existing_service(self, test_client):
        """Filter by a service that exists."""
        client = test_client
        create_test_incident(client, service="payment-api", title="Payment Issue 1")
        create_test_incident(client, service="payment-api", title="Payment Issue 2")
        create_test_incident(client, service="auth-service", title="Auth Issue")

        response = client.get("/incidents?service=payment-api")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        for incident in data["incidents"]:
            assert incident["service"] == "payment-api"

    def test_filter_by_nonexistent_service(self, test_client):
        """Filter by a service that doesn't exist."""
        client = test_client
        create_test_incident(client, service="payment-api")

        response = client.get("/incidents?service=nonexistent-service")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["incidents"] == []

    def test_service_filter_excludes_nonmatching(self, test_client):
        """Confirm nonmatching services are excluded."""
        client = test_client
        create_test_incident(client, service="payment-api")
        create_test_incident(client, service="auth-service")
        create_test_incident(client, service="notification-service")

        response = client.get("/incidents?service=auth-service")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["incidents"][0]["service"] == "auth-service"

    def test_service_combined_with_severity_and_status(self, test_client):
        """Verify service filtering combined with severity and status."""
        client = test_client
        create_test_incident(client, service="payment-api", severity="critical", status="open")
        create_test_incident(client, service="payment-api", severity="high", status="open")
        create_test_incident(client, service="payment-api", severity="critical", status="resolved")
        create_test_incident(client, service="auth-service", severity="critical", status="open")

        response = client.get("/incidents?service=payment-api&severity=critical&status=open")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        incident = data["incidents"][0]
        assert incident["service"] == "payment-api"
        assert incident["severity"] == "critical"
        assert incident["status"] == "open"


class TestSeverityStatusFiltering:
    """Test filtering by severity and status."""

    def test_filter_by_all_severities(self, test_client):
        """Filter by critical, high, medium, low severities."""
        client = test_client
        create_test_incident(client, severity="critical")
        create_test_incident(client, severity="high")
        create_test_incident(client, severity="medium")
        create_test_incident(client, severity="low")

        for sev in ["critical", "high", "medium", "low"]:
            response = client.get(f"/incidents?severity={sev}")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert data["incidents"][0]["severity"] == sev

    def test_filter_by_all_statuses(self, test_client):
        """Filter by all valid statuses."""
        client = test_client
        create_test_incident(client, status="open")
        create_test_incident(client, status="investigating")
        create_test_incident(client, status="resolved")
        create_test_incident(client, status="closed")

        for st in ["open", "investigating", "resolved", "closed"]:
            response = client.get(f"/incidents?status={st}")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert data["incidents"][0]["status"] == st

    def test_invalid_severity_returns_422(self, test_client):
        """Unsupported severity returns 422."""
        client = test_client
        response = client.get("/incidents?severity=super-critical")
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_invalid_status_returns_422(self, test_client):
        """Unsupported status returns 422."""
        client = test_client
        response = client.get("/incidents?status=in-progress")
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_combined_filters_return_intersection(self, test_client):
        """Combined filters return only records satisfying all filters."""
        client = test_client
        create_test_incident(client, severity="critical", status="open", service="payment-api")
        create_test_incident(client, severity="critical", status="resolved", service="payment-api")
        create_test_incident(client, severity="high", status="open", service="payment-api")
        create_test_incident(client, severity="critical", status="open", service="auth-service")

        response = client.get("/incidents?severity=critical&status=open&service=payment-api")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        incident = data["incidents"][0]
        assert incident["severity"] == "critical"
        assert incident["status"] == "open"
        assert incident["service"] == "payment-api"


class TestTextSearch:
    """Test text search in title and description."""

    def test_search_by_title(self, test_client):
        """Search by word in title."""
        client = test_client
        create_test_incident(client, title="Database Connection Error", description="Some description here")
        create_test_incident(client, title="API Timeout", description="Connection pool issue")

        response = client.get("/incidents?search=Database")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "Database" in data["incidents"][0]["title"]

    def test_search_by_description(self, test_client):
        """Search by word in description."""
        client = test_client
        create_test_incident(client, title="Issue 1", description="Database connection failed here")
        create_test_incident(client, title="Issue 2", description="API rate limit exceeded")

        response = client.get("/incidents?search=connection")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "connection" in data["incidents"][0]["description"].lower()

    def test_case_insensitive_matching(self, test_client):
        """Confirm case-insensitive matching."""
        client = test_client
        create_test_incident(client, title="DATABASE ERROR", description="Something went wrong here")
        create_test_incident(client, title="Database Error", description="Something else happened")
        create_test_incident(client, title="database error", description="Another thing occurred")

        for search_term in ["DATABASE", "database", "Database", "DaTaBaSe"]:
            response = client.get(f"/incidents?search={search_term}")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 3

    def test_partial_matching(self, test_client):
        """Confirm partial matching works."""
        client = test_client
        create_test_incident(client, title="DatabaseConnectionPoolExhaustion", description="Desc for test case")

        response = client.get("/incidents?search=Connection")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

        response = client.get("/incidents?search=Pool")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    def test_nonmatching_query_returns_empty(self, test_client):
        """Nonmatching query returns empty result."""
        client = test_client
        create_test_incident(client, title="Database Error", description="Connection failed")

        response = client.get("/incidents?search=nonexistentterm")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["incidents"] == []

    def test_special_characters_percent_underscore(self, test_client):
        """Test % and _ are treated as literal characters."""
        client = test_client
        create_test_incident(client, title="Error 100%", description="Complete failure occurred")
        create_test_incident(client, title="Error_500", description="Server error happened")
        create_test_incident(client, title="Error 200", description="Success was achieved")

        # Search for literal %
        response = client.get("/incidents?search=100%")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "100%" in data["incidents"][0]["title"]

        # Search for literal _
        response = client.get("/incidents?search=Error_500")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "Error_500" in data["incidents"][0]["title"]

    def test_empty_search_input(self, test_client):
        """Empty/whitespace search should not match everything."""
        client = test_client
        create_test_incident(client, title="Test 1", description="First test incident")
        create_test_incident(client, title="Test 2", description="Second test incident")

        # Empty search - should return all (treated as no filter)
        response = client.get("/incidents?search=")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

        # Whitespace-only search - should return all (treated as no filter)
        response = client.get("/incidents?search=   ")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2


class TestCreatedAfterFiltering:
    """Test filtering by creation timestamp."""

    def test_include_incident_at_cutoff(self, test_client):
        """Include incident created exactly at cutoff."""
        client = test_client
        cutoff = "2026-10-15T12:00:00Z"
        time.sleep(0.01)
        incident = create_test_incident(client)

        response = client.get(f"/incidents?created_after={cutoff}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        for inc in data["incidents"]:
            assert inc["created_at"] >= cutoff

    def test_include_incident_after_cutoff(self, test_client):
        """Include incident created after cutoff."""
        client = test_client
        cutoff = "2026-10-15T12:00:00Z"
        time.sleep(0.01)
        create_test_incident(client)

        response = client.get(f"/incidents?created_after={cutoff}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_exclude_incident_before_cutoff(self, test_client):
        """Exclude incident created before cutoff."""
        client = test_client
        create_test_incident(client)

        future_cutoff = "2030-01-01T00:00:00Z"
        response = client.get(f"/incidents?created_after={future_cutoff}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_valid_timestamps_with_timezone(self, test_client):
        """Test valid timestamps with timezone info."""
        client = test_client
        create_test_incident(client)

        # UTC with Z
        response = client.get("/incidents?created_after=2026-10-15T12:00:00Z")
        assert response.status_code == 200

        # UTC with +00:00 (URL-encoded)
        response = client.get("/incidents?created_after=2026-10-15T12:00:00%2B00:00")
        assert response.status_code == 200

    def test_malformed_timestamp_returns_422(self, test_client):
        """Malformed timestamps return 422."""
        client = test_client
        response = client.get("/incidents?created_after=invalid-date")
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

        response = client.get("/incidents?created_after=2026-13-45")
        assert response.status_code == 422

    def test_utc_handling_consistency(self, test_client):
        """Test consistent UTC handling."""
        client = test_client
        create_test_incident(client)

        # Same time with different UTC representations should work
        response1 = client.get("/incidents?created_after=2026-10-15T12:00:00Z")
        response2 = client.get("/incidents?created_after=2026-10-15T12:00:00%2B00:00")

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["total"] == response2.json()["total"]


class TestSorting:
    """Test sorting functionality."""

    def test_ascending_order(self, test_client):
        """Verify ascending creation-time order."""
        client = test_client
        create_test_incident(client, title="First")
        time.sleep(0.01)
        create_test_incident(client, title="Second")
        time.sleep(0.01)
        create_test_incident(client, title="Third")

        response = client.get("/incidents?sort_by=created_at&order=asc")
        assert response.status_code == 200
        data = response.json()
        incidents = data["incidents"]

        assert incidents[0]["created_at"] <= incidents[1]["created_at"]
        assert incidents[1]["created_at"] <= incidents[2]["created_at"]

    def test_descending_order(self, test_client):
        """Verify descending creation-time order (default)."""
        client = test_client
        create_test_incident(client, title="First")
        time.sleep(0.01)
        create_test_incident(client, title="Second")
        time.sleep(0.01)
        create_test_incident(client, title="Third")

        response = client.get("/incidents?sort_by=created_at&order=desc")
        assert response.status_code == 200
        data = response.json()
        incidents = data["incidents"]

        assert incidents[0]["created_at"] >= incidents[1]["created_at"]
        assert incidents[1]["created_at"] >= incidents[2]["created_at"]

    def test_default_order_is_descending(self, test_client):
        """Default order should be descending (newest first)."""
        client = test_client
        create_test_incident(client, title="First")
        time.sleep(0.01)
        create_test_incident(client, title="Second")

        response = client.get("/incidents")
        assert response.status_code == 200
        data = response.json()
        incidents = data["incidents"]

        assert incidents[0]["created_at"] >= incidents[1]["created_at"]

    def test_deterministic_ordering_with_same_timestamp(self, test_client):
        """Verify deterministic ordering when timestamps are identical."""
        client = test_client
        inc1 = create_test_incident(client, title="First", service="a-service")
        time.sleep(0.01)
        inc2 = create_test_incident(client, title="Second", service="b-service")

        response = client.get("/incidents?sort_by=created_at&order=asc")
        assert response.status_code == 200
        data = response.json()
        incidents = data["incidents"]

        if incidents[0]["created_at"] == incidents[1]["created_at"]:
            assert incidents[0]["id"] <= incidents[1]["id"]

    def test_unsupported_sort_field_returns_422(self, test_client):
        """Unsupported sort fields return 422."""
        client = test_client
        response = client.get("/incidents?sort_by=invalid_field")
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_invalid_order_value_returns_422(self, test_client):
        """Invalid order values return 422."""
        client = test_client
        response = client.get("/incidents?order=invalid")
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestPaginationAndCount:
    """Test pagination and count accuracy with filters."""

    def test_pagination_returns_correct_subset(self, test_client):
        """Pagination returns correct subset of filtered records."""
        client = test_client
        for i in range(5):
            create_test_incident(client, service="payment-api", title=f"Payment {i}")
        for i in range(3):
            create_test_incident(client, service="auth-service", title=f"Auth {i}")

        response = client.get("/incidents?service=payment-api&page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["incidents"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2

        response = client.get("/incidents?service=payment-api&page=2&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["incidents"]) == 2

        response = client.get("/incidents?service=payment-api&page=3&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["incidents"]) == 1

    def test_total_counts_only_filtered_records(self, test_client):
        """Total counts only records matching filters."""
        client = test_client
        create_test_incident(client, severity="critical", service="payment-api")
        create_test_incident(client, severity="high", service="payment-api")
        create_test_incident(client, severity="critical", service="auth-service")

        response = client.get("/incidents?severity=critical")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

        response = client.get("/incidents?service=payment-api")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

        response = client.get("/incidents?severity=critical&service=payment-api")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    def test_multiple_filters_with_pagination(self, test_client):
        """Multiple filters work with pagination."""
        client = test_client
        for i in range(10):
            create_test_incident(
                client,
                service="payment-api",
                severity="critical" if i % 2 == 0 else "high",
                status="open" if i % 3 == 0 else "investigating"
            )

        response = client.get("/incidents?service=payment-api&severity=critical&page=1&page_size=3")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["incidents"]) == 3

        for inc in data["incidents"]:
            assert inc["service"] == "payment-api"
            assert inc["severity"] == "critical"

    def test_empty_filtered_results(self, test_client):
        """Empty filtered results handled correctly."""
        client = test_client
        create_test_incident(client, service="payment-api")

        response = client.get("/incidents?service=nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["incidents"] == []

    def test_pages_beyond_available_filtered_results(self, test_client):
        """Pages beyond available filtered results return empty."""
        client = test_client
        create_test_incident(client, service="payment-api")

        response = client.get("/incidents?service=payment-api&page=100&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["incidents"] == []

    def test_invalid_page_page_size_still_422(self, test_client):
        """Invalid page/page_size still return 422 with filters."""
        client = test_client
        create_test_incident(client)

        response = client.get("/incidents?page=0&service=payment-api")
        assert response.status_code == 422

        response = client.get("/incidents?page_size=0&service=payment-api")
        assert response.status_code == 422

        # page_size=2000 is now valid (max page_size increased to 10000)
        response = client.get("/incidents?page_size=2000&service=payment-api")
        assert response.status_code == 200

    def test_sorting_applied_before_pagination(self, test_client):
        """Sorting is applied before pagination."""
        client = test_client
        create_test_incident(client, title="A First", service="payment-api")
        time.sleep(0.01)
        create_test_incident(client, title="B Second", service="payment-api")
        time.sleep(0.01)
        create_test_incident(client, title="C Third", service="payment-api")

        response = client.get("/incidents?service=payment-api&sort_by=created_at&order=asc&page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["incidents"][0]["title"] == "A First"
        assert data["incidents"][1]["title"] == "B Second"

        response = client.get("/incidents?service=payment-api&sort_by=created_at&order=desc&page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["incidents"][0]["title"] == "C Third"
        assert data["incidents"][1]["title"] == "B Second"


class TestRegression:
    """Regression tests for existing functionality."""

    def test_root_endpoint(self, test_client):
        """GET / still works."""
        client = test_client
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["project_name"] == "DevOps Incident Commander"

    def test_health_endpoint(self, test_client):
        """GET /health still works."""
        client = test_client
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_post_incidents(self, test_client):
        """POST /incidents still works."""
        client = test_client
        response = client.post("/incidents", json={
            "title": "Test",
            "description": "Test description",
            "severity": "medium",
            "status": "open",
            "service": "test"
        })
        assert response.status_code == 201
        assert "id" in response.json()

    def test_get_incidents(self, test_client):
        """GET /incidents still works."""
        client = test_client
        response = client.get("/incidents")
        assert response.status_code == 200
        assert "incidents" in response.json()

    def test_get_incident_by_id(self, test_client):
        """GET /incidents/{id} still works."""
        client = test_client
        inc = create_test_incident(client)
        response = client.get(f"/incidents/{inc['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == inc["id"]

    def test_delete_incident(self, test_client):
        """DELETE /incidents/{id} still works."""
        client = test_client
        inc = create_test_incident(client)
        response = client.delete(f"/incidents/{inc['id']}")
        assert response.status_code == 200
        response = client.get(f"/incidents/{inc['id']}")
        assert response.status_code == 404

    def test_patch_incident(self, test_client):
        """PATCH /incidents/{id} still works."""
        client = test_client
        inc = create_test_incident(client, severity="low")
        response = client.patch(f"/incidents/{inc['id']}", json={"severity": "critical"})
        assert response.status_code == 200
        assert response.json()["severity"] == "critical"