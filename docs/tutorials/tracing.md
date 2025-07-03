# Tracing and Observability with Refinire

Refinire provides comprehensive tracing capabilities to help you monitor and debug your AI agent workflows. This tutorial covers both built-in console tracing and advanced OpenTelemetry integration.

## Overview

Refinire offers two levels of tracing:

1. **Built-in Console Tracing** - Always available, no additional dependencies
2. **OpenTelemetry Tracing** - Advanced observability with OTLP export (requires optional dependencies)

## Built-in Console Tracing

By default, Refinire displays detailed trace information in the console with color-coded output:

- **🔵 Instructions** - Agent generation instructions (blue)
- **🟢 User Input** - User queries and inputs (green)  
- **🟡 LLM Output** - Model responses and results (yellow)
- **🔴 Errors** - Error messages and warnings (red)

### Example Console Output

```python
from refinire import RefinireAgent
from refinire.agents.flow import Context

agent = RefinireAgent(
    name="example_agent",
    generation_instructions="You are a helpful assistant.",
    model="gpt-4o-mini"
)

ctx = Context()
result = await agent.run_async("What is quantum computing?", ctx)
```

Console output:
```
🔵 [Instructions] You are a helpful assistant.
🟢 [User Input] What is quantum computing?
🟡 [LLM Output] Quantum computing is a revolutionary computing paradigm...
✅ [Result] Operation completed successfully
```

## OpenTelemetry Tracing

For production environments and advanced debugging, Refinire supports OpenTelemetry with OTLP export to observability platforms like Grafana Tempo, Jaeger, and others.

### Installation

Install the optional OpenInference instrumentation dependencies:

```bash
# Install via extras
pip install refinire[openinference-instrumentation]

# Or install manually
pip install openinference-instrumentation openinference-instrumentation-openai opentelemetry-exporter-otlp
```

### Basic OpenTelemetry Setup

```python
from refinire import (
    RefinireAgent,
    enable_opentelemetry_tracing,
    disable_opentelemetry_tracing
)
from refinire.agents.flow import Context

# Enable OpenTelemetry tracing
enable_opentelemetry_tracing(
    service_name="my-agent-app",
    otlp_endpoint="http://localhost:4317",  # Grafana Tempo endpoint
    console_output=True  # Also show console traces
)

# Create agent - will automatically be traced as spans
agent = RefinireAgent(
    name="traced_agent",
    generation_instructions="You are a helpful assistant.",
    model="gpt-4o-mini"
)

# Every agent execution automatically creates a span
ctx = Context()
result = await agent.run_async("What is machine learning?", ctx)

# The following information is automatically captured in spans:
# - Agent name: "RefinireAgent(traced_agent)"
# - Input: user query
# - Instructions: generation instructions
# - Output: agent response
# - Model: "gpt-4o-mini"
# - Success/error status
# - Evaluation scores (if evaluation is enabled)

# Disable tracing when done
disable_opentelemetry_tracing()
```

### Disabling All Tracing

To completely disable all tracing (both console and OpenTelemetry), use the `disable_tracing()` function:

```python
from refinire import disable_tracing

# Disable all tracing output
disable_tracing()

# Now all agent executions will run silently without any trace output
agent = RefinireAgent(
    name="silent_agent",
    generation_instructions="You are a helpful assistant.",
    model="gpt-4o-mini"
)

result = agent.run("This will execute silently")
# No console output, no OpenTelemetry spans created
```

### Re-enabling Tracing

If you need to re-enable tracing after disabling it:

```python
from refinire import enable_console_tracing, enable_opentelemetry_tracing

# Re-enable console tracing only
enable_console_tracing()

# Or re-enable OpenTelemetry tracing
enable_opentelemetry_tracing(
    service_name="my-service",
    otlp_endpoint="http://localhost:4317"
)
```

### Environment Variable Configuration

Refinire supports environment-based configuration using the `REFINIRE_TRACE_*` variables:

