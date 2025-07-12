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
- **Comprehensive observability** — Automatic tracing with OpenTelemetry integration

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
    generation_instructions="Generate high-quality, informative content with clear structure and engaging writing style",
    evaluation_instructions="""Evaluate the content quality on a scale of 0-100 based on:
    - Clarity and readability (0-25 points)
    - Accuracy and factual correctness (0-25 points)  
    - Structure and organization (0-25 points)
    - Engagement and writing style (0-25 points)
    
    Provide your evaluation as:
    Score: [0-100]
    Comments:
    - [Specific feedback on strengths]
    - [Areas for improvement]
    - [Suggestions for enhancement]""",
    threshold=85.0,  # Automatically regenerate if score < 85
    max_retries=3,
    model="gpt-4o-mini"
)

result = agent.run("Write an article about AI")
print(f"Quality Score: {result.evaluation_score}")
print(f"Content: {result.content}")
```

## Orchestration Mode - Multi-Agent Coordination

**The Challenge**: Building complex multi-agent systems requires standardized communication protocols between agents. Different output formats make agent coordination difficult and error-prone.

**The Solution**: RefinireAgent's orchestration mode provides structured JSON output with standardized status, result, reasoning, and next-step hints. This enables seamless integration in multi-agent workflows where agents need to communicate their status and recommend next actions.

**Key Benefits**:
- **Standardized Communication**: Unified JSON protocol for agent-to-agent interaction
- **Smart Coordination**: Agents provide hints about recommended next steps
- **Error Handling**: Clear status reporting (completed/failed) for robust workflows
- **Type Safety**: Structured output with optional Pydantic model integration

### Basic Orchestration Mode

```python
from refinire import RefinireAgent

# Agent configured for orchestration
orchestrator_agent = RefinireAgent(
    name="analysis_worker",
    generation_instructions="Analyze the provided data and provide insights",
    orchestration_mode=True,  # Enable structured output
    model="gpt-4o-mini"
)

# Returns structured JSON instead of Context
result = orchestrator_agent.run("Analyze user engagement trends")

# Standard orchestration response format
print(f"Status: {result['status']}")           # "completed" or "failed"
print(f"Result: {result['result']}")           # Analysis output
print(f"Reasoning: {result['reasoning']}")     # Why this result was generated
print(f"Next Task: {result['next_hint']['task']}")        # Recommended next step
print(f"Confidence: {result['next_hint']['confidence']}")  # Confidence level (0-1)
```

### Orchestration with Structured Output

```python
from pydantic import BaseModel
from refinire import RefinireAgent

class AnalysisReport(BaseModel):
    findings: list[str]
    recommendations: list[str]
    confidence_score: float

# Orchestration mode with typed result
agent = RefinireAgent(
    name="structured_analyst",
    generation_instructions="Generate detailed analysis report",
    orchestration_mode=True,
    output_model=AnalysisReport,  # Result will be typed
    model="gpt-4o-mini"
)

result = agent.run("Analyze customer feedback data")

# result['result'] is now a typed AnalysisReport object
report = result['result']
print(f"Findings: {report.findings}")
print(f"Recommendations: {report.recommendations}")
print(f"Confidence: {report.confidence_score}")
```

### Multi-Agent Workflow Coordination

```python
from refinire import RefinireAgent, Flow, FunctionStep

# Orchestration-enabled agents
data_collector = RefinireAgent(
    name="data_collector",
    generation_instructions="Collect and prepare data for analysis",
    orchestration_mode=True,
    model="gpt-4o-mini"
)

analyzer = RefinireAgent(
    name="analyzer", 
    generation_instructions="Perform deep analysis on collected data",
    orchestration_mode=True,
    model="gpt-4o-mini"
)

reporter = RefinireAgent(
    name="reporter",
    generation_instructions="Generate final report with recommendations",
    orchestration_mode=True,
    model="gpt-4o-mini"
)

