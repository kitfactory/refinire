"""
Refinire Core - LLM abstraction and infrastructure

This module provides the core functionality for the Refinire AI agent platform:
- Unified LLM interface across multiple providers (OpenAI, Anthropic, Google, Ollama)
- Tracing and observability infrastructure  
- Prompt management with PromptStore
- Provider model implementations
"""

__version__ = "0.2.0"

# LLM abstraction layer
from .llm import ProviderType, get_llm, get_available_models, get_available_models_async

# Provider model implementations
from .anthropic import ClaudeModel
from .gemini import GeminiModel
from .ollama import OllamaModel

# Tracing and observability
from .tracing import enable_console_tracing, disable_tracing
from .trace_registry import TraceRegistry, TraceMetadata, get_global_registry, set_global_registry

# OpenTelemetry tracing (optional, requires openinference-instrumentation)
try:
    from .opentelemetry_tracing import (
        enable_opentelemetry_tracing, 
        disable_opentelemetry_tracing, 
        is_opentelemetry_enabled,
        is_openinference_available,
        get_tracer
    )
    _OPENTELEMETRY_AVAILABLE = True
except ImportError:
    _OPENTELEMETRY_AVAILABLE = False
    # Provide no-op functions when OpenTelemetry is not available
    def enable_opentelemetry_tracing(*args, **kwargs):
        return False
    def disable_opentelemetry_tracing():
        pass
    def is_opentelemetry_enabled():
        return False
    def is_openinference_available():
        return False
    def get_tracer(*args, **kwargs):
        return None

# Message and localization
from .message import get_message, DEFAULT_LANGUAGE

# Prompt management
from .prompt_store import PromptStore, StoredPrompt, PromptReference, P, detect_system_language, get_default_storage_dir

__all__ = [
    # LLM abstraction
    "ProviderType", 
    "get_llm", 
    "get_available_models", 
    "get_available_models_async",
    
    # Provider models
    "ClaudeModel",
    "GeminiModel", 
    "OllamaModel",
    
    # Tracing
    "enable_console_tracing", 
    "disable_tracing",
    "TraceRegistry", 
    "TraceMetadata", 
    "get_global_registry", 
    "set_global_registry",
    
    # OpenTelemetry tracing
    "enable_opentelemetry_tracing",
    "disable_opentelemetry_tracing", 
    "is_opentelemetry_enabled",
    "is_openinference_available",
    "get_tracer",
    
    # Message and localization
    "get_message",
    "DEFAULT_LANGUAGE",
    
    # Prompt management
    "PromptStore",
    "StoredPrompt", 
    "PromptReference",
    "P",
    "detect_system_language",
    "get_default_storage_dir"
]