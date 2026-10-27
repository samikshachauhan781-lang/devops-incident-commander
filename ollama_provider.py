"""
Ollama Provider for DevOps Incident Commander

This module provides an Ollama-based AI provider implementation.
It integrates with the existing AI provider foundation to enable
local LLM-powered incident analysis using Ollama.

The implementation follows the existing provider interface patterns
and includes robust error handling, configuration management, and
testing support without requiring external dependencies for unit tests.
"""

import json
import os
import requests
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import time

from ai_provider import (
    AIProvider,
    AIProviderConfig,
    IncidentData,
    AnalysisRequest,
    AnalysisResult,
    AIProviderError,
    ProviderNotAvailableError,
    ProviderConfigurationError,
    AnalysisError,
)

# ==============================================================================
# Ollama-Specific Data Models
# ==============================================================================

@dataclass
class OllamaConfig:
    """Configuration for Ollama provider."""

    model: str = "llama3.2:3b"
    base_url: str = "http://localhost:11434"
    timeout_seconds: int = 30
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.0
    request_timeout: int = 30
    health_check_timeout: int = 5

    @classmethod
    def from_ai_config(cls, ai_config: Dict[str, Any]) -> 'OllamaConfig':
        """Create OllamaConfig from AI provider configuration."""
        ollama_config = cls()

        # Override with AI config values if present
        if 'model' in ai_config:
            ollama_config.model = ai_config['model']
        if 'base_url' in ai_config:
            ollama_config.base_url = ai_config['base_url']
        if 'timeout_seconds' in ai_config:
            ollama_config.timeout_seconds = ai_config['timeout_seconds']
        if 'max_tokens' in ai_config:
            ollama_config.max_tokens = ai_config['max_tokens']
        if 'temperature' in ai_config:
            ollama_config.temperature = ai_config['temperature']
        if 'top_p' in ai_config:
            ollama_config.top_p = ai_config['top_p']
        if 'top_k' in ai_config:
            ollama_config.top_k = ai_config['top_k']
        if 'repeat_penalty' in ai_config:
            ollama_config.repeat_penalty = ai_config['repeat_penalty']

        return ollama_config

# ==============================================================================
# Ollama Provider Implementation
# ==============================================================================

