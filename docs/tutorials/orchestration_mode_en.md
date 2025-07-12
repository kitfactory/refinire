# Orchestration Mode Tutorial - Multi-Agent Coordination

This tutorial covers RefinireAgent's orchestration mode, which provides standardized communication protocols for building complex multi-agent systems.

## Table of Contents

1. [Understanding Orchestration Mode](#understanding-orchestration-mode)
2. [Basic Orchestration Setup](#basic-orchestration-setup)
3. [Structured Output Integration](#structured-output-integration)
4. [Multi-Agent Workflow Coordination](#multi-agent-workflow-coordination)
5. [Advanced Orchestration Patterns](#advanced-orchestration-patterns)
6. [Error Handling and Recovery](#error-handling-and-recovery)
7. [Best Practices](#best-practices)

## Understanding Orchestration Mode

### The Challenge

Traditional AI agents return unstructured text or context objects, making it difficult to:
- Coordinate multiple agents in a workflow
- Determine if an agent completed its task successfully
- Know what action should be taken next
- Build robust error handling and recovery mechanisms

### The Solution

Orchestration mode transforms RefinireAgent output into a standardized JSON format:

```json
{
  "status": "completed",          // "completed" or "failed"
  "result": "task outcome",       // Actual result (string or typed object)
  "reasoning": "why this result", // Agent's reasoning process
  "next_hint": {                  // Recommendation for next step
    "task": "validation",
    "confidence": 0.85,
    "rationale": "Ready for validation step"
  }
}
```

### Key Benefits

- **Standardized Communication**: Uniform interface for agent-to-agent interaction
- **Status Clarity**: Clear success/failure indication for workflow control
- **Smart Recommendations**: Agents suggest optimal next steps
- **Type Safety**: Optional Pydantic model integration for result field
- **Error Transparency**: Structured error reporting for robust systems

## Basic Orchestration Setup

### Simple Orchestration Agent

```python
from refinire import RefinireAgent

# Create an orchestration-enabled agent
agent = RefinireAgent(
    name="data_analyzer",
    generation_instructions="Analyze the provided data and identify key insights",
    orchestration_mode=True,  # Enable structured output
    model="gpt-4o-mini"
)

# Run the agent
result = agent.run("Analyze customer satisfaction survey data")

# Access structured response
print(f"Status: {result['status']}")
print(f"Analysis Result: {result['result']}")
print(f"Reasoning: {result['reasoning']}")

# Check next step recommendation
next_step = result['next_hint']
print(f"Recommended next task: {next_step['task']}")
print(f"Confidence level: {next_step['confidence']}")
print(f"Rationale: {next_step['rationale']}")
```

### Orchestration vs Normal Mode

```python
from refinire import RefinireAgent

# Normal mode agent (default)
normal_agent = RefinireAgent(
    name="normal_agent",
    generation_instructions="Provide helpful analysis",
    orchestration_mode=False,  # Default
    model="gpt-4o-mini"
)

# Orchestration mode agent
orchestration_agent = RefinireAgent(
    name="orchestration_agent", 
    generation_instructions="Provide helpful analysis",
    orchestration_mode=True,
    model="gpt-4o-mini"
)

input_text = "Analyze this data"

# Normal mode returns Context
normal_result = normal_agent.run(input_text)
print(f"Normal result type: {type(normal_result)}")  # <class 'Context'>
print(f"Content: {normal_result.result}")

# Orchestration mode returns dict
orch_result = orchestration_agent.run(input_text)
print(f"Orchestration result type: {type(orch_result)}")  # <class 'dict'>
print(f"Status: {orch_result['status']}")
print(f"Result: {orch_result['result']}")
```

## Structured Output Integration

### Using Pydantic Models with Orchestration

When you specify an `output_model`, the `result` field will contain a typed object:

```python
from pydantic import BaseModel, Field
from refinire import RefinireAgent
from typing import List

class DataAnalysisReport(BaseModel):
    """Structured analysis report"""
    summary: str = Field(description="Executive summary of findings")
    key_findings: List[str] = Field(description="List of important discoveries")
    recommendations: List[str] = Field(description="Actionable recommendations")
    confidence_score: float = Field(description="Confidence in analysis (0-1)")
    data_quality: str = Field(description="Assessment of data quality")

# Agent with structured output
structured_agent = RefinireAgent(
    name="structured_analyst",
    generation_instructions="""
    Analyze the provided data thoroughly and generate a comprehensive report.
    Include key findings, recommendations, and assess data quality.
    """,
    orchestration_mode=True,
    output_model=DataAnalysisReport,  # Result will be typed
    model="gpt-4o-mini"
)

# Run analysis
result = structured_agent.run("Analyze customer feedback data from Q3 2024")

# Access typed result
report = result['result']  # This is a DataAnalysisReport object
print(f"Status: {result['status']}")
print(f"Summary: {report.summary}")
print(f"Key Findings: {report.key_findings}")
print(f"Recommendations: {report.recommendations}")
print(f"Confidence: {report.confidence_score}")
print(f"Data Quality: {report.data_quality}")

# Access orchestration metadata
print(f"Agent Reasoning: {result['reasoning']}")
print(f"Next Recommended Task: {result['next_hint']['task']}")
```

### Mixed Output Types

```python
from pydantic import BaseModel

class TaskResult(BaseModel):
    task_id: str
    completed: bool
    details: str

# Agent that sometimes uses structured output
flexible_agent = RefinireAgent(
    name="flexible_worker",
    generation_instructions="""
    Process the request. For complex tasks, provide structured output.
    For simple tasks, provide string responses.
    """,
    orchestration_mode=True,
    output_model=TaskResult,  # Will be used when appropriate
    model="gpt-4o-mini"
)

# Simple request - result is string
simple_result = flexible_agent.run("What is 2 + 2?")
print(f"Simple result: {simple_result['result']}")  # String: "4"

# Complex request - result is TaskResult object
complex_result = flexible_agent.run("Process customer order #12345")
task = complex_result['result']  # TaskResult object
print(f"Task ID: {task.task_id}")
print(f"Completed: {task.completed}")
```

## Multi-Agent Workflow Coordination

### Orchestration-Based Routing

```python
from refinire import RefinireAgent, Flow, ConditionStep, FunctionStep

# Define orchestration-enabled agents
data_collector = RefinireAgent(
    name="data_collector",
    generation_instructions="""
    Collect and validate the required data for analysis.
    Determine if the data is sufficient for analysis or if more is needed.
    """,
    orchestration_mode=True,
    model="gpt-4o-mini"
)

data_analyzer = RefinireAgent(
    name="data_analyzer",
    generation_instructions="""
    Perform comprehensive data analysis and generate insights.
    Determine if results should go to reporting or need validation first.
    """,
    orchestration_mode=True,
    model="gpt-4o-mini"
)

validator = RefinireAgent(
    name="validator",
    generation_instructions="""
    Validate analysis results for accuracy and completeness.
    Determine if results are ready for reporting or need revision.
    """,
    orchestration_mode=True,
    model="gpt-4o-mini"
)

reporter = RefinireAgent(
    name="reporter",
    generation_instructions="""
    Generate final reports with recommendations.
    Mark the workflow as complete.
    """,
    orchestration_mode=True,
    model="gpt-4o-mini"
)

def orchestration_router(ctx):
    """Route based on agent recommendations"""
    if hasattr(ctx, 'result') and isinstance(ctx.result, dict):
        next_task = ctx.result.get('next_hint', {}).get('task', 'unknown')
        confidence = ctx.result.get('next_hint', {}).get('confidence', 0.0)
        
        # High confidence routing
        if confidence > 0.8:
            if next_task == 'analysis':
                return 'analyze'
            elif next_task == 'validation':
                return 'validate'
            elif next_task == 'reporting':
                return 'report'
        
        # Fallback routing based on status
        if ctx.result.get('status') == 'failed':
            return 'error_handler'
    
    return 'end'

# Create workflow with orchestration routing
workflow = Flow({
    "collect": data_collector,
    "route_after_collect": ConditionStep("route", orchestration_router, "analyze", "end"),
    "analyze": data_analyzer,
    "route_after_analyze": ConditionStep("route", orchestration_router, "validate", "report"),
    "validate": validator,
    "route_after_validate": ConditionStep("route", orchestration_router, "report", "analyze"),
    "report": reporter,
    "error_handler": FunctionStep("error_handler", handle_errors)
})

# Execute workflow
result = await workflow.run("Process customer survey data for Q3 analysis")
```

### Agent Chain with Context Passing

```python
from refinire import RefinireAgent, Context

# Create a chain of orchestration agents
agents = {
    "preprocessor": RefinireAgent(
        name="preprocessor",
        generation_instructions="Clean and prepare data for analysis",
        orchestration_mode=True,
        model="gpt-4o-mini"
    ),
    "analyzer": RefinireAgent(
        name="analyzer", 
        generation_instructions="Analyze preprocessed data and identify patterns",
        orchestration_mode=True,
        model="gpt-4o-mini"
    ),
    "summarizer": RefinireAgent(
        name="summarizer",
        generation_instructions="Create executive summary of analysis",
        orchestration_mode=True,
        model="gpt-4o-mini"
    )
}

def run_agent_chain(input_data, agent_sequence):
    """Execute a sequence of orchestration agents"""
    ctx = Context()
    results = []
    
    for agent_name in agent_sequence:
        agent = agents[agent_name]
        
        # Use previous result as input for next agent
        if results:
            previous_result = results[-1]['result']
            input_text = f"Process this data: {previous_result}"
        else:
            input_text = input_data
        
        # Execute agent
        result = agent.run(input_text, ctx)
        results.append(result)
        
        # Check for failure
        if result['status'] == 'failed':
            print(f"Agent {agent_name} failed: {result['reasoning']}")
            break
        
        # Log progress
        print(f"{agent_name} completed: {result['next_hint']['task']} recommended")
        
        # Update context with result
        ctx.shared_state[f"{agent_name}_result"] = result['result']
    
    return results

# Execute chain
chain_results = run_agent_chain(
    "Raw customer feedback data from Q3 2024",
    ["preprocessor", "analyzer", "summarizer"]
)

# Review results
for i, result in enumerate(chain_results):
    agent_name = ["preprocessor", "analyzer", "summarizer"][i]
    print(f"\n{agent_name.upper()} RESULTS:")
    print(f"Status: {result['status']}")
    print(f"Result: {result['result'][:100]}...")
    print(f"Next recommended: {result['next_hint']['task']}")
```

## Advanced Orchestration Patterns

### Conditional Agent Selection

```python
from refinire import RefinireAgent

class OrchestrationController:
    """Controller for managing orchestration agents"""
    
    def __init__(self):
        self.agents = {
            "simple_analyzer": RefinireAgent(
                name="simple_analyzer",
                generation_instructions="Perform basic data analysis for small datasets",
                orchestration_mode=True,
                model="gpt-4o-mini"
            ),
            "advanced_analyzer": RefinireAgent(
                name="advanced_analyzer",
                generation_instructions="Perform complex analysis for large datasets",
                orchestration_mode=True,
                model="gpt-4o"  # More powerful model
            ),
            "specialist_analyzer": RefinireAgent(
                name="specialist_analyzer",
                generation_instructions="Perform specialized domain analysis",
                orchestration_mode=True,
                model="gpt-4o-mini"
            )
        }
    
    def select_agent(self, task_description, data_size, domain):
        """Select appropriate agent based on task characteristics"""
        if data_size > 1000 and "complex" in task_description.lower():
            return "advanced_analyzer"
        elif domain in ["finance", "medical", "legal"]:
            return "specialist_analyzer"
        else:
            return "simple_analyzer"
    
    def execute_task(self, task_description, data_size=100, domain="general"):
        """Execute task with optimal agent selection"""
        agent_name = self.select_agent(task_description, data_size, domain)
        agent = self.agents[agent_name]
        
        # Execute with metadata
        task_input = f"""
        Task: {task_description}
        Data size: {data_size} records
        Domain: {domain}
        Selected agent: {agent_name}
        """
        
        result = agent.run(task_input)
        
        # Add selection metadata
        result['metadata'] = {
            'selected_agent': agent_name,
            'data_size': data_size,
            'domain': domain
        }
        
        return result

# Usage
controller = OrchestrationController()

# Simple task
simple_result = controller.execute_task(
    "Basic customer satisfaction analysis",
    data_size=50,
    domain="general"
)

# Complex task
complex_result = controller.execute_task(
    "Complex pattern analysis with machine learning insights",
    data_size=5000,
    domain="finance"
)

print(f"Simple task agent: {simple_result['metadata']['selected_agent']}")
print(f"Complex task agent: {complex_result['metadata']['selected_agent']}")
```

### Parallel Orchestration

```python
from refinire import RefinireAgent, Flow
import asyncio

# Create multiple orchestration agents for parallel processing
parallel_agents = [
    RefinireAgent(
        name=f"analyzer_{i}",
        generation_instructions=f"Analyze data segment {i} and provide insights",
        orchestration_mode=True,
        model="gpt-4o-mini"
    )
    for i in range(3)
]

async def parallel_orchestration(data_segments):
    """Execute multiple agents in parallel"""
    tasks = []
    
    for i, (agent, segment) in enumerate(zip(parallel_agents, data_segments)):
        # Create async task for each agent
        task = asyncio.create_task(
            agent.run_async(f"Analyze segment {i}: {segment}")
        )
        tasks.append(task)
    
    # Wait for all agents to complete
    results = await asyncio.gather(*tasks)
    
    # Aggregate results
    successful = [r for r in results if r['status'] == 'completed']
    failed = [r for r in results if r['status'] == 'failed']
    
    return {
        'total_agents': len(results),
        'successful': len(successful),
        'failed': len(failed),
        'results': results,
        'aggregated_insights': [r['result'] for r in successful]
    }

# Execute parallel processing
data_segments = [
    "Customer feedback from Q1",
    "Customer feedback from Q2", 
    "Customer feedback from Q3"
]

parallel_result = await parallel_orchestration(data_segments)
print(f"Completed: {parallel_result['successful']}/{parallel_result['total_agents']} agents")
```

## Error Handling and Recovery

### Robust Error Handling

```python
from refinire import RefinireAgent
import logging

logger = logging.getLogger(__name__)

class RobustOrchestrationAgent:
    """Wrapper for orchestration agent with enhanced error handling"""
    
    def __init__(self, agent_config):
        self.agent = RefinireAgent(**agent_config, orchestration_mode=True)
        self.max_retries = 3
        self.retry_count = 0
    
    def run_with_recovery(self, input_text, recovery_strategies=None):
        """Run agent with automatic error recovery"""
        recovery_strategies = recovery_strategies or [
            "simplify_request",
            "provide_context",
            "reduce_scope"
        ]
        
        for attempt in range(self.max_retries):
            try:
                result = self.agent.run(input_text)
                
                if result['status'] == 'completed':
                    return result
                elif result['status'] == 'failed':
                    logger.warning(f"Agent failed on attempt {attempt + 1}: {result['reasoning']}")
                    
                    # Apply recovery strategy
                    if attempt < len(recovery_strategies):
                        strategy = recovery_strategies[attempt]
                        input_text = self._apply_recovery_strategy(input_text, strategy, result)
                        logger.info(f"Applying recovery strategy: {strategy}")
                
            except Exception as e:
                logger.error(f"Agent execution error on attempt {attempt + 1}: {e}")
                
                if attempt == self.max_retries - 1:
                    return {
                        'status': 'failed',
                        'result': None,
                        'reasoning': f"All {self.max_retries} attempts failed. Last error: {str(e)}",
                        'next_hint': {
                            'task': 'manual_intervention',
                            'confidence': 0.0,
                            'rationale': 'Requires manual review and intervention'
                        }
                    }
        
        return {
            'status': 'failed',
            'result': None,
            'reasoning': f"Max retries ({self.max_retries}) exceeded",
            'next_hint': {
                'task': 'escalate',
                'confidence': 0.0,
                'rationale': 'Escalate to human operator'
            }
        }
    
    def _apply_recovery_strategy(self, input_text, strategy, failed_result):
        """Apply recovery strategy to modify input"""
        if strategy == "simplify_request":
            return f"Simplified request: {input_text[:100]}..."
        elif strategy == "provide_context":
            return f"Please analyze this step by step: {input_text}"
        elif strategy == "reduce_scope":
            return f"Focus on the main aspects of: {input_text}"
        return input_text

# Usage
robust_agent = RobustOrchestrationAgent({
    'name': 'robust_analyzer',
    'generation_instructions': 'Analyze complex data patterns',
    'model': 'gpt-4o-mini'
})

result = robust_agent.run_with_recovery(
    "Analyze extremely complex multi-dimensional data with 47 variables",
    recovery_strategies=["simplify_request", "provide_context", "reduce_scope"]
)

print(f"Final status: {result['status']}")
if result['status'] == 'completed':
    print(f"Analysis: {result['result']}")
else:
    print(f"Failed: {result['reasoning']}")
    print(f"Recommended action: {result['next_hint']['task']}")
```

### Workflow Recovery Patterns

```python
from refinire import RefinireAgent, Flow, FunctionStep

def create_fault_tolerant_workflow():
    """Create workflow with built-in error recovery"""
    
    # Primary agents
    primary_analyzer = RefinireAgent(
        name="primary_analyzer",
        generation_instructions="Perform comprehensive analysis",
        orchestration_mode=True,
        model="gpt-4o"
    )
    
    # Backup agents with simpler instructions
    backup_analyzer = RefinireAgent(
        name="backup_analyzer", 
        generation_instructions="Perform basic analysis as backup",
        orchestration_mode=True,
        model="gpt-4o-mini"
    )
    
    def error_recovery_router(ctx):
        """Route to backup systems on failure"""
        if hasattr(ctx, 'result') and isinstance(ctx.result, dict):
            if ctx.result.get('status') == 'failed':
                return 'backup_analysis'
            elif ctx.result.get('status') == 'completed':
                confidence = ctx.result.get('next_hint', {}).get('confidence', 0.0)
                if confidence < 0.5:  # Low confidence
                    return 'validation'
                else:
                    return 'complete'
        return 'error'
    
    def validation_check(ctx):
        """Validate results and determine next action"""
        # Implementation of validation logic
        return {
            'status': 'completed',
            'result': 'Validation passed',
            'reasoning': 'Results meet quality standards',
            'next_hint': {
                'task': 'finalize',
                'confidence': 0.9,
                'rationale': 'Ready for finalization'
            }
        }
    
    return Flow({
        "primary": primary_analyzer,
        "route": ConditionStep("route", error_recovery_router, "complete", "backup_analysis"),
        "backup_analysis": backup_analyzer,
        "validation": FunctionStep("validation", validation_check),
        "complete": FunctionStep("complete", lambda ctx: "Workflow completed successfully"),
        "error": FunctionStep("error", lambda ctx: "Workflow failed - manual intervention required")
    })

# Execute fault-tolerant workflow
fault_tolerant_flow = create_fault_tolerant_workflow()
result = await fault_tolerant_flow.run("Analyze complex business data")
```

## Best Practices

### 1. Agent Design for Orchestration

```python
# GOOD: Clear, specific instructions with orchestration in mind
good_agent = RefinireAgent(
    name="data_validator",
    generation_instructions="""
    Validate the provided data for completeness and accuracy.
    
    Your task:
    1. Check data completeness (missing values, required fields)
    2. Verify data accuracy (format, ranges, consistency)
    3. Assess data quality score (0-1)
    
    If validation passes (score > 0.8), recommend 'analysis' as next task.
    If validation fails (score < 0.5), recommend 'data_cleanup' as next task.
    If borderline (0.5-0.8), recommend 'manual_review' as next task.
    
    Always explain your validation reasoning clearly.
    """,
    orchestration_mode=True,
    model="gpt-4o-mini"
)

# AVOID: Vague instructions that don't guide orchestration
bad_agent = RefinireAgent(
    name="generic_agent",
    generation_instructions="Do something with the data",
    orchestration_mode=True,
    model="gpt-4o-mini"
)
```

### 2. Confidence Level Guidelines

```python
def interpret_confidence_levels(confidence):
    """Guidelines for interpreting agent confidence levels"""
    if confidence >= 0.9:
        return "High confidence - proceed immediately"
    elif confidence >= 0.7:
        return "Good confidence - proceed with monitoring"
    elif confidence >= 0.5:
        return "Moderate confidence - consider validation"
    elif confidence >= 0.3:
        return "Low confidence - validation recommended"
    else:
        return "Very low confidence - manual review required"

# Use in workflow decisions
def confidence_based_routing(ctx):
    """Route based on agent confidence levels"""
    if hasattr(ctx, 'result') and isinstance(ctx.result, dict):
        confidence = ctx.result.get('next_hint', {}).get('confidence', 0.0)
        
        if confidence >= 0.8:
            return ctx.result['next_hint']['task']  # Follow recommendation
        elif confidence >= 0.5:
            return 'validation'  # Validate first
        else:
            return 'manual_review'  # Human oversight
    
    return 'error'
```

### 3. Structured Logging for Orchestration

```python
import logging
import json

class OrchestrationLogger:
    """Specialized logger for orchestration workflows"""
    
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create structured formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_orchestration_result(self, agent_name, result, execution_time=None):
        """Log orchestration result with structured data"""
        log_data = {
            'agent_name': agent_name,
            'status': result.get('status', 'unknown'),
            'next_task': result.get('next_hint', {}).get('task', 'none'),
            'confidence': result.get('next_hint', {}).get('confidence', 0.0),
            'execution_time': execution_time,
            'result_length': len(str(result.get('result', '')))
        }
        
        if result['status'] == 'completed':
            self.logger.info(f"Agent completed: {json.dumps(log_data)}")
        else:
            log_data['error_reason'] = result.get('reasoning', 'Unknown error')
            self.logger.error(f"Agent failed: {json.dumps(log_data)}")
    
    def log_workflow_progress(self, workflow_name, step_name, total_steps, current_step):
        """Log workflow progress"""
        progress_data = {
            'workflow': workflow_name,
            'step': step_name,
            'progress': f"{current_step}/{total_steps}",
            'completion_percentage': (current_step / total_steps) * 100
        }
        self.logger.info(f"Workflow progress: {json.dumps(progress_data)}")

# Usage
logger = OrchestrationLogger("orchestration_workflow")

# In your workflow
import time
start_time = time.time()
result = agent.run("Analyze data")
execution_time = time.time() - start_time

logger.log_orchestration_result("data_analyzer", result, execution_time)
```

### 4. Testing Orchestration Agents

```python
import pytest
from refinire import RefinireAgent

class TestOrchestrationAgent:
    """Test suite for orchestration agents"""
    
    def setup_method(self):
        """Set up test agent"""
        self.agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Analyze test data and provide results",
            orchestration_mode=True,
            model="gpt-4o-mini"
        )
    
    def test_successful_execution(self):
        """Test successful agent execution"""
        result = self.agent.run("Test data for analysis")
        
        # Verify orchestration structure
        assert isinstance(result, dict)
        assert 'status' in result
        assert 'result' in result
        assert 'reasoning' in result
        assert 'next_hint' in result
        
        # Verify status
        assert result['status'] in ['completed', 'failed']
        
        # Verify next_hint structure
        next_hint = result['next_hint']
        assert 'task' in next_hint
        assert 'confidence' in next_hint
        assert 0.0 <= next_hint['confidence'] <= 1.0
    
    def test_with_structured_output(self):
        """Test orchestration with Pydantic models"""
        from pydantic import BaseModel
        
        class TestOutput(BaseModel):
            summary: str
            score: float
        
        structured_agent = RefinireAgent(
            name="structured_test_agent",
            generation_instructions="Generate structured test output",
            orchestration_mode=True,
            output_model=TestOutput,
            model="gpt-4o-mini"
        )
        
        result = structured_agent.run("Generate test report")
        
        # Verify structured result
        if result['status'] == 'completed':
            assert isinstance(result['result'], TestOutput)
            assert hasattr(result['result'], 'summary')
            assert hasattr(result['result'], 'score')
    
    def test_error_handling(self):
        """Test error handling in orchestration mode"""
        # This would require mocking to simulate failures
        # Implementation depends on your testing framework
        pass

# Run tests
if __name__ == "__main__":
    pytest.main([__file__])
```

## Summary

Orchestration mode transforms RefinireAgent from a simple text generator into a coordinated member of complex multi-agent systems. Key takeaways:

1. **Enable with `orchestration_mode=True`** for structured JSON output
2. **Combine with `output_model`** for type-safe results
3. **Use `next_hint`** for intelligent workflow routing
4. **Monitor `confidence` levels** for quality control
5. **Implement error recovery** with robust handling patterns
6. **Design clear instructions** that guide orchestration decisions
7. **Log structured data** for monitoring and debugging

Orchestration mode enables you to build sophisticated AI workflows where agents communicate their status, results, and recommendations in a standardized format, making complex multi-agent coordination reliable and maintainable.

For more advanced patterns, see:
- [Flow Complete Guide](flow_complete_guide_en.md) - Building complex workflows
- [Context Management](context_management.md) - Sharing data between agents
- [Advanced Features](advanced.md) - Additional RefinireAgent capabilities