```bash
# Set environment variables
export REFINIRE_TRACE_OTLP_ENDPOINT="http://localhost:4317"
export REFINIRE_TRACE_SERVICE_NAME="my-agent-service"
export REFINIRE_TRACE_RESOURCE_ATTRIBUTES="environment=production,team=ai"

# No parameters needed - uses environment variables
enable_opentelemetry_tracing()
```

### Using oneenv for Configuration Management

Refinire provides oneenv templates for easy environment management:

```bash
# Initialize tracing configuration template
oneenv init --template refinire.tracing

# This creates a .env file with:
# REFINIRE_TRACE_OTLP_ENDPOINT=
# REFINIRE_TRACE_SERVICE_NAME=refinire-agent
# REFINIRE_TRACE_RESOURCE_ATTRIBUTES=

# Edit the .env file with your settings
# REFINIRE_TRACE_OTLP_ENDPOINT=http://localhost:4317
# REFINIRE_TRACE_SERVICE_NAME=my-application
# REFINIRE_TRACE_RESOURCE_ATTRIBUTES=environment=production,team=ai
```

Then in your Python code:

```python
from oneenv import load_env

# Load environment variables from .env file
load_env()

# Now you can use the tracing functions
from refinire import enable_opentelemetry_tracing

# Environment variables are automatically used
enable_opentelemetry_tracing()
```

## Automatic Agent Tracing

### What Gets Traced Automatically

When you enable OpenTelemetry tracing, every RefinireAgent execution automatically creates a span with rich metadata:

```python
from refinire import RefinireAgent, enable_opentelemetry_tracing
from refinire.agents.flow import Context

# Enable tracing - this is all you need!
enable_opentelemetry_tracing(
    service_name="my-app",
    otlp_endpoint="http://localhost:4317"
)

# Create agent with evaluation
agent = RefinireAgent(
    name="helpful_assistant",
    generation_instructions="You are a helpful assistant specializing in technology.",
    evaluation_instructions="Rate the response quality from 0-100 based on accuracy and helpfulness.",
    threshold=75.0,
    model="gpt-4o-mini"
)

# This single call automatically creates a span with:
# - Span name: "RefinireAgent(helpful_assistant)"
# - Input text, instructions, and output
# - Model name and parameters
# - Success/failure status
# - Evaluation score and pass/fail status
# - Error details if any failures occur
ctx = Context()
result = await agent.run_async("Explain quantum computing", ctx)
```

### Automatic Span Coverage

Refinire automatically creates spans for:

#### **RefinireAgent Spans**
Every RefinireAgent execution creates a detailed span with:
- **`input`**: The user query or input text
- **`instructions`**: The agent's generation instructions
- **`output`**: The generated response
- **`model`**: The LLM model used (e.g., "gpt-4o-mini")
- **`success`**: Boolean indicating if execution succeeded
- **`evaluation.score`**: Evaluation score (0-100) if evaluation is enabled
- **`evaluation.passed`**: Boolean indicating if evaluation threshold was met
- **`error`**: Error message if execution failed

#### **Workflow Step Spans**
All workflow steps automatically create spans:

**ConditionStep Spans:**
- **`condition_result`**: Boolean result of condition evaluation
- **`if_true`**: Step name for true branch
- **`if_false`**: Step name for false branch
- **`next_step`**: Actual next step taken

**FunctionStep Spans:**
- **`function_name`**: Name of executed function
- **`next_step`**: Next step after execution
- **`success`**: Execution success status

**ParallelStep Spans:**
- **`parallel_steps`**: List of parallel step names
- **`execution_time_seconds`**: Total parallel execution time
- **`successful_steps`**: List of successfully completed steps
- **`failed_steps`**: Number of failed parallel steps
- **`total_steps`**: Total number of parallel steps

**All Step Types Include:**
- **`step.name`**: Step identifier
- **`step.type`**: Step class name (ConditionStep, FunctionStep, etc.)
- **`step.category`**: Step category (condition, function, parallel, etc.)
- **`current_step`**: Current workflow position
- **`step_count`**: Number of steps executed
- **`recent_messages`**: Last 3 context messages

