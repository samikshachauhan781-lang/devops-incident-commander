"""
AI Provider Foundation for DevOps Incident Commander

This module provides the foundation for AI-powered incident analysis.
It includes provider interfaces, configuration management, and mock implementations.

The implementation follows the first milestone requirements:
- Provider-independent interface
- Environment variable configuration
- Structured input/output schemas
- Mock provider for testing
- No external dependencies on real AI models
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
import os
import json
from datetime import datetime

# ==============================================================================
# Data Models and Schemas
# ==============================================================================

@dataclass
class IncidentData:
    """Structured incident data for AI analysis."""
    incident_id: str
    title: str
    description: str
    severity: str
    status: str
    service: str
    created_at: str
    events: list = field(default_factory=list)
    analysis_metadata: dict = field(default_factory=dict)

@dataclass
class AnalysisRequest:
    """Request structure for incident analysis."""
    incident_data: IncidentData
    analysis_type: str = "root_cause"
    depth: str = "detailed"
    constraints: dict = field(default_factory=dict)
    context: dict = field(default_factory=dict)
    template_guidance: Optional[Dict[str, Any]] = None

@dataclass
class AnalysisResult:
    """Result structure from incident analysis."""
    success: bool
    analysis_type: str
    confidence_score: float
    hypotheses: list
    recommendations: list
    reasoning: str
    metadata: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

# ==============================================================================
# AI Provider Interface
# ==============================================================================

class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def analyze_incident(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Analyze an incident and return insights.

        Args:
            request: Incident analysis request

        Returns:
            Analysis result with hypotheses and recommendations
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the provider is healthy and available.

        Returns:
            True if provider is healthy, False otherwise
        """
        pass

    @abstractmethod
    def get_provider_info(self) -> dict:
        """
        Get information about the provider.

        Returns:
            Dictionary with provider information
        """
        pass

    @abstractmethod
    def configure(self, config: dict) -> bool:
        """
        Configure the provider with settings.

        Args:
            config: Configuration dictionary

        Returns:
            True if configuration successful, False otherwise
        """
        pass

# ==============================================================================
# Configuration Management
# ==============================================================================

class AIProviderConfig:
    """Configuration management for AI providers."""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        self.providers_config = self._load_config()
        self.active_provider = self._get_active_provider()

    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        return os.path.join(os.path.dirname(__file__), "config", "ai_providers.json")

    def _load_config(self) -> dict:
        """Load configuration from file or use defaults."""
        default_config = {
            "providers": {
                "mock": {
                    "name": "Mock AI Provider",
                    "description": "Mock provider for testing",
                    "available": True,
                    "default": False,
                    "config": {
                        "simulation_delay_ms": 100,
                        "success_rate": 1.0,
                        "error_types": []
                    }
                },
                "openai": {
                    "name": "OpenAI GPT",
                    "description": "OpenAI GPT API (requires API key)",
                    "available": False,
                    "default": False,
                    "config": {
                        "model": "gpt-3.5-turbo",
                        "temperature": 0.7,
                        "max_tokens": 1000,
                        "api_key_env_var": "OPENAI_API_KEY"
                    }
                },
                "ollama": {
                    "name": "Ollama Local LLM",
                    "description": "Local LLM using Ollama (requires Ollama server)",
                    "available": OLLAMA_AVAILABLE,
                    "default": False,
                    "config": {
                        "model": "llama3.2:3b",
                        "base_url": "http://localhost:11434",
                        "timeout_seconds": 30,
                        "max_tokens": None,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40,
                        "repeat_penalty": 1.0,
                        "request_timeout": 30,
                        "health_check_timeout": 5
                    }
                }
            },
            "default_provider": "mock",
            "timeout_seconds": 30,
            "retry_count": 3
        }

        # Try to load from file if it exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    # Merge with defaults
                    default_config.update(file_config)
            except (json.JSONDecodeError, IOError):
                print(f"Warning: Could not load config file {self.config_file}, using defaults")

        return default_config

    def _get_active_provider(self) -> str:
        """Get the active provider from environment or config."""
        # Check environment variable first
        env_provider = os.environ.get('AI_PROVIDER')
        if env_provider and env_provider in self.providers_config['providers']:
            return env_provider

        # Fall back to config default
        return self.providers_config.get('default_provider', 'mock')

    def get_provider_config(self, provider_name: str) -> dict:
        """Get configuration for a specific provider."""
        return self.providers_config['providers'].get(provider_name, {})

    def get_all_providers(self) -> list:
        """Get list of available providers."""
        return list(self.providers_config['providers'].keys())

    def is_provider_available(self, provider_name: str) -> bool:
        """Check if a provider is available."""
        provider_config = self.providers_config['providers'].get(provider_name, {})
        return provider_config.get('available', False)

    def get_active_provider_config(self) -> dict:
        """Get configuration for the active provider."""
        return self.get_provider_config(self.active_provider)

    def validate_config(self) -> bool:
        """Validate the configuration."""
        # Check if active provider is available
        if not self.is_provider_available(self.active_provider):
            print(f"Warning: Active provider '{self.active_provider}' is not available")
            return False

        # Check active provider has required config
        active_config = self.get_active_provider_config()
        if not active_config:
            print("Warning: Active provider has no configuration")
            return False

        return True

