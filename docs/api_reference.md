# Refinire API Reference

This document provides comprehensive API documentation for the core components of Refinire: RefinireAgent and Flow.

## Table of Contents

1. [RefinireAgent API](#refinireagent-api)
2. [Flow API](#flow-api)
3. [Context API](#context-api)
4. [Step Classes](#step-classes)
5. [Factory Functions](#factory-functions)
6. [Unified LLM Interface](#unified-llm-interface)

---

## RefinireAgent API

The `RefinireAgent` class is the core agent component that provides unified LLM interfaces, built-in evaluation, and tool integration capabilities.

### Class: RefinireAgent

```python
from refinire import RefinireAgent
```

#### Constructor

```python
RefinireAgent(
    name: str,
    generation_instructions: Union[str, PromptReference],
    evaluation_instructions: Optional[Union[str, PromptReference]] = None,
    model: str = "gpt-4o-mini",
    evaluation_model: Optional[str] = None,
    output_model: Optional[Type[BaseModel]] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    timeout: float = 30.0,
    threshold: float = 85.0,
    max_retries: int = 3,
    input_guardrails: Optional[List[Callable[[str], bool]]] = None,
    output_guardrails: Optional[List[Callable[[Any], bool]]] = None,
    session_history: Optional[List[str]] = None,
    history_size: int = 10,
    context_providers_config: Optional[Union[str, List[Dict[str, Any]]]] = None,
    locale: str = "en",
    tools: Optional[List[Callable]] = None,
    mcp_servers: Optional[List[str]] = None,
    improvement_callback: Optional[Callable[[LLMResult, EvaluationResult], str]] = None,
    next_step: Optional[str] = None,
    store_result_key: Optional[str] = None,
    orchestration_mode: bool = False,
    routing_instruction: Optional[str] = None,
    namespace: Optional[str] = None
)
```

##### Parameters

**Required Parameters:**
- `name` (str): Unique identifier for the agent
- `generation_instructions` (str | PromptReference): Instructions that guide the agent's content generation

**Model Configuration:**
- `model` (str, default: "gpt-4o-mini"): Primary LLM model. Supports:
  - OpenAI: "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"
  - Anthropic: "claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"
  - Google: "gemini-1.5-pro", "gemini-1.5-flash"
  - Ollama: "llama2", "codellama", etc.
- `evaluation_model` (str, optional): Separate model for evaluation (defaults to main model)
- `temperature` (float, default: 0.7): Sampling temperature (0.0 = deterministic, 1.0 = very random)
- `max_tokens` (int, optional): Maximum tokens to generate
- `timeout` (float, default: 30.0): Request timeout in seconds

**Quality Assurance:**
- `evaluation_instructions` (str | PromptReference, optional): Instructions for quality evaluation
- `threshold` (float, default: 85.0): Minimum quality score (0-100) for accepting responses
- `max_retries` (int, default: 3): Maximum retry attempts for quality improvement
- `input_guardrails` (List[Callable], optional): Functions to validate input before processing
- `output_guardrails` (List[Callable], optional): Functions to validate output before returning

**Structured Output:**
- `output_model` (Type[BaseModel], optional): Pydantic model for structured output validation
- `orchestration_mode` (bool, default: False): Enable JSON output format for workflow integration

**Tools and Integration:**
- `tools` (List[Callable], optional): Python functions to register as tools for function calling
- `mcp_servers` (List[str], optional): MCP server identifiers for external tool integration

**History and Context:**
- `session_history` (List[str], optional): Previous conversation history
- `history_size` (int, default: 10): Maximum number of history entries to maintain
- `context_providers_config` (str | List[Dict], optional): Configuration for dynamic context injection

**Workflow Integration:**
- `next_step` (str, optional): Next step name for Flow integration
- `store_result_key` (str, optional): Key for storing results in workflow context
- `routing_instruction` (str, optional): Instructions for routing decisions in workflows

**Other:**
- `locale` (str, default: "en"): Language locale ("en" or "ja")
- `namespace` (str, optional): Environment variable namespace for oneenv integration
- `improvement_callback` (Callable, optional): Custom function for improving failed responses

#### Core Methods

##### run(user_input: str, ctx: Optional[Context] = None) -> Context

Executes the agent synchronously.

```python
# Basic usage
result = agent.run("What is the weather like today?")
print(result.result)

# With workflow context
from refinire.agents.flow.context import Context
ctx = Context()
result = agent.run("Process this data", ctx)
```

**Parameters:**
- `user_input` (str): The input text to process
- `ctx` (Context, optional): Workflow context for integration

**Returns:**
- `Context`: Updated context object with result in `ctx.result`

##### run_async(user_input: Optional[str], ctx: Optional[Context] = None) -> Context

Executes the agent asynchronously.

```python
import asyncio

async def main():
    result = await agent.run_async("Generate a summary")
    print(result.result)

asyncio.run(main())
```

**Parameters:**
- `user_input` (str, optional): Input text (can be None for workflow integration)
- `ctx` (Context, optional): Workflow context

**Returns:**
- `Context`: Updated context object

##### run_streamed(user_input: str, ctx: Optional[Context] = None, callback: Optional[Callable[[str], None]] = None)

Executes the agent with streaming output.

```python
async def stream_example():
    async for chunk in agent.run_streamed("Tell me a story"):
        print(chunk, end="", flush=True)
    print()  # New line after streaming completes
```

**Parameters:**
- `user_input` (str): Input text to process
- `ctx` (Context, optional): Workflow context
- `callback` (Callable, optional): Function called for each chunk

**Yields:**
- `str`: Content chunks as they are generated

#### Configuration Methods

##### update_instructions(generation_instructions: Optional[str] = None, evaluation_instructions: Optional[str] = None) -> None

Updates agent instructions dynamically.

```python
agent.update_instructions(
    generation_instructions="You are now a creative writer.",
    evaluation_instructions="Rate creativity and originality."
)
```

##### set_threshold(threshold: float) -> None

Updates the evaluation threshold.

```python
agent.set_threshold(90.0)  # Require 90% quality score
```

#### History Management

##### clear_history() -> None

Clears all session history and context providers.

##### get_history() -> List[Dict[str, Any]]

Returns a copy of the execution history.

##### clear_context() -> None

Clears context providers while preserving session history.

#### Properties

```python
# Model configuration
agent.model_name          # Current model name
agent.temperature         # Sampling temperature
agent.max_tokens          # Token limit
agent.timeout            # Request timeout

# Instructions
agent.generation_instructions  # Current generation instructions
agent.evaluation_instructions  # Current evaluation instructions
agent.routing_instruction     # Routing instructions

# Quality control
agent.threshold          # Quality threshold
agent.max_retries       # Maximum retry attempts
agent.input_guardrails  # Input validation functions
agent.output_guardrails # Output validation functions

# Integration
agent.tools             # Registered tools
agent.mcp_servers       # MCP server list
agent.session_history   # Current history
agent.orchestration_mode # Orchestration flag
```

---

## Flow API

The `Flow` class provides workflow orchestration capabilities for complex multi-step processes.

### Class: Flow

```python
from refinire.agents.flow import Flow
```

#### Constructor

```python
Flow(
    start: Optional[str] = None,
    steps: Optional[Union[Dict[str, Step], List[Step], Step]] = None,
    context: Optional[Context] = None,
    max_steps: int = 1000,
    trace_id: Optional[str] = None,
    name: Optional[str] = None
)
```

##### Parameters

- `start` (str, optional): Starting step name (required for Dict mode)
- `steps` (Dict[str, Step] | List[Step] | Step): Step definitions:
  - `Dict[str, Step]`: Traditional named step mapping
  - `List[Step]`: Sequential workflow (auto-connects steps)
  - `Step`: Single-step workflow
- `context` (Context, optional): Initial context state
- `max_steps` (int, default: 1000): Maximum execution steps (prevents infinite loops)
- `trace_id` (str, optional): Unique trace identifier for observability
- `name` (str, optional): Flow name for identification and debugging

#### Flow Definition Examples

```python
# Traditional dictionary-based flow
flow = Flow(
    start="analyze",
    steps={
        "analyze": FunctionStep("analyze", analyze_function),
        "decide": ConditionStep("decide", decision_function, "process", "end"),
        "process": FunctionStep("process", process_function, next_step="end"),
        "end": FunctionStep("end", final_function)
    }
)

# Sequential list-based flow (auto-connected)
flow = Flow(steps=[
    FunctionStep("step1", function1),
    FunctionStep("step2", function2),
    FunctionStep("step3", function3)
])

# Single-step flow
flow = Flow(steps=FunctionStep("single", single_function))

# Parallel execution support
flow = Flow(
    start="parallel_start",
    steps={
        "parallel_start": {
            "parallel": [
                FunctionStep("task1", task1_function),
                FunctionStep("task2", task2_function),
                FunctionStep("task3", task3_function)
            ],
            "next_step": "merge_results",
            "max_workers": 3
        },
        "merge_results": FunctionStep("merge", merge_function)
    }
)
```

#### Execution Methods

##### run(input_data: Optional[str] = None, initial_input: Optional[str] = None) -> Context

Executes the flow to completion.

```python
# Basic execution
result = await flow.run("Initial input data")
print(f"Flow completed: {result.is_finished()}")

# Access final result
if hasattr(result, 'result'):
    print(f"Final result: {result.result}")
```

##### run_streamed(input_data: Optional[str] = None, callback: Optional[Callable[[str], None]] = None)

Executes flow with streaming output from supported steps.

```python
async def stream_flow():
    async for chunk in flow.run_streamed("Process this"):
        print(f"Stream: {chunk}")
```

##### run_loop() -> None

Runs flow as a background task with user input coordination.

```python
# Start background execution
await flow.run_loop()

# In another context, provide user input when needed
if flow.context.awaiting_user_input:
    flow.feed("User response")
```

#### Interactive Methods

##### feed(user_input: str) -> None

Provides user input to a waiting flow.

```python
# Check if flow is waiting for input
if flow.context.awaiting_user_input:
    prompt = flow.next_prompt()
    print(f"Flow asks: {prompt}")
    
    # Provide input
    flow.feed("User's response")
```

##### next_prompt() -> Optional[str]

Gets the current prompt when flow is waiting for user input.

##### step() -> None

Executes one step synchronously (for CLI applications).

#### Flow Control Constants

```python
# Flow termination constants
Flow.END         # "_FLOW_END_"
Flow.TERMINATE   # "_FLOW_TERMINATE_"
Flow.FINISH      # "_FLOW_FINISH_"

# Usage in steps
def routing_function(user_input: str, context: Context) -> str:
    if condition_met:
        return Flow.END  # Terminate flow
    return "next_step"
```

#### Observability Methods

##### get_step_history() -> List[Dict[str, Any]]

Returns detailed execution history.

```python
history = flow.get_step_history()
for step_info in history:
    print(f"Step: {step_info['step_name']} at {step_info['timestamp']}")
```

##### get_flow_summary() -> Dict[str, Any]

Returns comprehensive flow execution summary.

```python
summary = flow.get_flow_summary()
print(f"Flow: {summary['flow_name']}")
print(f"Current Step: {summary['current_step']}")
print(f"Completed: {summary['finished']}")
print(f"Total Steps: {summary['step_count']}")
```

##### show(format: str = "mermaid", include_history: bool = True) -> str

Generates flow diagram visualization.

```python
# Mermaid diagram
mermaid_code = flow.show("mermaid", include_history=True)
print(mermaid_code)

# Text diagram
text_diagram = flow.show("text", include_history=False)
print(text_diagram)
```

#### Hooks and Monitoring

##### add_hook(hook_type: str, callback: Callable) -> None

Adds observability hooks for monitoring flow execution.

```python
def before_step_hook(step_name: str, context: Context):
    print(f"About to execute: {step_name}")

def after_step_hook(step_name: str, context: Context, result: Any):
    print(f"Completed: {step_name}")

def error_hook(step_name: str, context: Context, error: Exception):
    print(f"Error in {step_name}: {error}")

flow.add_hook("before_step", before_step_hook)
flow.add_hook("after_step", after_step_hook)
flow.add_hook("error", error_hook)
```

#### Properties

```python
# Flow state
flow.finished              # bool: Is flow completed?
flow.current_step_name     # str: Current step name
flow.next_step_name        # str: Next step name
flow.flow_id              # str: Unique flow identifier
flow.flow_name            # str: Flow name
flow.context              # Context: Current flow context

# Configuration
flow.start                # str: Starting step name
flow.steps                # Dict[str, Step]: Step definitions
flow.max_steps            # int: Maximum execution steps
flow.trace_id             # str: Trace identifier
```

#### Utility Methods

##### reset() -> None

Resets flow to initial state.

##### stop() -> None

Stops flow execution and cleanup.

##### get_possible_routes(step_name: str) -> List[str]

Returns possible next steps from a given step.

```python
routes = flow.get_possible_routes("decision_step")
print(f"Possible routes: {routes}")
```

---

## Context API

The `Context` class manages shared state between steps and agents in workflows.

### Class: Context

```python
from refinire.agents.flow.context import Context
```

#### Constructor

```python
Context(
    trace_id: Optional[str] = None,
    shared_state: Optional[Dict[str, Any]] = None
)
```

#### Core Methods

##### State Management

```python
# Access shared state
context.shared_state["key"] = "value"
value = context.shared_state.get("key")

# Finish workflow
context.finish()

# Check completion status
is_done = context.is_finished()
```

##### Message Management

```python
# Add messages
context.add_user_message("User input")
context.add_assistant_message("Assistant response")
context.add_system_message("System notification")

# Access messages
messages = context.messages
last_user = context.last_user_input
```

##### Result Handling

```python
# Store results
context.result = "Final result"
context.artifacts["data"] = processed_data

# Access routing and evaluation results
routing = context.routing_result
evaluation = context.evaluation_result
```

---

## Step Classes

Step classes define individual workflow operations.

### Base Step Class

```python
from refinire.agents.flow.step import Step

class CustomStep(Step):
    def __init__(self, name: str, next_step: Optional[str] = None):
        super().__init__(name, next_step)
    
    async def run_async(self, user_input: Optional[str], context: Context) -> Context:
        # Implement step logic here
        return context
```

### Built-in Step Types

#### FunctionStep

```python
from refinire.agents.flow.step import FunctionStep

def my_function(user_input: str, context: Context) -> Context:
    context.shared_state["processed"] = user_input.upper()
    return context

step = FunctionStep("process", my_function, next_step="next_step")
```

#### ConditionStep

```python
from refinire.agents.flow.step import ConditionStep

def decision_function(user_input: str, context: Context) -> bool:
    return len(user_input) > 10

step = ConditionStep(
    name="decide",
    condition_function=decision_function,
    if_true="long_text_handler",
    if_false="short_text_handler"
)
```

#### ParallelStep

```python
from refinire.agents.flow.step import ParallelStep

parallel_step = ParallelStep(
    name="parallel_processing",
    parallel_steps=[
        FunctionStep("task1", task1_function),
        FunctionStep("task2", task2_function),
        FunctionStep("task3", task3_function)
    ],
    next_step="merge_results",
    max_workers=3
)
```

---

## Factory Functions

Convenience functions for creating common agent configurations.

### create_simple_agent

```python
from refinire import create_simple_agent

agent = create_simple_agent(
    name="simple_assistant",
    instructions="You are a helpful assistant.",
    model="gpt-4o-mini",
    temperature=0.7
)
```

### create_evaluated_agent

```python
from refinire import create_evaluated_agent

agent = create_evaluated_agent(
    name="quality_writer",
    generation_instructions="Write high-quality blog posts.",
    evaluation_instructions="Rate content quality, clarity, and engagement.",
    threshold=90.0,
    max_retries=3
)
```

### create_tool_enabled_agent

```python
from refinire import create_tool_enabled_agent

def get_weather(city: str) -> str:
    return f"Weather in {city}: 72°F and sunny"

agent = create_tool_enabled_agent(
    name="weather_assistant",
    instructions="Help users with weather information.",
    tools=[get_weather]
)
```

### Utility Functions

#### create_simple_flow

```python
from refinire.agents.flow import create_simple_flow

flow = create_simple_flow([
    ("analyze", FunctionStep("analyze", analyze_function)),
    ("process", FunctionStep("process", process_function)),
    ("finalize", FunctionStep("finalize", finalize_function))
], name="simple_pipeline")
```

#### create_conditional_flow

```python
from refinire.agents.flow import create_conditional_flow

flow = create_conditional_flow(
    initial_step=FunctionStep("start", start_function),
    condition_step=ConditionStep("check", check_function, "yes", "no"),
    true_branch=[FunctionStep("yes", yes_function)],
    false_branch=[FunctionStep("no", no_function)]
)
```

---

## Unified LLM Interface

### get_llm

Factory function for handling multiple LLM providers with a unified interface.

```python
from refinire import get_llm

# OpenAI
llm = get_llm("gpt-4o-mini")

# Anthropic Claude
llm = get_llm("claude-3-5-sonnet-20241022")

# Google Gemini
llm = get_llm("gemini-1.5-pro")

# Ollama (Local)
llm = get_llm("llama3.1:8b")
```

#### Parameters

| Name       | Type               | Required/Optional | Default | Description                                   |
|------------|--------------------|-------------------|---------|-----------------------------------------------|
| model      | str                | Required          | -       | LLM model name to use                         |
| provider   | str                | Optional          | None    | Model provider name (auto-inferred if None)  |
| temperature| float              | Optional          | 0.3     | Sampling temperature (0.0-2.0)               |
| api_key    | str                | Optional          | None    | Provider API key                              |
| base_url   | str                | Optional          | None    | Provider API base URL                         |
| thinking   | bool               | Optional          | False   | Claude model thinking mode                    |
| tracing    | bool               | Optional          | False   | Enable Agents SDK tracing                     |

#### Returns
- **LLM Instance**: LLM object for the specified provider

#### Supported Models

**OpenAI**
- gpt-4o, gpt-4o-mini
- gpt-4-turbo, gpt-4
- gpt-3.5-turbo

**Anthropic Claude**
- claude-3-5-sonnet-20241022
- claude-3-sonnet, claude-3-haiku
- claude-3-opus

**Google Gemini**
- gemini-pro, gemini-pro-vision
- gemini-1.5-pro, gemini-1.5-flash

**Ollama**
- llama3.1:8b, llama3.1:70b
- mistral:7b
- codellama:7b

---

## Integration Examples

### RefinireAgent in Flow

```python
# Create an agent
agent = RefinireAgent(
    name="text_processor",
    generation_instructions="Process and improve text quality.",
    evaluation_instructions="Rate text improvement quality.",
    orchestration_mode=True  # Enable workflow integration
)

# Wrap agent in Flow step
def agent_step(user_input: str, context: Context) -> Context:
    return await agent.run_async(user_input, context)

# Create workflow
flow = Flow(steps=[
    FunctionStep("prepare", prepare_function),
    FunctionStep("process", agent_step),
    FunctionStep("finalize", finalize_function)
])

# Execute
result = await flow.run("Input text to process")
```

### Multi-Agent Workflow

```python
# Create specialized agents
analyzer = create_simple_agent("analyzer", "Analyze input requirements.")
generator = create_evaluated_agent("generator", "Generate content.", "Rate quality.")
reviewer = create_simple_agent("reviewer", "Review and improve content.")

# Create workflow
def create_multi_agent_flow():
    async def analyze_step(input_text: str, context: Context) -> Context:
        return await analyzer.run_async(input_text, context)
    
    async def generate_step(user_input: str, context: Context) -> Context:
        analysis = context.shared_state.get("analysis", "")
        prompt = f"Based on this analysis: {analysis}\nGenerate: {user_input}"
        return await generator.run_async(prompt, context)
    
    async def review_step(user_input: str, context: Context) -> Context:
        content = context.result
        prompt = f"Review and improve: {content}"
        return await reviewer.run_async(prompt, context)
    
    return Flow(steps=[
        FunctionStep("analyze", analyze_step),
        FunctionStep("generate", generate_step),
        FunctionStep("review", review_step)
    ])

# Execute multi-agent workflow
flow = create_multi_agent_flow()
result = await flow.run("Create a marketing plan")
```

### Streaming Workflow

```python
# Create streaming-enabled workflow
def create_streaming_flow():
    agent = RefinireAgent(
        name="writer",
        generation_instructions="Write engaging content with detailed explanations.",
        model="gpt-4o-mini"
    )
    
    def prepare_step(user_input: str, context: Context) -> Context:
        context.shared_state["prepared_input"] = f"Enhanced: {user_input}"
        return context
    
    async def write_step(user_input: str, context: Context) -> Context:
        prepared = context.shared_state.get("prepared_input", user_input)
        return await agent.run_async(prepared, context)
    
    return Flow(steps=[
        FunctionStep("prepare", prepare_step),
        FunctionStep("write", write_step)
    ])

# Stream workflow output
flow = create_streaming_flow()
async for chunk in flow.run_streamed("Write about AI advancements"):
    print(chunk, end="", flush=True)
```

This API reference provides comprehensive documentation for building sophisticated AI workflows using Refinire's core components. The combination of RefinireAgent's built-in quality assurance and Flow's orchestration capabilities enables robust, reliable AI applications.