def orchestration_router(ctx):
    """Route based on agent recommendations"""
    if hasattr(ctx, 'result') and isinstance(ctx.result, dict):
        next_task = ctx.result.get('next_hint', {}).get('task', 'unknown')
        if next_task == 'analysis':
            return 'analyzer'
        elif next_task == 'reporting':
            return 'reporter'
    return 'end'

# Workflow with orchestration-based routing
flow = Flow({
    "collect": data_collector,
    "route": ConditionStep("route", orchestration_router, "analyzer", "end"),
    "analyzer": analyzer,
    "report": reporter
})

result = await flow.run("Process customer survey data")
```

**Key Orchestration Features**:
- **Status Tracking**: Clear completion/failure status for workflow control
- **Result Typing**: Optional Pydantic model integration for type safety
- **Next-Step Hints**: Agents recommend optimal next actions with confidence levels
- **Reasoning Transparency**: Agents explain their decision-making process
- **Error Handling**: Structured error reporting for robust multi-agent systems
- **Backward Compatibility**: Normal mode continues to work unchanged (orchestration_mode=False)

## Streaming Output - Real-time Response Display

**Stream responses in real-time** for improved user experience and immediate feedback. Both RefinireAgent and Flow support streaming output, perfect for chat interfaces, live dashboards, and interactive applications.

### Basic RefinireAgent Streaming

```python
from refinire import RefinireAgent

agent = RefinireAgent(
    name="streaming_assistant",
    generation_instructions="Provide detailed, helpful responses",
    model="gpt-4o-mini"
)

# Stream response chunks as they arrive
async for chunk in agent.run_streamed("Explain quantum computing"):
    print(chunk, end="", flush=True)  # Real-time display
```

### Streaming with Callback Processing

```python
# Custom processing for each chunk
chunks_received = []
def process_chunk(chunk: str):
    chunks_received.append(chunk)
    # Send to websocket, update UI, save to file, etc.

async for chunk in agent.run_streamed(
    "Write a Python tutorial", 
    callback=process_chunk
):
    print(chunk, end="", flush=True)

print(f"\nReceived {len(chunks_received)} chunks")
```

### Context-Aware Streaming

```python
from refinire import Context

# Maintain conversation context across streaming responses
ctx = Context()

# First message
async for chunk in agent.run_streamed("Hello, I'm learning Python", ctx=ctx):
    print(chunk, end="", flush=True)

# Context-aware follow-up
ctx.add_user_message("What about async programming?")
async for chunk in agent.run_streamed("What about async programming?", ctx=ctx):
    print(chunk, end="", flush=True)
```

### Flow Streaming

**Flows also support streaming** for complex multi-step workflows:

```python
from refinire import Flow, FunctionStep

flow = Flow({
    "analyze": FunctionStep("analyze", analyze_input),
    "generate": RefinireAgent(
        name="writer", 
        generation_instructions="Write detailed content"
    )
})

# Stream entire flow output
async for chunk in flow.run_streamed("Create a technical article"):
    print(chunk, end="", flush=True)
```

### Structured Output Streaming

**Important**: When using structured output (Pydantic models) with streaming, the response is streamed as **JSON chunks**, not parsed objects:

```python
from pydantic import BaseModel

class Article(BaseModel):
    title: str
    content: str
    tags: list[str]

agent = RefinireAgent(
    name="structured_writer",
    generation_instructions="Generate an article",
    output_model=Article  # Structured output
)

# Streams JSON chunks: {"title": "...", "content": "...", "tags": [...]}
async for json_chunk in agent.run_streamed("Write about AI"):
    print(json_chunk, end="", flush=True)
    