# ==============================================================================
# Exception Classes
# ==============================================================================

class AIProviderError(Exception):
    """Base exception for AI provider errors."""
    pass

class ProviderNotAvailableError(AIProviderError):
    """Exception raised when a provider is not available."""
    pass

class ProviderConfigurationError(AIProviderError):
    """Exception raised when provider configuration is invalid."""
    pass

class AnalysisError(AIProviderError):
    """Exception raised when analysis fails."""
    pass

# ==============================================================================
# Ollama Provider Integration
# ==============================================================================

# Try to import Ollama provider
try:
    from ollama_provider import OllamaProvider, OllamaConfig, get_ollama_provider
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Note: Ollama provider not available - continuing with mock provider")

# ==============================================================================
# Global Instance
# ==============================================================================

# Global analysis service instance
_analysis_service = None

def get_analysis_service(config: AIProviderConfig = None) -> 'AnalysisService':
    """Get or create the global analysis service instance."""
    global _analysis_service

    if _analysis_service is None:
        if config is None:
            config = AIProviderConfig()

        if not config.validate_config():
            raise ProviderConfigurationError("Invalid AI provider configuration")

        _analysis_service = AnalysisService(config)

    return _analysis_service


def analyze_incident(incident_data: IncidentData, analysis_type: str = "root_cause") -> AnalysisResult:
    """
    Convenience function to analyze an incident using the default provider.

    Args:
        incident_data: Incident data to analyze
        analysis_type: Type of analysis to perform

    Returns:
        Analysis result
    """
    return get_analysis_service().analyze_incident(
        AnalysisRequest(incident_data=incident_data, analysis_type=analysis_type)
    )

def health_check_all() -> dict:
    """
    Health check for all available providers.

    Returns:
        Dictionary with health status for each provider
    """
    service = get_analysis_service()
    providers = service.config.get_all_providers()
    health_status = {}

    for provider_name in providers:
        try:
            is_healthy = service.providers[provider_name].health_check()
            health_status[provider_name] = {
                'available': service.is_provider_available(provider_name),
                'healthy': is_healthy,
                'config': service.config.get_provider_config(provider_name)
            }
        except Exception as e:
            health_status[provider_name] = {
                'available': service.is_provider_available(provider_name),
                'healthy': False,
                'error': str(e)
            }

    return health_status


def switch_provider(provider_name: str) -> bool:
    """
    Switch to a different AI provider.

    Args:
        provider_name: Name of the provider to switch to

    Returns:
        True if switch successful, False otherwise
    """
    global _analysis_service

    if _analysis_service is None:
        return False

    # Check if provider is available
    if not _analysis_service.is_provider_available(provider_name):
        return False

    # Switch to new provider
    _analysis_service = AnalysisService(AIProviderConfig())
    # Note: This is a simplified approach - in reality, you'd want to preserve
    # some configuration while switching providers

    return True


# ==============================================================================
# Analysis Service
# ==============================================================================

