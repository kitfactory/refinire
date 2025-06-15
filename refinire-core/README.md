# Refinire Core

Core LLM provider abstractions and tracing infrastructure for the Refinire AI agent platform.

## Features

- Unified LLM interface across multiple providers (OpenAI, Anthropic, Google, Ollama)
- Comprehensive tracing and observability infrastructure
- Provider model implementations

## Installation

```bash
pip install refinire-core
```

## Usage

```python
from refinire.core import get_llm

# Get an LLM instance
llm = get_llm(provider="openai", model="gpt-4o-mini")

# Use the LLM
response = llm.generate("Hello, world!")
```

For more documentation, visit [https://kitfactory.github.io/refinire/](https://kitfactory.github.io/refinire/)