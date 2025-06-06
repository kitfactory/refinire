# Agents SDK Models 🤖🔌

[![PyPI Downloads](https://static.pepy.tech/badge/agents-sdk-models)](https://pepy.tech/projects/agents-sdk-models)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents 0.0.9](https://img.shields.io/badge/OpenAI-Agents_0.0.9-green.svg)](https://github.com/openai/openai-agents-python)
[![Coverage](https://img.shields.io/badge/coverage-74%25-brightgreen.svg)]

A collection of model adapters and workflow utilities for the OpenAI Agents SDK, enabling you to use various LLM providers and build practical agent pipelines with a unified interface!

## ⚡ Recommended: Flow/Step Architecture - **Super Simple!** 

**🎉 New in v0.0.24:** Enhanced **Flow/Step architecture** with **standalone agent execution** and **trace search capabilities**. All agents can now run independently!

### 🚀 **Just 3 Lines to Get Started!**

```python
from agents_sdk_models import create_simple_gen_agent, Flow, Context
import asyncio

# Step 1: Create a GenAgent (like AgentPipeline, but better!)
gen_agent = create_simple_gen_agent(
    name="simple_gen",
    instructions="You are a helpful assistant. Answer user questions concisely.",
    model="gpt-4o-mini"
)

# Step 2: Run standalone (no Flow needed!) - NEW in v0.24!
context = Context()
result = asyncio.run(gen_agent.run("Hello! Tell me about Japanese culture briefly.", context))
print(result.shared_state["simple_gen_result"])  # Your response is ready!

# OR Step 2: Create a Flow (if you need complex workflows)
flow = Flow(steps=gen_agent)  # Single step - that's it!
result = asyncio.run(flow.run(input_data="Hello! Tell me about Japanese culture briefly."))
print(result.get_result("simple_gen_result"))
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
from agents_sdk_models import create_evaluated_gen_agent, Context
import asyncio

# Create GenAgent with evaluation (replaces complex AgentPipeline setup)
gen_agent = create_evaluated_gen_agent(
    name="eval_gen",
    generation_instructions="Explain the future of AI in about 200 characters, clearly and accurately.",
    evaluation_instructions="Evaluate if the answer is about 200 characters, clear, and accurate.",
    model="gpt-4o-mini"
)

# Run with evaluation
context = Context()
context.add_user_message("Please explain the future of AI in about 200 characters.")

result = asyncio.run(gen_agent.run("Please explain the future of AI in about 200 characters.", context))
print(result.shared_state["eval_gen_result"])
print("Evaluation:", result.shared_state.get("eval_gen_evaluation"))
# Automatically handles: generation → evaluation → feedback
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
    instructions="...",
    model="gpt-4o-mini"
)
# Use GenAgent directly - no complex Flow needed!
result = asyncio.run(gen_agent.run("Your input", Context()))  # Done!
```

### 🏗️ **Advanced Features Made Simple**

```python
# Simple Flow Example
from agents_sdk_models import Context, FunctionStep, Flow, create_simple_flow
import asyncio

def process_greeting(user_input, ctx):
    """Process greeting with user data"""
    name = ctx.shared_state.get("user_name", "Anonymous")
    task = ctx.shared_state.get("task", "something")
    greeting = f"Hello, {name}! I'll help you with {task}."
    ctx.shared_state["greeting"] = greeting
    ctx.finish()
    return ctx

# Create simple flow
context = Context()
context.shared_state["user_name"] = "Taro"
context.shared_state["task"] = "programming learning"

greeting_step = FunctionStep("greeting", process_greeting)
flow = create_simple_flow([("greeting", greeting_step)], context)

result = asyncio.run(flow.run())
print(result.shared_state.get("greeting"))  # "Hello, Taro! I'll help you with programming learning."
```

### Example: Conditional Flow
```python
from agents_sdk_models import Context, ConditionStep, FunctionStep, Flow
import asyncio

# Create context with user level
context = Context()
context.shared_state["user_level"] = "beginner"

# Create condition function
def is_beginner(ctx):
    return ctx.shared_state.get("user_level") == "beginner"

# Create action functions
def beginner_action(user_input, ctx):
    ctx.shared_state["message"] = "Starting beginner tutorial."
    ctx.finish()
    return ctx

def advanced_action(user_input, ctx):
    ctx.shared_state["message"] = "Displaying advanced content."
    ctx.finish()
    return ctx

# Create conditional flow
condition_step = ConditionStep("condition", is_beginner, "beginner", "advanced")
beginner_step = FunctionStep("beginner", beginner_action)
advanced_step = FunctionStep("advanced", advanced_action)

flow = Flow(
    start="condition",
    steps={
        "condition": condition_step,
        "beginner": beginner_step,
        "advanced": advanced_step
    },
    context=context
)

result = asyncio.run(flow.run())
print(result.shared_state.get("message"))  # "Starting beginner tutorial."
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
- 🤖 **Standalone Agent Execution**: All agents (GenAgent, ClarifyAgent, LLMPipeline) can run independently without Flow.
- 🔍 **Trace Search & Monitoring**: Search and analyze execution traces by flow name, agent name, and custom criteria.
- 💬 **Interactive Agents**: Multi-turn conversation support with state management and context persistence.
- 🛡️ **Guardrails**: Add input/output guardrails for safe and compliant agent behavior.
- 🛠️ **Simple Interface**: Minimal code, maximum flexibility.
- ✨ **Zero-Code Evaluation & Self-Improvement**: Just specify model names and system prompts to automatically run generation, evaluation, and feedback-driven retries.
- 🔍 **Custom Console Tracing**: Console tracing is enabled by default using `ConsoleTracingProcessor`. While the OpenAI Agents SDK uses OpenAI's Tracing service by default (requiring `OPENAI_API_KEY`), this library provides a lightweight console-based tracer that works with any provider. You can disable tracing entirely with `disable_tracing()`.

---

## v0.24 Release Notes
- **🔍 TraceRegistry System** - Comprehensive trace search and analysis by flow name, agent name, tags, status, and time ranges
- **🤖 Agent Standalone Execution** - All agents (GenAgent, ClarifyAgent, LLMPipeline) can now run independently without Flow
- **💬 Interactive Agent Enhancements** - ClarifyAgent with multi-turn conversation loops and state management
- **📁 Agent Organization** - Restructured agents into `/agents` folder for better organization
- **📊 Real-time Flow Monitoring** - Search and monitor running flows with comprehensive statistics
- **📤 Trace Export/Import** - Data persistence for trace analysis and backup
- **🧪 Comprehensive Test Suite** - Full test coverage for all new features
- **📖 Japanese Documentation** - Complete Japanese language documentation and examples
- **⚠️ Library Name Change Notice** - Starting from v0.1.0, this library will be renamed to `ai-flow-sdk`. Please plan for migration.

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
pytest --cov=refinire --cov-report=term-missing
```
- ✅ All tests currently pass successfully.
- The coverage badge indicates the line coverage percentage for the `refinire` package (measured by pytest-cov).

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

### 🔍 NEW: Trace Search & Flow Monitoring
```python
from agents_sdk_models import get_global_registry, Flow
import asyncio

# Create and run flows
flow = Flow(steps=create_simple_gen_agent("ai_assistant", "You are helpful", "gpt-4o-mini"))
await flow.run(input_data="Hello!")

# Search traces by flow and agent names
registry = get_global_registry()

# Find flows by name (exact or partial match)
flows = registry.search_by_flow_name("ai_assistant")
print(f"Found {len(flows)} flows")

# Find flows by agent name
agent_flows = registry.search_by_agent_name("ai_assistant", exact_match=False)
print(f"Found {len(agent_flows)} flows using similar agents")

# Complex search with multiple criteria
complex_results = registry.complex_search(
    flow_name_pattern="ai",
    agent_name_pattern="assistant", 
    status="completed"
)
```

### 🤖 NEW: Standalone Agent Execution
```python
from agents_sdk_models import create_simple_clarify_agent, Context
import asyncio

# Create ClarifyAgent for handling ambiguous requests
agent = create_simple_clarify_agent(
    name="clarify_agent",
    instructions="Ask questions to clarify ambiguous user requests.",
    model="gpt-4o-mini"
)

# Run standalone - no Flow needed!
context = Context()
result = asyncio.run(agent.run("I want to create an API", context))
print("Clarified:", result.shared_state.get("clarify_agent_result"))

# Interactive loop for multi-turn clarification
user_inputs = ["Create a task", "Web app development", "High priority, due next week"]
for turn, user_input in enumerate(user_inputs, 1):
    result = asyncio.run(agent.run(user_input, context))
    print(f"Turn {turn}: {result.shared_state.get('clarify_agent_result')}")
    context = result  # Continue conversation
```

### Example: Multi-Provider LLM Access
```python
from agents_sdk_models import get_llm

# Try different providers
providers = [
    ("openai", "gpt-4o-mini"),
    ("anthropic", "claude-3-haiku-20240307"),
    ("google", "gemini-1.5-flash"),
    ("ollama", "llama3.1:8b")
]

for provider, model in providers:
    try:
        llm = get_llm(provider=provider, model=model)
        print(f"✓ {provider}: {model} - Ready")
    except Exception as e:
        print(f"✗ {provider}: {model} - Error: {str(e)}")
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

## 🛠️ LLMPipeline: Modern Tool-Enabled AI Pipelines (✅ Recommended)

**✅ Recommended:** `LLMPipeline` provides a modern, stable implementation using OpenAI Python SDK directly, with full tool support and automatic function calling.

### 🚀 Key Features

- **🔧 Automatic Tool Execution**: LLM automatically decides when to use tools and executes them seamlessly
- **🚀 No Manual Tool Calling**: Tools are called automatically by the LLM when needed  
- **🔄 Function Calling Loop**: Handles complex multi-tool workflows automatically
- **🔍 Trace Search**: Search and analyze execution traces by flow name, agent name, and custom criteria
- **📊 Built-in Evaluation**: Optional content evaluation with scoring
- **🛡️ Guardrails**: Input/output validation and safety checks
- **💾 Session History**: Maintains conversation context
- **📈 Observability**: Comprehensive tracing and monitoring with span-level tracking
- **🎯 Structured Output**: Pydantic model support for typed responses

### Quick Start with Tools

```python
from agents_sdk_models import create_tool_enabled_llm_pipeline

# Define your tools as simple Python functions
def get_weather(city: str) -> str:
    """Get the current weather for a city"""
    # Your weather API integration here
    return f"Weather in {city}: Sunny, 22°C"

def calculate(expression: str) -> float:
    """Calculate mathematical expressions"""
    return eval(expression)  # Use safer evaluation in production

# Create pipeline with automatic tool registration
pipeline = create_tool_enabled_llm_pipeline(
    name="smart_assistant",
    instructions="You are a helpful assistant with access to tools. Use them when needed.",
    tools=[get_weather, calculate],  # Tools automatically registered
    model="gpt-4o-mini"
)

# Use the pipeline - tools are called automatically! 🎯
result = pipeline.run("What's the weather in Tokyo and what's 15 * 23?")
print(result.content)
# The LLM will automatically:
# 1. Call get_weather("Tokyo") 
# 2. Call calculate("15 * 23")
# 3. Combine results in a natural response

# 🔍 Search execution traces
from agents_sdk_models import get_global_registry

registry = get_global_registry()
# Find all flows that used weather tools
weather_traces = registry.search_by_agent_name("weather", exact_match=False)
print(f"Found {len(weather_traces)} flows using weather tools")
```

### 🏗️ Pre-built Pipeline Types

```python
from agents_sdk_models import (
    create_calculator_pipeline,
    create_web_search_pipeline, 
    create_evaluated_llm_pipeline
)

# 🧮 Calculator pipeline with safe math evaluation
calc_pipeline = create_calculator_pipeline(
    name="math_assistant",
    model="gpt-4o-mini"
)

# 🔍 Web search pipeline (template for search integration)
search_pipeline = create_web_search_pipeline(
    name="search_assistant",
    model="gpt-4o-mini"
)

# ⭐ Pipeline with evaluation and quality control
quality_pipeline = create_evaluated_llm_pipeline(
    name="quality_assistant",
    generation_instructions="Provide helpful, accurate information.",
    evaluation_instructions="Rate accuracy, helpfulness, and clarity (0-100).",
    threshold=80.0,  # Minimum quality score
    model="gpt-4o-mini"
)
```

### ⚙️ Manual Tool Management

```python
from agents_sdk_models import LLMPipeline

# Create pipeline and add tools dynamically
pipeline = LLMPipeline(
    name="custom_assistant",
    generation_instructions="You are a helpful assistant.",
    model="gpt-4o-mini",
    tools=[]
)

# Add tools one by one
def greet(name: str) -> str:
    """Greet a user by name"""
    return f"Hello, {name}!"

pipeline.add_function_tool(greet)

# Manage tools
print(f"Available tools: {pipeline.list_tools()}")
pipeline.remove_tool("greet")
```

### 📊 Why LLMPipeline is Better

| Feature | AgentPipeline (Deprecated) | LLMPipeline (Recommended) |
|---------|---------------------------|---------------------------|
| **API Implementation** | ⚠️ Legacy implementation patterns | ✅ Proper OpenAI Agents SDK usage |
| **Tool Execution** | ⚠️ Manual implementation required | ✅ Automatic tool calling loop |
| **Function Calling** | ⚠️ Limited support | ✅ Full OpenAI function calling |
| **Future Proof** | ❌ Will be removed in v0.1.0 | ✅ Stable, actively maintained |
| **Async Issues** | ❌ Flow integration problems | ✅ Clean async/sync support |
| **Tool Registration** | ⚠️ Complex setup | ✅ Simple function decoration |

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

See the `examples/` directory for comprehensive usage examples:

### Core Features
- `standalone_agent_demo.py`: Standalone agent execution (GenAgent, ClarifyAgent, LLMPipeline)
- `trace_search_demo.py`: Trace search and flow monitoring
- `llm_pipeline_example.py`: Tool-enabled LLM pipelines
- `interactive_pipeline_example.py`: Multi-turn interactive conversations

### Flow Architecture
- `flow_show_example.py`: Flow visualization and debugging
- `simple_flow_test.py`: Basic flow construction and execution
- `router_agent_example.py`: Flow routing and conditional logic

### Agent Types
- `clarify_agent_example.py`: Interactive requirement clarification
- `notification_agent_example.py`: Event-driven notifications
- `extractor_agent_example.py`: Data extraction from text
- `validator_agent_example.py`: Content validation and safety

### Legacy (Deprecated)
- `pipeline_simple_generation.py`: Minimal generation (use GenAgent instead)
- `pipeline_with_evaluation.py`: Generation + evaluation (use LLMPipeline instead)
- `pipeline_with_tools.py`: Tool-augmented generation (use LLMPipeline instead)
- `pipeline_with_guardrails.py`: Guardrails (input filtering)

---

## 📄 License & Credits

MIT License. Powered by [OpenAI Agents SDK](https://github.com/openai/openai-agents-python).