class OllamaProvider(AIProvider):
    """Ollama provider implementation for local LLM incident analysis."""

    def __init__(self, config: OllamaConfig):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = config.request_timeout
        self.call_count = 0
        self.health_check_timeout = config.health_check_timeout

        # Set up default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'DevOps-Incident-Commander-Ollama/1.0'
        })

    def analyze_incident(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Analyze an incident using Ollama.

        Args:
            request: Incident analysis request

        Returns:
            Analysis result from Ollama

        Raises:
            AnalysisError: If Ollama analysis fails
            ProviderNotAvailableError: If Ollama is not available
        """
        self.call_count += 1

        try:
            # Prepare prompt from incident data
            prompt = self._prepare_prompt(request.incident_data, request.analysis_type, request.template_guidance)

            # Prepare Ollama request - always request JSON output
            ollama_request = {
                'model': self.config.model,
                'prompt': prompt,
                'options': {
                    'temperature': self.config.temperature,
                    'top_p': self.config.top_p,
                    'top_k': self.config.top_k,
                    'num_predict': self.config.max_tokens or 1000,
                    'repeat_penalty': self.config.repeat_penalty,
                },
                'stream': False,
                'format': 'json'
            }

            # Make request to Ollama with timeout
            # Use per-request timeout if provided, otherwise fall back to config
            req_timeout = request.constraints.get('investigation_timeout')
            if req_timeout is not None:
                # Explicitly reject boolean values (bool is subclass of int in Python)
                if isinstance(req_timeout, bool):
                    raise AnalysisError(
                        f"Invalid investigation timeout: {req_timeout}. Must be a positive number (int or float), not a boolean."
                    )
                if not isinstance(req_timeout, (int, float)) or req_timeout <= 0:
                    raise AnalysisError(
                        f"Invalid investigation timeout: {req_timeout}. Must be a positive number."
                    )
                timeout = req_timeout
            else:
                timeout = self.config.request_timeout

            response = self.session.post(
                f"{self.config.base_url}/api/generate",
                json=ollama_request,
                timeout=timeout
            )

            if response.status_code != 200:
                raise AnalysisError(
                    f"Ollama API error: HTTP {response.status_code} - {response.text}"
                )

            # Parse Ollama response
            ollama_response = response.json()

            # Parse and validate Ollama response
            analysis_text = ollama_response.get('response', '')
            if not analysis_text:
                raise AnalysisError("Ollama returned empty response")

            # Parse the analysis result as JSON - no text fallback
            try:
                analysis_data = json.loads(analysis_text)
            except json.JSONDecodeError as e:
                raise AnalysisError(
                    f"Ollama returned invalid JSON: {e}. "
                    f"Raw response preview: {analysis_text[:200]}"
                )

            # Create AnalysisResult from Ollama response
            return self._create_analysis_result(request, analysis_data, ollama_response)

        except requests.exceptions.ConnectionError as e:
            raise ProviderNotAvailableError(
                f"Failed to connect to Ollama at {self.config.base_url}: {e}"
            )
        except requests.exceptions.Timeout as e:
            raise ProviderNotAvailableError(
                f"Ollama request timed out after {self.config.request_timeout}s: {e}"
            )
        except requests.exceptions.HTTPError as e:
            raise AnalysisError(f"Ollama HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            raise ProviderNotAvailableError(
                f"Ollama request failed: {e}"
            )
        except AnalysisError:
            raise
        except ProviderNotAvailableError:
            raise
        except Exception as e:
            # Handle generic exceptions that may wrap connection errors
            error_msg = str(e).lower()
            if "connection refused" in error_msg or "connection error" in error_msg:
                raise ProviderNotAvailableError(
                    f"Failed to connect to Ollama at {self.config.base_url}: {e}"
                )
            if "timeout" in error_msg or "timed out" in error_msg:
                raise ProviderNotAvailableError(
                    f"Ollama request timed out: {e}"
                )
            raise AnalysisError(f"Unexpected error analyzing incident with Ollama: {e}")

    def health_check(self) -> bool:
        """
        Check if Ollama is healthy and available.

        Returns:
            True if Ollama is healthy, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.config.base_url}/api/tags",
                timeout=self.health_check_timeout
            )

            if response.status_code == 200:
                tags_response = response.json()
                models = tags_response.get('models', [])

                # Check if configured model is available
                model_available = any(
                    model['name'] == self.config.model
                    for model in models
                )

                return model_available

            return False

        except requests.exceptions.RequestException:
            return False
        except Exception:
            return False

    def get_provider_info(self) -> dict:
        """
        Get information about the Ollama provider.

        Returns:
            Dictionary with Ollama provider information
        """
        return {
            'name': 'Ollama Local LLM Provider',
            'description': f'Local LLM using Ollama model: {self.config.model}',
            'available': self.health_check(),
            'model': self.config.model,
            'base_url': self.config.base_url,
            'type': 'local_llm',
            'ollama_specific': True
        }

    def configure(self, config: dict) -> bool:
        """
        Update Ollama provider configuration.

        Args:
            config: Configuration dictionary with Ollama-specific settings

        Returns:
            True if configuration successful, False otherwise
        """
        try:
            # Update configuration
            if 'model' in config:
                self.config.model = config['model']
            if 'base_url' in config:
                self.config.base_url = config['base_url']
            if 'timeout_seconds' in config:
                self.config.timeout_seconds = config['timeout_seconds']
            if 'max_tokens' in config:
                self.config.max_tokens = config['max_tokens']
            if 'temperature' in config:
                self.config.temperature = config['temperature']
            if 'top_p' in config:
                self.config.top_p = config['top_p']
            if 'top_k' in config:
                self.config.top_k = config['top_k']
            if 'repeat_penalty' in config:
                self.config.repeat_penalty = config['repeat_penalty']

            # Update session timeout
            self.session.timeout = self.config.request_timeout

            return True
        except Exception:
            return False

    def _prepare_prompt(self, incident_data: IncidentData, analysis_type: str, template_guidance: Optional[Dict[str, Any]] = None) -> str:
        """
        Prepare prompt for Ollama from incident data.

        Args:
            incident_data: Incident data to analyze
            analysis_type: Type of analysis to perform
            template_guidance: Optional template guidance for investigation

        Returns:
            Formatted prompt for Ollama
        """
        prompt_parts = [
            f"Analyze the following incident:",
            f"",
            f"Incident ID: {incident_data.incident_id}",
            f"Title: {incident_data.title}",
            f"Description: {incident_data.description}",
            f"Severity: {incident_data.severity}",
            f"Status: {incident_data.status}",
            f"Service: {incident_data.service}",
            f"Created At: {incident_data.created_at}",
        ]

        if incident_data.events:
            prompt_parts.append(f"Events:")
            for i, event in enumerate(incident_data.events):
                prompt_parts.append(f"  Event {i+1}: {event}")

        prompt_parts.extend([
            f"",
            f"Please provide analysis focusing on:",
            f"- Root cause identification",
            f"- Pattern analysis",
            f"- Severity assessment",
            f"- Recommendations for remediation"
        ])

        if analysis_type == 'detailed':
            prompt_parts.extend([
                f"",
                f"Provide detailed analysis including:",
                f"- Timeline analysis",
                f"- Impact assessment",
                f"- Risk evaluation",
                f"- Action prioritization"
            ])

        # Add template guidance if meaningful guidance is provided
        if template_guidance:
            # Check if template guidance has meaningful content
            # Only process if it has meaningful information beyond just identifiers
            has_meaningful_content = (
                template_guidance.get('checks') or  # Has investigative checks
                template_guidance.get('guidance') or  # Has investigative guidance
                template_guidance.get('description')  # Has description
            )

            if has_meaningful_content:
                prompt_parts.extend([
                    f"",
                    f"=== INVESTIGATIVE TEMPLATE GUIDANCE ===",
                    f"The following template provides investigative guidance for this analysis:",
                    f"",
                    f"Template: {template_guidance.get('name', 'Unknown Template')}",
                    f"Description: {template_guidance.get('description', 'No description available')}",
                    f"",
                    f"Template checks and recommendations:",
                ])

                checks = template_guidance.get('checks', [])
                if checks:
                    prompt_parts.append(f"- Checks to consider: {', '.join(checks)}")

                guidance = template_guidance.get('guidance', [])
                if guidance:
                    prompt_parts.append(f"- Investigative guidance: {', '.join(guidance)}")

                applicable_services = template_guidance.get('applicable_services', [])
                if applicable_services:
                    prompt_parts.append(f"- Applicable to services: {', '.join(applicable_services)}")

                prompt_parts.extend([
                    f"",
                    f"IMPORTANT: This template guidance is investigative suggestions only.",
                    f"Do not treat these checks or recommendations as verified evidence.",
                    f"Only perform suggested checks if you have evidence that they are relevant.",
                    f"Avoid claiming you have executed commands or collected evidence unless",
                    f"you actually have done so. Focus on analyzing the actual incident data",
                    f"provided above, using this template only as a guide for investigation approach.",
                ])

        prompt_parts.append(f"")
        return "\n".join(prompt_parts)

    def _create_analysis_result(
        self,
        request: AnalysisRequest,
        analysis_data: Dict[str, Any],
        ollama_response: Dict[str, Any]
    ) -> AnalysisResult:
        """
        Create AnalysisResult from Ollama response.

        Args:
            request: Original analysis request
            analysis_data: Parsed analysis data from Ollama
            ollama_response: Raw Ollama response

        Returns:
            AnalysisResult with Ollama-derived insights

        Raises:
            AnalysisError: If response schema is invalid
        """
        # Validate response schema
        required_fields = ['hypotheses', 'recommendations', 'confidence_score', 'reasoning']
        for field in required_fields:
            if field not in analysis_data:
                raise AnalysisError(f"Ollama response missing required field: '{field}'")

        # Validate field types
        if not isinstance(analysis_data['hypotheses'], list):
            raise AnalysisError("Ollama response field 'hypotheses' must be a list")

        if not isinstance(analysis_data['recommendations'], list):
            raise AnalysisError("Ollama response field 'recommendations' must be a list")

        if not isinstance(analysis_data['reasoning'], str):
            raise AnalysisError("Ollama response field 'reasoning' must be a string")

        # Validate confidence_score: numeric (int/float, not bool), between 0 and 1
        confidence = analysis_data['confidence_score']
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            raise AnalysisError("Ollama response field 'confidence_score' must be a number (int or float)")
        if not (0 <= confidence <= 1):
            raise AnalysisError("Ollama response field 'confidence_score' must be between 0 and 1")

        # Create metadata
        metadata = {
            'provider': 'ollama',
            'model': self.config.model,
            'base_url': self.config.base_url,
            'ollama_response': ollama_response,
            'call_count': self.call_count,
            'total_duration_ms': ollama_response.get('total_duration', 0) // 1000000,
            'eval_duration_ms': ollama_response.get('eval_duration', 0) // 1000000,
            'prompt_eval_duration_ms': ollama_response.get('prompt_eval_duration', 0) // 1000000,
        }

        return AnalysisResult(
            success=analysis_data.get('success', True),
            analysis_type=request.analysis_type,
            confidence_score=confidence,
            hypotheses=analysis_data['hypotheses'],
            recommendations=analysis_data['recommendations'],
            reasoning=analysis_data['reasoning'],
            metadata=metadata,
            errors=analysis_data.get('errors', []),
            warnings=analysis_data.get('warnings', [])
        )

