# Quick Start

This tutorial introduces minimal LLM usage examples with Refinire. You can create working AI agents in just a few minutes.

## Prerequisites

- Python 3.9 or higher installed
- OpenAI API key configured (`OPENAI_API_KEY` environment variable)

```bash
# Environment variable setup (Windows)
set OPENAI_API_KEY=your_api_key_here

# Environment variable setup (Linux/Mac)
export OPENAI_API_KEY=your_api_key_here
```

## 1. Getting Model Instances

Handle multiple LLM providers with a unified interface.

```python
from refinire import get_llm

# OpenAI
llm = get_llm("gpt-4o-mini")

# Anthropic Claude
llm = get_llm("claude-3-sonnet")

# Google Gemini
llm = get_llm("gemini-pro")

# Ollama (Local LLM)
llm = get_llm("llama3.1:8b")
```

## 2. Simple Agent Creation

Create a basic conversational agent.

```python
from agents import Agent, Runner
from refinire import get_llm

llm = get_llm("gpt-4o-mini")
agent = Agent(
    name="Assistant",
    model=llm,
    instructions="You are a helpful assistant. Provide clear and understandable responses."
)

result = Runner.run_sync(agent, "Hello!")
print(result.final_output)
```

## 3. RefinireAgent + Flow for Advanced Workflows (Recommended)

Create advanced agents with automatic evaluation and quality improvement features.

```python
from refinire import create_evaluated_agent, Flow, Context
import asyncio

# Create RefinireAgent with automatic evaluation
agent = create_evaluated_agent(
    name="ai_expert",
    generation_instructions="""
    You are an AI assistant with deep expertise.
    Generate accurate and clear content based on user requests.
    Always provide explanations when using technical terms.
    """,
    evaluation_instructions="""
    Evaluate the generated content on a 100-point scale based on:
    - Accuracy (40 points)
    - Clarity (30 points)
    - Completeness (30 points)
    
    Provide specific improvement suggestions if any issues are found.
    """,
    model="gpt-4o-mini",
    threshold=75  # Regenerate if score < 75
)

# Create ultra-simple Flow
flow = Flow(steps=agent)

# Execute
async def main():
    result = await flow.run(input_data="Explain the difference between machine learning and deep learning")
    print("Generated result:")
    print(result.shared_state["ai_expert_result"])
    
    # Check evaluation score and result
    if result.evaluation_result:
        print(f"\nQuality Score: {result.evaluation_result['score']}")
        print(f"Passed: {result.evaluation_result['passed']}")
        print(f"Feedback: {result.evaluation_result['feedback']}")

# Run
asyncio.run(main())
```

## 4. Tool-Enabled Agents

Create agents that can use external functions.

```python
from refinire import create_simple_gen_agent, Flow
import asyncio

def get_weather(city: str) -> str:
    """Get weather for the specified city"""
    # Return dummy data instead of calling actual API
    return f"Weather in {city}: Sunny, 22°C"

def calculate(expression: str) -> float:
    """Calculate mathematical expressions"""
    try:
        return eval(expression)
    except:
        return 0.0

# Tool-enabled agent
tool_agent = create_simple_gen_agent(
    name="tool_assistant",
    instructions="Answer user questions using tools when necessary.",
    model="gpt-4o-mini",
    tools=[get_weather, calculate]
)

flow = Flow(steps=tool_agent)

async def main():
    result = await flow.run(input_data="What's the weather in Tokyo and what's 15 * 23?")
    print(result.shared_state["tool_assistant_result"])

asyncio.run(main())
```

## 5. Multi-Step Workflows

Create complex workflows combining multiple steps easily.

```python
from refinire import Flow, FunctionStep, Context
import asyncio

def analyze_input(user_input: str, ctx: Context) -> Context:
    """Analyze user input"""
    ctx.shared_state["analysis"] = f"Analyzed input: '{user_input}'"
    return ctx

def generate_response(user_input: str, ctx: Context) -> Context:
    """Generate response"""
    analysis = ctx.shared_state.get("analysis", "")
    ctx.shared_state["response"] = f"Generated response based on {analysis}"
    ctx.finish()  # End workflow
    return ctx

# Multi-step Flow
flow = Flow([
    ("analyze", FunctionStep("analyze", analyze_input)),
    ("respond", FunctionStep("respond", generate_response))
])

async def main():
    result = await flow.run(input_data="Tell me about AI")
    print(result.shared_state["response"])

asyncio.run(main())
```

## 6. Legacy AgentPipeline (Deprecated)

```python
# Warning: AgentPipeline will be removed in v0.1.0
from refinire import AgentPipeline

pipeline = AgentPipeline(
    name="eval_example",
    generation_instructions="You are a helpful assistant.",
    evaluation_instructions="Evaluate the generated text for clarity on a 100-point scale.",
    model="gpt-4o-mini",
    threshold=70
)

result = pipeline.run("Tell me about AI use cases")
print(result)
```

---

## Key Points

### ✅ Recommended Approaches
- **`get_llm`** for easy access to major LLMs
- **`RefinireAgent + Flow`** for end-to-end generation, evaluation, and self-improvement
- **`Flow(steps=agent)`** makes complex workflows **ultra-simple**
- **Automatic quality management**: maintain quality with threshold settings
- **Context-based result access**: seamless data flow between agents

### ⚠️ Important Notes
- Legacy `AgentPipeline` will be removed in v0.1.0 (migration is easy)
- Asynchronous processing (`asyncio`) is recommended
- Set API keys properly via environment variables

### 🔗 Next Steps
- [API Reference](../api_reference.md) - Detailed feature documentation
- [Composable Flow Architecture](../composable-flow-architecture.md) - Advanced workflows
- [Examples](../../examples/) - Practical use cases