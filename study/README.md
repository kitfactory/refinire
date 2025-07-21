# Refinire Study Samples

This directory contains carefully curated sample code to help you learn and understand the Refinire framework. Each file demonstrates specific features and best practices.

## Getting Started

### Basic Usage
1. **`refinire_simple.py`** - Simplest example with error handling
   - Basic RefinireAgent usage
   - Error handling patterns
   - Good starting point for beginners

2. **`refinire_agent_basic_study.py`** - Comprehensive basic features
   - RefinireAgent configuration
   - Generation and evaluation
   - Multiple providers (OpenAI, Anthropic, Google)

### Flow (Workflow) Examples
3. **`ultra_simple_flow.py`** - Simplest possible workflow (NEW!)
   - Ultra-simple SimpleFlow usage
   - Minimum code for maximum effect
   - Perfect for quick workflows

4. **`simple_flow_demo.py`** - Easy workflow creation (NEW!)
   - SimpleFlow with builder pattern
   - 3-step content creation workflow
   - Clean, readable implementation

5. **`flow_simple_clean.py`** - Clean Flow implementation
   - Simple multi-step workflow
   - Best practices for Flow usage
   - Clear step definitions

6. **`flow_sample.py`** - Complex workflow example
   - Content creation pipeline
   - Multiple agent coordination
   - Real-world use case

7. **`flow_routing_sample.py`** - Flow with routing
   - Flow + RefinireAgent integration
   - Routing instruction usage
   - Dynamic flow control

### Advanced Features
8. **`advanced_features_demo.py`** - Advanced feature integration
   - Routing instructions
   - Fast mode
   - Flow combination
   - Multiple provider usage

9. **`fast_mode_sample.py`** - High-performance mode
   - Fast mode configuration
   - Performance comparison
   - When to use fast mode

10. **`routing_instruction_sample.py`** - Content routing
    - Basic routing functionality
    - Classification examples
    - Route-based processing

### Specialized Examples
11. **`code_generation_routing.py`** - Code generation with routing
    - AI-powered code generation
    - Complexity evaluation
    - Quality assessment

12. **`code_generation_simple.py`** - Simple code generation (NEW!)
    - SimpleFlow-based code generation
    - Easy 3-step workflow
    - Complexity assessment and recommendations

13. **`processing_with_routing.py`** - Quality classification
    - Processing result classification
    - Quality assessment routing
    - Multi-tier processing

14. **`refinire_agent_tools_study.py`** - Tool integration
    - External tool usage
    - Tool calling patterns
    - Function integration

### Comparison and Analysis
15. **`compare_direct_vs_refinire.py`** - Framework comparison
    - Direct OpenAI Agents SDK vs Refinire
    - Benefits demonstration
    - Migration guidance

### Monitoring and Debugging
16. **`tracing_study.py`** - Tracing and monitoring
    - Execution tracing
    - Performance monitoring
    - Debugging capabilities

## Usage Instructions

1. **Install Dependencies**: Ensure Refinire is installed with all dependencies
   ```bash
   pip install -e .[dev]
   ```

2. **Set Environment Variables**: Configure your API keys
   ```bash
   export OPENAI_API_KEY="your-key"
   export ANTHROPIC_API_KEY="your-key"
   ```

3. **Run Examples**: Execute any sample file
   ```bash
   python study/refinire_simple.py
   ```

## Learning Path

### Beginner Path
1. Start with `refinire_simple.py`
2. Move to `refinire_agent_basic_study.py`
3. Try `flow_simple_clean.py`
4. Experiment with `fast_mode_sample.py`

### Intermediate Path
1. Study `flow_sample.py`
2. Learn `routing_instruction_sample.py`
3. Explore `processing_with_routing.py`
4. Try `refinire_agent_tools_study.py`

### Advanced Path
1. Master `advanced_features_demo.py`
2. Study `code_generation_routing.py`
3. Analyze `compare_direct_vs_refinire.py`
4. Use `tracing_study.py` for monitoring

## Key Concepts Demonstrated

- **RefinireAgent**: Core agent functionality
- **Flow**: Multi-step workflow orchestration
- **Routing Instructions**: Dynamic content routing
- **Fast Mode**: High-performance execution
- **Tool Integration**: External function calling
- **Multi-Provider Support**: OpenAI, Anthropic, Google
- **Error Handling**: Robust error management
- **Tracing**: Execution monitoring

Each sample is self-contained and includes comments explaining the key concepts and implementation details.