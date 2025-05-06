# Agents SDK Models 🤖🔌

[![PyPI Downloads](https://static.pepy.tech/badge/agents-sdk-models)](https://pepy.tech/projects/agents-sdk-models)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents 0.0.9](https://img.shields.io/badge/OpenAI-Agents_0.0.9-green.svg)](https://github.com/openai/openai-agents-python)

A collection of model adapters for OpenAI Agents SDK, allowing you to use various LLM providers with a unified interface via the `get_llm` function! 🚀

## 🌟 Features

- 🔄 **Unified Factory**: Use the `get_llm` function to easily get model instances for different providers.
- 🧩 **Multiple Providers**: Support for OpenAI, Ollama, Google Gemini, and Anthropic Claude.
- 📊 **Structured Output**: All models instantiated via `get_llm` support structured output using Pydantic models.
- 🏭 **Simple Interface**: Just specify the provider and optionally the model name.

## 🛠️ Installation

### From PyPI (Recommended)

```bash
# Install from PyPI
pip install agents-sdk-models

# For examples with structured output (includes pydantic)
# You can install the optional dependencies using:
# pip install agents-sdk-models[examples]
# Or install pydantic directly:
pip install agents-sdk-models pydantic>=2.10,<3
```

### From Source

```bash
# Clone the repository
git clone https://github.com/kitfactory/agents-sdk-models.git
cd agents-sdk-models

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install the package in development mode
pip install -e .[dev] # Install with dev dependencies (pytest etc.)
```

## 🚀 Quick Start: Using `get_llm`

The `get_llm` function now supports specifying the model as the first argument, and provider as the second argument. You can also call `get_llm` with only the model argument, and the provider will be inferred automatically if possible.

**New argument order:**
```python
get_llm(model="claude-3-5-sonnet-latest", provider="anthropic")
# or simply
get_llm("claude-3-5-sonnet-latest")
```

- If only the model is specified, the provider will be inferred based on the model name.
- The previous usage with provider as the first argument is still supported for backward compatibility.

```python
import asyncio
import os
from agents import Agent, Runner
# Import the factory function
from agents_sdk_models import get_llm

async def main():
    # --- Example: OpenAI ---
    # Requires OPENAI_API_KEY environment variable
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key:
        print("\nRunning OpenAI example...")
        # Get the model using get_llm
        model_openai = get_llm(
            model="gpt-4o-mini",    # Specify the model name (optional, uses default if None)
            temperature=0.7,
            api_key=openai_api_key # Pass API key if required
        )
        agent_openai = Agent(
            name="Assistant",
            instructions="You are a helpful assistant.",
            model=model_openai
        )
        response_openai = await Runner.run(agent_openai, "What is your name and what can you do?")
        print(response_openai.final_output)
    else:
        print("OPENAI_API_KEY not found. Skipping OpenAI example.")

    # --- Example: Ollama ---
    # Assumes Ollama server is running locally
    print("\nRunning Ollama example...")
    try:
        # Get the model using get_llm
        model_ollama = get_llm(
            model="llama3", # Specify the model name available in your Ollama instance
            temperature=0.7
            # base_url="http://localhost:11434" # Optional: specify if not default
        )
        agent_ollama = Agent(
            name="Assistant",
            instructions="You are a helpful assistant.",
            model=model_ollama
        )
        response_ollama = await Runner.run(agent_ollama, "What is your name and what can you do?")
        print(response_ollama.final_output)
    except Exception as e:
        print(f"Could not run Ollama example: {e}")
        print("Ensure the Ollama server is running and the model 'llama3' is available.")


    # --- Example: Google Gemini ---
    # Requires GOOGLE_API_KEY environment variable
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    if google_api_key:
        print("\nRunning Google Gemini example...")
        # Get the model using get_llm
        model_gemini = get_llm(
            model="gemini-1.5-flash", # Specify the model name
            temperature=0.7,
            api_key=google_api_key
        )
        agent_gemini = Agent(
            name="Assistant",
            instructions="You are a helpful assistant.",
            model=model_gemini
        )
        response_gemini = await Runner.run(agent_gemini, "What is your name and what can you do?")
        print(response_gemini.final_output)
    else:
        print("GOOGLE_API_KEY not found. Skipping Google Gemini example.")


    # --- Example: Anthropic Claude ---
    # Requires ANTHROPIC_API_KEY environment variable
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_api_key:
        print("\nRunning Anthropic Claude example...")
        # Get the model using get_llm
        model_claude = get_llm(
            model="claude-3-haiku-20240307", # Specify the model name
            temperature=0.7,
            api_key=anthropic_api_key,
            thinking=True # Pass provider-specific arguments like 'thinking' for Claude
        )
        agent_claude = Agent(
            name="Assistant",
            instructions="You are a helpful assistant.",
            model=model_claude
        )
        response_claude = await Runner.run(agent_claude, "What is your name and what can you do?")
        print(response_claude.final_output)
    else:
        print("ANTHROPIC_API_KEY not found. Skipping Anthropic Claude example.")


if __name__ == "__main__":
    # Disable tracing for non-OpenAI providers if desired
    # import sys
    # provider = sys.argv[1] if len(sys.argv) > 1 else "openai"
    # if provider != "openai":
    #     from agents import set_tracing_disabled
    #     set_tracing_disabled(True)
    asyncio.run(main())
```

## 📊 Structured Output with `get_llm`

All models obtained via `get_llm` support structured output using Pydantic models:

```python
import asyncio
import os
from agents import Agent, Runner
from agents_sdk_models import get_llm
from pydantic import BaseModel
from typing import List

# --- Define Pydantic Model ---
class WeatherInfo(BaseModel):
    location: str
    temperature: float
    condition: str
    recommendation: str

class WeatherReport(BaseModel):
    report_date: str
    locations: List<WeatherInfo>

# --- Get a model instance (e.g., OpenAI) ---
async def run_structured_example():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        print("OPENAI_API_KEY not found. Skipping structured output example.")
        return

    model = get_llm(
        model="gpt-4o-mini",
        api_key=openai_api_key
    )

    # --- Create Agent with Structured Output ---
    agent = Agent(
        name="Weather Reporter",
        model=model,
        instructions="You are a helpful weather reporter. Provide the date in YYYY-MM-DD format.",
        output_type=WeatherReport # Specify the Pydantic model
    )

    # --- Run Agent and Get Structured Response ---
    print("\nRunning structured output example...")
    response = await Runner.run(agent, "What's the weather like today in Tokyo, Osaka, and Sapporo?")

    # --- Access the structured output ---
    if response.final_output:
        weather_report: WeatherReport = response.final_output
        print(f"Report Date: {weather_report.report_date}")
        for info in weather_report.locations:
            print(f"- Location: {info.location}, Temp: {info.temperature}, Condition: {info.condition}")
            print(f"  Recommendation: {info.recommendation}")
    else:
        print("Failed to get structured output.")
        print(f"Raw output: {response.raw_output}") # Print raw output for debugging

if __name__ == "__main__":
    asyncio.run(run_structured_example())

```

## 🔧 Supported Environments

- **Operating Systems**: Windows, macOS, Linux
- **Python Version**: 3.9+
- **Dependencies**:
  - **Core Dependencies** (defined in `pyproject.toml`):
    - `openai>=1.68.0`
    - `openai-agents>=0.0.6`
  - **Optional Dependencies** (for examples, especially structured output):
    - `pydantic>=2.10,<3` (Can be installed via `pip install agents-sdk-models[examples]` or separately)

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [Ollama](https://ollama.ai/)
- [Google Gemini](https://ai.google.dev/)
- [Anthropic Claude](https://www.anthropic.com/claude)
