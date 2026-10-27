#!/usr/bin/env python3
"""
Simple template loading tests for InvestigationService
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from investigation_service import InvestigationService

def test_template_loading_simple():
    """Simple test to verify template loading functionality."""
    print("Testing InvestigationService template loading...")

    service = InvestigationService()

    # Test 1: No template_id should return None
    print("\nTest 1: No template_id")
    result = service._load_template_guidance(None, "api")
    assert result is None
    print("✅ Pass: None template_id returns None")

    # Test 2: Unknown template should raise ValueError
    print("\nTest 2: Unknown template")
    try:
        result = service._load_template_guidance("nonexistent_template", "api")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Template 'nonexistent_template' not found" in str(e)
        print(f"✅ Pass: Unknown template raises ValueError: {e}")

    # Test 3: Valid template with matching service
    print("\nTest 3: Valid template with matching service (api with api_failure_v1)")
    result = service._load_template_guidance("api_failure_v1", "api")
    assert result is not None
    assert result['template_id'] == 'api_failure_v1'
    assert result['applicability']['is_applicable'] == True
    print(f"✅ Pass: Template loaded successfully with applicability: {result['applicability']['is_applicable']}")

    # Test 4: Valid template with non-matching service
    print("\nTest 4: Valid template with non-matching service (web-service with api_failure_v1)")
    result = service._load_template_guidance("api_failure_v1", "web-service")
    assert result is None
    print("✅ Pass: Non-matching service returns None (no guidance)")

    # Test 5: Case-insensitive service matching
    print("\nTest 5: Case-insensitive service matching")
    result = service._load_template_guidance("api_failure_v1", "API")
    assert result is not None
    assert result['applicability']['is_applicable'] == True
    print(f"✅ Pass: Case-insensitive matching works: {result['applicability']['is_applicable']}")

    print("\n✅ All simple template loading tests passed!")

if __name__ == "__main__":
    test_template_loading_simple()