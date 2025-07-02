# Refinire ✨ - Refined Simplicity for Agentic AI

[![PyPI Downloads](https://static.pepy.tech/badge/refinire)](https://pepy.tech/projects/refinire)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents 0.0.17](https://img.shields.io/badge/OpenAI-Agents_0.0.17-green.svg)](https://github.com/openai/openai-agents-python)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)]

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

**The Challenge**: Building complex AI workflows requires managing multiple agents, conditional logic, parallel processing, and error handling. Traditional approaches lead to rigid, hard-to-maintain code.

**The Solution**: Refinire's Flow Architecture lets you compose workflows from reusable steps. Each step can be a function, condition, parallel execution, or AI agent. Flows handle routing, error recovery, and state management automatically.

**Key Benefits**:
- **Composable Design**: Build complex workflows from simple, reusable components
- **Visual Logic**: Workflow structure is immediately clear from the code
- **Automatic Orchestration**: Flow engine handles execution order and data passing
- **Built-in Parallelization**: Dramatic performance improvements with simple syntax

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

**The Challenge**: Switching between AI providers requires different SDKs, APIs, and authentication methods. Managing multiple provider integrations creates vendor lock-in and complexity.

**The Solution**: RefinireAgent provides a single, consistent interface across all major LLM providers. Provider selection happens automatically based on your environment configuration, eliminating the need to manage multiple SDKs or rewrite code when switching providers.

**Key Benefits**:
- **Provider Freedom**: Switch between OpenAI, Anthropic, Google, and Ollama without code changes
- **Zero Vendor Lock-in**: Your agent logic remains independent of provider specifics
- **Automatic Resolution**: Environment variables determine the optimal provider automatically
- **Consistent API**: Same method calls work across all providers

```python
from refinire import RefinireAgent

# Just specify the model name—provider is resolved automatically
agent = RefinireAgent(
    name="assistant",
    generation_instructions="You are a helpful assistant.",
    model="gpt-4o-mini"  # OpenAI
)

# Anthropic, Google, and Ollama are also supported in the same way
agent2 = RefinireAgent(
    name="anthropic_assistant",
    generation_instructions="For Anthropic model",
    model="claude-3-sonnet"  # Anthropic
)

agent3 = RefinireAgent(
    name="google_assistant",
    generation_instructions="For Google Gemini",
    model="gemini-pro"  # Google
)

agent4 = RefinireAgent(
    name="ollama_assistant",
    generation_instructions="For Ollama model",
    model="llama3.1:8b"  # Ollama
)
```

This makes switching between providers and managing API keys extremely simple, greatly increasing development flexibility.

**📖 Tutorial:** [Quickstart Guide](docs/tutorials/quickstart.md) | **Details:** [Unified LLM Interface](docs/unified-llm-interface.md)

## 2. Autonomous Quality Assurance

**The Challenge**: AI outputs can be inconsistent, requiring manual review and regeneration. Quality control becomes a bottleneck in production systems.

**The Solution**: RefinireAgent includes built-in evaluation that automatically assesses output quality and regenerates content when it falls below your standards. This creates a self-improving system that maintains consistent quality without manual intervention.

**Key Benefits**:
- **Automatic Quality Control**: Set thresholds and let the system maintain standards
- **Self-Improving**: Failed outputs trigger regeneration with improved prompts
- **Production Ready**: Consistent quality without manual oversight
- **Configurable Standards**: Define your own evaluation criteria and thresholds

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

# With Context for workflow integration
from refinire import Context
ctx = Context()
result_ctx = agent.run("Explain quantum computing", ctx)
print(f"Evaluation Result: {result_ctx.evaluation_result}")
print(f"Score: {result_ctx.evaluation_result['score']}")
print(f"Passed: {result_ctx.evaluation_result['passed']}")
print(f"Feedback: {result_ctx.evaluation_result['feedback']}")
```

If evaluation falls below threshold, content is automatically regenerated for consistent high quality.

**📖 Tutorial:** [Advanced Features](docs/tutorials/advanced.md) | **Details:** [Autonomous Quality Assurance](docs/autonomous-quality-assurance.md)

## 3. Tool Integration - Automated Function Calling

**The Challenge**: AI agents often need to interact with external systems, APIs, or perform calculations. Manual tool integration is complex and error-prone.

**The Solution**: RefinireAgent automatically detects when to use tools and executes them seamlessly. Simply provide decorated functions, and the agent handles tool selection, parameter extraction, and execution automatically.

**Key Benefits**:
- **Zero Configuration**: Decorated functions are automatically available as tools
- **Intelligent Selection**: Agent chooses appropriate tools based on user requests
- **Error Handling**: Built-in retry and error recovery for tool execution
- **Extensible**: Easy to add custom tools for your specific use cases

```python
from refinire import RefinireAgent, tool

@tool
def calculate(expression: str) -> float:
    """Calculate mathematical expressions"""
    return eval(expression)

@tool
def get_weather(city: str) -> str:
    """Get weather for a city"""
    return f"Weather in {city}: Sunny, 22°C"

# Agent with tools
agent = RefinireAgent(
    name="tool_assistant",
    generation_instructions="Answer questions using tools",
    tools=[calculate, get_weather],
    model="gpt-4o-mini"
)

result = agent.run("What's the weather in Tokyo? Also, what's 15 * 23?")
print(result.content)  # Automatically answers both questions
```

**📖 Tutorial:** [Advanced Features](docs/tutorials/advanced.md) | **Details:** [Composable Flow Architecture](docs/composable-flow-architecture.md)

## 4. Automatic Parallel Processing: Dramatic Performance Boost

**The Challenge**: Sequential processing of independent tasks creates unnecessary bottlenecks. Manual async implementation is complex and error-prone.

**The Solution**: Refinire's parallel processing automatically identifies independent operations and executes them simultaneously. Simply wrap operations in a `parallel` block, and the system handles all async coordination.

**Key Benefits**:
- **Automatic Optimization**: System identifies parallelizable operations
- **Dramatic Speedup**: 4x+ performance improvements are common
- **Zero Complexity**: No async/await or thread management required
- **Scalable**: Configurable worker pools adapt to your workload

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

# Sequential execution → Parallel execution (significant speedup)
result = await flow.run("Analyze this comprehensive text...")
```

Run complex analysis tasks simultaneously without manual async implementation.

**📖 Tutorial:** [Advanced Features](docs/tutorials/advanced.md) | **Details:** [Composable Flow Architecture](docs/composable-flow-architecture.md)

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

### Parallel Processing: Dramatic Performance Boost

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

# Sequential execution → Parallel execution (significant speedup)
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
from refinire import RefinireAgent, tool

@tool
def web_search(query: str) -> str:
    """Search the web for information"""
    # Your search implementation
    return f"Search results for: {query}"

agent = RefinireAgent(
    name="research_assistant",
    generation_instructions="Help with research using web search",
    tools=[web_search],
    model="gpt-4o-mini"
)
```

### Context Management - Intelligent Memory

**The Challenge**: AI agents lose context between conversations and lack awareness of relevant files or code. This leads to repetitive questions and less helpful responses.

**The Solution**: RefinireAgent's context management automatically maintains conversation history, analyzes relevant files, and searches your codebase for pertinent information. The agent builds a comprehensive understanding of your project and maintains it across conversations.

**Key Benefits**:
- **Persistent Memory**: Conversations build upon previous interactions
- **Code Awareness**: Automatic analysis of relevant source files
- **Dynamic Context**: Context adapts based on current conversation topics
- **Intelligent Filtering**: Only relevant information is included to avoid token limits

RefinireAgent provides sophisticated context management for enhanced conversations:

```python
from refinire import RefinireAgent

# Agent with conversation history and file context
agent = RefinireAgent(
    name="code_assistant",
    generation_instructions="Help with code analysis and improvements",
    context_providers_config=[
        {
            "type": "conversation_history",
            "max_items": 10
        },
        {
            "type": "fixed_file",
            "file_path": "src/main.py",
            "description": "Main application file"
        },
        {
            "type": "source_code",
            "base_path": "src/",
            "file_patterns": ["*.py"],
            "max_files": 5
        }
    ],
    model="gpt-4o-mini"
)

# Context is automatically managed across conversations
result = agent.run("What's the main function doing?")
print(result.content)

# Context persists and evolves
result = agent.run("How can I improve the error handling?")
print(result.content)
```

**📖 Tutorial:** [Context Management](docs/tutorials/context_management.md) | **Details:** [Context Management](docs/context_management.md)

### Context-Based Result Access

**The Challenge**: Chaining multiple AI agents requires complex data passing and state management. Results from one agent need to flow seamlessly to the next.

**The Solution**: Refinire's Context system automatically tracks agent results, evaluation data, and shared state. Agents can access previous results, evaluation scores, and custom data without manual state management.

**Key Benefits**:
- **Automatic State Management**: Context handles data flow between agents
- **Rich Result Access**: Access not just outputs but also evaluation scores and metadata
- **Flexible Data Storage**: Store custom data for complex workflow requirements
- **Seamless Integration**: No boilerplate code for agent communication

Access agent results and evaluation data through Context for seamless workflow integration:

```python
from refinire import RefinireAgent, Context, create_evaluated_agent

# Create agent with evaluation
agent = create_evaluated_agent(
    name="analyzer",
    generation_instructions="Analyze the input thoroughly",
    evaluation_instructions="Rate analysis quality 0-100",
    threshold=80
)

# Run with Context
ctx = Context()
result_ctx = agent.run("Analyze this data", ctx)

# Simple result access
print(f"Result: {result_ctx.result}")

# Evaluation result access
if result_ctx.evaluation_result:
    score = result_ctx.evaluation_result["score"]
    passed = result_ctx.evaluation_result["passed"]
    feedback = result_ctx.evaluation_result["feedback"]
    
# Agent chain data passing
next_agent = create_simple_agent("summarizer", "Create summaries")
summary_ctx = next_agent.run(f"Summarize: {result_ctx.result}", result_ctx)

# Access previous agent outputs
analyzer_output = summary_ctx.prev_outputs["analyzer"]
summarizer_output = summary_ctx.prev_outputs["summarizer"]

# Custom data storage
result_ctx.shared_state["custom_data"] = {"key": "value"}
```

**Seamless data flow between agents with automatic result tracking.**

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
- `llm_pipeline_example.py` - RefinireAgent with tool integration
- `interactive_pipeline_example.py` - Multi-turn conversation agents

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

### Context Management
- `context_management_basic.py` - Basic context provider usage
- `context_management_advanced.py` - Advanced context with source code analysis
- `context_management_practical.py` - Real-world context management scenarios

---

## Supported Environments

- **Python**: 3.10+
- **Platforms**: Windows, Linux, macOS  
- **Dependencies**: OpenAI Agents SDK 0.0.17+

---

## License & Credits

MIT License. Built with gratitude on the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python).

**Refinire**: Where complexity becomes clarity, and development becomes art.

---

## Release Notes - v0.2.8

### 🛠️ Revolutionary Tool Integration
- **New @tool Decorator**: Introduced intuitive `@tool` decorator for seamless tool creation
- **Simplified Imports**: Clean `from refinire import tool` replaces complex external SDK knowledge
- **Enhanced Debugging**: Added `get_tool_info()` and `list_tools()` for better tool introspection
- **Backward Compatibility**: Full support for existing `function_tool` decorated functions
- **Simplified Tool Development**: Streamlined tool creation process with intuitive decorator syntax

### 📚 Documentation Revolution
- **Concept-Driven Explanations**: READMEs now focus on Challenge-Solution-Benefits structure
- **Tutorial Integration**: Every feature section links to step-by-step tutorials
- **Improved Clarity**: Reduced cognitive load with clear explanations before code examples
- **Bilingual Enhancement**: Both English and Japanese documentation significantly improved
- **User-Centric Approach**: Documentation redesigned from developer perspective

### 🔄 Developer Experience Transformation
- **Unified Import Strategy**: All tool functionality available from single `refinire` package
- **Future-Proof Architecture**: Tool system insulated from external SDK changes
- **Enhanced Metadata**: Rich tool information for debugging and development
- **Intelligent Error Handling**: Better error messages and troubleshooting guidance
- **Streamlined Workflow**: From idea to working tool in under 5 minutes

### 🚀 Quality & Performance
- **Context-Based Evaluation**: New `ctx.evaluation_result` for workflow integration
- **Comprehensive Testing**: 100% test coverage for all new tool functionality
- **Migration Examples**: Complete migration guides and comparison demonstrations
- **API Consistency**: Unified patterns across all Refinire components
- **Zero Breaking Changes**: Existing code continues to work while new features enhance capability

### 💡 Key Benefits for Users
- **Faster Tool Development**: Significantly reduced tool creation time with streamlined workflow
- **Reduced Learning Curve**: No need to understand external SDK complexities
- **Better Debugging**: Rich metadata and introspection capabilities
- **Future Compatibility**: Protected from external SDK breaking changes
- **Intuitive Development**: Natural Python decorator patterns familiar to all developers

**This release represents a major step forward in making Refinire the most developer-friendly AI agent platform available.**