# For parsed objects, use regular run() method:
result = await agent.run_async("Write about AI")
article = result.content  # Returns Article object
```

**Key Streaming Features**:
- **Real-time Output**: Immediate response as content is generated
- **Callback Support**: Custom processing for each chunk  
- **Context Continuity**: Streaming works with conversation context
- **Flow Integration**: Stream complex multi-step workflows
- **JSON Streaming**: Structured output streams as JSON chunks
- **Error Handling**: Graceful handling of streaming interruptions


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
from refinire import Flow, FunctionStep, ConditionStep

# Define your workflow as a composable flow
flow = Flow({
    "start": FunctionStep("analyze", analyze_request),
    "route": ConditionStep("route", route_by_complexity, "simple", "complex"),
    "simple": RefinireAgent(name="simple", generation_instructions="Quick response"),
    "complex": {
        "parallel": [
            RefinireAgent(name="expert1", generation_instructions="Deep analysis"),
            RefinireAgent(name="expert2", generation_instructions="Alternative perspective")
        ],
        "next_step": "aggregate"
    },
    "aggregate": FunctionStep("combine", combine_results)
})

result = await flow.run("Complex user request")
```

**🎯 Complete Flow Guide**: For comprehensive workflow construction learning, explore our detailed step-by-step guides:

**📖 English**: [Complete Flow Guide](docs/tutorials/flow_complete_guide_en.md) - From basics to advanced parallel processing  
**📖 日本語**: [Flow完全ガイド](docs/tutorials/flow_complete_guide_ja.md) - 包括的なワークフロー構築ガイド

### Flow Design Patterns

**Simple Routing**:
```python
# Automatic routing based on user language
def detect_language(ctx):
    return "japanese" if any(char in ctx.user_input for char in "あいうえお") else "english"

flow = Flow({
    "detect": ConditionStep("detect", detect_language, "jp_agent", "en_agent"),
    "jp_agent": RefinireAgent(name="jp", generation_instructions="日本語で丁寧に回答"),
    "en_agent": RefinireAgent(name="en", generation_instructions="Respond in English professionally")
})
```

**High-Performance Parallel Analysis**:
```python
# Execute multiple analyses simultaneously
flow = Flow(start="preprocess", steps={
    "preprocess": FunctionStep("preprocess", clean_data),
    "analysis": {
        "parallel": [
            RefinireAgent(name="sentiment", generation_instructions="Perform sentiment analysis"),
            RefinireAgent(name="keywords", generation_instructions="Extract keywords"),
            RefinireAgent(name="summary", generation_instructions="Create summary"),
            RefinireAgent(name="classification", generation_instructions="Classify content")
        ],
        "next_step": "report",
        "max_workers": 4
    },
    "report": FunctionStep("report", generate_final_report)
})
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

### MCP Server Integration - Model Context Protocol

RefinireAgent natively supports **MCP (Model Context Protocol) servers**, providing standardized access to external data sources and tools:

```python
from refinire import RefinireAgent

# MCP server integrated agent
agent = RefinireAgent(
    name="mcp_agent",
    generation_instructions="Use MCP server tools to accomplish tasks",
    mcp_servers=[
        "stdio://filesystem-server",  # Local filesystem access
        "http://localhost:8000/mcp",  # Remote API server
        "stdio://database-server --config db.json"  # Database access
    ],
    model="gpt-4o-mini"
)

# MCP tools become automatically available
result = agent.run("Analyze project files and include database information in your report")
```

**MCP Server Types:**
- **stdio servers**: Run as local subprocess
- **HTTP servers**: Remote HTTP endpoints  
- **WebSocket servers**: Real-time communication support

**Automatic Features:**
- Tool auto-discovery from MCP servers
- Dynamic tool registration and execution
- Error handling and retry logic
- Parallel management of multiple servers

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

**📖 Tutorial:** [Context Management](docs/tutorials/context_management.md) | **Details:** [Context Management Design](docs/context_management.md)

### Dynamic Prompt Generation - Variable Embedding

RefinireAgent's new variable embedding feature enables dynamic prompt generation based on context:

```python
from refinire import RefinireAgent, Context

# Variable embedding capable agent
agent = RefinireAgent(
    name="dynamic_responder",
    generation_instructions="You are a {{agent_role}} providing {{response_style}} responses to {{user_type}} users. Previous result: {{RESULT}}",
    model="gpt-4o-mini"
)

