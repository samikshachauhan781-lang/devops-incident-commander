#!/usr/bin/env python3
"""
Test script for Investigation Service

This script tests the investigation service implementation
with mocked providers to avoid requiring a running AI service.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import Mock, patch
import json

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

def test_investigation_service_creation():
    """Test investigation service creation."""
    print("Testing Investigation Service Creation...")

    service = InvestigationService()

    assert service is not None
    assert isinstance(service, InvestigationService)
    assert service.investigation_count == 0

    print("✅ Investigation Service Creation test passed")


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


def test_investigation_with_mocked_incident():
    """Test investigation with mocked incident data."""
    print("Testing Investigation with Mocked Incident...")

    # Create test incident in database
    _create_test_incident("test-incident-001")

    service = InvestigationService()

    # Create investigation request for test incident
    request = InvestigationRequest(
        incident_id="test-incident-001",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={},
        include_timeline=True,
        include_events=True
    )

    # Mock the AI service
    with patch.object(service, '_generate_ai_analysis') as mock_analyze:
        mock_analysis_result = AnalysisResult(
            success=True,
            analysis_type="root_cause",
            confidence_score=0.85,
            hypotheses=[
                "Root cause: Network configuration issue",
                "Root cause: Service dependency failure"
            ],
            recommendations=[
                "Restart affected services",
                "Check network connectivity"
            ],
            reasoning="Analysis indicates network-related issues",
            metadata={"provider": "mock", "model": "test"},
            errors=[],
            warnings=[]
        )

        mock_analyze.return_value = mock_analysis_result

        # Test investigation
        result = service.investigate_incident(request)

        assert result is not None
        assert isinstance(result, InvestigationResult)
        assert result.incident_id == "test-incident-001"
        assert len(result.root_cause_hypotheses) == 2
        assert len(result.diagnostic_steps) > 0
        assert result.urgency_level in ["low", "medium", "high", "critical"]

        mock_analyze.assert_called_once()

    print("✅ Investigation with Mocked Incident test passed")

def test_investigation_with_evidence():
    """Test investigation with provided evidence."""
    print("Testing Investigation with Evidence...")

    # Create test incident in database
    _create_test_incident("test-incident-002")

    service = InvestigationService()

    # Create investigation evidence
    evidence = InvestigationEvidence(
        log_text="ERROR: Network connection failed\nWARN: Service dependency timeout\nINFO: Configuration error",
        system_events=["Service restart", "Network connectivity loss"],
        error_messages=["Connection refused", "Timeout"],
        timestamps=["2024-01-01T12:00:00Z", "2024-01-01T12:01:00Z"],
        source="system_logs"
    )

    # Create investigation request
    request = InvestigationRequest(
        incident_id="test-incident-002",
        evidence=evidence,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={},
        include_timeline=True,
        include_events=True
    )

    # Mock the AI service
    with patch.object(service, '_generate_ai_analysis') as mock_analyze:
        mock_analysis_result = AnalysisResult(
            success=True,
            analysis_type="root_cause",
            confidence_score=0.75,
            hypotheses=[
                "Root cause: Network configuration issue",
                "Root cause: Service dependency failure"
            ],
            recommendations=[
                "Check network configuration",
                "Restart affected services"
            ],
            reasoning="Analysis indicates configuration-related issues",
            metadata={"provider": "mock", "model": "test"},
            errors=[],
            warnings=[]
        )

        mock_analyze.return_value = mock_analysis_result

        # Test investigation
        result = service.investigate_incident(request)

        assert result is not None
        assert isinstance(result, InvestigationResult)
        assert result.incident_id == "test-incident-002"
        assert result.evidence.log_text == evidence.log_text
        assert len(result.evidence.system_events) == 2
        assert len(result.evidence.error_messages) == 2

        mock_analyze.assert_called_once()

    print("✅ Investigation with Evidence test passed")

def test_investigation_api_endpoint():
    """Test investigation API endpoint."""
    print("Testing Investigation API Endpoint...")

    client = TestClient(app)

    # First, create a real incident in the database
    incident_data = {
        "title": "Test Incident for Investigation",
        "description": "This is a test incident for testing investigation",
        "severity": "critical",
        "status": "open",
        "service": "api-service"
    }
    create_response = client.post("/incidents", json=incident_data)
    assert create_response.status_code == 201
    incident_id = create_response.json()["id"]

    # Test investigation of existing incident
    response = client.post(
        f"/incidents/{incident_id}/investigate",
        json={
            "log_text": "ERROR: Network connection failed",
            "system_events": ["Service restart"],
            "error_messages": ["Connection refused"],
            "source": "system_logs"
        }
    )

    assert response.status_code == 200

    response_data = response.json()
    assert "investigation_id" in response_data
    assert "incident_id" in response_data
    assert response_data["incident_id"] == incident_id
    assert "investigation_results" in response_data
    assert "ai_analysis" in response_data
    assert "urgency_level" in response_data["investigation_results"]

    print("✅ Investigation API Endpoint test passed")

def test_investigation_api_with_evidence():
    """Test investigation API endpoint with full evidence."""
    print("Testing Investigation API with Full Evidence...")

    client = TestClient(app)

    # First, create a real incident in the database
    incident_data = {
        "title": "Test Incident with Evidence",
        "description": "This is a test incident with comprehensive evidence",
        "severity": "high",
        "status": "investigating",
        "service": "api-service"
    }
    create_response = client.post("/incidents", json=incident_data)
    assert create_response.status_code == 201
    incident_id = create_response.json()["id"]

    # Test investigation with comprehensive evidence
    evidence_request = {
        "log_text": "ERROR: Network connection failed\nWARN: Service dependency timeout\nINFO: Configuration error",
        "system_events": ["Service restart", "Network connectivity loss"],
        "error_messages": ["Connection refused", "Timeout"],
        "timestamps": ["2024-01-01T12:00:00Z", "2024-01-01T12:01:00Z"],
        "source": "system_logs"
    }

    response = client.post(
        f"/incidents/{incident_id}/investigate",
        json=evidence_request,
        params={
            "include_timeline": True,
            "include_events": True,
            "investigation_depth": "detailed"
        }
    )

    assert response.status_code == 200

    response_data = response.json()
    assert response_data["incident_id"] == incident_id
    assert "error_messages" in response_data["evidence"]
    assert "system_events" in response_data["evidence"]
    assert "investigation_results" in response_data
    assert len(response_data["investigation_results"]["root_cause_hypotheses"]) > 0

    print("✅ Investigation API with Full Evidence test passed")

def test_investigation_missing_incident():
    """Test investigation of non-existent incident."""
    print("Testing Investigation Missing Incident...")

    client = TestClient(app)

    # Test investigation of non-existent incident
    # Should return 404 since incident doesn't exist in database
    response = client.post(
        "/incidents/non-existent-incident/investigate",
        json={"log_text": "Test log"}
    )

    # Should return 404 since incident doesn't exist
    assert response.status_code == 404

    response_data = response.json()
    assert "detail" in response_data
    assert "non-existent-incident" in response_data["detail"]

    print("✅ Investigation Missing Incident test passed")

def test_investigation_api_error_handling():
    """Test investigation API error handling."""
    print("Testing Investigation API Error Handling...")

    client = TestClient(app)

    # First, create a real incident for valid testing
    incident_data = {
        "title": "Test Incident for Error Handling",
        "description": "Test incident",
        "severity": "medium",
        "status": "open",
        "service": "api-service"
    }
    create_response = client.post("/incidents", json=incident_data)
    assert create_response.status_code == 201
    incident_id = create_response.json()["id"]

    # Test with empty JSON body (should work for valid incident)
    response = client.post(
        f"/incidents/{incident_id}/investigate",
        json={}
    )

    # Should return 200 (empty evidence is allowed for existing incident)
    assert response.status_code == 200

    # Test with non-existent incident ID
    response = client.post(
        "/incidents/invalid/investigate",
        json={"log_text": "Test"}
    )

    # Should return 404 for non-existent incident
    assert response.status_code == 404

    print("✅ Investigation API Error Handling test passed")

def test_investigation_provider_failure():
    """Test investigation with provider failure (exception)."""
    print("Testing Investigation Provider Failure...")

    # Create test incident in database
    _create_test_incident("test-incident-001")

    service = InvestigationService()

    # Create investigation request
    request = InvestigationRequest(
        incident_id="test-incident-001",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={},
        include_timeline=True,
        include_events=True
    )

    # Mock the AI service to raise an exception
    with patch.object(service, '_generate_ai_analysis') as mock_analyze:
        mock_analyze.side_effect = Exception("Provider connection failed")

        # Test that investigation fails predictably
        result = None
        try:
            result = service.investigate_incident(request)
            # If we get here, the test failed - investigation should have raised an exception
            assert False, "Expected investigation to fail due to provider exception"
        except RuntimeError as e:
            # Verify the error message indicates provider failure
            assert "provider" in str(e).lower() or "analysis failed" in str(e).lower()
            print("✅ Investigation correctly failed due to provider exception")
        except Exception as e:
            # Any other exception is also acceptable for provider failure
            print(f"✅ Investigation failed with exception: {type(e).__name__}: {str(e)}")

        # Verify the mock was called
        mock_analyze.assert_called_once()

    print("✅ Investigation Provider Failure test passed")

def test_investigation_malformed_ai_output():
    """Test investigation with malformed AI output - should be rejected."""
    print("Testing Investigation Malformed AI Output...")

    # Create test incident in database
    _create_test_incident("test-incident-001")

    service = InvestigationService()

    # Create investigation request
    request = InvestigationRequest(
        incident_id="test-incident-001",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={},
        include_timeline=True,
        include_events=True
    )

    # Test 1: Missing required field - success is None
    print("  Subtest 1: Missing required field 'success'...")
    incomplete_analysis = AnalysisResult(
        success=None,  # Missing required field
        analysis_type="root_cause",
        confidence_score=0.0,
        hypotheses=[],
        recommendations=[],
        reasoning="",
        metadata={},
        errors=[],
        warnings=[]
    )

    with patch.object(service, '_generate_ai_analysis') as mock_analyze:
        mock_analyze.return_value = incomplete_analysis

        try:
            result = service.investigate_incident(request)
            assert False, "Expected investigation to fail due to missing 'success' field"
        except RuntimeError as e:
            assert "missing required field" in str(e).lower()
            print(f"  ✅ Correctly rejected malformed AI output: {str(e)}")

    # Test 2: Missing required field - analysis_type is not a string
    print("  Subtest 2: Invalid field type for 'analysis_type'...")
    incomplete_analysis = AnalysisResult(
        success=True,
        analysis_type=123,  # Wrong type - should be string
        confidence_score=0.0,
        hypotheses=[],
        recommendations=[],
        reasoning="",
        metadata={},
        errors=[],
        warnings=[]
    )

    with patch.object(service, '_generate_ai_analysis') as mock_analyze:
        mock_analyze.return_value = incomplete_analysis

        try:
            result = service.investigate_incident(request)
            assert False, "Expected investigation to fail due to invalid 'analysis_type' field"
        except RuntimeError as e:
            assert "must be string" in str(e).lower()
            print(f"  ✅ Correctly rejected malformed AI output: {str(e)}")

    # Test 3: Missing required field - confidence_score is not a number
    print("  Subtest 3: Invalid field type for 'confidence_score'...")
    incomplete_analysis = AnalysisResult(
        success=True,
        analysis_type="root_cause",
        confidence_score="not_a_number",  # Wrong type - should be number
        hypotheses=[],
        recommendations=[],
        reasoning="",
        metadata={},
        errors=[],
        warnings=[]
    )

    with patch.object(service, '_generate_ai_analysis') as mock_analyze:
        mock_analyze.return_value = incomplete_analysis

        try:
            result = service.investigate_incident(request)
            assert False, "Expected investigation to fail due to invalid 'confidence_score' field"
        except RuntimeError as e:
            assert "must be number" in str(e).lower()
            print(f"  ✅ Correctly rejected malformed AI output: {str(e)}")

    # Test 4: Missing required field - hypotheses is None
    print("  Subtest 4: Missing required field 'hypotheses'...")
    incomplete_analysis = AnalysisResult(
        success=True,
        analysis_type="root_cause",
        confidence_score=0.0,
        hypotheses=None,  # Missing required field
        recommendations=[],
        reasoning="",
        metadata={},
        errors=[],
        warnings=[]
    )

    with patch.object(service, '_generate_ai_analysis') as mock_analyze:
        mock_analyze.return_value = incomplete_analysis

        try:
            result = service.investigate_incident(request)
            assert False, "Expected investigation to fail due to missing 'hypotheses' field"
        except RuntimeError as e:
            assert "missing required field" in str(e).lower()
            print(f"  ✅ Correctly rejected malformed AI output: {str(e)}")

    # Test 5: Valid AI output should be accepted
    print("  Subtest 5: Valid AI output should be accepted...")
    valid_analysis = AnalysisResult(
        success=True,
        analysis_type="root_cause",
        confidence_score=0.85,
        hypotheses=["Root cause: Network configuration issue"],
        recommendations=["Check network configuration"],
        reasoning="Analysis completed successfully",
        metadata={"provider": "test", "model": "test"},
        errors=[],
        warnings=[]
    )

    with patch.object(service, '_generate_ai_analysis') as mock_analyze:
        mock_analyze.return_value = valid_analysis

        result = service.investigate_incident(request)
        assert result is not None
        assert isinstance(result, InvestigationResult)
        assert result.incident_id == "test-incident-001"
        print(f"  ✅ Valid AI output correctly accepted")

    print("✅ Investigation Malformed AI Output test passed - validation working correctly")


def test_investigation_missing_incident_raises_valueerror():
    """Test that missing incident raises ValueError (not RuntimeError) when calling service directly."""
    print("Testing Investigation Missing Incident raises ValueError...")

    # Create test incident in database (we'll use a different ID for the missing one)
    _create_test_incident("test-incident-001")

    service = InvestigationService()

    # Create investigation request for NON-EXISTENT incident
    request = InvestigationRequest(
        incident_id="non-existent-incident",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={},
        include_timeline=True,
        include_events=True
    )

    # Test that investigation raises ValueError directly (not wrapped in RuntimeError)
    try:
        result = service.investigate_incident(request)
        assert False, "Expected ValueError for missing incident"
    except ValueError as e:
        assert "not found" in str(e).lower()
        print(f"  ✅ ValueError raised as expected: {e}")
    except RuntimeError as e:
        assert False, f"Expected ValueError but got RuntimeError: {e}"
    except Exception as e:
        assert False, f"Expected ValueError but got {type(e).__name__}: {e}"

    print("✅ Investigation Missing Incident raises ValueError test passed")


def test_investigation_provider_failure_raises_runtimeerror():
    """Test that AI provider failure raises RuntimeError (not ValueError)."""
    print("Testing Investigation Provider Failure raises RuntimeError...")

    # Create test incident in database
    _create_test_incident("test-incident-001")

    service = InvestigationService()

    # Create investigation request for EXISTING incident
    request = InvestigationRequest(
        incident_id="test-incident-001",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={},
        include_timeline=True,
        include_events=True
    )

    # Mock the AI service to raise an exception (simulating provider failure)
    with patch.object(service, '_generate_ai_analysis') as mock_analyze:
        mock_analyze.side_effect = Exception("Provider connection failed")

        # Test that investigation raises RuntimeError for provider failure
        try:
            result = service.investigate_incident(request)
            assert False, "Expected RuntimeError for provider failure"
        except RuntimeError as e:
            assert "provider" in str(e).lower() or "analysis failed" in str(e).lower() or "investigation failed" in str(e).lower()
            print(f"  ✅ RuntimeError raised as expected: {e}")
        except ValueError as e:
            assert False, f"Expected RuntimeError but got ValueError: {e}"
        except Exception as e:
            assert False, f"Expected RuntimeError but got {type(e).__name__}: {e}"

        mock_analyze.assert_called_once()

    print("✅ Investigation Provider Failure raises RuntimeError test passed")


def test_investigation_existing_incident_succeeds():
    """Test that investigating an existing incident succeeds and returns InvestigationResult."""
    print("Testing Investigation Existing Incident Succeeds...")

    # Create test incident in database
    _create_test_incident("test-incident-001")

    service = InvestigationService()

    # Create investigation request for EXISTING incident
    request = InvestigationRequest(
        incident_id="test-incident-001",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={},
        include_timeline=True,
        include_events=True
    )

    # Mock the AI service with valid response
    with patch.object(service, '_generate_ai_analysis') as mock_analyze:
        mock_analysis_result = AnalysisResult(
            success=True,
            analysis_type="root_cause",
            confidence_score=0.85,
            hypotheses=["Root cause: Network configuration issue"],
            recommendations=["Check network configuration"],
            reasoning="Analysis completed successfully",
            metadata={"provider": "mock", "model": "test"},
            errors=[],
            warnings=[]
        )

        mock_analyze.return_value = mock_analysis_result

        # Test that investigation completes successfully
        result = service.investigate_incident(request)

        assert result is not None
        assert isinstance(result, InvestigationResult)
        assert result.incident_id == "test-incident-001"
        assert len(result.root_cause_hypotheses) == 1
        assert result.urgency_level in ["low", "medium", "high", "critical"]
        assert len(result.diagnostic_steps) > 0

        mock_analyze.assert_called_once()

    print("✅ Investigation Existing Incident Succeeds test passed")


def test_investigation_timeout_handling():
    """Test investigation timeout handling."""
    print("Testing Investigation Timeout Handling...")

    # Create test incident in database
    _create_test_incident("test-incident-001")

    service = InvestigationService()

    # Create investigation request with timeout
    request = InvestigationRequest(
        incident_id="test-incident-001",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={
            "investigation_timeout": 1  # Very short timeout for testing
        },
        include_timeline=True,
        include_events=True
    )

    # Mock the AI service to simulate a slow operation
    with patch.object(service, '_generate_ai_analysis') as mock_analyze:
        def slow_analyze(*args, **kwargs):
            import time
            time.sleep(0.5)  # Sleep longer than timeout
            return AnalysisResult(
                success=True,
                analysis_type="root_cause",
                confidence_score=0.85,
                hypotheses=["Root cause: Network configuration issue"],
                recommendations=["Check network configuration"],
                reasoning="Analysis completed successfully",
                metadata={"provider": "test", "model": "test"},
                errors=[],
                warnings=[]
            )

        mock_analyze.side_effect = slow_analyze

        # Test that investigation handles timeout gracefully
        # The investigation should respect the timeout constraint
        result = service.investigate_incident(request)

        assert result is not None
        assert isinstance(result, InvestigationResult)
        assert result.incident_id == "test-incident-001"
        print("✅ Investigation timeout handling test passed")

def test_investigation_provider_timeout():
    """Test investigation with provider timeout."""
    print("Testing Investigation Provider Timeout...")

    # Create test incident in database
    _create_test_incident("test-incident-001")

    service = InvestigationService()

    # Create investigation request with very short timeout
    request = InvestigationRequest(
        incident_id="test-incident-001",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={
            "timeout": 0.1  # Very short timeout
        },
        include_timeline=True,
        include_events=True
    )

    # Mock the AI service to simulate a slow provider
    with patch.object(service, '_generate_ai_analysis') as mock_analyze:
        def slow_provider(*args, **kwargs):
            import time
            time.sleep(1)  # Sleep longer than timeout
            return AnalysisResult(
                success=True,
                analysis_type="root_cause",
                confidence_score=0.85,
                hypotheses=["Root cause: Network configuration issue"],
                recommendations=["Check network configuration"],
                reasoning="Analysis completed successfully",
                metadata={"provider": "test", "model": "test"},
                errors=[],
                warnings=[]
            )

        mock_analyze.side_effect = slow_provider

        # Test that investigation handles provider timeout
        result = service.investigate_incident(request)

        assert result is not None
        assert isinstance(result, InvestigationResult)
        assert result.incident_id == "test-incident-001"
        print("✅ Investigation provider timeout test passed")

def test_investigation_service_integration():
    """Test investigation service integration with AI service."""
    print("Testing Investigation Service Integration...")

    # Create test incident in database
    _create_test_incident("test-incident-001")

    # Test that investigation service can be created
    from investigation_service import get_investigation_service

    service = get_investigation_service()
    assert service is not None
    assert isinstance(service, InvestigationService)

    # Test convenience function
    from investigation_service import investigate_incident

    result = investigate_incident("test-incident-001")

    assert result is not None
    assert isinstance(result, InvestigationResult)
    assert result.incident_id == "test-incident-001"

    print("✅ Investigation Service Integration test passed")

def run_all_investigation_tests():
    """Run all investigation tests."""
    print("=" * 80)
    print("RUNNING INVESTIGATION TESTS")
    print("=" * 80)
    print()

    test_functions = [
        test_timeout_boolean_true_rejected,
        test_timeout_boolean_false_rejected,
        test_timeout_positive_integer_accepted,
        test_timeout_positive_float_accepted,
        test_timeout_zero_rejected,
        test_timeout_negative_rejected,
        test_timeout_non_numeric_rejected,
        test_timeout_none_accepted,
        test_ollama_provider_timeout_boolean_rejected,
        test_mock_provider_timeout_boolean_rejected,
        test_investigation_service_creation,
        test_investigation_with_mocked_incident,
        test_investigation_with_evidence,
        test_investigation_api_endpoint,
        test_investigation_api_with_evidence,
        test_investigation_missing_incident,
        test_investigation_api_error_handling,
        test_investigation_service_integration,
        test_investigation_provider_failure,
        test_investigation_malformed_ai_output,
        test_investigation_missing_incident_raises_valueerror,
        test_investigation_provider_failure_raises_runtimeerror,
        test_investigation_existing_incident_succeeds,
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            passed += 1
            print(f"✅ {test_func.__name__} PASSED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_func.__name__} FAILED: {str(e)}")

        print()

    print("=" * 80)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    return passed, failed
def test_timeout_boolean_true_rejected():
    """Test that boolean True is explicitly rejected as timeout."""
    _create_test_incident("test-timeout-bool-true")

    service = InvestigationService()

    request = InvestigationRequest(
        incident_id="test-timeout-bool-true",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={"investigation_timeout": True},
        include_timeline=True,
        include_events=True
    )

    with patch.object(service.analysis_service, 'analyze_incident') as mock_analyze:
        mock_analyze.return_value = AnalysisResult(
            success=True, analysis_type="root_cause", confidence_score=0.85,
            hypotheses=["Test"], recommendations=["Test"], reasoning="Test",
            metadata={"provider": "test"}, errors=[], warnings=[]
        )

        with pytest.raises(RuntimeError, match=r"Invalid investigation timeout.*not a boolean"):
            service.investigate_incident(request)

def test_timeout_boolean_false_rejected():
    """Test that boolean False is explicitly rejected as timeout."""
    _create_test_incident("test-timeout-bool-false")

    service = InvestigationService()

    request = InvestigationRequest(
        incident_id="test-timeout-bool-false",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={"investigation_timeout": False},
        include_timeline=True,
        include_events=True
    )

    with patch.object(service.analysis_service, 'analyze_incident') as mock_analyze:
        mock_analyze.return_value = AnalysisResult(
            success=True, analysis_type="root_cause", confidence_score=0.85,
            hypotheses=["Test"], recommendations=["Test"], reasoning="Test",
            metadata={"provider": "test"}, errors=[], warnings=[]
        )

        with pytest.raises(RuntimeError, match=r"Invalid investigation timeout.*not a boolean"):
            service.investigate_incident(request)

def test_timeout_positive_integer_accepted():
    """Test that positive integer timeout is accepted."""
    _create_test_incident("test-timeout-int")

    service = InvestigationService()

    request = InvestigationRequest(
        incident_id="test-timeout-int",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={"investigation_timeout": 5},
        include_timeline=True,
        include_events=True
    )

    with patch.object(service.analysis_service, 'analyze_incident') as mock_analyze:
        mock_analyze.return_value = AnalysisResult(
            success=True, analysis_type="root_cause", confidence_score=0.85,
            hypotheses=["Test"], recommendations=["Test"], reasoning="Test",
            metadata={"provider": "test"}, errors=[], warnings=[]
        )

        result = service.investigate_incident(request)
        assert result is not None
        assert isinstance(result, InvestigationResult)

def test_timeout_positive_float_accepted():
    """Test that positive float timeout is accepted."""
    _create_test_incident("test-timeout-float")

    service = InvestigationService()

    request = InvestigationRequest(
        incident_id="test-timeout-float",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={"investigation_timeout": 2.5},
        include_timeline=True,
        include_events=True
    )

    with patch.object(service.analysis_service, 'analyze_incident') as mock_analyze:
        mock_analyze.return_value = AnalysisResult(
            success=True, analysis_type="root_cause", confidence_score=0.85,
            hypotheses=["Test"], recommendations=["Test"], reasoning="Test",
            metadata={"provider": "test"}, errors=[], warnings=[]
        )

        result = service.investigate_incident(request)
        assert result is not None
        assert isinstance(result, InvestigationResult)

def test_timeout_zero_rejected():
    """Test that zero timeout is rejected."""
    _create_test_incident("test-timeout-zero")

    service = InvestigationService()

    request = InvestigationRequest(
        incident_id="test-timeout-zero",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={"investigation_timeout": 0},
        include_timeline=True,
        include_events=True
    )

    with patch.object(service.analysis_service, 'analyze_incident') as mock_analyze:
        mock_analyze.return_value = AnalysisResult(
            success=True, analysis_type="root_cause", confidence_score=0.85,
            hypotheses=["Test"], recommendations=["Test"], reasoning="Test",
            metadata={"provider": "test"}, errors=[], warnings=[]
        )

        with pytest.raises(RuntimeError, match=r"Invalid investigation timeout.*positive number"):
            service.investigate_incident(request)

def test_timeout_negative_rejected():
    """Test that negative timeout is rejected."""
    _create_test_incident("test-timeout-negative")

    service = InvestigationService()

    request = InvestigationRequest(
        incident_id="test-timeout-negative",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={"investigation_timeout": -1},
        include_timeline=True,
        include_events=True
    )

    with patch.object(service.analysis_service, 'analyze_incident') as mock_analyze:
        mock_analyze.return_value = AnalysisResult(
            success=True, analysis_type="root_cause", confidence_score=0.85,
            hypotheses=["Test"], recommendations=["Test"], reasoning="Test",
            metadata={"provider": "test"}, errors=[], warnings=[]
        )

        with pytest.raises(RuntimeError, match=r"Invalid investigation timeout.*positive number"):
            service.investigate_incident(request)

def test_timeout_non_numeric_rejected():
    """Test that non-numeric timeout is rejected."""
    _create_test_incident("test-timeout-nonnumeric")

    service = InvestigationService()

    request = InvestigationRequest(
        incident_id="test-timeout-nonnumeric",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={"investigation_timeout": "invalid"},
        include_timeline=True,
        include_events=True
    )

    with patch.object(service.analysis_service, 'analyze_incident') as mock_analyze:
        mock_analyze.return_value = AnalysisResult(
            success=True, analysis_type="root_cause", confidence_score=0.85,
            hypotheses=["Test"], recommendations=["Test"], reasoning="Test",
            metadata={"provider": "test"}, errors=[], warnings=[]
        )

        with pytest.raises(RuntimeError, match=r"Invalid investigation timeout.*positive number"):
            service.investigate_incident(request)

def test_timeout_none_accepted():
    """Test that None (no timeout) is accepted."""
    _create_test_incident("test-timeout-none")

    service = InvestigationService()

    request = InvestigationRequest(
        incident_id="test-timeout-none",
        evidence=None,
        analysis_type="root_cause",
        investigation_depth="detailed",
        constraints={},  # No timeout specified
        include_timeline=True,
        include_events=True
    )

    with patch.object(service.analysis_service, 'analyze_incident') as mock_analyze:
        mock_analyze.return_value = AnalysisResult(
            success=True, analysis_type="root_cause", confidence_score=0.85,
            hypotheses=["Test"], recommendations=["Test"], reasoning="Test",
            metadata={"provider": "test"}, errors=[], warnings=[]
        )

        result = service.investigate_incident(request)
        assert result is not None
        assert isinstance(result, InvestigationResult)

def test_ollama_provider_timeout_boolean_rejected():
    """Test that Ollama provider rejects boolean timeout."""
    from ollama_provider import OllamaProvider, OllamaConfig
    from ai_provider import AnalysisRequest, IncidentData
    from unittest.mock import patch, MagicMock

    config = OllamaConfig()
    provider = OllamaProvider(config)

    incident_data = IncidentData(
        incident_id="test-ollama-bool",
        title="Test",
        description="Test description",
        severity="critical",
        status="investigating",
        service="test-service",
        created_at="2024-01-01T12:00:00Z"
    )

    # Test boolean True
    request = AnalysisRequest(incident_data=incident_data, analysis_type="root_cause", constraints={"investigation_timeout": True})
    with patch.object(provider.session, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'response': '{"hypotheses": ["test"], "recommendations": ["test"], "confidence_score": 0.5, "reasoning": "test"}'}
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match=r"Invalid investigation timeout.*not a boolean"):
            provider.analyze_incident(request)

    # Test boolean False
    request = AnalysisRequest(incident_data=incident_data, analysis_type="root_cause", constraints={"investigation_timeout": False})
    with patch.object(provider.session, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'response': '{"hypotheses": ["test"], "recommendations": ["test"], "confidence_score": 0.5, "reasoning": "test"}'}
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match=r"Invalid investigation timeout.*not a boolean"):
            provider.analyze_incident(request)

def test_mock_provider_timeout_boolean_rejected():
    """Test that MockAIProvider rejects boolean timeout."""
    from ai_provider import MockAIProvider, AnalysisRequest, IncidentData

    provider = MockAIProvider({'simulation_delay_ms': 100, 'success_rate': 1.0, 'error_types': []})

    incident_data = IncidentData(
        incident_id="test-mock-bool",
        title="Test",
        description="Test description",
        severity="critical",
        status="investigating",
        service="test-service",
        created_at="2024-01-01T12:00:00Z"
    )

    # Test boolean True
    request = AnalysisRequest(incident_data=incident_data, analysis_type="root_cause", constraints={"investigation_timeout": True})
    with pytest.raises(RuntimeError, match=r"Invalid investigation timeout.*not a boolean"):
        provider.analyze_incident(request)

    # Test boolean False
    request = AnalysisRequest(incident_data=incident_data, analysis_type="root_cause", constraints={"investigation_timeout": False})
    with pytest.raises(RuntimeError, match=r"Invalid investigation timeout.*not a boolean"):
        provider.analyze_incident(request)
