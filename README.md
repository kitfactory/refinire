# Agents SDK Models 🤖🔌

[![PyPI Downloads](https://static.pepy.tech/badge/agents-sdk-models)](https://pepy.tech/projects/agents-sdk-models)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents 0.0.9](https://img.shields.io/badge/OpenAI-Agents_0.0.9-green.svg)](https://github.com/openai/openai-agents-python)
[![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen.svg)]

A collection of model adapters and workflow utilities for the OpenAI Agents SDK, enabling you to use various LLM providers and build practical agent pipelines with a unified interface!

## ⚡ Recommended: Flow/Step Architecture - **Super Simple!** 

**🎉 New in v0.0.22:** We now recommend using the **Flow/Step architecture** with **GenAgent**. It's incredibly simple and powerful!

### 🚀 **Just 3 Lines to Get Started!**

```python
from agents_sdk_models import create_simple_gen_agent, create_simple_flow

# Step 1: Create a GenAgent (like AgentPipeline, but better!)
gen_agent = create_simple_gen_agent(
    name="story_generator",
    generation_instructions="Generate creative stories",
    model="gpt-4o-mini"
)

# Step 2: Create a Flow (even simpler now!)
flow = Flow(steps=gen_agent)  # Single step - that's it!

# Step 3: Run it! (same simple interface as before)
result = await flow.run(input_data="A robot learning to paint")
print(result.shared_state["story_generator_result"])  # Your creative story is ready!
```

### 🚀 **NEW: Ultra-Simple Flow Creation!**

Now you can create flows in **3 different ways**:

```python
# 1. Single Step (NEW!)
flow = Flow(steps=gen_agent)

# 2. Sequential Steps (NEW!)
flow = Flow(steps=[step1, step2, step3])  # Auto-connects them!

# 3. Traditional (for complex flows)
flow = Flow(start="step1", steps={"step1": step1, "step2": step2})
```

### 🎯 **Why is it SO Much Simpler?**

| **LangChain/LangGraph (~50-100+ lines)** | **GenAgent + Flow (3-5 lines)** |
|---------------------------|----------------------------|
| 🔧 **Complex imports** (10+ modules) | ✨ **One import** - everything included |
| 📝 **Manual prompt templates** | 🎯 **Simple instruction strings** |
| 🧩 **Graph/Chain building** (20+ lines) | 🔄 **Auto-generated workflows** |
| ⚙️ **Custom error handling** | 🛡️ **Built-in error recovery** |
| 🔁 **Manual retry logic** | 🔄 **Auto-retry with evaluation** |
| 🛠️ **State management code** | 📦 **Handled automatically** |

### 🌟 **Real-World Example: Content Generator with Evaluation**

```python
from agents_sdk_models import create_simple_gen_agent
from agents_sdk_models.flow import Flow
from agents_sdk_models.step import UserInputStep, DebugStep

# Create GenAgent with evaluation (replaces complex AgentPipeline setup)
gen_agent = create_simple_gen_agent(
    name="content_creator",
    generation_instructions="Create engaging blog posts",
    evaluation_instructions="Rate creativity and readability (0-100)",  # Auto-evaluation!
    model="gpt-4o-mini",
    threshold=70  # Auto-retry if score < 70!
)

# Build a Flow in seconds (not minutes!)
flow = Flow(steps=[gen_agent, DebugStep("debug", "See what happened")])  # Sequential steps!

# Run the complete workflow
result = await flow.run(input_data="Create a blog about AI")
print(result.shared_state["content_creator_result"])
# Automatically handles: generation → evaluation → retry → output
```

### 🎨 **Compared to LangChain/LangGraph - HUGE Difference!**

```python
# LangChain/LangGraph way (~80+ lines, complex setup)
"""
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from langchain.callbacks import BaseCallbackHandler
from langchain.schema.runnable import RunnablePassthrough
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
# ... (約15行のimport文) ...

class AgentState(TypedDict):
    input: str
    generation: str
    evaluation: dict
    retry_count: int
    # ... (約10行の状態定義) ...

def generation_node(state):
    # ... (約15行の生成ロジック) ...
    
def evaluation_node(state):
    # ... (約20行の評価ロジック) ...
    
def should_retry(state):
    # ... (約10行のリトライ判定) ...

workflow = StateGraph(AgentState)
workflow.add_node("generate", generation_node)
workflow.add_node("evaluate", evaluation_node)
workflow.add_conditional_edges(
    "evaluate", 
    should_retry,
    {"retry": "generate", "end": END}
)
# ... (約10行のグラフ構築) ...
"""

# GenAgent + Flow way (3 lines!)
gen_agent = create_simple_gen_agent(
    name="simple_setup",
    generation_instructions="...",
    evaluation_instructions="...",  # Auto-evaluation & retry!
    model="gpt-4o-mini",
    threshold=70
)
flow = Flow(steps=gen_agent)  # Just one line!
result = await flow.run(input_data="Your input")  # Done!
```

### 🏗️ **Advanced Features Made Simple**

```python
# Complex workflows? Still just a few lines!
from agents_sdk_models.step import ConditionStep, FunctionStep

def check_content_type(user_input, ctx):
    return "blog" if "blog" in user_input.lower() else "story"

# Build complex logic with simple steps
blog_gen = create_simple_gen_agent("blog", "Write blogs", "gpt-4o")
story_gen = create_simple_gen_agent("story", "Write stories", "claude-3-5-sonnet-latest")

# Traditional mode for complex flows
advanced_flow = Flow(
    start="check_type",
    steps={
        "check_type": ConditionStep("check_type", check_content_type, "blog_gen", "story_gen"),
        "blog_gen": blog_gen,
        "story_gen": story_gen,
        "done": DebugStep("done", "Finished!")  # Finished!
    }
)
```

### ✨ **Benefits You'll Love:**
- 🔄 **More Flexibility**: Compose complex workflows using modular steps
- 🧩 **Better Reusability**: Steps can be reused across different flows  
- 🎯 **Cleaner Architecture**: Clear separation of concerns
- 🚀 **Future-Proof**: Designed for scalability and extensibility
- 💡 **Intuitive**: If you understand AgentPipeline, you already understand this!

**Note:** Compared to LangChain/LangGraph's 50-100+ lines of complex setup, GenAgent + Flow achieves the same functionality in just 3-5 lines! `AgentPipeline` is now deprecated and will be removed in v0.1.0.

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

## v0.22 Release Notes
- **🚀 Major: New Flow Constructor** - Added ultra-simple Flow creation with 3 modes:
  - Single step: `Flow(steps=gen_agent)` 
  - Sequential steps: `Flow(steps=[step1, step2, step3])` (auto-connects)
  - Traditional: `Flow(start="step1", steps={"step1": step1, "step2": step2})`
- **🚀 Enhanced Flow.run()** - Added `input_data` parameter (preferred over `initial_input`)
- **✨ GenAgent + Flow Architecture** - Now recommended over AgentPipeline for new projects
- **⚠️ AgentPipeline Deprecation** - AgentPipeline is now deprecated and will be removed in v0.1.0
- **📚 Complete Documentation Update** - All tutorials and examples updated to showcase new Flow features

## v0.21 Release Notes
- Fix `get_available_models` synchronous function to work properly in environments with running event loops (e.g., Jupyter Notebook, IPython)
- Support dynamic model discovery for Ollama via `/api/tag` endpoint

## v0.20 Release Notes
- Support `OLLAMA_BASE_URL` environment variable for Ollama configuration
- Remove OpenAI Agents SDK standard Trace and use console-only tracing for better compatibility

## v0.19 Release Notes
- Add `get_available_models()` and `get_available_models_async()` functions to retrieve available model names from different providers
- Update model lists to latest versions: Claude-4 (Opus/Sonnet), Gemini 2.5 (Pro/Flash), OpenAI latest models (gpt-4.1, o3, o4-mini)

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

### Example: Get Available Models
```python
from agents_sdk_models import get_available_models, get_available_models_async

# Get models from all providers (synchronous)
models = get_available_models(["openai", "google", "anthropic", "ollama"])
print("Available models:", models)

# Get models from specific providers (asynchronous)
import asyncio
async def main():
    models = await get_available_models_async(["openai", "google"])
    for provider, model_list in models.items():
        print(f"{provider}: {model_list}")

asyncio.run(main())

# Custom Ollama URL
models = get_available_models(["ollama"], ollama_base_url="http://custom-host:11434")
```

---

## 🏗️ AgentPipeline Class: Easy LLM Workflows (⚠️ Deprecated)

**⚠️ Deprecated:** `AgentPipeline` is deprecated as of v0.0.22 and will be removed in v0.1.0. Please use [GenAgent with Flow/Step architecture](#-recommended-flowstep-architecture) instead.

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