# Context setup
ctx = Context()
ctx.shared_state = {
    "agent_role": "customer support expert",
    "user_type": "premium",
    "response_style": "prompt and detailed"
}
ctx.result = "Customer inquiry reviewed"

# Execute with dynamic prompt
result = agent.run("Handle {{user_type}} user {{priority_level}} request", ctx)
```

**Key Variable Embedding Features:**
- **`{{RESULT}}`**: Previous step execution result
- **`{{EVAL_RESULT}}`**: Detailed evaluation information
- **`{{custom_variables}}`**: Any value from `ctx.shared_state`
- **Real-time Substitution**: Dynamic prompt generation at runtime

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

## Comprehensive Observability - Automatic Tracing

**The Challenge**: Debugging AI workflows and understanding agent behavior in production requires visibility into execution flows, performance metrics, and failure patterns. Manual logging is insufficient for complex multi-agent systems.

**The Solution**: Refinire provides comprehensive tracing capabilities with zero configuration. Every agent execution, workflow step, and evaluation is automatically captured and can be exported to industry-standard observability platforms like Grafana Tempo and Jaeger.

**Key Benefits**:
- **Zero Configuration**: Built-in console tracing works out of the box
- **Production Ready**: OpenTelemetry integration with OTLP export
- **Automatic Span Creation**: All agents and workflow steps traced automatically
- **Rich Metadata**: Captures inputs, outputs, evaluation scores, and performance metrics
- **Industry Standard**: Compatible with existing observability infrastructure

### Built-in Console Tracing

Every agent execution shows detailed, color-coded trace information by default:

```python
from refinire import RefinireAgent

agent = RefinireAgent(
    name="traced_agent",
    generation_instructions="You are a helpful assistant.",
    model="gpt-4o-mini"
)

result = agent.run("What is quantum computing?")
# Console automatically shows:
# 🔵 [Instructions] You are a helpful assistant.
# 🟢 [User Input] What is quantum computing?
# 🟡 [LLM Output] Quantum computing is a revolutionary computing paradigm...
# ✅ [Result] Operation completed successfully
```

### Production OpenTelemetry Integration

For production environments, enable OpenTelemetry tracing with a single function call:

```python
from refinire import (
    RefinireAgent,
    enable_opentelemetry_tracing,
    disable_opentelemetry_tracing
)

# Enable comprehensive tracing
enable_opentelemetry_tracing(
    service_name="my-agent-app",
    otlp_endpoint="http://localhost:4317",  # Grafana Tempo endpoint
    console_output=True  # Also show console traces
)

# All agent executions are now automatically traced
agent = RefinireAgent(
    name="production_agent",
    generation_instructions="Generate high-quality responses",
    evaluation_instructions="Rate quality from 0-100",
    threshold=85.0,
    model="gpt-4o-mini"
)

# This execution creates detailed spans with:
# - Agent name: "RefinireAgent(production_agent)"
# - Input/output text and instructions
# - Model name and parameters
# - Evaluation scores and pass/fail status
# - Success/error status and timing
result = agent.run("Explain machine learning concepts")

# Clean up when done
disable_opentelemetry_tracing()
```

### Disabling All Tracing

To completely disable all tracing (both console and OpenTelemetry):

```python
from refinire import disable_tracing

# Disable all tracing output
disable_tracing()

# Now all agent executions will run without any trace output
agent = RefinireAgent(name="silent_agent", model="gpt-4o-mini")
result = agent.run("This will execute silently")  # No trace output
```

### Environment Variable Configuration

Use environment variables for streamlined configuration:

```bash
# Set tracing configuration
export REFINIRE_TRACE_OTLP_ENDPOINT="http://localhost:4317"
export REFINIRE_TRACE_SERVICE_NAME="my-agent-service"
export REFINIRE_TRACE_RESOURCE_ATTRIBUTES="environment=production,team=ai"

