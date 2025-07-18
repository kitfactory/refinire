"""
Environment variable templates for Refinire platform

Minimal set of environment variables directly used by the library.
"""

def core_template():
    """Core LLM provider configuration template"""
    return [
        {
            "category": "LLM",
            "option": "OpenAI",
            "env": {
                "OPENAI_API_KEY": {
                    "description": "OpenAI API key for GPT models\nGet from: https://platform.openai.com/api-keys",
                    "default": "",
                    "required": False,
                    "importance": "important"
                }
            }
        },
        {
            "category": "LLM",
            "option": "Anthropic",
            "env": {
                "ANTHROPIC_API_KEY": {
                    "description": "Anthropic API key for Claude models\nGet from: https://console.anthropic.com/",
                    "default": "",
                    "required": False,
                    "importance": "important"
                }
            }
        },
        {
            "category": "LLM",
            "option": "Google",
            "env": {
                "GOOGLE_API_KEY": {
                    "description": "Google API key for Gemini models\nGet from: https://aistudio.google.com/app/apikey",
                    "default": "",
                    "required": False,
                    "importance": "important"
                }
            }
        },
        {
            "category": "LLM",
            "option": "OpenRouter",
            "env": {
                "OPENROUTER_API_KEY": {
                    "description": "OpenRouter API key for accessing multiple model providers\nGet from: https://openrouter.ai/keys",
                    "default": "",
                    "required": False,
                    "importance": "important"
                }
            }
        },
        {
            "category": "LLM",
            "option": "Groq",
            "env": {
                "GROQ_API_KEY": {
                    "description": "Groq API key for fast inference models\nGet from: https://console.groq.com/keys",
                    "default": "",
                    "required": False,
                    "importance": "important"
                }
            }
        },
        {
            "category": "LLM",
            "option": "Ollama",
            "env": {
                "OLLAMA_BASE_URL": {
                    "description": "Ollama server base URL for local models",
                    "default": "http://localhost:11434",
                    "required": False,
                    "importance": "optional"
                }
            }
        },
        {
            "category": "LLM",
            "option": "LMStudio",
            "env": {
                "LMSTUDIO_BASE_URL": {
                    "description": "LM Studio server base URL for local models",
                    "default": "http://localhost:1234/v1",
                    "required": False,
                    "importance": "optional"
                }
            }
        }
    ]


def tracing_template():
    """OpenTelemetry tracing configuration template"""
    return [
        {
            "category": "Tracing",
            "option": "OpenTelemetry",
            "env": {
                "REFINIRE_TRACE_OTLP_ENDPOINT": {
                    "description": "OTLP endpoint URL for OpenTelemetry trace export\nExample: http://localhost:4317 (Grafana Tempo)\nExample: http://jaeger:4317 (Jaeger)",
                    "default": "",
                    "required": False,
                    "importance": "optional"
                },
                "REFINIRE_TRACE_SERVICE_NAME": {
                    "description": "Service name for OpenTelemetry traces\nUsed to identify your application in trace data",
                    "default": "refinire-agent",
                    "required": False,
                    "importance": "optional"
                },
                "REFINIRE_TRACE_RESOURCE_ATTRIBUTES": {
                    "description": "Additional resource attributes for traces\nFormat: key1=value1,key2=value2\nExample: environment=production,team=ai,version=1.0.0",
                    "default": "",
                    "required": False,
                    "importance": "optional"
                }
            }
        }
    ]


def agents_template():
    """AI agent and pipeline configuration template"""
    return [
        {
            "category": "Agents",
            "option": "Configuration",
            "env": {
                "REFINIRE_DEFAULT_LLM_MODEL": {
                    "description": "Default LLM model to use when not specified\nFallback for all tasks when task-specific models are not defined",
                    "default": "gpt-4o-mini",
                    "required": False,
                    "importance": "important"
                },
                "REFINIRE_DEFAULT_GENERATION_LLM_MODEL": {
                    "description": "Default LLM model for generation tasks\nPriority: Direct specification > This setting > REFINIRE_DEFAULT_LLM_MODEL",
                    "default": "gpt-4o-mini",
                    "required": False,
                    "importance": "optional"
                },
                "REFINIRE_DEFAULT_ROUTING_LLM_MODEL": {
                    "description": "Default LLM model for routing decisions\nPriority: Direct specification > This setting > REFINIRE_DEFAULT_LLM_MODEL",
                    "default": "gpt-4o-mini",
                    "required": False,
                    "importance": "optional"
                },
                "REFINIRE_DEFAULT_EVALUATION_LLM_MODEL": {
                    "description": "Default LLM model for evaluation tasks\nPriority: Direct specification > This setting > REFINIRE_DEFAULT_LLM_MODEL",
                    "default": "gpt-4o-mini",
                    "required": False,
                    "importance": "optional"
                },
                "REFINIRE_DEFAULT_TEMPERATURE": {
                    "description": "Default temperature for LLM generation (0.0-2.0)",
                    "default": "0.7",
                    "required": False,
                    "importance": "optional"
                },
                "REFINIRE_DEFAULT_MAX_TOKENS": {
                    "description": "Default maximum tokens for LLM responses",
                    "default": "2048",
                    "required": False,
                    "importance": "optional"
                }
            }
        }
    ]


def development_template():
    """Development and debugging configuration template"""
    return [
        {
            "category": "Development",
            "option": "Debugging",
            "env": {
                "REFINIRE_DEBUG": {
                    "description": "Enable debug mode for verbose output",
                    "default": "false",
                    "required": False,
                    "importance": "optional"
                },
            }
        }
    ]