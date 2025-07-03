# Advanced Features Tutorial

This tutorial covers advanced features of Refinire for building sophisticated AI workflows.

## 1. Tool Integration with RefinireAgent

### Modern Tool Integration
```python
from refinire import RefinireAgent, tool

@tool
def get_weather(location: str) -> str:
    """Get weather information for a location"""
    return f"Weather in {location}: Sunny, 25°C"

@tool
def calculate(expression: str) -> float:
    """Perform mathematical calculations"""
    return eval(expression)

# Tool-enabled agent
agent = RefinireAgent(
    name="assistant",
    generation_instructions="You are a helpful assistant with access to weather and calculation tools.",
    tools=[get_weather, calculate],
    model="gpt-4o-mini"
)

result = agent.run("What's the weather in Tokyo and what's 15 * 23?")
print(result.content)
```

### MCP Server Integration
```python
from refinire import RefinireAgent

# Agent with MCP server support
agent = RefinireAgent(
    name="mcp_agent",
    generation_instructions="Use MCP server tools to accomplish tasks",
    mcp_servers=[
        "stdio://filesystem-server",
        "http://localhost:8000/mcp",
        "stdio://database-server --config db.json"
    ],
    model="gpt-4o-mini"
)

result = agent.run("Analyze project files and include database information")
```

## 2. Advanced Flow Architectures

### Sequential Processing with Flow
```python
from refinire import RefinireAgent, Flow, FunctionStep

def preprocess_data(ctx):
    # Data preprocessing logic
    ctx.shared_state["processed"] = True
    return "Data preprocessed"

# Sequential workflow
writer = RefinireAgent(
    name="writer",
    generation_instructions="Write detailed technical content",
    model="gpt-4o"
)

reviewer = RefinireAgent(
    name="reviewer", 
    generation_instructions="Review and improve the content",
    model="claude-3-sonnet"
)

flow = Flow(start="preprocess", steps={
    "preprocess": FunctionStep("preprocess", preprocess_data),
    "write": writer,
    "review": reviewer
})

result = await flow.run("Write about AI technology")
```

### Conditional Workflows
```python
from refinire import ConditionStep

def check_complexity(ctx):
    """Route based on input complexity"""
    user_input = ctx.user_input or ""
    return "complex" if len(user_input) > 100 else "simple"

# Simple and complex processing agents
simple_agent = RefinireAgent(
    name="simple",
    generation_instructions="Provide a brief, concise response",
    model="gpt-4o-mini"
)

complex_agent = RefinireAgent(
    name="complex",
    generation_instructions="Provide detailed, comprehensive analysis",
    model="gpt-4o"
)

flow = Flow(start="route", steps={
    "route": ConditionStep("route", check_complexity, "simple", "complex"),
    "simple": simple_agent,
    "complex": complex_agent
})

result = await flow.run("Explain quantum computing in detail")
```

### Parallel Processing for Performance
```python
from refinire import Flow, FunctionStep

def analyze_sentiment(ctx):
    return "Positive sentiment detected"

def extract_keywords(ctx):
    return "AI, technology, innovation"

def classify_topic(ctx):
    return "Technology"

# High-performance parallel analysis
flow = Flow(start="preprocess", steps={
    "preprocess": FunctionStep("preprocess", preprocess_data),
    "analysis": {
        "parallel": [
            FunctionStep("sentiment", analyze_sentiment),
            FunctionStep("keywords", extract_keywords),
            FunctionStep("topic", classify_topic),
            RefinireAgent(name="summary", generation_instructions="Create summary")
        ],
        "next_step": "aggregate",
        "max_workers": 4
    },
    "aggregate": FunctionStep("aggregate", combine_results)
})

result = await flow.run("Analyze this comprehensive text...")
```

## 3. Quality Assurance and Evaluation

### Automatic Quality Control
```python
from refinire import RefinireAgent

# Agent with automatic evaluation and retry
agent = RefinireAgent(
    name="quality_writer",
    generation_instructions="Generate high-quality technical content",
    evaluation_instructions="Rate the content quality from 0-100 based on accuracy, clarity, and completeness",
    threshold=85.0,  # Automatically retry if score < 85
    max_retries=3,
    model="gpt-4o-mini"
)

result = agent.run("Explain machine learning algorithms")
print(f"Quality Score: {result.evaluation_score}")
print(f"Attempts: {result.attempts}")
```

### Custom Guardrails
```python
def content_safety_check(content: str) -> bool:
    """Check content for safety"""
    prohibited = ["harmful", "dangerous", "illegal"]
    return not any(word in content.lower() for word in prohibited)

def input_validation(input_text: str) -> bool:
    """Validate input format"""
    return len(input_text.strip()) > 0

agent = RefinireAgent(
    name="safe_assistant",
    generation_instructions="Provide helpful and safe responses",
    input_guardrails=[input_validation],
    output_guardrails=[content_safety_check],
    model="gpt-4o-mini"
)
```

## 4. Dynamic Prompt Generation with Variable Embedding

### Basic Variable Embedding
```python
from refinire import RefinireAgent, Context

# Agent with variable embedding capability
agent = RefinireAgent(
    name="dynamic_assistant",
    generation_instructions="You are a {{role}} providing {{style}} responses to {{audience}} users. Context: {{RESULT}}",
    model="gpt-4o-mini"
)

# Setup context with variables
ctx = Context()
ctx.shared_state = {
    "role": "technical expert",
    "style": "detailed and practical", 
    "audience": "developer"
}
ctx.result = "Previous analysis completed"

# Dynamic prompt generation
result = agent.run("Help {{audience}} with {{task_type}} implementation", ctx)
```