# Use oneenv for easy configuration management
oneenv init --template refinire.tracing
```

### Automatic Span Coverage

When tracing is enabled, Refinire automatically creates spans for:

#### **RefinireAgent Spans**
- Input text, generation instructions, and output
- Model name and evaluation scores
- Success/failure status and error details

#### **Workflow Step Spans**
- **ConditionStep**: Boolean results and routing decisions
- **FunctionStep**: Function execution and next steps
- **ParallelStep**: Parallel execution timing and success rates

#### **Flow Workflow Spans**
- Complete workflow execution with step counts
- Flow input/output and completion status
- Step names and execution sequence

### Grafana Tempo Integration

Set up complete observability with Grafana Tempo:

```yaml
# tempo.yaml
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318

storage:
  trace:
    backend: local
    local:
      path: /tmp/tempo/traces
```

```bash
# Start Tempo
./tempo -config.file=tempo.yaml

# Run your traced application
python my_agent_app.py

# View traces in Grafana at http://localhost:3000
# Search: {service.name="my-agent-service"}
```

### Advanced Workflow Tracing

For complex workflows, add custom spans around groups of operations:

```python
from refinire import get_tracer, enable_opentelemetry_tracing

enable_opentelemetry_tracing(
    service_name="workflow-app",
    otlp_endpoint="http://localhost:4317"
)

tracer = get_tracer("workflow-tracer")

with tracer.start_as_current_span("multi-agent-workflow") as span:
    span.set_attribute("workflow.type", "analysis-pipeline")
    span.set_attribute("user.id", "user123")
    
    # These agents automatically create spans within the workflow span
    analyzer = RefinireAgent(name="analyzer", model="gpt-4o-mini")
    expert = RefinireAgent(name="expert", model="gpt-4o-mini")
    
    # Each call automatically creates detailed spans
    analysis = analyzer.run("Analyze this data")
    response = expert.run("Provide expert analysis")
    
    span.set_attribute("workflow.status", "completed")
```

**📖 Complete Guide:** [Tracing and Observability Tutorial](docs/tutorials/tracing.md) - Comprehensive setup and usage

**🔗 Integration Examples:**
- [OpenTelemetry Example](examples/opentelemetry_tracing_example.py) - Basic OpenTelemetry setup
- [Grafana Tempo Example](examples/grafana_tempo_tracing_example.py) - Complete Tempo integration
- [Environment Configuration](examples/oneenv_tracing_example.py) - oneenv configuration management

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

### Tracing and Observability
- `opentelemetry_tracing_example.py` - Basic OpenTelemetry setup and usage
- `grafana_tempo_tracing_example.py` - Complete Grafana Tempo integration
- `oneenv_tracing_example.py` - Environment configuration with oneenv

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

## Release Notes

### v0.2.10 - MCP Server Integration

### 🔌 Model Context Protocol (MCP) Server Support
- **Native MCP Integration**: RefinireAgent now supports MCP (Model Context Protocol) servers through the `mcp_servers` parameter
- **Multiple Server Types**: Support for stdio, HTTP, and WebSocket MCP servers
- **Automatic Tool Discovery**: MCP server tools are automatically discovered and integrated
- **OpenAI Agents SDK Compatibility**: Leverages OpenAI Agents SDK MCP capabilities with simplified configuration

```python
# MCP server integrated agent
agent = RefinireAgent(
    name="mcp_agent",
    generation_instructions="Use MCP server tools to accomplish tasks",
    mcp_servers=[
        "stdio://filesystem-server",  # Local filesystem access
        "http://localhost:8000/mcp",  # Remote API server
        "stdio://database-server --config db.json"  # Database access
    ],
    model="gpt-4o-mini"
)

