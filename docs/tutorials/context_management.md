# Context Management Tutorial

This tutorial provides a step-by-step guide to using Refinire's context management features.

## Table of Contents

1. [Basic Concepts](#basic-concepts)
2. [Basic Usage](#basic-usage)
3. [Context Provider Types](#context-provider-types)
4. [Advanced Configuration](#advanced-configuration)
5. [Practical Examples](#practical-examples)
6. [Best Practices](#best-practices)

## Basic Concepts

Context management is a system that automatically provides AI agents with the information they need to generate more appropriate responses.

### Key Features

- **Conversation History Management**: Properly maintain and manage past conversations
- **File Context**: Automatically provide content from relevant files
- **Source Code Search**: Automatically search for code related to user questions
- **Context Compression**: Compress long contexts to appropriate sizes
- **Dynamic Selection**: Select optimal context based on the situation

## Basic Usage

### 1. Simple Configuration

```python
from refinire.agents.pipeline import RefinireAgent

# Basic context configuration
context_config = [
    {
        "type": "conversation_history",
        "max_items": 5,
        "max_tokens": 1000
    }
]

agent = RefinireAgent(
    model="gpt-3.5-turbo",
    context_providers_config=context_config
)
```

### 2. Using Multiple Providers

```python
context_config = [
    {
        "type": "conversation_history",
        "max_items": 5
    },
    {
        "type": "fixed_file",
        "file_path": "README.md"
    },
    {
        "type": "source_code",
        "max_files": 3,
        "max_file_size": 500
    }
]
```

## Context Provider Types

### 1. ConversationHistoryProvider

Manages conversation history.

```python
{
    "type": "conversation_history",
    "max_items": 10        # Number of messages to keep
}
```

### 2. FixedFileProvider

Always provides content from specified files.

```python
{
    "type": "fixed_file",
    "file_path": "config.yaml"
}
```

### 3. SourceCodeProvider

Automatically searches for source code related to user questions.

```python
{
    "type": "source_code",
    "max_files": 5,                    # Maximum number of files
    "max_file_size": 1000              # Maximum file size in bytes
}
```

### 4. CutContextProvider

Compresses context to specified length.

```python
{
    "type": "cut_context",
    "provider": {
        "type": "source_code",
        "max_files": 10,
        "max_file_size": 2000
    },
    "max_chars": 3000,           # Maximum character count
    "cut_strategy": "middle",     # Compression strategy (start/end/middle)
    "preserve_sections": True     # Preserve sections
}
```

## Advanced Configuration

### 1. String-based Configuration

You can describe configuration using YAML-like strings.

```python
string_config = """
- type: conversation_history
  max_items: 5
- type: source_code
  max_files: 3
  max_file_size: 500
"""

agent = RefinireAgent(
    model="gpt-3.5-turbo",
    context_providers_config=string_config
)
```

### 2. Chained Processing

Providers can receive and process context from previous providers.

```python
context_config = [
    {
        "type": "source_code",
        "max_files": 10,
        "max_file_size": 2000
    },
    {
        "type": "cut_context",
        "provider": {
            "type": "source_code",
            "max_files": 10,
            "max_file_size": 2000
        },
        "max_chars": 3000,
        "cut_strategy": "middle"
    }
]
```

## Practical Examples

### 1. Code Review Assistance

```python
context_config = [
    {
        "type": "source_code",
        "max_files": 10,
        "max_file_size": 2000
    },
    {
        "type": "fixed_file",
        "file_path": "CONTRIBUTING.md"
    },
    {
        "type": "conversation_history",
        "max_items": 5
    }
]
```

agent = RefinireAgent(
    name="CodeReviewAgent",
    generation_instructions="Review code for quality, best practices, error handling, performance, and documentation completeness.",
    model="gpt-4",
    context_providers_config=context_config
)

response = await agent.run_async("Please review the quality of this code")
```

### 2. Documentation Generation

```python
context_config = [
    {
        "type": "source_code",
        "max_files": 15,
        "max_file_size": 1500
    },
    {
        "type": "cut_context",
        "provider": {
            "type": "source_code",
            "max_files": 15,
            "max_file_size": 1500
        },
        "max_chars": 4000,
        "cut_strategy": "start"
    }
]
```

agent = RefinireAgent(
    name="DocRefinireAgent",
    generation_instructions="Generate comprehensive documentation based on source code and existing documentation.",
    model="gpt-4",
    context_providers_config=context_config
)

response = await agent.run_async("Generate API documentation")
```

### 3. Debugging Assistance

```python
context_config = [
    {
        "type": "source_code",
        "max_files": 8,
        "max_file_size": 1000
    },
    {
        "type": "conversation_history",
        "max_items": 10
    }
]
```

agent = RefinireAgent(
    name="DebugAgent",
    generation_instructions="Help investigate and resolve errors by analyzing source code and error messages.",
    model="gpt-4",
    context_providers_config=context_config
)

response = await agent.run_async("Please investigate the cause of this error")
```

## Best Practices

### 1. Provider Order

1. **Information Collection Providers** (source_code, fixed_file)
2. **Processing Providers** (cut_context, filter)
3. **History Providers** (conversation_history)

### 2. Appropriate Size Settings

- **max_files**: 3-10 files
- **max_file_size**: 500-2000 bytes
- **max_chars**: 1000-3000 characters

### 3. Error Handling

```python
try:
    response = await agent.run_async("Question")
except Exception as e:
    print(f"An error occurred: {e}")
    # Clear context and retry
    agent.clear_context()
```

### 4. Performance Optimization

- Remove unnecessary providers
- Set appropriate size limits
- Utilize caching

## Troubleshooting

### Common Issues

1. **File not found**
   - Verify file path is correct
   - Distinguish between relative and absolute paths

2. **Context too long**
   - Use CutContextProvider
   - Adjust size limits

3. **Related files not found**
   - Check SourceCodeProvider settings
   - Adjust file name similarity

### Debugging Methods

```python
# Check available provider schemas
schemas = agent.get_context_provider_schemas()
for schema in schemas:
    print(f"- {schema['name']}: {schema['description']}")

# Clear context
agent.clear_context()
```

## Next Steps

- Check detailed specifications in the [API Reference](../api_reference.md)
- Reference actual code in the [Examples](../../examples/)
- Understand the overall system in the [Architecture Design](../architecture.md) 