# Agents SDK Models 🤖🔌

[![PyPI Downloads](https://static.pepy.tech/badge/agents-sdk-models)](https://pepy.tech/projects/agents-sdk-models)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents 0.0.9](https://img.shields.io/badge/OpenAI-Agents_0.0.9-green.svg)](https://github.com/openai/openai-agents-python)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)]

A collection of model adapters and workflow utilities for the OpenAI Agents SDK, enabling you to use various LLM providers and build practical agent pipelines with a unified interface!

---

## 🌟 Features

- 🔄 **Unified Factory**: Use the `get_llm` function to easily get model instances for different providers.
- 🧩 **Multiple Providers**: Support for OpenAI, Ollama, Google Gemini, and Anthropic Claude.
- 📊 **Structured Output**: All models instantiated via `get_llm` support structured output using Pydantic models.
- 🏗️ **AgentPipeline Class**: Easily compose generation, evaluation, tool integration, and guardrails in one workflow.
- 🛡️ **Guardrails**: Add input/output guardrails for safe and compliant agent behavior.
- 🛠️ **Simple Interface**: Minimal code, maximum flexibility.
- ✨ **Zero-Code Evaluation & Self-Improvement**: Just specify model names and system prompts to automatically run generation, evaluation, and feedback-driven retries.
- 🔍 **Custom Console Tracing**: Console tracing is enabled by default using `ConsoleTracingProcessor`. While the OpenAI Agents SDK uses OpenAI's Tracing service by default (requiring `OPENAI_API_KEY`), this library provides a lightweight console-based tracer that works with any provider. You can disable tracing entirely with `disable_tracing()`.

---

## v0.18 Release Notes
- Support OpenAI Agents SDK Trace feature, with default console tracing enabled.
- Add `evaluation_model` parameter to switch evaluation model separately from generation model.

## 🛠️ Installation

### From PyPI (Recommended)
```bash
pip install agents-sdk-models
```

### From Source
```bash
git clone https://github.com/kitfactory/agents-sdk-models.git
cd agents-sdk-models
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -e .[dev]
```

## 🧪 Tests & Coverage

Run tests and generate a coverage report:

```bash
pytest --cov=agents_sdk_models --cov-report=term-missing
```
- ✅ All tests currently pass successfully.
- The coverage badge indicates the line coverage percentage for the `agents_sdk_models` package (measured by pytest-cov).

---

## 🚀 Quick Start: Using `get_llm`

The `get_llm` function supports specifying the model and provider, or just the model (provider is inferred):

```python
from agents_sdk_models import get_llm

# Specify both model and provider
llm = get_llm(model="gpt-4o-mini", provider="openai")
# Or just the model (provider inferred)
llm = get_llm("claude-3-5-sonnet-latest")
```

### Example: Structured Output
```python
from agents import Agent, Runner
from agents_sdk_models import get_llm
from pydantic import BaseModel

class WeatherInfo(BaseModel):
    location: str
    temperature: float
    condition: str

llm = get_llm("gpt-4o-mini")
agent = Agent(
    name="Weather Reporter",
    model=llm,
    instructions="You are a helpful weather reporter.",
    output_type=WeatherInfo
)
result = Runner.run_sync(agent, "What's the weather in Tokyo?")
print(result.final_output)
```

### Example: Tracing
```python
from agents_sdk_models import enable_console_tracing, disable_tracing
from agents_sdk_models.pipeline import AgentPipeline
from agents.tracing import trace

# Enable console tracing (uses ConsoleTracingProcessor)
enable_console_tracing()

pipeline = AgentPipeline(
    name="trace_example",
    generation_instructions="You are a helpful assistant.",
    evaluation_instructions=None,
    model="gpt-4o-mini"
)

# Run pipeline under a trace context
with trace("MyTrace"):
    result = pipeline.run("Hello, world!")

print(result)
```

---

## 🏗️ AgentPipeline Class: Easy LLM Workflows

The `AgentPipeline` class provides an all-in-one solution for AI agent workflows. It:
  - Generates content based on user-defined instructions
  - Evaluates the generated content with scoring and comments
  - Integrates custom tools (via `function_tool`) for external data or computation
  - Applies input/output guardrails (via `input_guardrail`) for safety and compliance
  - Manages session history and context
  - Supports configurable retries with automatic feedback (via `retry_comment_importance`)

Key initialization parameters:
  - `generation_instructions` (str): System prompt for content generation
  - `evaluation_instructions` (str, optional): System prompt for content evaluation
  - `model` (str, optional): LLM model to use (e.g., "gpt-4o-mini")
  - `evaluation_model` (str, optional): LLM model to use for evaluation (overrides `model`).
  - Note: You can specify a different model provider for `evaluation_model`, such as using OpenAI for generation and a local Ollama model for evaluation, to reduce cost and improve performance.
  - `generation_tools` (list, optional): Tools for generation stage
  - `input_guardrails`, `output_guardrails` (list, optional): Guardrails for input/output
  - `threshold` (int): Minimum score to accept generated content
  - `retries` (int): Number of retry attempts on low evaluation
  - `retry_comment_importance` (list[str], optional): Importance levels (`"serious"`, `"normal"`, `"minor"`) whose comments will be prepended to the prompt on retry

### Basic Usage
```python
from agents_sdk_models.pipeline import AgentPipeline

pipeline = AgentPipeline(
    name="simple_generator",
    generation_instructions="""
    You are a helpful assistant that generates creative stories.
    Please generate a short story based on the user's input.
    """,
    evaluation_instructions=None,  # No evaluation
    model="gpt-4o"
)
result = pipeline.run("A story about a robot learning to paint")
```

### With Evaluation
```python
pipeline = AgentPipeline(
    name="evaluated_generator",
    generation_instructions="""
    You are a helpful assistant that generates creative stories.
    Please generate a short story based on the user's input.
    """,
    evaluation_instructions="""
    You are a story evaluator. Please evaluate the generated story based on:
    1. Creativity (0-100)
    2. Coherence (0-100)
    3. Emotional impact (0-100)
    Calculate the average score and provide specific comments for each aspect.
    """,
    model="gpt-4o",
    threshold=70
)
result = pipeline.run("A story about a robot learning to paint")
```

### With Tools
```python
from agents import function_tool

@function_tool
def search_web(query: str) -> str:
    # Implement actual web search here
    return f"Search results for: {query}"

@function_tool
def get_weather(location: str) -> str:
    # Implement actual weather API here
    return f"Weather in {location}: Sunny, 25°C"

tools = [search_web, get_weather]

pipeline = AgentPipeline(
    name="tooled_generator",
    generation_instructions="""
    You are a helpful assistant that can use tools to gather information.
    You have access to the following tools:
    1. search_web: Search the web for information
    2. get_weather: Get current weather for a location
    Please use these tools when appropriate to provide accurate information.
    """,
    evaluation_instructions=None,
    model="gpt-4o",
    generation_tools=tools
)
result = pipeline.run("What's the weather like in Tokyo?")
```

### With Guardrails (input_guardrails)
```python
from agents import Agent, input_guardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, Runner, RunContextWrapper
from agents_sdk_models.pipeline import AgentPipeline
from pydantic import BaseModel

class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking you to do their math homework.",
    output_type=MathHomeworkOutput,
)

@input_guardrail
async def math_guardrail(ctx: RunContextWrapper, agent: Agent, input: str):
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math_homework,
    )

pipeline = AgentPipeline(
    name="guardrail_pipeline",
    generation_instructions="""
    You are a helpful assistant. Please answer the user's question.
    """,
    evaluation_instructions=None,
    model="gpt-4o",
    input_guardrails=[math_guardrail],
)

try:
    result = pipeline.run("Can you help me solve for x: 2x + 3 = 11?")
    print(result)
except InputGuardrailTripwireTriggered:
    print("[Guardrail Triggered] Math homework detected. Request blocked.")
```

### With Dynamic Prompt
```python
# You can provide a custom function to dynamically build the prompt.
from agents_sdk_models.pipeline import AgentPipeline

def my_dynamic_prompt(user_input: str) -> str:
    # Example: Uppercase the user input and add a prefix
    return f"[DYNAMIC PROMPT] USER SAID: {user_input.upper()}"

pipeline = AgentPipeline(
    name="dynamic_prompt_example",
    generation_instructions="""
    You are a helpful assistant. Respond to the user's request.
    """,
    evaluation_instructions=None,
    model="gpt-4o",
    dynamic_prompt=my_dynamic_prompt
)
result = pipeline.run("Tell me a joke.")
print(result)
```

---

## 🖥️ Supported Environments

- Python 3.9+
- OpenAI Agents SDK 0.0.9+
- Windows, Linux, MacOS

---

## 💡 Why use this?

- **Unified**: One interface for all major LLM providers
- **Flexible**: Compose generation, evaluation, tools, and guardrails as you like
- **Easy**: Minimal code to get started, powerful enough for advanced workflows
- **Safe**: Guardrails for compliance and safety
- **Self-Improving**: Automatic feedback and retry mechanism with minimal configuration

---

## 📂 Examples

See the `examples/` directory for more advanced usage:
- `pipeline_simple_generation.py`: Minimal generation
- `pipeline_with_evaluation.py`: Generation + evaluation
- `pipeline_with_tools.py`: Tool-augmented generation
- `pipeline_with_guardrails.py`: Guardrails (input filtering)

---

## 📄 License & Credits

MIT License. Powered by [OpenAI Agents SDK](https://github.com/openai/openai-agents-python).