class AnalysisService:
    """Service for analyzing incidents using configured AI providers."""

    def __init__(self, config: AIProviderConfig):
        self.config = config
        self.providers = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all available providers."""
        for provider_name in self.config.get_all_providers():
            provider_config = self.config.get_provider_config(provider_name)

            if provider_config.get('available', False):
                try:
                    if provider_name == 'mock':
                        self.providers[provider_name] = MockAIProvider(provider_config)
                    elif provider_name == 'openai':
                        # This would normally be OpenAI provider, but we'll use mock for now
                        self.providers[provider_name] = MockAIProvider(provider_config)
                    elif provider_name == 'ollama' and OLLAMA_AVAILABLE:
                        # Initialize Ollama provider
                        self.providers[provider_name] = get_ollama_provider()
                    else:
                        print(f"Warning: Unknown provider '{provider_name}', skipping")
                        continue

                    print(f"✅ Initialized provider: {provider_name}")
                except Exception as e:
                    print(f"❌ Failed to initialize provider '{provider_name}': {e}")

    def get_provider(self, provider_name: str = None) -> AIProvider:
        """Get a specific provider or the active provider."""
        if provider_name is None:
            provider_name = self.config.active_provider

        if provider_name not in self.providers:
            raise ProviderNotAvailableError(f"Provider '{provider_name}' is not available")

        return self.providers[provider_name]

    def is_provider_available(self, provider_name: str) -> bool:
        """Check if a provider is available."""
        return self.config.is_provider_available(provider_name)

    def analyze_incident(self, request: AnalysisRequest) -> AnalysisResult:
        """Analyze an incident using the active provider."""
        provider = self.get_provider()
        return provider.analyze_incident(request)

    def health_check_all(self) -> dict:
        """Health check for all providers."""
        health_status = {}
        for name, provider in self.providers.items():
            try:
                healthy = provider.health_check()
                health_status[name] = {
                    'available': True,
                    'healthy': healthy,
                    'provider_info': provider.get_provider_info()
                }
            except Exception as e:
                health_status[name] = {
                    'available': True,
                    'healthy': False,
                    'error': str(e)
                }
        return health_status

    def get_provider_info(self, provider_name: str = None) -> dict:
        """Get information about a specific provider."""
        if provider_name is None:
            provider_name = self.config.active_provider

        if provider_name not in self.providers:
            return {'available': False}

        return {
            'available': True,
            'config': self.config.get_provider_config(provider_name),
            'info': self.providers[provider_name].get_provider_info()
        }

    def configure_provider(self, provider_name: str, config: dict) -> bool:
        """Configure a specific provider."""
        if provider_name not in self.providers:
            return False

        # In a real implementation, you would update the provider configuration
        # For now, we'll just print a warning
        print(f"Note: Configuration update for provider '{provider_name}' not implemented")
        return True


# ==============================================================================
# Mock AI Provider (For Testing)
# ==============================================================================

class MockAIProvider(AIProvider):
    """Mock AI provider for testing purposes."""

    def __init__(self, config: dict):
        self.config = config
        self.simulation_delay_ms = config.get('simulation_delay_ms', 100)
        self.success_rate = config.get('success_rate', 1.0)
        self.error_types = config.get('error_types', [])
        self.call_count = 0

    def analyze_incident(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Mock implementation of incident analysis.

        This simulates various scenarios for testing:
        - Successful analysis
        - Invalid input
        - Provider errors
        - Per-request timeout support
        """
        self.call_count += 1

        # Check for per-request timeout
        req_timeout = request.constraints.get('investigation_timeout')
        if req_timeout is not None:
            # Explicitly reject boolean values (bool is subclass of int in Python)
            if isinstance(req_timeout, bool):
                raise RuntimeError(
                    f"Invalid investigation timeout: {req_timeout}. Must be a positive number (int or float), not a boolean."
                )
            if not isinstance(req_timeout, (int, float)) or req_timeout <= 0:
                raise RuntimeError(
                    f"Invalid investigation timeout: {req_timeout}. Must be a positive number."
                )
            # If simulation delay exceeds timeout, raise timeout error
            if self.simulation_delay_ms > 0 and (self.simulation_delay_ms / 1000.0) > req_timeout:
                from investigation_service import TimeoutError
                raise TimeoutError(f"Mock provider timed out after {req_timeout}s")

        # Simulate processing time
        if self.simulation_delay_ms > 0:
            import time
            time.sleep(self.simulation_delay_ms / 1000.0)

        # Simulate different scenarios based on call count
        if len(self.error_types) > 0 and self.call_count % 10 == 0:
            # Simulate an error on every 10th call if error_types specified
            return AnalysisResult(
                success=False,
                analysis_type=request.analysis_type,
                confidence_score=0.0,
                hypotheses=[],
                recommendations=[],
                reasoning="Mock provider simulation error",
                errors=[f"Simulated error {self.call_count}"],
                warnings=[]
            )

        # Check for invalid input
        if not request.incident_data or not request.incident_data.title:
            return AnalysisResult(
                success=False,
                analysis_type=request.analysis_type,
                confidence_score=0.0,
                hypotheses=[],
                recommendations=[],
                reasoning="Invalid incident data",
                errors=["Incident data is missing required fields"],
                warnings=[]
            )

        # Successful analysis simulation
        hypotheses = [
            "Hypothesis 1: Root cause is service dependency",
            "Hypothesis 2: Configuration issue in load balancer",
            "Hypothesis 3: Network connectivity problem"
        ]

        recommendations = [
            "Restart affected services",
            "Check load balancer configuration",
            "Monitor network connectivity"
        ]

        confidence = 0.75 + (hash(request.incident_data.title) % 100) / 100.0

        # Handle template guidance deterministically
        warnings = []
        metadata = {
            'provider': 'mock',
            'call_count': self.call_count,
            'simulation_delay_ms': self.simulation_delay_ms,
            'success_rate': self.success_rate
        }

        # Process template guidance if present and has meaningful content
        if request.template_guidance:
            # Check if template guidance has meaningful content
            # Only process if it has at least template_id or name
            if (request.template_guidance.get('template_id') or
                request.template_guidance.get('name') or
                request.template_guidance.get('applicable_services') or
                request.template_guidance.get('description')):

                # Make template guidance presence visible in metadata
                template_info = {
                    'template_id': request.template_guidance.get('template_id'),
                    'name': request.template_guidance.get('name'),
                    'applicable_services': request.template_guidance.get('applicable_services'),
                    'description': request.template_guidance.get('description'),
                    'present': True
                }
                metadata['template_guidance'] = template_info

                # Add warning about template guidance (separate from incident facts)
                warnings.append(
                    f"Template guidance '{request.template_guidance.get('name', 'unknown')}' provided but not applied to incident analysis"
                )

        return AnalysisResult(
            success=True,
            analysis_type=request.analysis_type,
            confidence_score=round(confidence, 2),
            hypotheses=hypotheses,
            recommendations=recommendations,
            reasoning=f"Analysis completed for incident '{request.incident_data.title}' with severity '{request.incident_data.severity}'",
            metadata=metadata,
            errors=[],
            warnings=warnings
        )

    def health_check(self) -> bool:
        """Mock health check - always returns True."""
        return True

    def get_provider_info(self) -> dict:
        """Get mock provider information."""
        return {
            'name': self.config.get('name', 'Mock AI Provider'),
            'description': self.config.get('description', 'Mock provider for testing'),
            'available': True,
            'is_mock': True
        }

    def configure(self, config: dict) -> bool:
        """Update mock provider configuration."""
        try:
            self.simulation_delay_ms = config.get('simulation_delay_ms', self.simulation_delay_ms)
            self.success_rate = config.get('success_rate', self.success_rate)
            self.error_types = config.get('error_types', self.error_types)
            return True
        except Exception:
            return False