#### **Flow Workflow Spans**
Complete workflows automatically create top-level spans:

**Flow Spans:**
- **`flow.name`**: Flow identifier name
- **`flow.id`**: Unique flow execution ID
- **`flow.start_step`**: Name of the starting step
- **`flow.step_count`**: Total number of defined steps
- **`flow.step_names`**: List of all step names in the flow
- **`flow_input`**: Input data provided to the flow
- **`flow_completed`**: Boolean indicating successful completion
- **`final_step_count`**: Number of steps actually executed
- **`flow_finished`**: Whether the flow reached a natural end
- **`flow_result`**: Final result from the flow (truncated to 500 chars)
- **`flow_error`**: Error message if flow execution failed

### Advanced Workflow Tracing (Optional)

For complex workflows, you can still add custom spans around groups of agent calls:

```python
from refinire import get_tracer, enable_opentelemetry_tracing
from refinire.agents.flow import Context

# Enable tracing
enable_opentelemetry_tracing(
    service_name="workflow-app",
    otlp_endpoint="http://localhost:4317"
)

# Get tracer for custom workflow spans (optional)
tracer = get_tracer("workflow-tracer")

with tracer.start_as_current_span("multi-agent-workflow") as span:
    span.set_attribute("workflow.type", "analysis-pipeline")
    span.set_attribute("user.id", "user123")
    
    # These agents will automatically create spans within the workflow span
    analyzer = RefinireAgent(
        name="content_analyzer",
        generation_instructions="Analyze and categorize the input.",
        model="gpt-4o-mini"
    )
    
    expert = RefinireAgent(
        name="domain_expert",
        generation_instructions="Provide expert analysis.",
        model="gpt-4o-mini"
    )
    
    ctx = Context()
    
    # Each of these calls automatically creates detailed spans
    analysis = await analyzer.run_async("Explain machine learning", ctx)
    response = await expert.run_async("Explain machine learning", ctx)
    
    span.set_attribute("workflow.status", "completed")
    span.set_attribute("agents.count", 2)
```

### Multi-Agent Pipeline Tracing

```python
# Create specialized agents with different roles
agents = {
    "analyzer": RefinireAgent(
        name="content_analyzer",
        generation_instructions="Analyze input and determine category.",
        model="gpt-4o-mini"
    ),
    "technical": RefinireAgent(
        name="technical_expert",
        generation_instructions="Provide technical explanations.",
        model="gpt-4o-mini"
    ),
    "business": RefinireAgent(
        name="business_expert", 
        generation_instructions="Provide business analysis.",
        model="gpt-4o-mini"
    )
}

tracer = get_tracer("multi-agent-pipeline")

with tracer.start_as_current_span("multi-agent-workflow") as workflow_span:
    user_query = "How should we implement CI/CD?"
    workflow_span.set_attribute("query", user_query)
    
    ctx = Context()
    
    # Route based on analysis
    with tracer.start_as_current_span("routing") as route_span:
        analysis = await agents["analyzer"].run_async(user_query, ctx)
        category = str(analysis.result).lower()
        route_span.set_attribute("route.category", category)
    
    # Execute with appropriate expert
    expert_key = "technical" if "technical" in category else "business"
    with tracer.start_as_current_span(f"{expert_key}-response") as expert_span:
        result = await agents[expert_key].run_async(user_query, ctx)
        expert_span.set_attribute("expert.type", expert_key)
        expert_span.set_attribute("response.length", len(str(result.result)))
```

## Integration with Observability Platforms

### Complete Grafana Tempo Setup Tutorial

This section provides a step-by-step guide to set up Grafana Tempo and send traces from Refinire.

#### Step 1: Download and Install Grafana Tempo

