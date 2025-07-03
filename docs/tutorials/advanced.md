# Advanced Features Tutorial

This tutorial covers advanced features of Refinire for building sophisticated AI workflows. Each section explains the concepts and implementation approaches rather than focusing on code details.

## 1. Tool Integration with RefinireAgent

### Understanding Tool Integration

Refinire provides two primary methods for integrating external tools with AI agents: direct function tools and MCP (Model Context Protocol) servers. Tool integration allows your agents to perform actions beyond text generation, such as accessing databases, calling APIs, or executing calculations.

#### Modern Tool Integration Approach

The `@tool` decorator creates function tools that your agents can automatically invoke. When you decorate a function with `@tool`, Refinire handles the automatic discovery, parameter extraction, and execution coordination. Your agent will intelligently decide when to use each tool based on user requests.

**Implementation Requirements:**
- Define functions with clear type hints and docstrings
- Use the `@tool` decorator from Refinire
- Pass tool functions to the `tools` parameter when creating agents
- Ensure tool functions handle errors gracefully

```python
# Example: Weather and calculation tools
@tool
def get_weather(location: str) -> str:
    """Get current weather information for a location"""
    # Implement weather API call logic
    pass

agent = RefinireAgent(
    name="assistant",
    generation_instructions="Use available tools to help users",
    tools=[get_weather],  # Tools automatically discovered
    model="gpt-4o-mini"
)
```

#### MCP Server Integration

MCP servers provide standardized access to external systems and data sources. Unlike function tools, MCP servers run as separate processes and communicate via defined protocols. This approach is ideal for complex integrations, database access, or when you need to share tools across multiple applications.

**Implementation Considerations:**
- Configure MCP server endpoints in the `mcp_servers` parameter
- Support stdio, HTTP, and WebSocket server types
- MCP servers handle their own error recovery and connection management
- Tools from MCP servers are automatically discovered and integrated

## 2. Advanced Flow Architectures

### Sequential Processing Patterns

Sequential flows process data through multiple stages, where each step builds upon the results of previous steps. This pattern is essential for complex analysis tasks, content creation workflows, or multi-stage data processing.

**Design Principles:**
- Each step should have a single, well-defined responsibility
- Use the `Context` object to pass data between steps
- Design steps to be independent and testable
- Consider error handling and recovery at each stage

Sequential flows automatically manage data flow between steps, eliminating the need for manual state management. The Flow engine handles execution order, error propagation, and result aggregation.

### Conditional Workflow Logic

Conditional workflows route execution based on input characteristics, user preferences, or dynamic conditions. This pattern enables adaptive behavior where different processing paths handle different types of requests.

**Implementation Strategy:**
- Create condition functions that return routing decisions
- Use `ConditionStep` to implement branching logic
- Design separate agents for each processing path
- Ensure all paths handle similar input types consistently

Condition functions receive the current context and should return clear routing decisions. Keep condition logic simple and focused on a single decision criterion.

### Parallel Processing for Performance

Parallel processing executes independent operations simultaneously, dramatically improving performance for tasks that can be decomposed into separate concerns. This pattern is particularly effective for analysis workflows, data enrichment, or multi-perspective processing.

**Performance Considerations:**
- Identify truly independent operations for parallel execution
- Configure `max_workers` based on your system resources
- Design parallel steps to avoid shared state dependencies
- Aggregate results consistently regardless of execution order

The `{"parallel": [...]}` syntax automatically handles async coordination, worker pool management, and result collection. Focus on designing independent steps rather than managing concurrency details.

## 3. Quality Assurance and Evaluation

### Automatic Quality Control Systems

Quality assurance in AI workflows requires systematic evaluation and automatic improvement mechanisms. Refinire's evaluation system allows you to define quality criteria, set thresholds, and automatically retry failed attempts with improved prompts.

**Evaluation Design Principles:**
- Define clear, measurable quality criteria
- Set realistic thresholds based on your application requirements
- Design evaluation instructions that provide actionable feedback
- Balance quality requirements with performance considerations

When evaluation scores fall below thresholds, the system automatically retries with enhanced prompts incorporating the evaluation feedback. This creates a self-improving loop that maintains quality standards without manual intervention.

### Custom Guardrails Implementation

Guardrails provide safety and compliance controls for AI agent behavior. Input guardrails validate requests before processing, while output guardrails ensure generated content meets your standards.

**Guardrail Design Strategies:**
- Create specific validation functions for different types of content
- Implement early validation to prevent unnecessary processing
- Design clear error messages for failed validations
- Consider performance impact of validation logic

Guardrails should be lightweight, focused functions that return boolean results. Complex validation logic should be modularized for maintainability and testing.