# ==============================================================================
# Ollama Provider Configuration and Integration
# ==============================================================================

class OllamaAIProviderConfig(AIProviderConfig):
    """Configuration for Ollama AI provider."""

    def __init__(self, config_file: Optional[str] = None):
        super().__init__(config_file)
        self.ollama_config = OllamaConfig()

    def get_ollama_config(self) -> OllamaConfig:
        """Get Ollama configuration."""
        return self.ollama_config

    def configure_ollama(self, config: dict) -> bool:
        """Configure Ollama settings."""
        try:
            # Update Ollama configuration
            ollama_config_dict = self.ollama_config.__dict__.copy()

            # Update with new configuration
            for key, value in config.items():
                if key in ollama_config_dict:
                    setattr(self.ollama_config, key, value)

            return True
        except Exception:
            return False

def get_ollama_provider(ollama_config: Optional[OllamaConfig] = None) -> OllamaProvider:
    """
    Get or create Ollama provider instance.

    Args:
        ollama_config: Ollama configuration (uses defaults if None)

    Returns:
        OllamaProvider instance
    """
    if ollama_config is None:
        ollama_config = OllamaConfig()

    return OllamaProvider(ollama_config)

def analyze_with_ollama(
    incident_data: IncidentData,
    analysis_type: str = "root_cause",
    ollama_config: Optional[OllamaConfig] = None
) -> AnalysisResult:
    """
    Convenience function to analyze incident using Ollama.

    Args:
        incident_data: Incident data to analyze
        analysis_type: Type of analysis to perform
        ollama_config: Ollama configuration (uses defaults if None)

    Returns:
        Analysis result from Ollama
    """
    provider = get_ollama_provider(ollama_config)
    request = AnalysisRequest(incident_data=incident_data, analysis_type=analysis_type)
    return provider.analyze_incident(request)

# Auto-initialize Ollama provider
_ollama_provider = get_ollama_provider()

print("✅ Ollama Provider Foundation initialized successfully")
print(f"📋 Ollama model: {_ollama_provider.config.model}")
print(f"📋 Ollama base URL: {_ollama_provider.config.base_url}")
print(f"📋 Ollama health check: {_ollama_provider.health_check()}")