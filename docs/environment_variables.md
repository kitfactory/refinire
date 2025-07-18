# Environment Variables Reference

This document provides a comprehensive reference for all environment variables supported by Refinire.

## Overview

Refinire uses environment variables for configuration and integrates with [oneenv](https://github.com/kitfactory/oneenv) to provide templates for easy setup. The variables are organized into four templates:

- **core**: Core LLM provider configuration
- **tracing**: OpenTelemetry tracing configuration  
- **agents**: AI agent and pipeline configuration
- **development**: Development and debugging configuration

## Usage with oneenv

Install and use oneenv to easily manage these environment variables:

```bash
pip install oneenv
oneenv init refinire:core
oneenv init refinire:tracing
oneenv init refinire:agents
oneenv init refinire:development
```

## Core LLM Provider Configuration
**Template**: `core`

### OPENAI_API_KEY
- **Type**: Optional
- **Description**: OpenAI API key for GPT models
- **Get from**: https://platform.openai.com/api-keys
- **Example**: `sk-proj-...`

### ANTHROPIC_API_KEY
- **Type**: Optional
- **Description**: Anthropic API key for Claude models
- **Get from**: https://console.anthropic.com/
- **Example**: `sk-ant-api03-...`

### GOOGLE_API_KEY
- **Type**: Optional
- **Description**: Google API key for Gemini models
- **Get from**: https://aistudio.google.com/app/apikey
- **Example**: `AIzaSy...`

### OPENROUTER_API_KEY
- **Type**: Optional
- **Description**: OpenRouter API key for accessing multiple model providers
- **Get from**: https://openrouter.ai/keys
- **Example**: `sk-or-v1-...`

### GROQ_API_KEY
- **Type**: Optional
- **Description**: Groq API key for fast inference models
- **Get from**: https://console.groq.com/keys
- **Example**: `gsk_...`

### OLLAMA_BASE_URL
- **Type**: Optional
- **Default**: `http://localhost:11434`
- **Description**: Ollama server base URL for local models
- **Example**: `http://192.168.1.100:11434`

### LMSTUDIO_BASE_URL
- **Type**: Optional
- **Default**: `http://localhost:1234/v1`
- **Description**: LM Studio server base URL for local models
- **Example**: `http://192.168.1.100:1234/v1`

## OpenTelemetry Tracing Configuration
**Template**: `tracing`

### REFINIRE_TRACE_OTLP_ENDPOINT
- **Type**: Optional
- **Description**: OTLP endpoint URL for OpenTelemetry trace export
- **Examples**: 
  - `http://localhost:4317` (Grafana Tempo)
  - `http://jaeger:4317` (Jaeger)
  - `https://api.honeycomb.io:443` (Honeycomb)

### REFINIRE_TRACE_SERVICE_NAME
- **Type**: Optional
- **Default**: `refinire-agent`
- **Description**: Service name for OpenTelemetry traces. Used to identify your application in trace data
- **Example**: `my-ai-app`, `customer-support-bot`

### REFINIRE_TRACE_RESOURCE_ATTRIBUTES
- **Type**: Optional
- **Description**: Additional resource attributes for traces
- **Format**: `key1=value1,key2=value2`
- **Example**: `environment=production,team=ai,version=1.0.0`

## AI Agent and Pipeline Configuration
**Template**: `agents`

### REFINIRE_DEFAULT_LLM_MODEL
- **Type**: Optional
- **Default**: `gpt-4o-mini`
- **Description**: Default LLM model to use when not specified
- **Example**: `gpt-4o`, `claude-3-sonnet-20240229`, `gemini-pro`

### REFINIRE_DEFAULT_TEMPERATURE
- **Type**: Optional
- **Default**: `0.7`
- **Description**: Default temperature for LLM generation (0.0-2.0)
- **Range**: 0.0 (deterministic) to 2.0 (very creative)

### REFINIRE_DEFAULT_MAX_TOKENS
- **Type**: Optional
- **Default**: `2048`
- **Description**: Default maximum tokens for LLM responses
- **Example**: `1024`, `4096`, `8192`

## Development and Debugging Configuration
**Template**: `development`

### REFINIRE_DEBUG
- **Type**: Optional
- **Default**: `false`
- **Description**: Enable debug mode for verbose output
- **Values**: `true`, `false`

### REFINIRE_LOG_LEVEL
- **Type**: Optional
- **Default**: `INFO`
- **Description**: Log level for debugging (**deprecated** - Refinire now uses exceptions instead of logging)
- **Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`

### REFINIRE_CACHE_DIR
- **Type**: Optional
- **Default**: `~/.cache/refinire`
- **Description**: Directory for caching agent responses and models
- **Example**: `/tmp/refinire-cache`, `./cache`

## Provider-Specific Environment Variables

### Azure OpenAI
```bash
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

### OpenRouter
```bash
OPENROUTER_API_KEY=sk-or-v1-...
```

### Groq
```bash
GROQ_API_KEY=gsk_...
```

### LM Studio
```bash
# LM Studio typically runs locally and doesn't require an API key
LMSTUDIO_BASE_URL=http://localhost:1234/v1
```

## Quick Setup Examples

### Basic OpenAI Setup
```bash
export OPENAI_API_KEY="sk-proj-..."
export REFINIRE_DEFAULT_LLM_MODEL="gpt-4o-mini"
```

### Multi-Provider Setup
```bash
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-api03-..."
export GOOGLE_API_KEY="AIzaSy..."
export REFINIRE_DEFAULT_LLM_MODEL="gpt-4o-mini"
```

### Local Development with Tracing
```bash
export REFINIRE_DEBUG="true"
export REFINIRE_TRACE_OTLP_ENDPOINT="http://localhost:4317"
export REFINIRE_TRACE_SERVICE_NAME="my-local-app"
```

### Production Setup
```bash
export OPENAI_API_KEY="sk-proj-..."
export REFINIRE_TRACE_OTLP_ENDPOINT="https://your-tempo-endpoint:443"
export REFINIRE_TRACE_SERVICE_NAME="production-ai-service"
export REFINIRE_TRACE_RESOURCE_ATTRIBUTES="environment=production,version=1.2.3,team=ai"
```

## Environment Variable Priority

Refinire follows this priority order for configuration:

1. **Explicit parameters** in code (highest priority)
2. **Environment variables**
3. **Default values** (lowest priority)

Example:
```python
# This will use the API key from the parameter, not from OPENAI_API_KEY
llm = get_llm(model="gpt-4o", api_key="explicit-key")

# This will use OPENAI_API_KEY environment variable
llm = get_llm(model="gpt-4o")
```

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment files** (`.env`) for local development
3. **Use secure secret management** in production (AWS Secrets Manager, Azure Key Vault, etc.)
4. **Rotate API keys** regularly
5. **Use least-privilege access** for API keys

## Troubleshooting

### Common Issues

**Missing API Key Error**:
```
RefinireConfigurationError: OpenAI API key is required
```
Solution: Set `OPENAI_API_KEY` environment variable

**Connection Error**:
```
RefinireConnectionError: Failed to connect to Ollama at http://localhost:11434
```
Solution: Check `OLLAMA_BASE_URL` and ensure Ollama is running

**Invalid Model Error**:
```
RefinireModelError: Model 'invalid-model' not found
```
Solution: Check `REFINIRE_DEFAULT_LLM_MODEL` value and available models

For more troubleshooting information, see the [main documentation](https://kitfactory.github.io/refinire/).