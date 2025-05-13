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

### With Retry Comment Feedback
```python
from agents_sdk_models.pipeline import AgentPipeline

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