**Option A: Download Binary**
```bash
# Download Tempo (replace with latest version)
wget https://github.com/grafana/tempo/releases/download/v2.3.0/tempo_2.3.0_linux_amd64.tar.gz
tar -xzf tempo_2.3.0_linux_amd64.tar.gz
```

**Option B: Using Docker**
```bash
# Run Tempo with Docker
docker run -d \
  --name tempo \
  -p 3200:3200 \
  -p 4317:4317 \
  -p 4318:4318 \
  -v $(pwd)/tempo.yaml:/etc/tempo.yaml \
  grafana/tempo:latest \
  -config.file=/etc/tempo.yaml
```

#### Step 2: Create Tempo Configuration

Create `tempo.yaml` configuration file:

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

# Enable search capabilities
storage:
  trace:
    backend: local
    local:
      path: /tmp/tempo/traces
    pool:
      max_workers: 100
      queue_depth: 10000
```

#### Step 3: Start Tempo Server

```bash
# If using binary
./tempo -config.file=tempo.yaml

# Verify Tempo is running
curl http://localhost:3200/ready
# Should return: ready
```

#### Step 4: Configure Refinire to Send Traces

```python
from refinire import (
    RefinireAgent,
    enable_opentelemetry_tracing,
    disable_opentelemetry_tracing
)

# Enable tracing with Tempo endpoint
enable_opentelemetry_tracing(
    service_name="refinire-tempo-demo",
    otlp_endpoint="http://localhost:4317",  # Tempo gRPC endpoint
    console_output=True,  # Also show traces in console
    resource_attributes={
        "environment": "development",
        "service.version": "1.0.0",
        "demo.type": "tempo-integration"
    }
)

# Create and run agent
agent = RefinireAgent(
    name="tempo_agent",
    generation_instructions="You are a helpful assistant for demonstrating tracing.",
    model="gpt-4o-mini"
)

from refinire.agents.flow import Context
ctx = Context()

# This will generate traces sent to Tempo
result = await agent.run_async("Explain the benefits of distributed tracing", ctx)
print(f"Response: {result.result}")

# Clean up
disable_opentelemetry_tracing()
```

#### Step 5: Set Up Grafana to View Traces

1. **Install Grafana**:
```bash
# Using Docker
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana:latest
```

2. **Access Grafana**:
   - Open http://localhost:3000
   - Login: admin/admin (change password on first login)

3. **Add Tempo Data Source**:
   - Go to Configuration → Data Sources
   - Click "Add data source"
   - Select "Tempo"
   - Set URL: `http://localhost:3200`
   - Click "Save & Test"

4. **View Traces**:
   - Go to Explore
   - Select Tempo data source
   - Use TraceQL query: `{service.name="refinire-tempo-demo"}`
   - Or search by service name in the dropdown

#### Step 6: Verify Traces Are Being Sent

Run the Grafana Tempo example to test the integration:

```bash
# Run the example
python examples/grafana_tempo_tracing_example.py
```

Expected output:
```
=== Grafana Tempo Tracing Example ===

✅ OpenTelemetry tracing enabled with Tempo endpoint: http://localhost:4317

--- Running operations (traces sent to Grafana Tempo) ---

🔍 Query 1: What are the benefits of using Grafana for observability?
📝 Response length: 342 characters
📊 First 100 chars: Grafana offers several key benefits for observability: 1. **Unified Dashboard**...

✅ All traces sent to Grafana Tempo at http://localhost:4317
🔗 Check your Grafana Tempo UI to view the traces!
```

#### Step 7: Explore Traces in Grafana

1. **Find Your Traces**:
   - In Grafana Explore, search for service: `refinire-tempo-demo`
   - Look for recent traces (within last 15 minutes)
   - Click on a trace to see detailed span information

2. **Trace Details You'll See**:
   - Service name: `refinire-tempo-demo`
   - Operation names: OpenAI API calls, agent operations
   - Duration and timing information
   - Resource attributes (environment, demo.type, etc.)
   - Error information if any failures occur

