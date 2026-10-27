#!/usr/bin/env python3
"""
Focused regression tests for investigation timeout API parameter.

Tests that the API endpoint correctly accepts, validates, and propagates
the investigation_timeout parameter through to the investigation service.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import Mock, patch
import time

from fastapi.testclient import TestClient
import pytest

# Import the FastAPI app
from main import app

# Import investigation models
from investigation_service import (
    InvestigationService,
    InvestigationEvidence,
    InvestigationRequest,
    InvestigationResult
)
from ai_provider import (
    AIProvider,
    AIProviderConfig,
    IncidentData,
    AnalysisRequest,
    AnalysisResult,
    get_analysis_service
)
# Import database helper for test incident persistence
from models import save_incident

def _create_test_incident(incident_id: str = "test-incident-001", title: str = None, severity: str = "critical", status: str = "investigating", service: str = "api-service"):
    """Helper to create a test incident in the test database."""
    incident_data = {
        "id": incident_id,
        "title": title or f"Test Incident {incident_id}",
        "description": f"Test incident {incident_id} for investigation",
        "severity": severity,
        "status": status,
        "service": service,
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z",
        "resolved_at": None
    }
    assert save_incident(incident_data), f"Failed to create test incident {incident_id}"
    return incident_data


def _create_mock_investigation_result(incident_id, incident_data_dict):
    """Helper to create a mock investigation result."""
    mock_result = InvestigationResult(
        investigation_id="test-inv-001",
        incident_id=incident_id,
        incident_data=Mock(),
        evidence=Mock(),
        ai_analysis=AnalysisResult(
            success=True,
            analysis_type="root_cause",
            confidence_score=0.85,
            hypotheses=["Test hypothesis"],
            recommendations=["Test recommendation"],
            reasoning="Test reasoning",
            metadata={"provider": "test"},
            errors=[],
            warnings=[]
        ),
        investigation_metadata={},
        root_cause_hypotheses=["Test hypothesis"],
        supporting_evidence={},
        confidence_scores={"overall": 0.85},
        diagnostic_steps=["Test step"],
        urgency_level="medium",
        investigation_type="root_cause"
    )
    mock_result.incident_data = Mock(
        incident_id=incident_id,
        title=incident_data_dict["title"],
        description=incident_data_dict["description"],
        severity=incident_data_dict["severity"],
        status=incident_data_dict["status"],
        service=incident_data_dict["service"],
        created_at="2024-01-01T12:00:00Z"
    )
    mock_result.evidence = Mock(
        log_text="",
        system_events=[],
        error_messages=[],
        timestamps=[],
        source="manual",
        collected_at="2024-01-01T12:00:00Z"
    )
    return mock_result


def test_api_endpoint_accepts_investigation_timeout():
    """Test that API endpoint accepts investigation_timeout query parameter."""
    client = TestClient(app)

    # Create a real incident
    incident_data = {
        "title": "Test Incident for Timeout API",
        "description": "This is a test incident for testing timeout parameter",
        "severity": "critical",
        "status": "open",
        "service": "api-service"
    }
    create_response = client.post("/incidents", json=incident_data)
    assert create_response.status_code == 201
    incident_id = create_response.json()["id"]

    # Test with investigation_timeout parameter
    with patch('investigation_service.InvestigationService.investigate_incident') as mock_investigate:
        mock_result = _create_mock_investigation_result(incident_id, incident_data)
        mock_investigate.return_value = mock_result

        response = client.post(
            f"/incidents/{incident_id}/investigate",
            json={"log_text": "Test log"},
            params={"investigation_timeout": 30.0}
        )

        assert response.status_code == 200
        mock_investigate.assert_called_once()

        # Verify the InvestigationRequest was created with the timeout in constraints
        call_args = mock_investigate.call_args[0][0]
        assert isinstance(call_args, InvestigationRequest)
        assert call_args.constraints.get('investigation_timeout') == 30.0


def test_api_endpoint_without_timeout_uses_none():
    """Test that omitting timeout results in no timeout constraint."""
    client = TestClient(app)

    # Create a real incident
    incident_data = {
        "title": "Test Incident No Timeout",
        "description": "Test incident without timeout",
        "severity": "medium",
        "status": "open",
        "service": "api-service"
    }
    create_response = client.post("/incidents", json=incident_data)
    assert create_response.status_code == 201
    incident_id = create_response.json()["id"]

    with patch('investigation_service.InvestigationService.investigate_incident') as mock_investigate:
        mock_result = _create_mock_investigation_result(incident_id, incident_data)
        mock_investigate.return_value = mock_result

        response = client.post(
            f"/incidents/{incident_id}/investigate",
            json={"log_text": "Test log"}
            # No investigation_timeout parameter
        )

        assert response.status_code == 200
        mock_investigate.assert_called_once()

        # Verify the InvestigationRequest was created without timeout in constraints
        call_args = mock_investigate.call_args[0][0]
        assert isinstance(call_args, InvestigationRequest)
        assert 'investigation_timeout' not in call_args.constraints


def test_api_endpoint_rejects_invalid_timeout_zero():
    """Test that API rejects zero timeout at validation level (422)."""
    _create_test_incident("test-timeout-zero-api")

    client = TestClient(app)

    response = client.post(
        "/incidents/test-timeout-zero-api/investigate",
        json={"log_text": "Test log"},
        params={"investigation_timeout": 0}
    )

    # FastAPI returns 422 for validation errors (gt=0 constraint)
    assert response.status_code == 422
    detail = response.json().get("detail", [])
    assert isinstance(detail, list)
    assert any("greater than 0" in err.get("msg", "") for err in detail)


def test_api_endpoint_rejects_invalid_timeout_negative():
    """Test that API rejects negative timeout at validation level (422)."""
    _create_test_incident("test-timeout-neg-api")

    client = TestClient(app)

    response = client.post(
        "/incidents/test-timeout-neg-api/investigate",
        json={"log_text": "Test log"},
        params={"investigation_timeout": -1}
    )

    # FastAPI returns 422 for validation errors (gt=0 constraint)
    assert response.status_code == 422
    detail = response.json().get("detail", [])
    assert isinstance(detail, list)
    assert any("greater than 0" in err.get("msg", "") for err in detail)


def test_api_endpoint_rejects_boolean_timeout_at_validation():
    """Test that FastAPI rejects boolean timeout at validation level (422)."""
    _create_test_incident("test-timeout-bool-api")

    client = TestClient(app)

    # FastAPI will reject "true" as a boolean for a float parameter
    response = client.post(
        "/incidents/test-timeout-bool-api/investigate",
        json={"log_text": "Test log"},
        params={"investigation_timeout": "true"}
    )

    # FastAPI returns 422 for type validation errors
    assert response.status_code == 422


def test_api_endpoint_rejects_non_numeric_timeout_at_validation():
    """Test that FastAPI rejects non-numeric timeout at validation level (422)."""
    _create_test_incident("test-timeout-str-api")

    client = TestClient(app)

    # FastAPI will reject "invalid" string for a float parameter
    response = client.post(
        "/incidents/test-timeout-str-api/investigate",
        json={"log_text": "Test log"},
        params={"investigation_timeout": "invalid"}
    )

    # FastAPI returns 422 for type validation errors
    assert response.status_code == 422


def test_api_endpoint_accepts_float_timeout():
    """Test that API accepts float timeout values."""
    client = TestClient(app)

    incident_data = {
        "title": "Test Incident Float Timeout",
        "description": "Test incident with float timeout",
        "severity": "high",
        "status": "investigating",
        "service": "api-service"
    }
    create_response = client.post("/incidents", json=incident_data)
    assert create_response.status_code == 201
    incident_id = create_response.json()["id"]

    with patch('investigation_service.InvestigationService.investigate_incident') as mock_investigate:
        mock_result = _create_mock_investigation_result(incident_id, incident_data)
        mock_investigate.return_value = mock_result

        response = client.post(
            f"/incidents/{incident_id}/investigate",
            json={"log_text": "Test log"},
            params={"investigation_timeout": 2.5}
        )

        assert response.status_code == 200
        call_args = mock_investigate.call_args[0][0]
        assert call_args.constraints.get('investigation_timeout') == 2.5


def test_api_endpoint_accepts_integer_timeout():
    """Test that API accepts integer timeout values."""
    client = TestClient(app)

    incident_data = {
        "title": "Test Incident Int Timeout",
        "description": "Test incident with integer timeout",
        "severity": "high",
        "status": "investigating",
        "service": "api-service"
    }
    create_response = client.post("/incidents", json=incident_data)
    assert create_response.status_code == 201
    incident_id = create_response.json()["id"]

    with patch('investigation_service.InvestigationService.investigate_incident') as mock_investigate:
        mock_result = _create_mock_investigation_result(incident_id, incident_data)
        mock_investigate.return_value = mock_result

        response = client.post(
            f"/incidents/{incident_id}/investigate",
            json={"log_text": "Test log"},
            params={"investigation_timeout": 10}
        )

        assert response.status_code == 200
        call_args = mock_investigate.call_args[0][0]
        assert call_args.constraints.get('investigation_timeout') == 10


def test_api_endpoint_missing_incident_returns_404():
    """Test that missing incident returns 404 even with timeout parameter."""
    client = TestClient(app)

    response = client.post(
        "/incidents/non-existent/investigate",
        json={"log_text": "Test log"},
        params={"investigation_timeout": 30}
    )

    assert response.status_code == 404
    assert "not found" in response.json().get("detail", "").lower()


def test_api_endpoint_timeout_reaches_provider():
    """Integration test: verify timeout reaches the AI provider."""
    _create_test_incident("test-timeout-provider")

    from investigation_service import InvestigationService

    service = InvestigationService()

    # Create request with timeout via constraints (as the API does)
    request = InvestigationRequest(
        incident_id="test-timeout-provider",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={"investigation_timeout": 5.0},
        include_timeline=True,
        include_events=True
    )

    with patch.object(service.analysis_service, 'analyze_incident') as mock_analyze:
        # Capture the AnalysisRequest passed to provider
        captured_request = {}

        def capture_request(req):
            captured_request['request'] = req
            return AnalysisResult(
                success=True,
                analysis_type="root_cause",
                confidence_score=0.85,
                hypotheses=["Test hypothesis"],
                recommendations=["Test recommendation"],
                reasoning="Test reasoning",
                metadata={"provider": "mock"},
                errors=[],
                warnings=[]
            )

        mock_analyze.side_effect = capture_request

        result = service.investigate_incident(request)

        assert result is not None
        assert 'request' in captured_request
        # Verify the timeout was passed to the provider via constraints
        assert captured_request['request'].constraints.get('investigation_timeout') == 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
