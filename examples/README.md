# Refinire Examples

This directory contains 8 essential examples that demonstrate Refinire's core capabilities through the three foundational pillars:

## 🏛️ Three Pillars of Refinire

1. **🔗 Unified LLM Interface** - Access multiple providers through one API
2. **🎯 Autonomous Quality Assurance** - Built-in evaluation and improvement
3. **🔧 Composable Flow Architecture** - Flexible workflow orchestration

## 📚 Essential Examples

### 1. Basic RefinireAgent Usage
**File:** `llm_pipeline_simple.py`
**Demonstrates:** Core agent functionality, structured output, and basic tool integration
```bash
python llm_pipeline_simple.py
```
**Key Features:**
- Basic RefinireAgent setup and usage
- Structured output with Pydantic models
- Simple tool integration
- Bilingual comments (English/Japanese)

### 2. Autonomous Quality Assurance
**File:** `evaluation_examples.py`
**Demonstrates:** Built-in evaluation system with quality thresholds
```bash
python evaluation_examples.py
```
**Key Features:**
- Automatic quality evaluation
- Custom scoring systems
- Iterative improvement
- Multiple evaluation patterns

### 3. Tool Integration
**File:** `refinire_tools_example.py`
**Demonstrates:** Modern tool integration using @tool decorator
```bash
python refinire_tools_example.py
```
**Key Features:**
- Function calling with @tool decorator
- Multiple tool types
- Tool parameter validation
- Error handling in tools

### 4. Simple Flow Workflow
**File:** `simple_flow_test.py`
**Demonstrates:** Basic workflow orchestration with Flow
```bash
python simple_flow_test.py
```
**Key Features:**
- Basic Flow creation and execution
- Step-by-step workflow
- Context management
- Flow state tracking

### 5. Multi-Agent Complex Workflow
**File:** `structured_orchestration_demo.py`
**Demonstrates:** Advanced multi-agent coordination and orchestration
```bash
python structured_orchestration_demo.py
```
**Key Features:**
- Multi-agent coordination
- Structured decision making
- Complex workflow patterns
- Business logic integration

### 6. Streaming Capabilities
**File:** `streaming_example.py`
**Demonstrates:** Real-time streaming responses
```bash
python streaming_example.py
```
**Key Features:**
- Real-time response streaming
- Callback integration
- Context-aware streaming
- Error handling in streams

### 7. Unified LLM Interface (Multi-Provider)
**File:** `openrouter_basic_usage.py`
**Demonstrates:** Multiple LLM providers through unified interface
```bash
python openrouter_basic_usage.py
```
**Key Features:**
- Multiple provider access
- Provider switching
- Unified API usage
- Provider-specific optimizations

### 8. Comprehensive Integration
**File:** `opentelemetry_tracing_example.py`
**Demonstrates:** Advanced observability and monitoring
```bash
python opentelemetry_tracing_example.py
```
**Key Features:**
- OpenTelemetry integration
- Production observability
- Complex workflow monitoring
- Performance tracking

## 🚀 Getting Started

### Prerequisites
```bash
# Install Refinire
pip install refinire

# Set up environment variables for providers
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"
```

### Quick Start
```python
from refinire import RefinireAgent

# Basic usage
agent = RefinireAgent(
    name="assistant",
    generation_instructions="You are a helpful AI assistant.",
    model="gpt-4o-mini"
)

result = agent.run("Hello, how are you?")
print(result.result)
```

## 📖 Learning Path

**For beginners:**
1. Start with `llm_pipeline_simple.py` - Understand basic concepts
2. Try `evaluation_examples.py` - Learn quality assurance
3. Explore `simple_flow_test.py` - Understand workflows

**For intermediate users:**
4. Run `refinire_tools_example.py` - Master tool integration
5. Test `streaming_example.py` - Real-time capabilities
6. Study `openrouter_basic_usage.py` - Multi-provider usage

**For advanced users:**
7. Examine `structured_orchestration_demo.py` - Complex workflows
8. Implement `opentelemetry_tracing_example.py` - Production monitoring

## 🎯 Core Concepts Demonstrated

### Unified LLM Interface
- **Provider Abstraction**: Same API for OpenAI, Anthropic, Google, Ollama
- **Automatic Detection**: Smart provider selection based on model names
- **Unified Configuration**: Consistent parameter handling across providers

### Autonomous Quality Assurance
- **Automatic Evaluation**: Built-in quality scoring (0-100 scale)
- **Threshold Management**: Configurable quality standards
- **Iterative Improvement**: Automatic regeneration for low-quality outputs

### Composable Flow Architecture
- **Step-Based Design**: Modular workflow components
- **Context Management**: Shared state between workflow steps
- **Flexible Orchestration**: Linear, conditional, and parallel execution

## 🛠️ Advanced Features

- **Structured Output**: Pydantic model integration
- **Tool Calling**: Function integration with automatic parameter handling
- **Streaming**: Real-time response generation
- **Observability**: OpenTelemetry and custom tracing
- **Multi-Language**: Built-in localization support
- **Error Handling**: Robust error recovery and fallback mechanisms

## 📝 Documentation

For detailed documentation:
- **API Reference**: `docs/api_reference.md`
- **Unified LLM Interface**: `docs/unified-llm-interface.md`
- **Quality Assurance**: `docs/autonomous-quality-assurance.md`
- **Flow Architecture**: `docs/composable-flow-architecture.md`

## 🤝 Contributing

These examples represent the essential patterns for using Refinire effectively. When contributing new examples, ensure they:

1. **Demonstrate core concepts** clearly
2. **Include comprehensive comments** (bilingual preferred)
3. **Handle errors gracefully**
4. **Follow current API patterns**
5. **Provide educational value**

## ⚡ Performance Tips

- **Provider Selection**: Choose providers based on task requirements
- **Quality Thresholds**: Balance quality vs. response time
- **Flow Design**: Use parallel steps where possible
- **Streaming**: Implement for better user experience
- **Monitoring**: Add observability for production usage

---

*These examples provide a comprehensive foundation for building sophisticated AI applications with Refinire's unified, quality-assured, and composable architecture.*