# MCP tools become automatically available
result = agent.run("Analyze project files and include database information in your report")
```

### 🚀 MCP Integration Benefits
- **Standardized Tool Access**: Use industry-standard MCP protocol for tool integration
- **Ecosystem Compatibility**: Works with existing MCP server implementations
- **Scalable Architecture**: Support for multiple concurrent MCP servers
- **Error Handling**: Built-in retry logic and error management for MCP connections
- **Context Integration**: MCP servers work seamlessly with RefinireAgent's context management system

### 💡 MCP Server Types and Use Cases
- **stdio servers**: Local subprocess execution for file system, databases, development tools
- **HTTP servers**: Remote API endpoints for web services and cloud integrations  
- **WebSocket servers**: Real-time communication support for streaming data and live updates

### 🔧 Implementation Details
- **Minimal Code Changes**: Simple `mcp_servers` parameter addition maintains backward compatibility
- **SDK Pass-through**: Direct integration with OpenAI Agents SDK MCP functionality
- **Comprehensive Examples**: Complete MCP integration examples in `examples/mcp_server_example.py`
- **Documentation**: Updated guides showing MCP server configuration and usage patterns

**📖 Detailed Guide:** [MCP Server Example](examples/mcp_server_example.py) - Complete MCP integration demonstration

---

### v0.2.11 - Comprehensive Observability and Automatic Tracing

### 🔍 Complete OpenTelemetry Integration
- **Automatic Agent Tracing**: All RefinireAgent executions automatically create detailed spans with zero configuration
- **Workflow Step Tracing**: ConditionStep, FunctionStep, and ParallelStep operations automatically tracked
- **Flow-Level Spans**: Complete workflow execution visibility with comprehensive metadata
- **Rich Span Metadata**: Captures inputs, outputs, evaluation scores, model parameters, and performance metrics

```python
from refinire import enable_opentelemetry_tracing, RefinireAgent

# Enable comprehensive tracing
enable_opentelemetry_tracing(
    service_name="my-agent-app",
    otlp_endpoint="http://localhost:4317"
)

# All executions automatically create detailed spans
agent = RefinireAgent(
    name="traced_agent",
    generation_instructions="Generate responses",
    evaluation_instructions="Rate quality 0-100",
    threshold=85.0,
    model="gpt-4o-mini"
)

# Automatic span with rich metadata
result = agent.run("Explain quantum computing")
```

### 🎯 Zero-Configuration Observability
- **Built-in Console Tracing**: Color-coded trace output works out of the box
- **Environment Variable Configuration**: `REFINIRE_TRACE_*` variables for streamlined setup
- **oneenv Template Support**: `oneenv init --template refinire.tracing` for easy configuration
- **Production Ready**: Industry-standard OTLP export to Grafana Tempo, Jaeger, and other platforms

### 🚀 Automatic Span Coverage
- **RefinireAgent Spans**: Input/output text, instructions, model name, evaluation scores, success/error status
- **ConditionStep Spans**: Boolean results, if_true/if_false branches, routing decisions
- **FunctionStep Spans**: Function name, execution success, next step information
- **ParallelStep Spans**: Parallel execution timing, success rates, worker utilization
- **Flow Spans**: Complete workflow metadata, step counts, execution sequence, completion status

### 📊 Advanced Observability Features
- **OpenAI Agents SDK Integration**: Leverages built-in tracing abstractions (`agent_span`, `custom_span`)
- **OpenTelemetry Bridge**: Seamless connection between Agents SDK spans and OpenTelemetry
- **Grafana Tempo Support**: Complete setup guide and integration examples
- **Custom Span Support**: Add business logic spans while maintaining automatic coverage

### 📖 Comprehensive Documentation
- **English Tutorial**: [Tracing and Observability](docs/tutorials/tracing.md) - Complete setup and usage guide
- **Japanese Tutorial**: [トレーシングと可観測性](docs/tutorials/tracing_ja.md) - 包括的なセットアップと使用ガイド
- **Integration Examples**: Complete examples for OpenTelemetry, Grafana Tempo, and environment configuration
- **Best Practices**: Guidelines for production deployment and performance optimization

### 🔧 Technical Implementation
- **Minimal Overhead**: Efficient span creation with automatic metadata collection
- **Error Handling**: Robust error capture and reporting in trace data
- **Performance Monitoring**: Automatic timing and performance metrics collection
- **Memory Efficiency**: Optimized trace data structure and export batching

### 💡 Developer Benefits
- **Production Debugging**: Complete visibility into multi-agent workflows and complex flows
- **Performance Optimization**: Identify bottlenecks and optimization opportunities
- **Quality Monitoring**: Track evaluation scores and improvement patterns
- **Zero Maintenance**: Automatic tracing with no manual instrumentation required

**📖 Complete Guides:**
- [Tracing Tutorial](docs/tutorials/tracing.md) - Comprehensive setup and integration guide
- [Grafana Tempo Example](examples/grafana_tempo_tracing_example.py) - Production observability setup

---

### v0.2.9 - Variable Embedding and Advanced Flow Features

### 🎯 Dynamic Variable Embedding System
- **`{{variable}}` Syntax**: Support for dynamic variable substitution in user input and generation_instructions
- **Reserved Variables**: Access previous step results and evaluations with `{{RESULT}}` and `{{EVAL_RESULT}}`
- **Context-Based**: Dynamically reference any variable from `ctx.shared_state`
- **Real-time Substitution**: Generate and customize prompts dynamically at runtime
- **Agent Flexibility**: Same agent can behave differently based on context state

```python
# Dynamic prompt generation example
agent = RefinireAgent(
    name="dynamic_agent",
    generation_instructions="You are a {{agent_role}} providing {{response_style}} responses for {{target_audience}}. Previous result: {{RESULT}}",
    model="gpt-4o-mini"
)

