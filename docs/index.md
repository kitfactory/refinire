# Welcome to Refinire

A comprehensive extension for OpenAI Agents SDK that provides unified interfaces for multiple LLM providers and advanced workflow capabilities.

## Key Features

- Easy switching between OpenAI, Gemini, Claude, Ollama and other major LLMs
- **🚀 New Feature:** Ultra-simple workflow creation with `Flow(steps=gen_agent)`
- **🚀 New Feature:** Automatic sequential execution with `Flow(steps=[step1, step2])`
- Integrated pipeline combining generation, evaluation, tools, and guardrails
- Self-improvement cycles with just model names and prompts
- Pydantic-based structured output support
- Python 3.9+ / Windows, Linux, MacOS support

## Installation

### From PyPI
```bash
pip install refinire
```

### Using uv
```bash
uv pip install refinire
```

## Development (Recommended)
```bash
git clone https://github.com/kitfactory/refinire.git
cd refinire
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
uv pip install -e .[dev]
```

## Supported Environments
- Python 3.9+
- OpenAI Agents SDK 0.0.9+
- Windows, Linux, MacOS 

## Tracing and Observability
Refinire provides comprehensive tracing capabilities with built-in console output and optional OpenTelemetry integration for advanced observability. For details, see [Tracing Tutorial](tutorials/tracing.md).

## Documentation

- [API Reference](api_reference.md) - Detailed class and function documentation
- [Quick Start](tutorials/quickstart.md) - Get started immediately
- [Composable Flow Architecture](composable-flow-architecture.md) - Advanced workflow construction

## Learning Resources

- [Tutorials](tutorials/) - Step-by-step learning content
- [Examples](../examples/) - Practical use cases  
- [Developer Guide](developer/) - Information for contributors 