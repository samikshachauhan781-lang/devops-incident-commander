#!/usr/bin/env python3
"""
Test suite for Investigation Template Engine

This script tests the existing investigation_templates.py and template_engine.py
implementations as specified in Phase 3, Task 1, Part 2B.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest
from typing import Dict, Any, List

from investigation_templates import (
    InvestigationTemplate,
    get_all_templates,
    get_template as investigation_get_template,
    template_exists,
    list_template_ids
)
from template_engine import (
    TemplateEngine,
    get_template_engine,
    get_template as engine_get_template,
    list_templates as engine_list_templates,
    is_template_available as engine_is_template_available
)
def test_all_built_in_templates_can_be_listed():
    """Test 1: All built-in templates can be listed."""
    # Test via investigation_templates module
    investigation_templates = get_all_templates()
    assert isinstance(investigation_templates, list)
    assert len(investigation_templates) > 0

    # Test via template_engine module
    engine = TemplateEngine()
    engine_templates = engine.list_templates()
    assert isinstance(engine_templates, list)
    assert len(engine_templates) > 0

    # Both methods should return the same count
    assert len(investigation_templates) == len(engine_templates)
def test_expected_template_ids_exist_and_are_unique():
    """Test 2: Expected template IDs exist and are unique."""
    # Get template IDs via investigation_templates module
    investigation_ids = set(list_template_ids())

    # Get template IDs via template_engine module
    engine_ids = set(TemplateEngine().list_templates())

    # Both should contain the expected IDs
    expected_ids = {"api_failure_v1", "database_incident_v1", "network_incident_v1"}

    assert investigation_ids == expected_ids
    assert engine_ids == expected_ids

    # Test via investigation_templates module
    for template_id in expected_ids:
        template = investigation_get_template(template_id)
        assert template is not None, f"Template {template_id} should exist"
        assert template.id == template_id

    # Test via template_engine module
    for template_id in expected_ids:
        template = engine_get_template(template_id)
        assert template is not None, f"Template {template_id} should exist via engine"
        assert template['template_id'] == template_id

    # Verify uniqueness
    assert len(investigation_ids) == len(expected_ids)
    assert len(engine_ids) == len(expected_ids)
def test_valid_template_lookup_returns_expected_template():
    """Test 3: Valid template lookup returns the expected template."""
    engine = TemplateEngine()

    # Test each built-in template
    for template_id in list_template_ids():
        # Test via investigation_templates module
        investigation_template = investigation_get_template(template_id)
        assert investigation_template is not None
        assert investigation_template.id == template_id
        assert investigation_template.name is not None
        assert investigation_template.description is not None
        assert investigation_template.applicable_services is not None
        assert investigation_template.checks is not None
        assert investigation_template.expected_evidence is not None
        assert investigation_template.validation_rules is not None
        assert investigation_template.guidance is not None

        # Test via template_engine module
        engine_template = engine.get_template(template_id)
        assert engine_template is not None
        assert engine_template['template_id'] == template_id
        assert engine_template['name'] == investigation_template.name
        assert engine_template['description'] == investigation_template.description
        assert engine_template['applicable_services'] == investigation_template.applicable_services

        # Verify structural consistency
        assert 'checks' in engine_template
        assert 'expected_evidence' in engine_template
        assert 'validation_rules' in engine_template
        assert 'guidance' in engine_template
def test_unknown_template_ids_follow_documented_behavior():
    """Test 4: Unknown template IDs follow the documented return/error behavior."""
    engine = TemplateEngine()

    # Test via investigation_templates module
    unknown_investigation_template = investigation_get_template("nonexistent_template_id")
    assert unknown_investigation_template is None

    # Test via template_engine module
    unknown_engine_template = engine.get_template("nonexistent_template_id")
    assert unknown_engine_template is None

    # Test template_exists function
    assert not template_exists("nonexistent_template_id")
    assert not engine.is_template_available("nonexistent_template_id")

    # Test convenience functions
    assert engine_get_template("nonexistent_template_id") is None
    assert not engine_is_template_available("nonexistent_template_id")

    # Test check_applicability with unknown template
    applicability_result = engine.check_applicability("nonexistent_template_id", "api")
    assert applicability_result['template_id'] == "nonexistent_template_id"
    assert applicability_result['applicable'] is False
    assert applicability_result['incident_service'] == "api"
    assert "Template 'nonexistent_template_id' does not exist" in applicability_result['reason']
def test_guidance_payload_contains_all_required_fields():
    """Test 5: Guidance payload contains all required fields."""
    engine = TemplateEngine()

    for template_id in list_template_ids():
        # Test without incident_service
        guidance_payload = engine.prepare_guidance_payload(template_id)
        assert guidance_payload is not None

        # Verify all required fields are present
        required_fields = [
            'template_id', 'name', 'description', 'applicable_services',
            'checks', 'expected_evidence', 'validation_rules', 'guidance',
            'applicability', 'incident_context'
        ]

        for field in required_fields:
            assert field in guidance_payload, f"Guidance payload missing field '{field}' for template {template_id}"

        # Verify field types and structure
        assert isinstance(guidance_payload['template_id'], str)
        assert isinstance(guidance_payload['name'], str)
        assert isinstance(guidance_payload['description'], str)
        assert isinstance(guidance_payload['applicable_services'], list)
        assert isinstance(guidance_payload['checks'], list)
        assert isinstance(guidance_payload['expected_evidence'], list)
        assert isinstance(guidance_payload['validation_rules'], dict)
        assert isinstance(guidance_payload['guidance'], dict)
        assert isinstance(guidance_payload['applicability'], dict)
        assert isinstance(guidance_payload['incident_context'], dict)

        # Test with incident_service
        guidance_payload_with_service = engine.prepare_guidance_payload(template_id, "api")
        assert guidance_payload_with_service is not None
        assert guidance_payload_with_service['incident_context']['service'] == "api"
        assert guidance_payload_with_service['incident_context']['can_proceed_without_service'] is False

        # Test with None incident_service
        guidance_payload_none_service = engine.prepare_guidance_payload(template_id, None)
        assert guidance_payload_none_service is not None
        assert guidance_payload_none_service['incident_context']['service'] is None
        assert guidance_payload_none_service['incident_context']['can_proceed_without_service'] is True
def test_applicability_is_correct_for_matching_services():
    """Test 6: Applicability is correct for matching services."""
    engine = TemplateEngine()

    # Test each template with its applicable services
    for template_id in list_template_ids():
        investigation_template = investigation_get_template(template_id)

        # Test each service in the template's applicable_services
        for service in investigation_template.applicable_services:
            applicability_result = engine.check_applicability(template_id, service)

            assert applicability_result['template_id'] == template_id
            assert applicability_result['incident_service'] == service
            assert applicability_result['applicable'] is True
            assert service in applicability_result['matching_services']
            assert len(applicability_result['matching_services']) == 1

            # Verify reason contains information about the match
            assert 'applies to service' in applicability_result['reason']
            assert service in applicability_result['reason']
def test_nonmatching_services_are_reported_as_not_applicable_without_blocking_execution():
    """Test 7: Nonmatching services are reported as not applicable without blocking execution."""
    engine = TemplateEngine()

    # For each template, test with a service that is not in its applicable_services
    for template_id in list_template_ids():
        investigation_template = investigation_get_template(template_id)

        # Find a service that is not applicable
        non_applicable_services = {"web", "mobile", "devops"}

        for service in non_applicable_services:
            # This should not raise an exception, just return False
            applicability_result = engine.check_applicability(template_id, service)

            assert applicability_result['template_id'] == template_id
            assert applicability_result['incident_service'] == service
            assert applicability_result['applicable'] is False
            assert service not in applicability_result['matching_services']

            # Should still list all applicable services as matching
            assert set(applicability_result['matching_services']) == set(investigation_template.applicable_services)

            # Should indicate why it doesn't apply
            assert 'does not apply' in applicability_result['reason']
            assert service in applicability_result['reason']
def test_service_matching_is_case_insensitive():
    """Test 8: Service matching is case-insensitive."""
    engine = TemplateEngine()

    for template_id in list_template_ids():
        investigation_template = investigation_get_template(template_id)

        for service in investigation_template.applicable_services:
            # Test with different cases of the same service
            for case_variant in [service.lower(), service.upper(), service.capitalize()]:
                applicability_result = engine.check_applicability(template_id, case_variant)

                assert applicability_result['applicable'] is True, \
                    f"Service '{case_variant}' should match '{service}' case-insensitively"
                assert service in applicability_result['matching_services']

                # Test with non-matching service (should be False)
                non_matching = "WEB"
                if non_matching.lower() != service.lower():
                    non_applicability = engine.check_applicability(template_id, non_matching)
                    assert non_applicability['applicable'] is False
def test_none_service_follows_documented_behavior():
    """Test 9: None service follows the documented behavior."""
    engine = TemplateEngine()

    for template_id in list_template_ids():
        # Test with None service
        applicability_result = engine.check_applicability(template_id, None)

        assert applicability_result['template_id'] == template_id
        assert applicability_result['incident_service'] is None
        assert applicability_result['applicable'] is True
        assert set(applicability_result['matching_services']) == set(
            investigation_get_template(template_id).applicable_services
        )

        # Should indicate it's applicable without service restriction
        assert 'applicable without service restriction' in applicability_result['reason']

        # Test guidance payload with None service
        guidance_payload = engine.prepare_guidance_payload(template_id, None)
        assert guidance_payload is not None
        assert guidance_payload['incident_context']['service'] is None
        assert guidance_payload['incident_context']['can_proceed_without_service'] is True
def test_mutating_returned_objects_does_not_mutate_built_in_definitions():
    """Test 10: Mutating returned templates or guidance payloads does not mutate built-in definitions."""
    engine = TemplateEngine()

    for template_id in list_template_ids():
        # Test InvestigationTemplate object - should be immutable
        investigation_template = investigation_get_template(template_id)
        original_name = investigation_template.name

        # Try to modify the InvestigationTemplate object - should fail because it's immutable
        try:
            investigation_template.name = "MODIFIED_NAME"
            raise AssertionError(f"InvestigationTemplate objects should be immutable: {template_id}")
        except AttributeError as e:
            if "immutable" in str(e):
                pass  # Expected: InvestigationTemplate objects are immutable
            else:
                raise  # Unexpected error

        # Verify the change didn't affect the built-in template
        assert investigation_get_template(template_id).name == original_name, \
            f"Modifying investigation template {template_id} should not affect built-in definition"

        # Test engine guidance payload - engine.get_template() returns basic structure (without applicability and incident_context)
        guidance_payload = engine.get_template(template_id)
        original_name = guidance_payload['name']

        # Try to modify nested structures in guidance payload
        guidance_payload['name'] = "MODIFIED_NAME"
        guidance_payload['applicable_services'].append("MODIFIED_SERVICE")
        guidance_payload['checks'].append({"modified": True})
        guidance_payload['expected_evidence'].append("MODIFIED_EVIDENCE")
        guidance_payload['validation_rules']['modified'] = True
        guidance_payload['guidance']['modified'] = True
        # Note: applicability and incident_context fields are not in engine.get_template() output

        # Verify the built-in template is unchanged
        investigation_template = investigation_get_template(template_id)
        assert investigation_template.name == original_name
        assert "MODIFIED_SERVICE" not in investigation_template.applicable_services
        assert not any(check.get('modified') for check in investigation_template.checks)
        assert "MODIFIED_EVIDENCE" not in investigation_template.expected_evidence
        assert 'modified' not in investigation_template.validation_rules
        assert 'modified' not in investigation_template.guidance

        # Test full guidance payload with mutations
        full_guidance_payload = engine.prepare_guidance_payload(template_id, "api")
        original_name = full_guidance_payload['name']

        # Modify nested structures in full payload
        full_guidance_payload['name'] = "MODIFIED_FULL_NAME"
        full_guidance_payload['applicable_services'].append("MODIFIED_FULL_SERVICE")
        full_guidance_payload['checks'][0]['modified'] = True
        full_guidance_payload['expected_evidence'][0] = "MODIFIED_FULL_EVIDENCE"
        full_guidance_payload['validation_rules']['modified'] = True
        full_guidance_payload['guidance']['modified'] = True
        full_guidance_payload['applicability']['modified'] = True
        full_guidance_payload['incident_context']['modified'] = True

        # Verify the built-in template is still unchanged
        investigation_template = investigation_get_template(template_id)
        assert investigation_template.name == original_name
        assert "MODIFIED_FULL_SERVICE" not in investigation_template.applicable_services
        assert not any(check.get('modified') for check in investigation_template.checks)
        assert "MODIFIED_FULL_EVIDENCE" not in investigation_template.expected_evidence
        assert 'modified' not in investigation_template.validation_rules
        assert 'modified' not in investigation_template.guidance
def test_repeated_calls_return_consistent_results():
    """Test 11: Repeated calls return consistent results."""
    engine = TemplateEngine()

    for template_id in list_template_ids():
        # Test get_template consistency
        template1 = engine.get_template(template_id)
        template2 = engine.get_template(template_id)

        assert template1 == template2, f"Repeated get_template calls should return same result for {template_id}"

        # Test list_templates consistency
        templates1 = engine.list_templates()
        templates2 = engine.list_templates()

        assert templates1 == templates2, f"Repeated list_templates calls should return same result"

        # Test check_applicability consistency with same parameters
        applicability1 = engine.check_applicability(template_id, "api")
        applicability2 = engine.check_applicability(template_id, "api")

        assert applicability1 == applicability2, f"Repeated check_applicability calls should return same result for {template_id}"

        # Test prepare_guidance_payload consistency
        payload1 = engine.prepare_guidance_payload(template_id, "api")
        payload2 = engine.prepare_guidance_payload(template_id, "api")

        assert payload1 == payload2, f"Repeated prepare_guidance_payload calls should return same result for {template_id}"

        # Test convenience functions consistency
        convenience1 = engine_get_template(template_id)
        convenience2 = engine_get_template(template_id)

        assert convenience1 == convenience2, f"Repeated convenience function calls should return same result for {template_id}"
def test_convenience_functions_behave_as_documented():
    """Test 12: Convenience functions behave as documented."""
    # Test module-level convenience functions
    for template_id in list_template_ids():
        # Test get_template (convenience function)
        template_via_convenience = engine_get_template(template_id)
        assert template_via_convenience is not None
        assert template_via_convenience['template_id'] == template_id

        # Test list_templates (convenience function)
        templates_via_convenience = engine_list_templates()
        assert template_id in templates_via_convenience

        # Test is_template_available (convenience function)
        available_via_convenience = engine_is_template_available(template_id)
        assert available_via_convenience is True

        # Test is_template_available for non-existent template
        assert engine_is_template_available("nonexistent_template_id") is False

        # Test get_template for non-existent template
        assert engine_get_template("nonexistent_template_id") is None

    # Test get_template_engine function
    engine1 = get_template_engine()
    engine2 = get_template_engine()

    # Should return the same instance (singleton)
    assert engine1 is engine2
    assert isinstance(engine1, TemplateEngine)
def test_missing_or_malformed_inputs_handled_consistently():
    """Test 13: Missing or malformed inputs are handled consistently with the existing API."""
    engine = TemplateEngine()

    # Test with empty string
    assert engine.get_template("") is None
    assert not engine.is_template_available("")

    applicability_result = engine.check_applicability("", "api")
    assert applicability_result['applicable'] is False
    assert "Template '' does not exist" in applicability_result['reason']

    # Test with whitespace-only string
    assert engine.get_template("   ") is None
    assert not engine.is_template_available("   ")

    # Test with very long string
    long_id = "a" * 1000
    assert engine.get_template(long_id) is None
    assert not engine.is_template_available(long_id)

    # Test with numeric string (should be treated as string)
    numeric_id = "12345"
    assert engine.get_template(numeric_id) is None
    assert not engine.is_template_available(numeric_id)

    # Test consistency with investigation_templates module
    assert investigation_get_template("") is None
    assert investigation_get_template("   ") is None
    assert investigation_get_template(long_id) is None
    assert investigation_get_template(numeric_id) is None

    # Test that non-applicable service with valid template still works
    applicability_result = engine.check_applicability("api_failure_v1", "nonexistent_service")
    assert applicability_result['applicable'] is False
    assert applicability_result['incident_service'] == "nonexistent_service"

    # Test None service with valid template
    applicability_result_none = engine.check_applicability("api_failure_v1", None)
    assert applicability_result_none['applicable'] is True
    assert applicability_result_none['incident_service'] is None

# Additional edge case tests
@pytest.mark.parametrize("template_id", ["api_failure_v1", "database_incident_v1", "network_incident_v1"])
def test_template_data_structure_integrity(template_id):
    """Test that each template has the expected data structure."""
    investigation_template = investigation_get_template(template_id)

    # Create engine instance to use prepare_guidance_payload
    engine = TemplateEngine()
    engine_template = engine.prepare_guidance_payload(template_id, "api")

    # Verify InvestigationTemplate structure
    assert hasattr(investigation_template, 'id')
    assert hasattr(investigation_template, 'name')
    assert hasattr(investigation_template, 'description')
    assert hasattr(investigation_template, 'applicable_services')
    assert hasattr(investigation_template, 'checks')
    assert hasattr(investigation_template, 'expected_evidence')
    assert hasattr(investigation_template, 'validation_rules')
    assert hasattr(investigation_template, 'guidance')

    # Verify engine guidance payload structure (complete guidance payload)
    required_engine_fields = [
        'template_id', 'name', 'description', 'applicable_services',
        'checks', 'expected_evidence', 'validation_rules', 'guidance',
        'applicability', 'incident_context'
    ]

    for field in required_engine_fields:
        assert field in engine_template, f"Missing field {field} in engine template"
        assert engine_template[field] is not None

    # Verify cross-consistency between investigation and engine templates
    assert investigation_template.id == engine_template['template_id']
    assert investigation_template.name == engine_template['name']
    assert investigation_template.description == engine_template['description']
    assert investigation_template.applicable_services == engine_template['applicable_services']
    assert investigation_template.checks == engine_template['checks']
    assert investigation_template.expected_evidence == engine_template['expected_evidence']
    assert investigation_template.validation_rules == engine_template['validation_rules']
    assert investigation_template.guidance == engine_template['guidance']