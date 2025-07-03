# Quick Start

This tutorial introduces minimal LLM usage examples with Refinire. You can create working AI agents in just a few minutes.

## Prerequisites

- Python 3.10 or higher installed
- API keys configured for your chosen provider

```bash
# OpenAI (if using OpenAI models)
export OPENAI_API_KEY=your_api_key_here

# Anthropic (if using Claude models)
export ANTHROPIC_API_KEY=your_api_key_here

# Google (if using Gemini models)
export GOOGLE_API_KEY=your_api_key_here
```

## Installation

```bash
pip install refinire
```

## 1. Simple Agent Creation

Create a basic conversational agent with RefinireAgent.

```python
from refinire import RefinireAgent

# Simple agent
agent = RefinireAgent(
    name="assistant",
    generation_instructions="You are a helpful assistant. Provide clear and understandable responses.",
    model="gpt-4o-mini"
)

result = agent.run("Hello! What can you help me with?")
print(result.content)
```

## 2. Multi-Provider Support

Use different LLM providers seamlessly.

```python
from refinire import RefinireAgent

# OpenAI
openai_agent = RefinireAgent(
    name="openai_assistant",
    generation_instructions="You are a helpful assistant.",
    model="gpt-4o-mini"
)

# Anthropic Claude
claude_agent = RefinireAgent(
    name="claude_assistant", 
    generation_instructions="You are a helpful assistant.",
    model="claude-3-haiku"
)

# Google Gemini
gemini_agent = RefinireAgent(
    name="gemini_assistant",
    generation_instructions="You are a helpful assistant.",
    model="gemini-1.5-flash"
)

# Ollama (Local)
ollama_agent = RefinireAgent(
    name="ollama_assistant",
    generation_instructions="You are a helpful assistant.",
    model="llama3.1:8b"
)
```

## 3. Automatic Quality Assurance

Create agents with built-in evaluation and automatic improvement.

```python
from refinire import RefinireAgent

# Agent with automatic quality control
agent = RefinireAgent(
    name="quality_assistant",
    generation_instructions="Generate accurate and clear content about technology topics.",
    evaluation_instructions="""
    Evaluate the generated content on accuracy, clarity, and completeness.
    Rate from 0-100 and provide specific feedback for improvement.
    """,
    threshold=80.0,  # Automatically retry if score < 80
    max_retries=2,
    model="gpt-4o-mini"
)

result = agent.run("Explain machine learning in simple terms")
print(f"Content: {result.content}")
print(f"Quality Score: {result.evaluation_score}")
print(f"Attempts: {result.attempts}")
```

## 4. Tool Integration

Create agents that can use external functions.

```python
from refinire import RefinireAgent, tool

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city"""
    # Implement your weather API logic here
    return f"Weather in {city}: Sunny, 22°C"

@tool
def calculate(expression: str) -> float:
    """Calculate mathematical expressions safely"""
    try:
        # Simple calculator - implement proper parsing in production
        return eval(expression.replace("^", "**"))
    except:
        return 0.0

# Agent with tools
agent = RefinireAgent(
    name="tool_assistant",
    generation_instructions="Help users by using available tools when needed.",
    tools=[get_weather, calculate],
    model="gpt-4o-mini"
)

result = agent.run("What's the weather in Tokyo and what's 15 * 23?")
print(result.content)
```

## 5. Context Management and Memory

Use context for stateful conversations and data sharing.

```python
from refinire import RefinireAgent, Context

# Agent with context management
agent = RefinireAgent(
    name="context_assistant",
    generation_instructions="You are a helpful assistant. Use previous context to provide relevant responses.",
    context_providers_config=[
        {
            "type": "conversation_history",
            "max_items": 5
        }
    ],
    model="gpt-4o-mini"
)

# Create shared context
ctx = Context()

# First interaction
result1 = agent.run("My name is Alice and I'm interested in machine learning", ctx)
print(f"Response 1: {result1.content}")

# Second interaction (remembers previous conversation)
result2 = agent.run("What topics should I start with?", ctx)
print(f"Response 2: {result2.content}")
```

## 6. Variable Embedding for Dynamic Prompts

Use dynamic variable substitution in prompts.

```python
from refinire import RefinireAgent, Context

# Agent with variable embedding
agent = RefinireAgent(
    name="dynamic_assistant",
    generation_instructions="You are a {{role}} helping {{audience}} with {{task_type}} questions. Style: {{response_style}}",
    model="gpt-4o-mini"
)

# Setup context with variables
ctx = Context()
ctx.shared_state = {
    "role": "technical expert",
    "audience": "beginner developers",
    "task_type": "programming",
    "response_style": "step-by-step explanations"
}

result = agent.run("How do I start learning {{task_type}}?", ctx)
print(result.content)
```

## 7. Advanced Workflows with Flow

Create complex multi-step workflows.

```python
from refinire import RefinireAgent, Flow, FunctionStep
import asyncio

def preprocess_data(ctx):
    """Preprocess user input"""
    ctx.shared_state["processed"] = True
    return "Data preprocessed successfully"

# Multi-step workflow
analyzer = RefinireAgent(
    name="analyzer",
    generation_instructions="Analyze the given topic and provide key insights.",
    model="gpt-4o-mini"
)

summarizer = RefinireAgent(
    name="summarizer",
    generation_instructions="Create a concise summary based on the analysis: {{RESULT}}",
    model="gpt-4o-mini"
)

# Create flow
flow = Flow(start="preprocess", steps={
    "preprocess": FunctionStep("preprocess", preprocess_data),
    "analyze": analyzer,
    "summarize": summarizer
})

async def main():
    result = await flow.run("Artificial Intelligence trends")
    print(f"Analysis: {result.shared_state.get('analyzer_result', 'N/A')}")
    print(f"Summary: {result.shared_state.get('summarizer_result', 'N/A')}")

# Run async workflow
asyncio.run(main())
```

## 8. MCP Server Integration

Integrate with Model Context Protocol servers for advanced tool capabilities.

```python
from refinire import RefinireAgent

# Agent with MCP server support
agent = RefinireAgent(
    name="mcp_assistant",
    generation_instructions="Use MCP server tools to help users with their requests.",
    mcp_servers=[
        "stdio://filesystem-server",
        "http://localhost:8000/mcp"
    ],
    model="gpt-4o-mini"
)

result = agent.run("Analyze the project files in the current directory")
print(result.content)
```

---

## Key Points

### ✅ Current Best Practices
- **RefinireAgent**: Unified interface for all LLM providers
- **Built-in Quality Assurance**: Automatic evaluation and retry mechanisms
- **Tool Integration**: Easy function calling with `@tool` decorator
- **Context Management**: Intelligent memory and conversation handling
- **Variable Embedding**: Dynamic prompt generation with `{{variable}}` syntax
- **Flow Architecture**: Complex workflows with simple declarative syntax
- **MCP Integration**: Standardized tool access via Model Context Protocol

### 🚀 Performance Features
- **Multi-Provider Support**: OpenAI, Anthropic, Google, Ollama
- **Automatic Parallelization**: Built-in parallel processing capabilities
- **Smart Context**: Automatic context filtering and optimization
- **Structured Output**: Type-safe responses with Pydantic models

### 🔗 Next Steps
- [Advanced Features](advanced.md) - Complex workflows and patterns
- [Context Management](context_management.md) - Memory and state management
- [Flow Guide](flow_complete_guide_en.md) - Comprehensive workflow construction
- [Examples](../../examples/) - Practical implementation examples