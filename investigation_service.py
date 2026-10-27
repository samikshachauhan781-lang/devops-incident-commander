"""
Investigation Service for DevOps Incident Commander

This module provides incident investigation capabilities using AI providers.
It integrates with the existing AI provider foundation to generate intelligent
investigation results with root-cause hypotheses, supporting evidence, confidence
scores, and diagnostic recommendations.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import uuid
import json
from datetime import datetime
from uuid import uuid4
import threading
import queue
import time

from ai_provider import (
    AIProvider,
    AIProviderConfig,
    IncidentData,
    AnalysisRequest,
    AnalysisResult,
    get_analysis_service,
)

# ==============================================================================
# Timeout Utilities
# ==============================================================================

class TimeoutError(Exception):
    """Exception raised when operation times out."""
    pass

def call_with_timeout(func, args, timeout_seconds):
    """
    Execute a function with a timeout.

    This is the thread-based timeout implementation recommended in the analysis
    report for cross-platform compatibility and proper cleanup.

    Args:
        func: Function to execute
        args: Arguments to pass to the function
        timeout_seconds: Maximum time to wait for the function to complete

    Returns:
        Result of the function call

    Raises:
        TimeoutError: If the function doesn't complete within the timeout period
        Exception: If the function raises an exception
    """
    # If timeout_seconds is None or <= 0, don't wait for timeout
    if timeout_seconds is None or timeout_seconds <= 0:
        return func(*args)

    result_queue = queue.Queue()
    exception_queue = queue.Queue()
    timeout_occurred = threading.Event()

    def worker():
        try:
            result = func(*args)
            result_queue.put(result)
        except Exception as e:
            exception_queue.put(e)

    thread = threading.Thread(target=worker)
    thread.daemon = True  # Daemon threads won't prevent program exit
    thread.start()
    thread.join(timeout_seconds)

    if thread.is_alive():
        timeout_occurred.set()
        # Don't force kill thread, just note timeout occurred
        raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")

    if not exception_queue.empty():
        raise exception_queue.get()

    return result_queue.get()

# ==============================================================================
# Investigation Data Models
# ==============================================================================

@dataclass
class InvestigationEvidence:
    """Evidence collected for investigation."""

    log_text: str = ""
    system_events: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    timestamps: List[str] = field(default_factory=list)
    source: str = "manual"
    collected_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class InvestigationResult:
    """Investigation results with AI-generated insights."""

    incident_id: str
    incident_data: IncidentData
    evidence: InvestigationEvidence
    ai_analysis: AnalysisResult
    investigation_metadata: Dict[str, Any] = field(default_factory=dict)
    investigation_id: str = field(default_factory=lambda: str(uuid4()))
    investigated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Investigation outcomes
    root_cause_hypotheses: List[str] = field(default_factory=list)
    supporting_evidence: Dict[str, List[str]] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    diagnostic_steps: List[str] = field(default_factory=list)
    urgency_level: str = "medium"
    investigation_type: str = "root_cause"

@dataclass
class InvestigationRequest:
    """Request structure for incident investigation."""

    incident_id: str
    evidence: Optional[InvestigationEvidence] = None
    analysis_type: str = "root_cause"
    investigation_depth: str = "detailed"
    constraints: Dict[str, Any] = field(default_factory=dict)
    include_timeline: bool = True
    include_events: bool = True
    investigation_timeout: Optional[float] = None  # Investigation timeout in seconds
    template_id: Optional[str] = None  # Optional template identifier

# ==============================================================================
# Investigation Service
# ==============================================================================

class InvestigationService:
    """Service for investigating incidents using AI providers."""

    def __init__(self, analysis_service=None):
        self.analysis_service = analysis_service or get_analysis_service()
        self.investigation_count = 0

    def _load_template_guidance(
        self,
        template_id: Optional[str],
        incident_service: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Load and validate template guidance from template engine.

        Args:
            template_id: Optional template identifier from investigation request
            incident_service: The incident service for applicability checking

        Returns:
            Template guidance payload if template exists, None otherwise.

        Raises:
            ValueError: If template_id is provided but template doesn't exist
        """
        if not template_id:
            return None

        try:
            from template_engine import get_template_engine
            engine = get_template_engine()

            # Check if template exists
            if not engine.is_template_available(template_id):
                raise ValueError(f"Template '{template_id}' not found")

            # Get guidance payload with incident service for applicability checking
            guidance = engine.prepare_guidance_payload(template_id, incident_service)

            # If template exists but is not applicable, return None (no guidance)
            # but investigation can continue
            if guidance and not guidance.get('applicability', {}).get('is_applicable', False):
                return None

            return guidance

        except ValueError:
            # Re-raise ValueError for template not found
            raise
        except Exception as e:
            # Do not swallow unrelated errors - let them propagate
            raise RuntimeError(f"Failed to load template guidance: {str(e)}")

    def investigate_incident(self, request: InvestigationRequest) -> InvestigationResult:
        """
        Investigate an incident using configured AI provider.

        Args:
            request: Investigation request with incident ID and optional evidence

        Returns:
            Investigation result with AI-generated insights

        Raises:
            ValueError: If incident not found or invalid request
            RuntimeError: If AI provider fails to analyze incident
        """
        self.investigation_count += 1

        try:
            # Step 0: Retrieve incident data first (needed for template applicability check)
            incident_data = self._get_incident_data(request.incident_id)

            # Step 1: Load template guidance if template_id is provided
            template_guidance = self._load_template_guidance(
                request.template_id,
                incident_data.service
            )

            # Step 2: Prepare investigation evidence
            evidence = request.evidence or InvestigationEvidence()

            # Step 3: Generate AI analysis using configured provider
            ai_analysis = self._generate_ai_analysis(
                incident_data,
                evidence,
                request.analysis_type,
                request.constraints,
                template_guidance,
                request.investigation_timeout
            )

            # Step 4: Process and validate AI results
            investigation_result = self._process_ai_results(
                incident_data,
                evidence,
                ai_analysis,
                request.investigation_depth,
                request.include_timeline,
                request.include_events
            )

            # Step 5: Store investigation results (if needed)
            self._store_investigation_results(investigation_result)

            return investigation_result

        except ValueError:
            # Preserve ValueError for "incident not found" to match documented behavior
            raise
        except Exception as e:
            raise RuntimeError(f"Investigation failed for incident {request.incident_id}: {str(e)}")

    def _get_incident_data(self, incident_id: str) -> IncidentData:
        """
        Retrieve incident data from database.

        Args:
            incident_id: ID of incident to retrieve

        Returns:
            Incident data structure

        Raises:
            ValueError: If incident not found
        """
        from models import get_incident, list_events

        # Fetch incident from database
        existing_incident = get_incident(incident_id)
        if not existing_incident:
            raise ValueError(f"Incident {incident_id} not found")

        # Fetch associated events
        events_result = list_events(incident_id=incident_id, page=1, page_size=100)
        event_list = [
            {
                "id": event["id"],
                "type": event["event_type"],
                "description": event["description"],
                "timestamp": event["created_at"]
            }
            for event in events_result.get("events", [])
        ]

        # Convert database record to IncidentData
        return IncidentData(
            incident_id=existing_incident["id"],
            title=existing_incident["title"],
            description=existing_incident["description"],
            severity=existing_incident["severity"],
            status=existing_incident["status"],
            service=existing_incident["service"],
            created_at=existing_incident["created_at"],
            events=event_list,
            analysis_metadata={}
        )

    def _generate_ai_analysis(
        self,
        incident_data: IncidentData,
        evidence: InvestigationEvidence,
        analysis_type: str,
        constraints: Dict[str, Any],
        template_guidance: Optional[Dict[str, Any]] = None,
        investigation_timeout: Optional[float] = None
    ) -> AnalysisResult:
        """
        Generate AI analysis for incident investigation.

        Args:
            incident_data: Incident data to analyze
            evidence: Investigation evidence
            analysis_type: Type of analysis to perform
            constraints: Analysis constraints
            template_guidance: Optional template guidance for investigation
            investigation_timeout: Optional investigation timeout (from InvestigationRequest)

        Returns:
            AI analysis result

        Raises:
            RuntimeError: If AI analysis fails
            TimeoutError: If investigation times out
        """
        # Use investigation_timeout parameter (already validated by FastAPI)
        timeout_seconds = investigation_timeout

        # For backward compatibility, also check constraints (for tests and direct service calls)
        if timeout_seconds is None and 'investigation_timeout' in constraints:
            timeout_seconds = constraints['investigation_timeout']

        # Validate timeout value
        if timeout_seconds is not None:
            # Explicitly reject boolean values (bool is subclass of int in Python)
            if isinstance(timeout_seconds, bool):
                raise RuntimeError(f"Invalid investigation timeout: {timeout_seconds}. Must be a positive number (int or float), not a boolean.")
            if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
                raise RuntimeError(f"Invalid investigation timeout: {timeout_seconds}. Must be a positive number.")

        try:
            # Prepare context for AI analysis
            context = self._prepare_analysis_context(incident_data, evidence, constraints, template_guidance)

            # Create analysis request
            request = AnalysisRequest(
                incident_data=incident_data,
                analysis_type=analysis_type,
                constraints=constraints,
                context=context,
                template_guidance=template_guidance
            )

            # Get analysis from configured AI provider with timeout support
            result = self._call_ai_analysis_with_timeout(request, timeout_seconds)

            if not result.success:
                raise RuntimeError(f"AI analysis failed: {result.errors}")

            # Add template information to AI analysis metadata if template guidance was provided
            if template_guidance:
                result.metadata['template_applied_info'] = {
                    'template_id': template_guidance.get('template_id'),
                    'name': template_guidance.get('name'),
                    'applicable_services': template_guidance.get('applicable_services'),
                    'applicability': template_guidance.get('applicability')
                }

            return result

        except TimeoutError as e:
            raise RuntimeError(f"Investigation timeout: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"AI analysis failed: {str(e)}")

    def _call_ai_analysis_with_timeout(
        self,
        request: AnalysisRequest,
        timeout_seconds: Optional[float] = None
    ) -> AnalysisResult:
        """
        Call AI analysis with optional timeout support.

        The timeout is passed to the provider via request.constraints.
        Providers are expected to respect the timeout natively.

        Args:
            request: Analysis request
            timeout_seconds: Optional timeout in seconds (from InvestigationRequest.investigation_timeout)

        Returns:
            AI analysis result
        """
        # Use timeout_seconds from parameter (already validated from InvestigationRequest)
        if timeout_seconds is not None and timeout_seconds > 0:
            request.constraints['investigation_timeout'] = timeout_seconds

        return self.analysis_service.analyze_incident(request)

    def _prepare_analysis_context(
        self,
        incident_data: IncidentData,
        evidence: InvestigationEvidence,
        constraints: Dict[str, Any],
        template_guidance: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Prepare context for AI analysis.

        Args:
            incident_data: Incident data
            evidence: Investigation evidence
            constraints: Analysis constraints
            template_guidance: Optional template guidance for investigation

        Returns:
            Context dictionary for AI analysis
        """
        context = {
            "incident_details": {
                "id": incident_data.incident_id,
                "title": incident_data.title,
                "description": incident_data.description,
                "severity": incident_data.severity,
                "status": incident_data.status,
                "service": incident_data.service,
                "created_at": incident_data.created_at,
            },
            "evidence_summary": {
                "log_text_length": len(evidence.log_text),
                "system_events_count": len(evidence.system_events),
                "error_messages_count": len(evidence.error_messages),
                "timestamps_count": len(evidence.timestamps),
                "source": evidence.source,
                "collected_at": evidence.collected_at,
            },
            "analysis_constraints": constraints,
            "investigation_requirements": {
                "investigation_type": "root_cause",
                "depth": "detailed",
                "include_timeline": True,
                "include_events": True,
            }
        }

        # Add template guidance if provided (separate from incident facts)
        if template_guidance:
            context["template_guidance"] = {
                "template_id": template_guidance.get('template_id'),
                "name": template_guidance.get('name'),
                "description": template_guidance.get('description'),
                "applicable_services": template_guidance.get('applicable_services'),
                "checks": template_guidance.get('checks'),
                "guidance": template_guidance.get('guidance'),
                "applicability": template_guidance.get('applicability'),
            }

        # Add evidence content if available
        if evidence.log_text:
            context["evidence_details"] = {
                "log_text": evidence.log_text,
                "system_events": evidence.system_events,
                "error_messages": evidence.error_messages,
                "timestamps": evidence.timestamps,
            }

        return context

    def _process_ai_results(
        self,
        incident_data: IncidentData,
        evidence: InvestigationEvidence,
        ai_analysis: AnalysisResult,
        investigation_depth: str,
        include_timeline: bool,
        include_events: bool
    ) -> InvestigationResult:
        """
        Process AI analysis results into investigation result.

        Args:
            incident_data: Original incident data
            evidence: Investigation evidence
            ai_analysis: AI analysis result
            investigation_depth: Depth of investigation
            include_timeline: Whether to include timeline analysis
            include_events: Whether to include event analysis

        Returns:
            Investigation result with processed AI insights

        Raises:
            RuntimeError: If AI analysis result is malformed or invalid
        """
        # Validate AI analysis result structure
        self._validate_ai_analysis_result(ai_analysis)

        # Extract key information from AI analysis
        root_cause_hypotheses = ai_analysis.hypotheses
        recommendations = ai_analysis.recommendations
        reasoning = ai_analysis.reasoning
        confidence_score = ai_analysis.confidence_score

        # Process and categorize hypotheses
        categorized_hypotheses = self._categorize_hypotheses(root_cause_hypotheses)

        # Generate supporting evidence for each hypothesis
        supporting_evidence = self._generate_supporting_evidence(
            categorized_hypotheses, evidence
        )

        # Generate diagnostic steps based on hypotheses and evidence
        diagnostic_steps = self._generate_diagnostic_steps(
            categorized_hypotheses, evidence, recommendations
        )

        # Determine urgency level based on severity and confidence
        urgency_level = self._determine_urgency_level(
            incident_data.severity, confidence_score, len(root_cause_hypotheses)
        )

        # Create investigation metadata
        investigation_metadata = {
            "provider": ai_analysis.metadata.get("provider", "unknown"),
            "model": ai_analysis.metadata.get("model", "unknown"),
            "analysis_type": ai_analysis.analysis_type,
            "confidence_score": ai_analysis.confidence_score,
            "investigation_depth": investigation_depth,
            "evidence_count": len(evidence.log_text) + len(evidence.system_events) + len(evidence.error_messages),
            "ai_analysis_successful": ai_analysis.success,
            "errors": ai_analysis.errors,
            "warnings": ai_analysis.warnings,
        }

        # Create investigation result
        result = InvestigationResult(
            incident_id=incident_data.incident_id,
            incident_data=incident_data,
            evidence=evidence,
            ai_analysis=ai_analysis,
            root_cause_hypotheses=categorized_hypotheses,
            supporting_evidence=supporting_evidence,
            confidence_scores={"overall": confidence_score, "detailed": {}},
            diagnostic_steps=diagnostic_steps,
            urgency_level=urgency_level,
            investigation_type=ai_analysis.analysis_type,
            investigation_metadata=investigation_metadata
        )

        return result

    def _validate_ai_analysis_result(self, ai_analysis: AnalysisResult):
        """
        Validate AI analysis result structure and content.

        Args:
            ai_analysis: AI analysis result to validate

        Raises:
            RuntimeError: If AI analysis result is malformed or invalid
        """
        # Validate required fields exist and have correct types
        if ai_analysis.success is None:
            raise RuntimeError("AI analysis result missing required field: success")

        if not isinstance(ai_analysis.analysis_type, str):
            raise RuntimeError("AI analysis result missing required field: analysis_type (must be string)")

        if not isinstance(ai_analysis.confidence_score, (int, float)):
            raise RuntimeError("AI analysis result missing required field: confidence_score (must be number)")

        if ai_analysis.hypotheses is None:
            raise RuntimeError("AI analysis result missing required field: hypotheses")

        if ai_analysis.recommendations is None:
            raise RuntimeError("AI analysis result missing required field: recommendations")

        if ai_analysis.reasoning is None:
            raise RuntimeError("AI analysis result missing required field: reasoning")

        # Validate field types
        if not isinstance(ai_analysis.hypotheses, list):
            raise RuntimeError("AI analysis result field 'hypotheses' must be a list")

        if not isinstance(ai_analysis.recommendations, list):
            raise RuntimeError("AI analysis result field 'recommendations' must be a list")

        if not isinstance(ai_analysis.reasoning, str):
            raise RuntimeError("AI analysis result field 'reasoning' must be a string")

        if not isinstance(ai_analysis.metadata, dict):
            raise RuntimeError("AI analysis result field 'metadata' must be a dictionary")

        if not isinstance(ai_analysis.errors, list):
            raise RuntimeError("AI analysis result field 'errors' must be a list")

        if not isinstance(ai_analysis.warnings, list):
            raise RuntimeError("AI analysis result field 'warnings' must be a list")

        # Validate that if analysis failed, there should be error information
        if not ai_analysis.success and not ai_analysis.errors:
            raise RuntimeError("AI analysis result failed but no error information provided")

    def _categorize_hypotheses(self, hypotheses: List[str]) -> List[str]:
        """
        Categorize and clean hypotheses for investigation.

        Args:
            hypotheses: Raw hypotheses from AI analysis

        Returns:
            Categorized and cleaned hypotheses
        """
        if not hypotheses:
            return []

        categorized = []
        for hypothesis in hypotheses:
            # Clean hypothesis text
            cleaned = hypothesis.strip()
            if not cleaned:
                continue

            # Remove hypothesis numbering if present
            if cleaned.startswith("Hypothesis"):
                # Extract hypothesis content
                parts = cleaned.split(":", 1)
                if len(parts) > 1:
                    cleaned = parts[1].strip()

            categorized.append(cleaned)

        return categorized

    def _generate_supporting_evidence(
        self,
        hypotheses: List[str],
        evidence: InvestigationEvidence
    ) -> Dict[str, List[str]]:
        """
        Generate supporting evidence for each hypothesis.

        Args:
            hypotheses: Categorized hypotheses
            evidence: Investigation evidence

        Returns:
            Dictionary mapping hypotheses to supporting evidence
        """
        supporting = {}

        for hypothesis in hypotheses:
            hypothesis_evidence = []

            # Check log text for relevant patterns
            if evidence.log_text:
                if "configuration" in hypothesis.lower():
                    hypothesis_evidence.append("Configuration log entries found")
                if "error" in hypothesis.lower() or "exception" in hypothesis.lower():
                    hypothesis_evidence.append("Error messages in logs")
                if "network" in hypothesis.lower():
                    hypothesis_evidence.append("Network connectivity logs")
                if "service" in hypothesis.lower():
                    hypothesis_evidence.append("Service-related log entries")

            # Check system events
            for event in evidence.system_events:
                if "error" in event.lower() or "fail" in event.lower():
                    hypothesis_evidence.append(f"System event: {event}")

            # Check error messages
            for error in evidence.error_messages:
                if "configuration" in error.lower():
                    hypothesis_evidence.append(f"Configuration error: {error}")
                if "network" in error.lower():
                    hypothesis_evidence.append(f"Network error: {error}")

            supporting[hypothesis] = hypothesis_evidence

        return supporting

    def _generate_diagnostic_steps(
        self,
        hypotheses: List[str],
        evidence: InvestigationEvidence,
        recommendations: List[str]
    ) -> List[str]:
        """
        Generate diagnostic steps based on hypotheses and evidence.

        Args:
            hypotheses: Categorized hypotheses
            evidence: Investigation evidence
            recommendations: AI recommendations

        Returns:
            List of diagnostic steps
        """
        steps = []

        # Add diagnostic steps for each hypothesis
        for i, hypothesis in enumerate(hypotheses, 1):
            steps.append(f"Step {i}: Investigate hypothesis: {hypothesis}")

        # Add evidence review steps
        if evidence.log_text:
            steps.append("Review system logs for error patterns")

        if evidence.system_events:
            steps.append("Analyze system events and their timing")

        if evidence.error_messages:
            steps.append("Correlate error messages with system events")

        # Add recommended steps from AI
        if recommendations:
            steps.append("Implement AI-recommended remediation steps:")
            for i, recommendation in enumerate(recommendations, 1):
                steps.append(f"  {i}. {recommendation}")

        return steps

    def _determine_urgency_level(
        self,
        severity: str,
        confidence_score: float,
        hypothesis_count: int
    ) -> str:
        """
        Determine urgency level based on severity, confidence, and hypothesis count.

        Args:
            severity: Incident severity
            confidence_score: AI analysis confidence score
            hypothesis_count: Number of root cause hypotheses

        Returns:
            Urgency level ("low", "medium", "high", "critical")
        """
        urgency_map = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4
        }

        # Base urgency on severity
        base_urgency = urgency_map.get(severity, 2)

        # Increase urgency if confidence is high
        if confidence_score > 0.8:
            base_urgency = min(base_urgency + 1, 4)

        # Increase urgency if multiple hypotheses
        if hypothesis_count > 2:
            base_urgency = min(base_urgency + 1, 4)

        # Map back to string
        reverse_map = {v: k for k, v in urgency_map.items()}
        return reverse_map.get(base_urgency, "medium")

    def _store_investigation_results(self, result: InvestigationResult):
        """
        Store investigation results (placeholder for future implementation).

        Args:
            result: Investigation result to store
        """
        # This would store investigation results in the database
        # For now, we'll just log that investigation was performed
        print(f"Investigation completed for incident {result.incident_id}")
        print(f"Investigation ID: {result.investigation_id}")
        print(f"Generated {len(result.root_cause_hypotheses)} hypotheses")
        print(f"Urgency level: {result.urgency_level}")
        print(f"Confidence score: {result.confidence_scores.get('overall', 0)}")

# Global investigation service instance
_investigation_service = None

def get_investigation_service() -> InvestigationService:
    """
    Get or create the global investigation service instance.

    Returns:
        InvestigationService instance
    """
    global _investigation_service

    if _investigation_service is None:
        _investigation_service = InvestigationService()

    return _investigation_service

def investigate_incident(incident_id: str, evidence: Optional[InvestigationEvidence] = None) -> InvestigationResult:
    """
    Convenience function to investigate an incident.

    Args:
        incident_id: ID of incident to investigate
        evidence: Optional investigation evidence

    Returns:
        Investigation result
    """
    service = get_investigation_service()

    request = InvestigationRequest(
        incident_id=incident_id,
        evidence=evidence,
        analysis_type="root_cause",
        investigation_depth="detailed",
        include_timeline=True,
        include_events=True
    )

    return service.investigate_incident(request)