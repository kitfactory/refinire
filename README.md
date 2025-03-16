# Agents SDK Models 🤖🔌

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents](https://img.shields.io/badge/OpenAI-Agents-green.svg)](https://github.com/openai/openai-agents-python)

A collection of model adapters for OpenAI Agents SDK, allowing you to use various LLM providers with a unified interface! 🚀

## 🌟 Features

- 🔄 **Unified Interface**: Use the same OpenAI Agents SDK interface with multiple model providers
- 🧩 **Multiple Models**: Support for Ollama, Google Gemini, and Anthropic Claude
- 📊 **Structured Output**: All models support structured output using Pydantic models
- 🌊 **Streaming**: Support for streaming responses (where available)
- 🤔 **Thinking**: Enable extended thinking capabilities for complex reasoning (Claude)

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/agents-sdk-models.git
cd agents-sdk-models

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install the package in development mode
pip install -e .
```

## 🚀 Quick Start

### Ollama

```python
import asyncio
from agents import Agent, Runner
from agents_sdk_models import OllamaModel

async def main():
    # Initialize the Ollama model
    model = OllamaModel(
        model="llama3",  # or any other model available in your Ollama instance
        temperature=0.7
    )
    
    # Create an agent with the model
    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant.",
        model=model
    )
    
    # Run the agent
    response = await Runner.run(agent, "What is your name and what can you do?")
    print(response.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

### Google Gemini

```python
import asyncio
import os
from agents import Agent, Runner
from agents_sdk_models import GeminiModel

async def main():
    # Get API key from environment variable
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    # Initialize the Gemini model
    model = GeminiModel(
        model="gemini-1.5-pro",
        temperature=0.7,
        api_key=api_key
    )
    
    # Create an agent with the model
    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant.",
        model=model
    )
    
    # Run the agent
    response = await Runner.run(agent, "What is your name and what can you do?")
    print(response.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

### Anthropic Claude

```python
import asyncio
import os
from agents import Agent, Runner
from agents_sdk_models import ClaudeModel

async def main():
    # Get API key from environment variable
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    # Initialize the Claude model
    model = ClaudeModel(
        model="claude-3-sonnet-20240229",
        temperature=0.7,
        api_key=api_key,
        thinking=True  # Enable thinking for complex reasoning
    )
    
    # Create an agent with the model
    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant.",
        model=model
    )
    
    # Run the agent
    response = await Runner.run(agent, "What is your name and what can you do?")
    print(response.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

## 📊 Structured Output

All models support structured output using Pydantic models:

```python
from pydantic import BaseModel
from typing import List

class WeatherInfo(BaseModel):
    location: str
    temperature: float
    condition: str
    recommendation: str

class WeatherReport(BaseModel):
    report_date: str
    locations: List[WeatherInfo]

# Create an agent with structured output
agent = Agent(
    name="Weather Reporter",
    model=model,
    instructions="You are a helpful weather reporter.",
    output_type=WeatherReport
)

# Get structured response
response = await Runner.run(agent, "What's the weather like in Tokyo, Osaka, and Sapporo?")
weather_report = response.final_output  # This is a WeatherReport object
```

## 🔧 Supported Environments

- **Operating Systems**: Windows, macOS, Linux
- **Python Version**: 3.11+
- **Dependencies**: 
  - openai>=1.66.2
  - openai-agents==0.0.4
  - pydantic>=2.10, <3
  - ollama>=0.4.7 (for Ollama support)

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [Ollama](https://ollama.ai/)
- [Google Gemini](https://ai.google.dev/)
- [Anthropic Claude](https://www.anthropic.com/claude)
