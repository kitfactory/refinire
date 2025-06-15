# Refinire ✨ - Refined Simplicity for Agentic AI

[![PyPI Downloads](https://static.pepy.tech/badge/refinire)](https://pepy.tech/projects/refinire)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents 0.0.17](https://img.shields.io/badge/OpenAI-Agents_0.0.17-green.svg)](https://github.com/openai/openai-agents-python)
[![Coverage](https://img.shields.io/badge/coverage-72%25-brightgreen.svg)]

**Transform ideas into working AI agents—intuitive agent framework**

---

## Why Refinire?

- **Simple installation** — Just `pip install refinire`
- **Simplify LLM-specific configuration** — No complex setup required
- **Unified API across providers** — OpenAI / Anthropic / Google / Ollama  
- **Built-in evaluation & regeneration loops** — Quality assurance out of the box
- **One-line parallel processing** — Complex async operations with just `{"parallel": [...]}`

## 30-Second Quick Start

```bash
pip install refinire
```

```python
from refinire import RefinireAgent

# Simple AI agent
agent = RefinireAgent(
    name="assistant",
    generation_instructions="You are a helpful assistant.",
    model="gpt-4o-mini"
)

result = agent.run("Hello!")
print(result.content)
```

## The Core Components

Refinire provides key components to support AI agent development.

## RefinireAgent - Integrated Generation and Evaluation

```python
from refinire import RefinireAgent

# Agent with automatic evaluation
agent = RefinireAgent(
    name="quality_writer",
    generation_instructions="Generate high-quality content",
    evaluation_instructions="Rate quality from 0-100",
    threshold=85.0,  # Automatically regenerate if score < 85
    max_retries=3,
    model="gpt-4o-mini"
)

result = agent.run("Write an article about AI")
print(f"Quality Score: {result.evaluation_score}")
print(f"Content: {result.content}")
```


## Flow Architecture: Orchestrate Complex Workflows

### Simple Yet Powerful

```python
from refinire import Flow, FunctionStep, ConditionStep, ParallelStep

# Define your workflow as a composable flow
flow = Flow({
    "start": FunctionStep("analyze", analyze_request),
    "route": ConditionStep("route", route_by_complexity, "simple", "complex"),
    "simple": RefinireAgent(name="simple", generation_instructions="Quick response"),
    "complex": ParallelStep("research", [
        RefinireAgent(name="expert1", generation_instructions="Deep analysis"),
        RefinireAgent(name="expert2", generation_instructions="Alternative perspective")
    ]),
    "aggregate": FunctionStep("combine", combine_results)
})

result = await flow.run("Complex user request")
```

**Compose steps like building blocks. Each step can be a function, condition, parallel execution, or LLM pipeline.**

---

## 1. Unified LLM Interface

Handle multiple LLM providers with a unified interface:

```python
from refinire import get_llm

# One interface, infinite possibilities
llm = get_llm("gpt-4o-mini")
response = llm.complete("Explain the concept of refinement")
```

**📖 Details:** [Unified LLM Interface](docs/unified-llm-interface.md)

## 2. Autonomous Quality Assurance

RefinireAgent's built-in evaluation ensures output quality:

```python
from refinire import RefinireAgent

# Agent with evaluation loop
agent = RefinireAgent(
    name="quality_assistant",
    generation_instructions="Generate helpful responses",
    evaluation_instructions="Rate accuracy and usefulness from 0-100",
    threshold=85.0,
    max_retries=3,
    model="gpt-4o-mini"
)

result = agent.run("Explain quantum computing")
print(f"Evaluation Score: {result.evaluation_score}")
print(f"Content: {result.content}")
```

If evaluation falls below threshold, content is automatically regenerated for consistent high quality.

**📖 Details:** [Autonomous Quality Assurance](docs/autonomous-quality-assurance.md)

## 3. Tool Integration - Automated Function Calling

RefinireAgent automatically executes function tools:

```python
from refinire import RefinireAgent

def calculate(expression: str) -> float:
    """Calculate mathematical expressions"""
    return eval(expression)

def get_weather(city: str) -> str:
    """Get weather for a city"""
    return f"Weather in {city}: Sunny, 22°C"

# Agent with tools
agent = RefinireAgent(
    name="tool_assistant",
    generation_instructions="Answer questions using tools",
    model="gpt-4o-mini"
)

agent.add_function_tool(calculate)
agent.add_function_tool(get_weather)

result = agent.run("What's the weather in Tokyo? Also, what's 15 * 23?")
print(result.content)  # Automatically answers both questions
```

**📖 Details:** [Composable Flow Architecture](docs/composable-flow-architecture.md)

## 4. Automatic Parallel Processing: 3.9x Performance Boost

Dramatically improve performance with parallel execution:

```python
from refinire import Flow, FunctionStep
import asyncio

# Define parallel processing with DAG structure
flow = Flow(start="preprocess", steps={
    "preprocess": FunctionStep("preprocess", preprocess_text),
    "parallel_analysis": {
        "parallel": [
            FunctionStep("sentiment", analyze_sentiment),
            FunctionStep("keywords", extract_keywords), 
            FunctionStep("topic", classify_topic),
            FunctionStep("readability", calculate_readability)
        ],
        "next_step": "aggregate",
        "max_workers": 4
    },
    "aggregate": FunctionStep("aggregate", combine_results)
})

# Sequential: 2.0s → Parallel: 0.5s (3.9x speedup)
result = await flow.run("Analyze this comprehensive text...")
```

Run complex analysis tasks simultaneously without manual async implementation.

**📖 Details:** [Composable Flow Architecture](docs/composable-flow-architecture.md)

### Conditional Intelligence

```python
# AI that makes decisions
def route_by_complexity(ctx):
    return "simple" if len(ctx.user_input) < 50 else "complex"

flow = Flow({
    "router": ConditionStep("router", route_by_complexity, "simple", "complex"),
    "simple": SimpleAgent(),
    "complex": ExpertAgent()
})
```

### Parallel Processing: 3.9x Performance Boost

```python
from refinire import Flow, FunctionStep

# Process multiple analysis tasks simultaneously
flow = Flow(start="preprocess", steps={
    "preprocess": FunctionStep("preprocess", preprocess_text),
    "parallel_analysis": {
        "parallel": [
            FunctionStep("sentiment", analyze_sentiment),
            FunctionStep("keywords", extract_keywords),
            FunctionStep("topic", classify_topic),
            FunctionStep("readability", calculate_readability)
        ],
        "next_step": "aggregate",
        "max_workers": 4
    },
    "aggregate": FunctionStep("aggregate", combine_results)
})

# Sequential execution: 2.0s → Parallel execution: 0.5s (3.9x speedup)
result = await flow.run("Analyze this comprehensive text...")
```

**Intelligence flows naturally through your logic, now with lightning speed.**

---

## Interactive Conversations

```python
from refinire import create_simple_interactive_pipeline

def completion_check(result):
    return "finished" in str(result).lower()

# Multi-turn conversation agent
pipeline = create_simple_interactive_pipeline(
    name="conversation_agent",
    instructions="Have a natural conversation with the user.",
    completion_check=completion_check,
    max_turns=10,
    model="gpt-4o-mini"
)

# Natural conversation flow
result = pipeline.run_interactive("Hello, I need help with my project")
while not result.is_complete:
    user_input = input(f"Turn {result.turn}: ")
    result = pipeline.continue_interaction(user_input)

print("Conversation complete:", result.content)
```

**Conversations that remember, understand, and evolve.**

---

## Monitoring and Insights

### Real-time Agent Analytics

```python
# Search and analyze your AI agents
registry = get_global_registry()

# Find specific patterns
customer_flows = registry.search_by_agent_name("customer_support")
performance_data = registry.complex_search(
    flow_name_pattern="support",
    status="completed",
    min_duration=100
)

# Understand performance patterns
for flow in performance_data:
    print(f"Flow: {flow.flow_name}")
    print(f"Average response time: {flow.avg_duration}ms")
    print(f"Success rate: {flow.success_rate}%")
```

### Quality Monitoring

```python
# Automatic quality tracking
quality_flows = registry.search_by_quality_threshold(min_score=80.0)
improvement_candidates = registry.search_by_quality_threshold(max_score=70.0)

# Continuous improvement insights
print(f"High-quality flows: {len(quality_flows)}")
print(f"Improvement opportunities: {len(improvement_candidates)}")
```

**Your AI's performance becomes visible, measurable, improvable.**

---

## Installation & Quick Start

### Install

```bash
pip install refinire
```

### Your First Agent (30 seconds)

```python
from refinire import RefinireAgent

# Create
agent = RefinireAgent(
    name="hello_world",
    generation_instructions="You are a friendly assistant.",
    model="gpt-4o-mini"
)

# Run
result = agent.run("Hello!")
print(result.content)
```

### Provider Flexibility

```python
from refinire import get_llm

# Test multiple providers
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
        print(f"✗ {provider}: {model} - {str(e)}")
```

---

## Advanced Features

### Structured Output

```python
from pydantic import BaseModel
from refinire import RefinireAgent

class WeatherReport(BaseModel):
    location: str
    temperature: float
    condition: str

agent = RefinireAgent(
    name="weather_reporter",
    generation_instructions="Generate weather reports",
    output_model=WeatherReport,
    model="gpt-4o-mini"
)

result = agent.run("Weather in Tokyo")
weather = result.content  # Typed WeatherReport object
```

### Guardrails and Safety

```python
from refinire import RefinireAgent

def content_filter(content: str) -> bool:
    """Filter inappropriate content"""
    return "inappropriate" not in content.lower()

agent = RefinireAgent(
    name="safe_assistant",
    generation_instructions="Be helpful and appropriate",
    output_guardrails=[content_filter],
    model="gpt-4o-mini"
)
```

### Custom Tool Integration

```python
def web_search(query: str) -> str:
    """Search the web for information"""
    # Your search implementation
    return f"Search results for: {query}"

agent = RefinireAgent(
    name="research_assistant",
    generation_instructions="Help with research using web search",
    model="gpt-4o-mini"
)

agent.add_function_tool(web_search)
```

---

## Why Refinire?

### For Developers
- **Immediate productivity**: Build AI agents in minutes, not days
- **Provider freedom**: Switch between OpenAI, Anthropic, Google, Ollama seamlessly  
- **Quality assurance**: Automatic evaluation and improvement
- **Transparent operations**: Understand exactly what your AI is doing

### For Teams
- **Consistent architecture**: Unified patterns across all AI implementations
- **Reduced maintenance**: Automatic quality management and error handling
- **Performance visibility**: Real-time monitoring and analytics
- **Future-proof**: Provider-agnostic design protects your investment

### For Organizations
- **Faster time-to-market**: Dramatically reduced development cycles
- **Lower operational costs**: Automatic optimization and provider flexibility
- **Quality compliance**: Built-in evaluation and monitoring
- **Scalable architecture**: From prototype to production seamlessly

---

## Examples

Explore comprehensive examples in the `examples/` directory:

### Core Features
- `standalone_agent_demo.py` - Independent agent execution
- `trace_search_demo.py` - Monitoring and analytics
- `llm_pipeline_example.py` - Tool-enabled pipelines
- `interactive_pipeline_example.py` - Multi-turn conversations

### Flow Architecture  
- `flow_show_example.py` - Workflow visualization
- `simple_flow_test.py` - Basic flow construction
- `router_agent_example.py` - Conditional routing
- `dag_parallel_example.py` - High-performance parallel processing

### Specialized Agents
- `clarify_agent_example.py` - Requirement clarification
- `notification_agent_example.py` - Event notifications
- `extractor_agent_example.py` - Data extraction
- `validator_agent_example.py` - Content validation

---

## Supported Environments

- **Python**: 3.10+
- **Platforms**: Windows, Linux, macOS  
- **Dependencies**: OpenAI Agents SDK 0.0.17+

---

## Developer Experience

> *"The complexity that once consumed days now resolves in minutes. Refinire doesn't just simplify—it elevates."*

> *"Switching between AI providers feels like changing a variable. The abstraction is invisible yet powerful."*

> *"Watching AI agents improve themselves through automatic evaluation—it's like witnessing the future of software."*

---

## License & Credits

MIT License. Built with gratitude on the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python).

**Refinire**: Where complexity becomes clarity, and development becomes art.

---

## Release Notes - v0.2.1

### New Features
- **P() Function**: Convenient shorthand alias for `PromptStore.get()` - access prompts with `P("name")` instead of `PromptStore.get("name")`

### Architecture Improvements
- **Single Package Structure**: Consolidated from multi-package to unified package structure for better maintenance
- **Reorganized Hierarchy**: Moved flow and pipeline modules under `agents` subpackage for cleaner organization
- **Updated Dependencies**: Upgraded to Python 3.10+ requirement and OpenAI Agents SDK 0.0.17+

### Quality & Testing
- **100% Test Pass Rate**: All 408 tests now passing after comprehensive migration fixes
- **72% Test Coverage**: Improved from 70% to 72% code coverage with better test quality
- **Enhanced Compatibility**: Fixed Pydantic v2 compatibility and Context API improvements

### Developer Experience
- **Simplified Imports**: All functionality accessible through single `refinire` package
- **Better Organization**: Clear separation between core, agents, flow, and pipeline modules
- **Maintained Backward Compatibility**: Existing code continues to work with new structure