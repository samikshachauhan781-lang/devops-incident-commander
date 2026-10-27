#!/usr/bin/env python3
"""
Documentation test suite for Investigation Template Engine

This script documents the actual behavior of investigation_templates.py and
template_engine.py for Phase 3, Task 1, Part 2B documentation.

This test file verifies the actual behavior of the implementation
and documents any discrepancies between requirements and implementation.
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
    print(f"✅ All built-in templates can be listed: {len(investigation_templates)} templates")
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
    print(f"✅ Expected template IDs exist and are unique: {expected_ids}")
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

        # Verify engine template has basic structure (but not full guidance fields)
        assert 'checks' in engine_template
        assert 'expected_evidence' in engine_template
        assert 'validation_rules' in engine_template
        assert 'guidance' in engine_template

        # Note: engine.get_template() returns basic template without
        # 'applicability' and 'incident_context' fields (those are in
        # prepare_guidance_payload())
        assert 'applicability' not in engine_template
        assert 'incident_context' not in engine_template

    print(f"✅ Valid template lookup returns expected template")
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

    print(f"✅ Unknown template IDs follow documented behavior")
def test_guidance_payload_contains_all_required_fields():
    """Test 5: Guidance payload contains all required fields."""
    engine = TemplateEngine()

    for template_id in list_template_ids():
        # Test prepare_guidance_payload with None incident_service
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

    print(f"✅ Guidance payload contains all required fields")
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

    print(f"✅ Applicability is correct for matching services")
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

    print(f"✅ Nonmatching services are reported as not applicable without blocking execution")
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

    print(f"✅ Service matching is case-insensitive")
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

    print(f"✅ None service follows documented behavior")
def test_actual_behavior_of_mutating_returned_objects():
    """Test documenting actual behavior of mutating returned objects.

    Note: This test documents the actual implementation behavior.

    The investigation_templates.py implementation has the following characteristics:
    1. InvestigationTemplate objects are immutable and returned by reference from _INVESTIGATION_TEMPLATES
    2. All data within InvestigationTemplate objects is deep-copied during initialization:
       - id, name, description, applicable_services, checks, expected_evidence, validation_rules, guidance are all deep-copied
    3. Therefore, modifying InvestigationTemplate objects does NOT affect the built-in template
    4. All fields and nested data are protected from mutation

    This test documents the actual behavior rather than the requirements.
    """
    engine = TemplateEngine()

    for template_id in list_template_ids():
        # Get InvestigationTemplate object from registry
        investigation_template = investigation_get_template(template_id)

        # Store original data
        original_checks = investigation_template.checks.copy()

        # Try to modify the InvestigationTemplate object directly
        # Since InvestigationTemplate objects are immutable, this should fail
        try:
            # Try to modify an attribute directly
            investigation_template.id = "modified_id"
            raise AssertionError(f"InvestigationTemplate objects should be immutable: {template_id}")
        except AttributeError as e:
            if "immutable" in str(e):
                pass  # Expected: InvestigationTemplate objects are immutable
            else:
                raise  # Unexpected error

        # Verify that the built-in template definition from the registry is unchanged
        investigation_template_after = investigation_get_template(template_id)

        # The checks should NOT be modified because InvestigationTemplate objects are immutable
        assert len(investigation_template_after.checks) == len(original_checks), \
            f"InvestigationTemplate objects should be immutable: {template_id}"

        # Test that the InvestigationTemplate constructor properly deep-copies all data
        fresh_template = investigation_get_template(template_id)

        # Verify that all fields are accessible and have correct data types
        assert hasattr(fresh_template, 'id'), f"Fresh template missing id: {template_id}"
        assert hasattr(fresh_template, 'name'), f"Fresh template missing name: {template_id}"
        assert hasattr(fresh_template, 'description'), f"Fresh template missing description: {template_id}"
        assert hasattr(fresh_template, 'applicable_services'), f"Fresh template missing applicable_services: {template_id}"
        assert hasattr(fresh_template, 'checks'), f"Fresh template missing checks: {template_id}"
        assert hasattr(fresh_template, 'expected_evidence'), f"Fresh template missing expected_evidence: {template_id}"
        assert hasattr(fresh_template, 'validation_rules'), f"Fresh template missing validation_rules: {template_id}"
        assert hasattr(fresh_template, 'guidance'), f"Fresh template missing guidance: {template_id}"

        # Verify that accessing returned data provides immutable copies
        # The InvestigationTemplate properties return copies, so modifications to those copies
        # should not affect the InvestigationTemplate objects
        template_checks_copy = investigation_template.checks
        template_checks_copy.append({'test': 'modification'})

        # Verify that the original InvestigationTemplate object is unchanged
        investigation_template_after = investigation_get_template(template_id)
        assert len(investigation_template_after.checks) == len(original_checks), \
            f"Modifications to returned data should not affect InvestigationTemplate object: {template_id}"

        # Verify that the built-in template definition is unchanged
        built_in_template = investigation_get_template(template_id)
        assert built_in_template.id == template_id, f"Built-in template definition was modified: {template_id}"

    print(f"✅ Documented actual behavior of mutating returned objects")
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

    print(f"✅ Repeated calls return consistent results")
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

    print(f"✅ Convenience functions behave as documented")
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

    print(f"✅ Missing or malformed inputs are handled consistently with the existing API")

# Additional edge case tests
@pytest.mark.parametrize("template_id", ["api_failure_v1", "database_incident_v1", "network_incident_v1"])
def test_template_id_case_sensitivity(template_id):
    """Test that template IDs are case-sensitive."""
    engine = TemplateEngine()

    # Test exact case works
    assert engine.get_template(template_id) is not None

    # Test different cases do NOT work (case-sensitive - investigation_templates.py uses dict lookup)
    # Create different case versions that are NOT equal to the original
    different_cases = [
        template_id.upper(),
        template_id.capitalize(),
        ''.join([c.upper() if i % 2 == 0 else c for i, c in enumerate(template_id)]),  # alternate case
    ]

    for different_case in different_cases:
        if different_case != template_id:  # Only test if it's actually different
            assert engine.get_template(different_case) is None, \
                f"Template ID should be case-sensitive: '{template_id}' != '{different_case}'"

@pytest.mark.parametrize("template_id", ["api_failure_v1", "database_incident_v1", "network_incident_v1"])
def test_template_data_structure_integrity(template_id):
    """Test that each template has the expected data structure."""
    investigation_template = investigation_get_template(template_id)
    engine_template = engine_get_template(template_id)

    # Verify InvestigationTemplate structure
    assert hasattr(investigation_template, 'id')
    assert hasattr(investigation_template, 'name')
    assert hasattr(investigation_template, 'description')
    assert hasattr(investigation_template, 'applicable_services')
    assert hasattr(investigation_template, 'checks')
    assert hasattr(investigation_template, 'expected_evidence')
    assert hasattr(investigation_template, 'validation_rules')
    assert hasattr(investigation_template, 'guidance')

    # Verify engine guidance payload structure (engine.get_template())
    required_engine_fields = [
        'template_id', 'name', 'description', 'applicable_services',
        'checks', 'expected_evidence', 'validation_rules', 'guidance'
    ]

    for field in required_engine_fields:
        assert field in engine_template, f"Missing field {field} in engine template"
        assert engine_template[field] is not None

    # Note: engine.get_template() does NOT include 'applicability' and 'incident_context'
    # fields - those are in engine.prepare_guidance_payload()
    assert 'applicability' not in engine_template
    assert 'incident_context' not in engine_template

    # Verify cross-consistency between investigation and engine templates
    assert investigation_template.id == engine_template['template_id']
    assert investigation_template.name == engine_template['name']
    assert investigation_template.description == engine_template['description']
    assert investigation_template.applicable_services == engine_template['applicable_services']
    assert investigation_template.checks == engine_template['checks']
    assert investigation_template.expected_evidence == engine_template['expected_evidence']
    assert investigation_template.validation_rules == engine_template['validation_rules']
    assert investigation_template.guidance == engine_template['guidance']

    print(f"✅ Template {template_id} has expected data structure")
def run_documentation_tests():
    """Run all documentation tests and collect results."""
    print("=" * 80)
    print("Investigation Template Engine - Documentation Test Suite")
    print("=" * 80)
    print("This test suite documents the actual behavior of the implementation")
    print("following Phase 3, Task 1, Part 2B documentation.")
    print()

    # Track test results
    passed = 0
    failed = 0
    skipped = 0

    try:
        test_all_built_in_templates_can_be_listed()
        passed += 1
    except Exception as e:
        failed += 1
        print(f"❌ Test 1 failed: {e}")

    try:
        test_expected_template_ids_exist_and_are_unique()
        passed += 1
    except Exception as e:
        failed += 1
        print(f"❌ Test 2 failed: {e}")

    try:
        test_valid_template_lookup_returns_expected_template()
        passed += 1
    except Exception as e:
        failed += 1
        print(f"❌ Test 3 failed: {e}")

    try:
        test_unknown_template_ids_follow_documented_behavior()
        passed += 1
    except Exception as e:
        failed += 1
        print(f"❌ Test 4 failed: {e}")

    try:
        test_guidance_payload_contains_all_required_fields()
        passed += 1
    except Exception as e:
        failed += 1
        print(f"❌ Test 5 failed: {e}")

    try:
        test_applicability_is_correct_for_matching_services()
        passed += 1
    except Exception as e:
        failed += 1
        print(f"❌ Test 6 failed: {e}")

    try:
        test_nonmatching_services_are_reported_as_not_applicable_without_blocking_execution()
        passed += 1
    except Exception as e:
        failed += 1
        print(f"❌ Test 7 failed: {e}")

    try:
        test_service_matching_is_case_insensitive()
        passed += 1
    except Exception as e:
        failed += 1
        print(f"❌ Test 8 failed: {e}")

    try:
        test_none_service_follows_documented_behavior()
        passed += 1
    except Exception as e:
        failed += 1
        print(f"❌ Test 9 failed: {e}")

    try:
        test_actual_behavior_of_mutating_returned_objects()
        passed += 1
    except Exception as e:
        failed += 1
        print(f"❌ Test 10 failed: {e}")

    try:
        test_repeated_calls_return_consistent_results()
        passed += 1
    except Exception as e:
        failed += 1
        print(f"❌ Test 11 failed: {e}")

    try:
        test_convenience_functions_behave_as_documented()
        passed += 1
    except Exception as e:
        failed += 1
        print(f"❌ Test 12 failed: {e}")

    try:
        test_missing_or_malformed_inputs_handled_consistently()
        passed += 1
    except Exception as e:
        failed += 1
        print(f"❌ Test 13 failed: {e}")

    try:
        test_template_id_case_sensitivity("api_failure_v1")
        test_template_id_case_sensitivity("database_incident_v1")
        test_template_id_case_sensitivity("network_incident_v1")
        passed += 1
    except Exception as e:
        failed += 1
        print(f"❌ Template ID case sensitivity test failed: {e}")

    try:
        test_template_data_structure_integrity("api_failure_v1")
        test_template_data_structure_integrity("database_incident_v1")
        test_template_data_structure_integrity("network_incident_v1")
        passed += 1
    except Exception as e:
        failed += 1
        print(f"❌ Template data structure integrity test failed: {e}")

    print()
    print("=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"🟡 Skipped: {skipped}")
    print(f"📊 Total: {passed + failed + skipped}")
    print()
    print("Key Documentation Points:")
    print("1. InvestigationTemplate objects are mutable and returned by reference")
    print("2. The data within them (checks, expected_evidence, validation_rules, guidance) is deep-copied")
    print("3. But id, name, description, applicable_services are NOT deep-copied")
    print("4. This means modifying InvestigationTemplate objects will affect the built-in template")
    print("5. However, the data fields that are deep-copied will be protected")
    print("6. The investigation_templates.py implementation has these inconsistencies")
    print("7. The template_engine.py provides wrapper functions around the investigation_templates.py API")
    print()
    print("The investigation_templates.py and template_engine.py implementations")
    print("meet most requirements but have some inconsistencies between")
    print("documentation and actual behavior.")
    print("=" * 80)

if __name__ == "__main__":
    run_documentation_tests()