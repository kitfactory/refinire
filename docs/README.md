### With Dynamic Prompt
```python
# You can provide a custom function to dynamically build the prompt.
from agents_sdk_models import AgentPipeline

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

### With Retry Comment Feedback
```python
from agents_sdk_models import AgentPipeline

pipeline = AgentPipeline(
    name="comment_retry",
    generation_instructions="Your generation prompt",
    evaluation_instructions="Your evaluation instructions",
    model="gpt-4o-mini",
    threshold=80,
    retries=2,
    retry_comment_importance=["serious", "normal"]
)
result = pipeline.run("Your input text")
print(result)
```
On each retry, comments of specified importance from the previous evaluation will be automatically prepended to the generation prompt to guide improvements.

## Get Available Models

You can retrieve available model names from different providers using the `get_available_models` functions:

### Synchronous Version
```python
from agents_sdk_models import get_available_models

# Get models from all providers
models = get_available_models(["openai", "google", "anthropic", "ollama"])
print("Available models:", models)

# Get models from specific providers
models = get_available_models(["openai", "google"])
for provider, model_list in models.items():
    print(f"{provider}: {model_list}")

# Custom Ollama URL
models = get_available_models(["ollama"], ollama_base_url="http://custom-host:11434")
```

### Asynchronous Version
```python
from agents_sdk_models import get_available_models_async
import asyncio

async def main():
    # Get models from all providers
    models = await get_available_models_async(["openai", "google", "anthropic", "ollama"])
    print("Available models:", models)
    
    # Custom Ollama URL with environment variable support
    models = await get_available_models_async(["ollama"], ollama_base_url="http://custom-host:11434")

asyncio.run(main())
```

### Features
- **Static Model Lists**: OpenAI, Google, and Anthropic return predefined lists of latest models
- **Dynamic Discovery**: Ollama queries the `/api/ps` endpoint for real-time model availability
- **Environment Variable Support**: Ollama base URL can be set via `OLLAMA_BASE_URL` environment variable
- **Error Handling**: Graceful handling of connection failures with empty lists and warnings
- **Latest Models**: Updated to include Claude-4, Gemini 2.5, and OpenAI's latest models

## 🚀 New Flow Features (v0.0.8+)

The new Flow constructor provides **ultra-simple** workflow creation with three modes:

### Single Step Flow (Simplest!)
```python
from agents_sdk_models import create_simple_gen_agent, Flow

gen_agent = create_simple_gen_agent("assistant", "You are helpful", "gpt-4o-mini")
flow = Flow(steps=gen_agent)  # Just 1 line!
result = await flow.run(input_data="Hello")
```

### Sequential Flow (Auto-connect!)
```python
from agents_sdk_models import create_simple_gen_agent, Flow, DebugStep

idea_gen = create_simple_gen_agent("idea", "Generate ideas", "gpt-4o-mini")
writer = create_simple_gen_agent("writer", "Write articles", "gpt-4o")
reviewer = create_simple_gen_agent("reviewer", "Review content", "claude-3-5-sonnet-latest")

flow = Flow(steps=[idea_gen, writer, reviewer])  # Auto-connected sequence!
result = await flow.run(input_data="AI technology")
```

### Traditional Mode (Complex workflows)
```python
flow = Flow(
    start="step1",
    steps={"step1": step1, "step2": step2}
)
```

**📚 See detailed guide:** [New Flow Features Complete Guide](new_flow_features.md)