# Refinire Agents

AI agents and workflow orchestration for the Refinire platform.

## Features

- Flow/Step based workflow architecture
- Specialized AI agents (generation, clarification, extraction, etc.)
- Pipeline functionality with evaluation and tools
- Context management and state sharing

## Installation

```bash
pip install refinire-core refinire-agents
```

## Usage

```python
from refinire.core import get_llm
from refinire.agents import Flow, create_simple_gen_agent

# Create a simple workflow
flow = Flow({
    "start": create_simple_gen_agent(get_llm("openai", "gpt-4o-mini"))
})

# Execute the workflow
result = flow.run("Generate a greeting")
```

For more documentation, visit [https://kitfactory.github.io/refinire/](https://kitfactory.github.io/refinire/)