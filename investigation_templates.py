"""
Investigation Template Definitions for DevOps Incident Commander

This module contains immutable built-in investigation templates for common
incident scenarios. Templates provide structured investigation guidance and
expected evidence collection instructions.

Templates are designed to be extended into customizable templates in future
iterations while maintaining backward compatibility.

Author: DevOps Incident Commander Team
Date: 2026-10-22
Version: 1.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from copy import deepcopy
from types import MappingProxyType


class InvestigationTemplate:
    """
    Data model for investigation templates.

    Templates provide structured investigation guidance for common incident
    scenarios. They are designed to be immutable and thread-safe.

    Attributes:
        id: Unique template identifier
        name: Human-readable template name
        description: Detailed description of when and how to use the template
        applicable_services: List of service names this template applies to
        checks: Ordered list of investigation checks with guidance
        expected_evidence: Types of evidence the template expects to find
        validation_rules: Rules for applying the template to incidents
        guidance: High-level investigation workflow guidance
    """

    _initialized = False

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        applicable_services: List[str],
        checks: List[Dict[str, Any]],
        expected_evidence: List[str],
        validation_rules: Dict[str, Any],
        guidance: Dict[str, Any]
    ):
        # Create deep copies to prevent external modification of internal data
        object.__setattr__(self, '_id', deepcopy(id))
        object.__setattr__(self, '_name', deepcopy(name))
        object.__setattr__(self, '_description', deepcopy(description))
        object.__setattr__(self, '_applicable_services', deepcopy(applicable_services))
        object.__setattr__(self, '_checks', deepcopy(checks))
        object.__setattr__(self, '_expected_evidence', deepcopy(expected_evidence))
        object.__setattr__(self, '_validation_rules', deepcopy(validation_rules))
        object.__setattr__(self, '_guidance', deepcopy(guidance))
        self._initialized = True

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def applicable_services(self) -> List[str]:
        """Return a copy of applicable services to prevent mutation."""
        return self._applicable_services.copy()

    @property
    def checks(self) -> List[Dict[str, Any]]:
        """Return a deep copy of checks to prevent mutation."""
        return deepcopy(self._checks)

    @property
    def expected_evidence(self) -> List[str]:
        """Return a deep copy of expected evidence to prevent mutation."""
        return deepcopy(self._expected_evidence)

    @property
    def validation_rules(self) -> Dict[str, Any]:
        """Return a deep copy of validation rules to prevent mutation."""
        return deepcopy(self._validation_rules)

    @property
    def guidance(self) -> Dict[str, Any]:
        """Return a deep copy of guidance to prevent mutation."""
        return deepcopy(self._guidance)

    def __setattr__(self, name, value):
        if getattr(self, '_initialized', False):
            raise AttributeError(f"InvestigationTemplate objects are immutable. Cannot modify attribute '{name}'.")
        # Allow setting during initialization
        object.__setattr__(self, name, value)

    # Prevent deletion of attributes
    def __delattr__(self, name):
        raise AttributeError(f"InvestigationTemplate objects are immutable. Cannot delete attribute '{name}'.")

    def __repr__(self) -> str:
        return f"InvestigationTemplate(id='{self.id}', name='{self.name}')"

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'applicable_services': self.applicable_services,
            'checks': deepcopy(self.checks),
            'expected_evidence': deepcopy(self.expected_evidence),
            'validation_rules': deepcopy(self.validation_rules),
            'guidance': deepcopy(self.guidance)
        }

# ============================================================================
# Built-in Investigation Templates
# ============================================================================

# Global templates registry - immutable after initialization
_INVESTIGATION_TEMPLATES: Dict[str, InvestigationTemplate] = {}


def _initialize_templates() -> None:
    """Initialize the global templates registry with built-in templates."""
    global _INVESTIGATION_TEMPLATES

    # Template 1: API Failure
    api_failure_template = InvestigationTemplate(
        id="api_failure_v1",
        name="API Service Failure",
        description=(
            "Comprehensive investigation guidance for API service incidents "
            "affecting authentication, endpoints, or rate limiting. This template "
            "provides structured checks for API service health, error patterns, "
            "database connectivity, and performance monitoring."
        ),
        applicable_services=["api", "auth", "gateway", "load-balancer"],
        checks=[
            {
                "system": "service_health",
                "description": (
                    "Check API service health endpoints and status. "
                    "Verify all critical endpoints are responding."
                ),
                "commands": [
                    "curl -X GET http://localhost:8080/health",
                    "curl -X GET http://localhost:8080/status",
                    "curl -X GET http://localhost:8080/metrics"
                ],
                "expected_outputs": ["healthy", "degraded", "unhealthy"],
                "importance": "high"
            },
            {
                "system": "error_patterns",
                "description": (
                    "Analyze error logs for common API issues. "
                    "Look for timeout, connection, and rate limiting patterns."
                ),
                "commands": [
                    "tail -n 100 /var/log/app.log | grep -i error",
                    "grep -i 'timeout|connection refused|rate limit' /var/log/app.log"
                ],
                "patterns": ["Timeout", "Connection refused", "Rate limit", "Authentication failed"],
                "importance": "high"
            },
            {
                "system": "database_connections",
                "description": (
                    "Verify database connectivity for API services. "
                    "Test connection pools and query performance."
                ),
                "commands": [
                    "redis-cli ping",
                    "mysql -h localhost -e 'SELECT 1'",
                    "psql -h localhost -c 'SELECT 1'"
                ],
                "expected_results": ["PONG", "success"],
                "importance": "medium"
            },
            {
                "system": "memory_usage",
                "description": (
                    "Check memory usage patterns that could cause API failures. "
                    "Look for memory leaks or high garbage collection."
                ),
                "commands": [
                    "ps aux | grep java | awk '{sum+=$2} END {print sum}' + '%'"
                ],
                "threshold": 80,
                "importance": "medium"
            }
        ],
        expected_evidence=[
            "API service logs (app.log, access.log)",
            "Database connection pool metrics",
            "Memory and thread dump analysis",
            "Load balancer health check results",
            "Network connectivity test results"
        ],
        validation_rules={
            "require_service_match": True,
            "require_min_log_entries": 10,
            "max_investigation_hours": 2,
            "required_checks_count": 3
        },
        guidance={
            "initial_focus": "Service health and basic connectivity",
            "secondary_focus": "Error analysis and performance",
            "escalation_criteria": [
                "Service not responding to health checks",
                "Multiple database connection failures",
                "Memory usage above 80% for extended periods"
            ],
            "recommended_tools": [
                "curl for endpoint testing",
                "tail for log analysis",
                "ps for process monitoring",
                "redis-cli/mysql-psql for database testing"
            ]
        }
    )

    # Template 2: Database Incident
    database_incident_template = InvestigationTemplate(
        id="database_incident_v1",
        name="Database Service Incident",
        description=(
            "Structured investigation for database connectivity, query performance, "
            "and schema issues. This template provides systematic checks for "
            "database health, performance metrics, and backup verification."
        ),
        applicable_services=["database", "cache", "storage"],
        checks=[
            {
                "system": "connectivity",
                "description": (
                    "Test database connection health and availability. "
                    "Verify all database instances are responding."
                ),
                "commands": [
                    "mysql -h localhost -e 'SELECT 1'",
                    "redis-cli ping",
                    "psql -h localhost -c 'SELECT 1'"
                ],
                "expected_results": ["success", "PONG"],
                "importance": "high"
            },
            {
                "system": "performance_metrics",
                "description": (
                    "Analyze query performance and response times. "
                    "Identify slow queries and performance bottlenecks."
                ),
                "commands": [
                    "SHOW PROCESSLIST",
                    "slow query log analysis",
                    "mysql -e 'SHOW STATUS LIKE \"Handler_read%\"'"
                ],
                "thresholds": {
                    "max_query_time": 5000,
                    "max_connections": 80,
                    "cache_hit_ratio": 95
                },
                "importance": "high"
            },
            {
                "system": "schema_integrity",
                "description": (
                    "Verify database schema and foreign keys. "
                    "Check for data corruption or structural issues."
                ),
                "commands": [
                    "SHOW TABLE STATUS",
                    "DESCRIBE users",
                    "SELECT COUNT(*) FROM important_table"
                ],
                "checks": ["tables_exist", "foreign_keys_valid", "data_counts_valid"],
                "importance": "medium"
            },
            {
                "system": "backup_verification",
                "description": (
                    "Confirm recent successful backups and recovery capabilities. "
                    "Verify disaster recovery procedures."
                ),
                "commands": [
                    "ls -la backups/",
                    "tail -n 10 backup.log",
                    "mysql -e 'RESTORE FROM LATEST_BACKUP' --dry-run"
                ],
                "minimum_recent_backups": 3,
                "importance": "medium"
            }
        ],
        expected_evidence=[
            "Database query logs (slow_query.log, error.log)",
            "Performance monitoring metrics",
            "Schema change logs",
            "Backup and recovery logs",
            "Connection pool statistics"
        ],
        validation_rules={
            "require_service_match": True,
            "require_min_log_entries": 5,
            "max_investigation_hours": 4,
            "required_checks_count": 2
        },
        guidance={
            "initial_focus": "Database connectivity and availability",
            "secondary_focus": "Performance optimization and schema integrity",
            "escalation_criteria": [
                "Database instances not responding",
                "Critical queries exceeding performance thresholds",
                "Data corruption detected in tables"
            ],
            "recommended_tools": [
                "SHOW PROCESSLIST for live queries",
                "slow query log for performance analysis",
                "database-specific monitoring tools",
                "backup verification utilities"
            ]
        }
    )

    # Template 3: Network Incident
    network_incident_template = InvestigationTemplate(
        id="network_incident_v1",
        name="Network Infrastructure Incident",
        description=(
            "Systematic approach to network connectivity, latency, and routing "
            "issues across infrastructure components. This template provides "
            "structured checks for connectivity, performance, and security."
        ),
        applicable_services=["network", "load-balancer", "firewall", "cdn"],
        checks=[
            {
                "system": "connectivity_test",
                "description": (
                    "Test basic network connectivity to critical services. "
                    "Verify end-to-end network paths."
                ),
                "commands": [
                    "ping -c 4 google.com",
                    "curl -I https://api.example.com/health",
                    "traceroute api.example.com"
                ],
                "expected_responses": ["ICMP success", "HTTP 200 OK"],
                "importance": "high"
            },
            {
                "system": "latency_analysis",
                "description": (
                    "Measure network latency and performance metrics. "
                    "Identify bandwidth and latency issues."
                ),
                "commands": [
                    "ping -c 10 api.example.com",
                    "curl -o /dev/null -s -w '%{time_total}\n' https://api.example.com/api/data",
                    "iperf3 -c server.example.com -t 10"
                ],
                "thresholds": {
                    "avg_latency_ms": 200,
                    "packet_loss_percent": 1,
                    "jitter_ms": 50
                },
                "importance": "high"
            },
            {
                "system": "firewall_rules",
                "description": (
                    "Analyze firewall logs and rule configurations. "
                    "Verify security policies and block rules."
                ),
                "commands": [
                    "iptables -L -n",
                    "firewall-cmd --list-all",
                    "grep 'DROP|REJECT' /var/log/firewall.log"
                ],
                "checks": ["rules_loaded", "allow_outbound", "block_suspicious"],
                "importance": "medium"
            },
            {
                "system": "ssl_certificates",
                "description": (
                    "Verify SSL certificate validity and expiration. "
                    "Check certificate chains and security configurations."
                ),
                "commands": [
                    "openssl s_client -connect api.example.com:443 -servername api.example.com",
                    "certbot certificates",
                    "curl -I https://api.example.com"
                ],
                "checks": ["cert_valid", "issuer_trusted", "not_expired"],
                "importance": "medium"
            }
        ],
        expected_evidence=[
            "Network device logs (syslog, firewall.log)",
            "DNS resolution results (nslookup, dig)",
            "SSL/TLS certificate information",
            "Load balancer health check results",
            "Bandwidth and latency metrics"
        ],
        validation_rules={
            "require_service_match": True,
            "require_min_log_entries": 8,
            "max_investigation_hours": 3,
            "required_checks_count": 2
        },
        guidance={
            "initial_focus": "Basic connectivity and latency testing",
            "secondary_focus": "Security analysis and certificate validation",
            "escalation_criteria": [
                "Network connectivity failures",
                "High latency or packet loss",
                "SSL certificate issues"
            ],
            "recommended_tools": [
                "ping and traceroute for connectivity",
                "curl for HTTPS testing",
                "iptables/firewall-cmd for rule analysis",
                "openssl for certificate validation"
            ]
        }
    )

    # Register all templates
    _INVESTIGATION_TEMPLATES[api_failure_template.id] = api_failure_template
    _INVESTIGATION_TEMPLATES[database_incident_template.id] = database_incident_template
    _INVESTIGATION_TEMPLATES[network_incident_template.id] = network_incident_template


# Global registry instance - initialized on module import
_initialize_templates()


def get_all_templates() -> List[InvestigationTemplate]:
    """
    Get all available investigation templates.

    Returns:
        List of all InvestigationTemplate objects.

    Note:
        Templates are returned as InvestigationTemplate objects for
        programmatic access. For dictionary representations, use
        template.to_dict().
    """
    return list(_INVESTIGATION_TEMPLATES.values())


def get_template(template_id: str) -> Optional[InvestigationTemplate]:
    """
    Retrieve an investigation template by ID.

    Args:
        template_id: The unique identifier of the template to retrieve.

    Returns:
        InvestigationTemplate object if found, None if not found.

    Example:
        >>> template = get_template("api_failure_v1")
        >>> if template:
        ...     print(template.name)
        'API Service Failure'
    """
    return _INVESTIGATION_TEMPLATES.get(template_id)


def template_exists(template_id: str) -> bool:
    """
    Check if a template exists by ID.

    Args:
        template_id: The template ID to check.

    Returns:
        True if template exists, False otherwise.
    """
    return template_id in _INVESTIGATION_TEMPLATES


def list_template_ids() -> List[str]:
    """
    Get list of all template IDs.

    Returns:
        List of template IDs (strings).
    """
    return list(_INVESTIGATION_TEMPLATES.keys())


# ============================================================================
# Module-level initialization and validation
# ============================================================================

# Validate that we have exactly three templates
assert len(_INVESTIGATION_TEMPLATES) == 3, (
    f"Expected exactly 3 investigation templates, found {len(_INVESTIGATION_TEMPLATES)}"
)

# Validate that all required templates exist
required_template_ids = {"api_failure_v1", "database_incident_v1", "network_incident_v1"}
missing_templates = required_template_ids - set(_INVESTIGATION_TEMPLATES.keys())
if missing_templates:
    raise ValueError(f"Missing required templates: {missing_templates}")

# Validate each template has required fields
for template_id, template in _INVESTIGATION_TEMPLATES.items():
    assert template.id == template_id, f"Template ID mismatch: expected {template_id}, got {template.id}"
    assert hasattr(template, 'name'), f"Template {template_id} missing name"
    assert hasattr(template, 'description'), f"Template {template_id} missing description"
    assert hasattr(template, 'applicable_services'), f"Template {template_id} missing applicable_services"
    assert hasattr(template, 'checks'), f"Template {template_id} missing checks"
    assert hasattr(template, 'expected_evidence'), f"Template {template_id} missing expected_evidence"
    assert hasattr(template, 'validation_rules'), f"Template {template_id} missing validation_rules"
    assert hasattr(template, 'guidance'), f"Template {template_id} missing guidance"

# Module metadata
__all__ = [
    'InvestigationTemplate',
    'get_all_templates',
    'get_template',
    'template_exists',
    'list_template_ids'
]

# ============================================================================
# End of investigation_templates.py
# ============================================================================