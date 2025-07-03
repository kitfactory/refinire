"""
Environment variable templates for Refinire platform

Minimal set of environment variables directly used by the library.
"""

def core_template():
    """Core LLM provider configuration template"""
    return {
        "ANTHROPIC_API_KEY": {
            "description": "Anthropic API key for Claude models\nGet from: https://console.anthropic.com/",
            "default": "",
            "required": False
        },
        "GOOGLE_API_KEY": {
            "description": "Google API key for Gemini models\nGet from: https://aistudio.google.com/app/apikey",
            "default": "",
            "required": False
        },
        "OLLAMA_BASE_URL": {
            "description": "Ollama server base URL for local models",
            "default": "http://localhost:11434",
            "required": False
        },
        "REFINIRE_DEFAULT_LLM_MODEL": {
            "description": "Default LLM model to use",
            "default": "gpt-4o-mini",
            "required": False
        }
    }


def tracing_template():
    """OpenTelemetry tracing configuration template"""
    return {
        "REFINIRE_TRACE_OTLP_ENDPOINT": {
            "description": "OTLP endpoint URL for OpenTelemetry trace export\nExample: http://localhost:4317 (Grafana Tempo)\nExample: http://jaeger:4317 (Jaeger)",
            "default": "",
            "required": False
        },
        "REFINIRE_TRACE_SERVICE_NAME": {
            "description": "Service name for OpenTelemetry traces\nUsed to identify your application in trace data",
            "default": "refinire-agent",
            "required": False
        },
        "REFINIRE_TRACE_RESOURCE_ATTRIBUTES": {
            "description": "Additional resource attributes for traces\nFormat: key1=value1,key2=value2\nExample: environment=production,team=ai,version=1.0.0",
            "default": "",
            "required": False
        }
    }