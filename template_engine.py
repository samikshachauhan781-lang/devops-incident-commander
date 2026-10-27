"""
Template Engine for DevOps Incident Commander

This module provides a minimal template engine interface for investigation
templates. It safely retrieves and prepares investigation template guidance
without executing commands, accessing external systems, or integrating with
the investigation workflow.

The engine provides:
- Retrieval of investigation templates by ID
- Listing of available templates
- Applicability checking based on incident service
- Structured guidance payloads for investigation planning
- Protection against mutation of built-in template definitions

Author: DevOps Incident Commander Team
Date: 2026-10-22
Version: 1.0
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import investigation_templates as templates
class TemplateEngine:
    """
    Minimal template engine for investigation templates.

    This engine provides safe access to built-in investigation templates,
    preparing structured guidance for investigation planning while protecting
    the underlying template definitions from mutation.

    The engine does not execute commands, access external systems, or integrate
    with the investigation workflow. It only provides template retrieval and
    applicability checking capabilities.

    Attributes:
        templates_module: Reference to the investigation_templates module
    """

    def __init__(self):
        """Initialize the template engine."""
        self.templates_module = templates

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an investigation template by ID and prepare guidance payload.

        Args:
            template_id: The unique identifier of the template to retrieve.

        Returns:
            Structured guidance payload containing template information
            if the template exists, None if not found.

        The returned payload is immutable and cannot be used to modify
            the built-in template definitions.

        Example:
            >>> engine = TemplateEngine()
            >>> guidance = engine.get_template("api_failure_v1")
            >>> if guidance:
            ...     print(guidance['name'])
            'API Service Failure'
        """
        # Retrieve the template object using the public API
        template = self.templates_module.get_template(template_id)

        if template is None:
            return None

        # Create a structured guidance payload with mutable copies for safe modification
        guidance_payload = {
            'template_id': template.id,
            'name': template.name,
            'description': template.description,
            'applicable_services': list(template.applicable_services),
            'checks': [dict(check) for check in template.checks],
            'expected_evidence': list(template.expected_evidence),
            'validation_rules': dict(template.validation_rules),
            'guidance': dict(template.guidance)
        }

        return guidance_payload

    def list_templates(self) -> List[str]:
        """
        List all available template IDs.

        Returns:
            List of template IDs (strings) that are available for use.

        Example:
            >>> engine = TemplateEngine()
            >>> template_ids = engine.list_templates()
            >>> print(template_ids)
            ['api_failure_v1', 'database_incident_v1', 'network_incident_v1']
        """
        return self.templates_module.list_template_ids()

    def is_template_available(self, template_id: str) -> bool:
        """
        Check if a template ID is available.

        Args:
            template_id: The template ID to check.

        Returns:
            True if the template exists and is available, False otherwise.

        Example:
            >>> engine = TemplateEngine()
            >>> available = engine.is_template_available("api_failure_v1")
            >>> print(available)
            True
        """
        return self.templates_module.template_exists(template_id)

    def check_applicability(
        self,
        template_id: str,
        incident_service: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if a template is applicable to an incident based on service.

        Args:
            template_id: The template ID to check.
            incident_service: The service field from the incident (optional).

        Returns:
            Dictionary containing:
            - 'applicable': bool indicating if template applies
            - 'template_id': the template ID checked
            - 'incident_service': the incident service that was checked
            - 'matching_services': list of services the template applies to
            - 'reason': description of why the template does or doesn't apply

        Note:
            This function only performs applicability checking and does not
            enforce any validation rules or block investigations. It provides
            information about template suitability for planning purposes.

        Example:
            >>> engine = TemplateEngine()
            >>> result = engine.check_applicability("api_failure_v1", "api")
            >>> print(result['applicable'])
            True
        """
        # Get the template using the public API
        template = self.templates_module.get_template(template_id)

        result = {
            'template_id': template_id,
            'incident_service': incident_service,
            'applicable': False,
            'matching_services': [],
            'reason': ''
        }

        if template is None:
            result['reason'] = f"Template '{template_id}' does not exist"
            return result

        # Check applicability based on service matching
        if incident_service is None:
            result['applicable'] = True
            result['matching_services'] = template.applicable_services
            result['reason'] = (
                f"Template '{template_id}' is applicable without service restriction"
            )
        else:
            matching = [
                service for service in template.applicable_services
                if service.lower() == incident_service.lower()
            ]

            if matching:
                result['applicable'] = True
                result['matching_services'] = matching
                result['reason'] = (
                    f"Template '{template_id}' applies to service '{incident_service}' "
                    f"(matches: {', '.join(matching)})"
                )
            else:
                result['applicable'] = False
                result['matching_services'] = template.applicable_services
                result['reason'] = (
                    f"Template '{template_id}' does not apply to service '{incident_service}' "
                    f"(applies only to: {', '.join(template.applicable_services)})"
                )

        return result

    def prepare_guidance_payload(
        self,
        template_id: str,
        incident_service: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Prepare a complete guidance payload for investigation planning.

        Args:
            template_id: The template ID to prepare guidance for.
            incident_service: The service field from the incident (optional).

        Returns:
            Complete guidance payload if the template exists,
            None if the template doesn't exist.

        The payload includes:
        - Template identification and metadata
        - Investigation checks and expected evidence
        - Applicability analysis
        - High-level guidance and recommendations
        - Validation rules for planning purposes

        Note:
            This function provides structured guidance for investigation
            planning and does not execute any commands or access external systems.
            """
        # Get the template using the public API
        template = self.templates_module.get_template(template_id)

        if template is None:
            return None

        # Check applicability
        applicability = self.check_applicability(template_id, incident_service)

        # Prepare the complete guidance payload
        guidance_payload = {
            'template_id': template.id,
            'name': template.name,
            'description': template.description,
            'applicable_services': list(template.applicable_services),
            'checks': [dict(check) for check in template.checks],
            'expected_evidence': list(template.expected_evidence),
            'validation_rules': dict(template.validation_rules),
            'guidance': dict(template.guidance),
            'applicability': {
                'is_applicable': applicability['applicable'],
                'matching_services': applicability['matching_services'],
                'reason': applicability['reason']
            },
            'incident_context': {
                'service': incident_service,
                'can_proceed_without_service': incident_service is None
            }
        }

        return guidance_payload
# Global engine instance for convenience
_engine: Optional[TemplateEngine] = None
def get_template_engine() -> TemplateEngine:
    """
    Get or create the global template engine instance.

    Returns:
        TemplateEngine instance.
    """
    global _engine
    if _engine is None:
        _engine = TemplateEngine()
    return _engine
# Module-level convenience functions for backward compatibility
def get_template(template_id: str) -> Optional[Dict[str, Any]]:
    """Get template guidance using the global engine."""
    return get_template_engine().get_template(template_id)
def list_templates() -> List[str]:
    """List all available template IDs using the global engine."""
    return get_template_engine().list_templates()
def is_template_available(template_id: str) -> bool:
    """Check if template is available using the global engine."""
    return get_template_engine().is_template_available(template_id)
# Module metadata
__all__ = [
    'TemplateEngine',
    'get_template_engine',
    'get_template',
    'list_templates',
    'is_template_available'
]

# ============================================================================
# End of template_engine.py
# ============================================================================