ctx = Context()
ctx.shared_state = {
    "agent_role": "technical expert",
    "target_audience": "developers", 
    "response_style": "detailed technical explanations"
}
result = agent.run("Handle {{user_type}} request for {{service_level}} at {{response_time}}", ctx)
```

### 📚 Complete Flow Guide
- **Step-by-Step Guide**: [Complete Flow Guide](docs/tutorials/flow_complete_guide_en.md) for comprehensive workflow construction
- **Bilingual Support**: [Japanese Guide](docs/tutorials/flow_complete_guide_ja.md) also available
- **Practical Examples**: Progressive learning from basic flows to complex parallel processing
- **Best Practices**: Guidelines for efficient flow design and performance optimization
- **Troubleshooting**: Common issues and their solutions

### 🔧 Enhanced Context Management
- **Variable Embedding Integration**: Added variable embedding examples to [Context Management Guide](docs/tutorials/context_management.md)
- **Dynamic Prompt Generation**: Change agent behavior based on context state
- **Workflow Integration**: Patterns for Flow and context provider collaboration
- **Memory Management**: Best practices for efficient context usage

### 🛠️ Developer Experience Improvements
- **Step Compatibility Fix**: Test environment preparation for `run()` to `run_async()` migration
- **Test Organization**: Organized test files from project root to tests/ directory
- **Performance Validation**: Comprehensive testing and performance optimization for variable embedding
- **Error Handling**: Robust error handling and fallbacks in variable substitution

### 🚀 Technical Improvements
- **Regex Optimization**: Efficient variable pattern matching and context substitution
- **Type Safety**: Proper type conversion and exception handling in variable embedding
- **Memory Efficiency**: Optimized variable processing for large-scale contexts
- **Backward Compatibility**: Full compatibility with existing RefinireAgent and Flow implementations

### 💡 Practical Benefits
- **Development Efficiency**: Dynamic prompt generation enables multiple roles with single agent
- **Maintainability**: Variable-based templating makes prompt management and updates easier
- **Flexibility**: Runtime customization of agent behavior based on execution state
- **Reusability**: Creation and sharing of generic prompt templates

**📖 Detailed Guides:**
- [Complete Flow Guide](docs/tutorials/flow_complete_guide_en.md) - Comprehensive workflow construction guide
- [Context Management](docs/tutorials/context_management.md) - Including variable embedding comprehensive context management

---

### v0.2.8 - Revolutionary Tool Integration

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