3. **Advanced Queries**:
   ```
   # Find traces with errors
   {service.name="refinire-tempo-demo" && status=error}
   
   # Find long-running traces
   {service.name="refinire-tempo-demo" && duration>5s}
   
   # Find traces by resource attribute
   {environment="development"}
   ```

#### Step 8: Advanced Tempo Configuration

For production use, consider these additional configurations:

```yaml
# tempo-production.yaml
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

# Use S3 for production storage
storage:
  trace:
    backend: s3
    s3:
      bucket: tempo-traces
      endpoint: s3.amazonaws.com

# Enable metrics generation
metrics_generator:
  registry:
    external_labels:
      source: tempo
  storage:
    path: /tmp/tempo/generator/wal
    remote_write:
      - url: http://prometheus:9090/api/v1/write
```

### Jaeger Setup

```bash
# Run Jaeger all-in-one
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 14250:14250 \
  jaegertracing/all-in-one:latest

# Configure Refinire
enable_opentelemetry_tracing(
    service_name="refinire-app",
    otlp_endpoint="http://localhost:14250"
)
```

## Example Files

Refinire includes comprehensive examples in the `examples/` directory:

- **`opentelemetry_tracing_example.py`** - Basic OpenTelemetry setup and usage
- **`grafana_tempo_tracing_example.py`** - Grafana Tempo integration examples
- **`oneenv_tracing_example.py`** - Environment configuration with oneenv

### Running the Examples

```bash
# Basic OpenTelemetry example
python examples/opentelemetry_tracing_example.py

# Grafana Tempo integration
python examples/grafana_tempo_tracing_example.py

# OneEnv configuration demo
python examples/oneenv_tracing_example.py
```

## Best Practices

### 1. Resource Attributes
Always include meaningful resource attributes:

```python
enable_opentelemetry_tracing(
    resource_attributes={
        "environment": "production",
        "service.version": "1.2.3",
        "deployment.environment": "kubernetes",
        "team": "ai-research"
    }
)
```

### 2. Custom Spans for Business Logic
Create spans for important business operations:

```python
with tracer.start_as_current_span("document-processing") as span:
    span.set_attribute("document.type", "pdf")
    span.set_attribute("document.size", file_size)
    # Processing logic here
    span.set_attribute("processing.status", "completed")
```

### 3. Error Handling
Always capture errors in traces:

```python
try:
    result = await agent.run_async(query, ctx)
    span.set_attribute("operation.success", True)
except Exception as e:
    span.set_attribute("operation.success", False)
    span.set_attribute("error.message", str(e))
    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
    raise
```

### 4. Performance Monitoring
Track performance metrics:

```python
import time

start_time = time.time()
result = await agent.run_async(query, ctx)
duration = time.time() - start_time

span.set_attribute("operation.duration_ms", duration * 1000)
span.set_attribute("tokens.input", len(query.split()))
span.set_attribute("tokens.output", len(str(result.result).split()))
```

## Troubleshooting

### Common Issues

1. **Traces not appearing**: Check OTLP endpoint connectivity
2. **Missing dependencies**: Install `refinire[openinference-instrumentation]`
3. **Environment variables**: Verify `REFINIRE_TRACE_*` variables are set correctly

### Debugging Tips

1. **Enable console output** during development:
```python
enable_opentelemetry_tracing(console_output=True)
```

2. **Check trace availability**:
```python
from refinire import is_openinference_available, is_opentelemetry_enabled

print(f"OpenInference available: {is_openinference_available()}")
print(f"Tracing enabled: {is_opentelemetry_enabled()}")
```

3. **Test connectivity**:
```python
import socket

def test_otlp_connection(host="localhost", port=4317):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

print(f"OTLP endpoint reachable: {test_otlp_connection()}")
```

## Next Steps

- Set up a production observability stack with Grafana + Tempo
- Implement custom metrics alongside tracing
- Create dashboards for agent performance monitoring
- Set up alerting based on trace data

For more examples and advanced configurations, check the `examples/` directory in the Refinire repository.