## 4. Dynamic Prompt Generation with Variable Embedding

### Variable Embedding Concepts

Variable embedding enables dynamic prompt construction using context-aware substitution. The `{{variable}}` syntax allows you to create flexible, reusable prompts that adapt based on execution context, previous results, or user-specific data.

**Variable Embedding Strategy:**
- Use descriptive variable names that clarify their purpose
- Leverage reserved variables `{{RESULT}}` and `{{EVAL_RESULT}}` for workflow integration
- Store dynamic values in `Context.shared_state` for cross-step access
- Design prompts that remain coherent with different variable values

This approach enables single agents to serve multiple roles by changing their behavior based on context variables. It also facilitates prompt maintenance by centralizing common patterns.

### Complex Variable Workflows

Multi-step workflows benefit from variable embedding by maintaining context continuity across different agents and processing stages. Each step can contribute to the shared context, building rich information that subsequent steps can utilize.

**Workflow Design Considerations:**
- Plan your variable namespace to avoid conflicts
- Use consistent naming conventions across workflow steps
- Design context variables that provide meaningful information
- Consider variable scope and lifecycle management

Variable embedding works seamlessly with evaluation systems, allowing quality criteria and feedback to flow between workflow stages.

## 5. Context Management and Memory

### Intelligent Context Providers

Context providers automatically manage relevant information for AI agents, including conversation history, file contents, and dynamic data sources. This system eliminates manual context management while ensuring agents have access to pertinent information.

**Context Provider Configuration:**
- Configure conversation history limits based on token considerations
- Specify relevant files and directories for automatic inclusion
- Set up source code analysis for development assistance scenarios
- Balance context richness with processing efficiency

Context providers operate transparently, allowing you to focus on agent behavior rather than information management. The system automatically filters and prioritizes context based on relevance and token limits.

### Context-Based Agent Chaining

Agent chaining through shared context enables sophisticated workflows where multiple specialized agents collaborate on complex tasks. Each agent contributes its expertise while building upon previous work.

**Chaining Design Patterns:**
- Use specialized agents for different aspects of complex problems
- Design context handoff patterns that preserve important information
- Implement evaluation at key transition points
- Consider error recovery and fallback strategies

The shared context maintains execution history, evaluation results, and accumulated state, enabling sophisticated coordination between agents.

## 6. Structured Output and Data Processing

### Pydantic Model Integration

Structured output ensures AI-generated content conforms to specific data schemas, enabling reliable integration with other systems. Pydantic models provide type safety, validation, and serialization for AI outputs.

**Structured Output Benefits:**
- Guarantee consistent data formats for downstream processing
- Enable type-safe integration with existing systems
- Provide automatic validation of AI-generated content
- Facilitate testing and debugging with predictable data structures

When you specify an `output_model`, Refinire ensures the agent's response conforms to the defined schema, automatically handling parsing and validation.

## 7. Multi-Provider Workflows

### Provider-Specific Optimization

Different LLM providers excel at different types of tasks. Multi-provider workflows leverage these strengths by routing specific processing steps to optimal providers.

**Provider Selection Strategy:**
- Use provider strengths for appropriate tasks (analysis, creativity, technical implementation)
- Consider cost and performance trade-offs for different providers
- Design workflows that gracefully handle provider-specific behaviors
- Implement fallback strategies for provider availability issues

Multi-provider approaches require careful consideration of model capabilities, response formats, and integration patterns.

## 8. Performance Monitoring and Analytics

### Trace Analysis and Debugging

Refinire's tracing system automatically captures detailed execution information, enabling performance analysis and debugging. The trace registry provides search and analysis capabilities for understanding system behavior.

**Monitoring Implementation:**
- Enable tracing for development and debugging scenarios
- Use trace search capabilities to identify performance patterns
- Implement custom trace analysis for specific monitoring needs
- Consider trace data volume and storage implications

Tracing provides insights into execution duration, success rates, and error patterns, enabling data-driven optimization of your AI workflows.

## Best Practices for Production Systems

### Error Handling and Resilience

Production AI systems require robust error handling strategies that gracefully manage failures while maintaining user experience. Design your systems to handle network issues, provider limitations, and unexpected input gracefully.

### Resource Management

Effective resource management ensures consistent performance and cost control. Consider token limits, request rates, and concurrency limitations when designing production workflows.

### Configuration Management

Use environment-based configuration to manage different deployment scenarios. Separate development, staging, and production configurations while maintaining consistent behavior patterns.

These advanced features enable sophisticated, production-ready AI workflows that adapt to complex requirements while maintaining reliability and performance.