### Complex Variable Workflows
```python
# Multi-step workflow with variable embedding
analyzer = RefinireAgent(
    name="analyzer",
    generation_instructions="Analyze {{content_type}} content and provide {{analysis_depth}} insights",
    evaluation_instructions="Rate analysis quality based on {{quality_criteria}}",
    threshold=80.0
)

synthesizer = RefinireAgent(
    name="synthesizer", 
    generation_instructions="Synthesize the analysis: {{RESULT}} with evaluation: {{EVAL_RESULT}}",
    model="gpt-4o"
)

# Context setup for workflow
ctx = Context()
ctx.shared_state = {
    "content_type": "technical documentation",
    "analysis_depth": "comprehensive",
    "quality_criteria": "accuracy and actionability"
}

# Execute workflow
analysis_result = analyzer.run("Analyze this API documentation", ctx)
synthesis_result = synthesizer.run("Create final recommendations", ctx)
```

## 5. Context Management and Memory

### Intelligent Context Providers
```python
from refinire import RefinireAgent

# Agent with advanced context management
agent = RefinireAgent(
    name="code_assistant",
    generation_instructions="Help with code analysis using available context",
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

# Context automatically includes relevant files and conversation history
result = agent.run("How can I improve error handling in the main module?")
```

### Context-Based Agent Chaining
```python
from refinire import Context

# Create shared context for agent chain
ctx = Context()

# First agent: Analysis
analyzer = RefinireAgent(
    name="analyzer",
    generation_instructions="Perform detailed code analysis",
    model="gpt-4o"
)

analysis_result = analyzer.run("Analyze this codebase for improvements", ctx)

# Second agent: Recommendations (uses previous result)
recommender = RefinireAgent(
    name="recommender",
    generation_instructions="Based on the analysis {{RESULT}}, provide specific recommendations",
    model="gpt-4o-mini"
)

recommendations = recommender.run("Generate improvement recommendations", ctx)

# Access results and evaluation data
print(f"Analysis: {ctx.result}")
print(f"Evaluation: {ctx.evaluation_result}")
print(f"Recommendations: {recommendations.content}")
```

## 6. Structured Output and Data Processing

### Pydantic Model Integration
```python
from pydantic import BaseModel
from typing import List
from refinire import RefinireAgent

class CodeAnalysis(BaseModel):
    language: str
    complexity_score: int
    issues: List[str]
    recommendations: List[str]

# Agent with structured output
agent = RefinireAgent(
    name="code_analyzer",
    generation_instructions="Analyze code and return structured analysis",
    output_model=CodeAnalysis,
    model="gpt-4o-mini"
)

result = agent.run("Analyze this Python function for issues")
analysis = result.content  # Typed CodeAnalysis object
print(f"Complexity: {analysis.complexity_score}")
print(f"Issues: {analysis.issues}")
```

## 7. Multi-Provider Workflows

### Provider-Specific Agents in Workflows
```python
# Use different providers for different tasks
flow = Flow(start="analyze", steps={
    "analyze": RefinireAgent(
        name="analyzer",
        generation_instructions="Perform initial analysis",
        model="gpt-4o"  # OpenAI for analysis
    ),
    "creative": RefinireAgent(
        name="creative",
        generation_instructions="Generate creative solutions based on: {{RESULT}}",
        model="claude-3-sonnet"  # Anthropic for creativity
    ),
    "technical": RefinireAgent(
        name="technical",
        generation_instructions="Provide technical implementation for: {{RESULT}}",
        model="gemini-pro"  # Google for technical details
    )
})

result = await flow.run("Design a new feature for our application")
```

## 8. Performance Monitoring and Analytics

### Trace Analysis and Debugging
```python
from refinire import get_global_registry, enable_console_tracing

# Enable detailed tracing
enable_console_tracing()

# Run your workflow
result = await flow.run("Complex analysis task")

# Analyze performance
registry = get_global_registry()

# Search for specific patterns
recent_flows = registry.search_by_flow_name("analysis_workflow")
performance_data = registry.complex_search(
    flow_name_pattern="analysis",
    status="completed",
    min_duration=100
)

# Performance insights
for flow in performance_data:
    print(f"Flow: {flow.flow_name}")
    print(f"Duration: {flow.duration}ms")
    print(f"Success: {flow.status}")
```

## Best Practices

### 1. Error Handling and Resilience
```python
try:
    result = agent.run("Complex task", timeout=60.0)
except Exception as e:
    print(f"Task failed: {e}")
    # Implement fallback logic
```

### 2. Resource Management
```python
# Use context managers for resource cleanup
async with flow.managed_execution() as executor:
    result = await executor.run("Task")
```

### 3. Configuration Management
```python
# Use environment-based configuration
agent = RefinireAgent(
    name="production_agent",
    generation_instructions="Handle production requests",
    model=os.getenv("PRODUCTION_MODEL", "gpt-4o-mini"),
    max_tokens=int(os.getenv("MAX_TOKENS", "2000")),
    timeout=float(os.getenv("TIMEOUT", "30.0"))
)
```

These advanced features enable you to build sophisticated, production-ready AI workflows with Refinire's powerful architecture.