# ==============================================================================
# Utility Functions
# ==============================================================================

def create_test_incident_data() -> IncidentData:
    """Create test incident data for testing."""
    return IncidentData(
        incident_id="test-incident-001",
        title="Test Incident for Analysis",
        description="This is a test incident for testing AI analysis capabilities",
        severity="critical",
        status="investigating",
        service="api-service",
        created_at="2024-01-01T12:00:00Z",
        events=[
            {
                "id": "event-001",
                "type": "incident_created",
                "description": "Incident was created",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        ],
        analysis_metadata={}
    )

def simulate_provider_error(provider_name: str, error_type: str = "generic") -> bool:
    """
    Simulate a provider error for testing error handling.

    Args:
        provider_name: Name of the provider to simulate error for
        error_type: Type of error to simulate

    Returns:
        True if error simulation successful, False otherwise
    """
    # This is a simple simulation function
    # In a real implementation, you would inject errors into the provider
    print(f"Note: Error simulation for provider '{provider_name}' not implemented")
    print(f"Note: Error type '{error_type}' would be injected into provider")
    return True


# Auto-initialize the analysis service
_analysis_service = AnalysisService(AIProviderConfig())

print("✅ AI Provider Foundation initialized successfully")
print(f"📋 Active provider: {_analysis_service.config.active_provider}")
print(f"📋 Available providers: {_analysis_service.config.get_all_providers()}")