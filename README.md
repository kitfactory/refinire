# Agents SDK Models 🤖🔌

[![PyPI Downloads](https://static.pepy.tech/badge/agents-sdk-models)](https://pepy.tech/projects/agents-sdk-models)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents 0.0.9](https://img.shields.io/badge/OpenAI-Agents_0.0.9-green.svg)](https://github.com/openai/openai-agents-python)

A collection of model adapters and workflow utilities for the OpenAI Agents SDK, enabling you to use various LLM providers and build practical agent pipelines with a unified interface!

---

## 🌟 Features

- 🔄 **Unified Factory**: Use the `get_llm` function to easily get model instances for different providers.
- 🧩 **Multiple Providers**: Support for OpenAI, Ollama, Google Gemini, and Anthropic Claude.
- 📊 **Structured Output**: All models instantiated via `get_llm` support structured output using Pydantic models.
- 🏗️ **Pipeline Class**: Easily compose generation, evaluation, tool integration, and guardrails in one workflow.
- 🛡️ **Guardrails**: Add input/output guardrails for safe and compliant agent behavior.
- 🛠️ **Simple Interface**: Minimal code, maximum flexibility.

---

## 🛠️ Installation

### From PyPI (Recommended)
```bash
pip install agents-sdk-models
# For examples with structured output (includes pydantic)
pip install agents-sdk-models[examples]
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

---

## 🏗️ Pipeline Class: Easy LLM Workflows

The `Pipeline` class lets you flexibly build LLM agent workflows by combining generation templates, evaluation templates, tools, and guardrails.

### Basic Usage
```python
from agents_sdk_models.pipeline import Pipeline

pipeline = Pipeline(
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
pipeline = Pipeline(
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

pipeline = Pipeline(
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
from agents_sdk_models.pipeline import Pipeline
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

pipeline = Pipeline(
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
from agents_sdk_models.pipeline import Pipeline

def my_dynamic_prompt(user_input: str) -> str:
    # Example: Uppercase the user input and add a prefix
    return f"[DYNAMIC PROMPT] USER SAID: {user_input.upper()}"

pipeline = Pipeline(
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