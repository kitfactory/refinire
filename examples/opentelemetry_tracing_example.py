"""
Example: OpenTelemetry Tracing with Refinire

This example demonstrates how to use OpenTelemetry tracing with Refinire agents
when openinference-instrumentation is installed.

Prerequisites:
    pip install refinire[openinference-instrumentation]

English: Shows how to enable OpenTelemetry tracing for comprehensive observability.
日本語: 包括的な可観測性のためのOpenTelemetryトレーシングの有効化方法を示します。
"""

import asyncio
from refinire import (
    RefinireAgent, 
    enable_opentelemetry_tracing, 
    disable_opentelemetry_tracing,
    is_openinference_available,
    is_opentelemetry_enabled,
    get_tracer
)


async def basic_opentelemetry_example():
    """
    Basic example of OpenTelemetry tracing with console output
    """
    print("=== Basic OpenTelemetry Tracing Example ===\n")
    
    # Check if OpenInference is available
    if not is_openinference_available():
        print("❌ OpenInference instrumentation not available.")
        print("Install with: pip install refinire[openinference-instrumentation]")
        return
    
    # Enable OpenTelemetry tracing with console output
    success = enable_opentelemetry_tracing(
        service_name="basic-example",
        console_output=True
    )
    
    if not success:
        print("❌ Failed to enable OpenTelemetry tracing")
        return
    
    print(f"✅ OpenTelemetry tracing enabled: {is_opentelemetry_enabled()}")
    
    # Create agent that will be traced
    agent = RefinireAgent(
        name="traced_agent",
        generation_instructions="You are a helpful assistant. Provide concise answers.",
        model="gpt-4o-mini"
    )
    
    # Run some operations that will be traced
    print("\n--- Running traced operations ---")
    
    from refinire.agents.flow import Context
    ctx = Context()
    
    result1 = await agent.run_async("What is the capital of Japan?", ctx)
    print(f"Result 1: {result1.result}")
    
    result2 = await agent.run_async("Explain quantum computing in one sentence.", ctx)
    print(f"Result 2: {result2.result}")
    
    # Disable tracing
    disable_opentelemetry_tracing()
    print(f"\n✅ OpenTelemetry tracing disabled: {not is_opentelemetry_enabled()}")


async def advanced_opentelemetry_example():
    """
    Advanced example with OTLP export and custom spans
    """
    print("\n=== Advanced OpenTelemetry Tracing Example ===\n")
    
    if not is_openinference_available():
        print("❌ OpenInference instrumentation not available.")
        return
    
    # Enable with custom configuration
    success = enable_opentelemetry_tracing(
        service_name="advanced-refinire-agent",
        service_version="1.0.0",
        # otlp_endpoint="http://localhost:4317",  # Uncomment for OTLP export
        console_output=True,
        resource_attributes={
            "environment": "development",
            "team": "ai-research",
            "project": "refinire-demo"
        }
    )
    
    if not success:
        print("❌ Failed to enable OpenTelemetry tracing")
        return
    
    print("✅ Advanced OpenTelemetry tracing enabled")
    
    # Get tracer for manual span creation
    tracer = get_tracer("example-tracer")
    
    if tracer:
        # Create custom span
        with tracer.start_as_current_span("custom-workflow") as span:
            span.set_attribute("workflow.type", "agent-pipeline")
            span.set_attribute("workflow.complexity", "advanced")
            
            # Create agent with evaluation
            agent = RefinireAgent(
                name="advanced_agent",
                generation_instructions="""
                You are an expert AI assistant. Analyze the input and provide detailed,
                well-structured responses with examples when appropriate.
                """,
                evaluation_instructions="""
                Evaluate the response on:
                1. Accuracy (0-100)
                2. Completeness (0-100) 
                3. Clarity (0-100)
                Provide overall score as average.
                """,
                threshold=75.0,
                model="gpt-4o-mini"
            )
            
            # Add span annotation
            span.add_event("agent-created", {"agent.name": "advanced_agent"})
            
            # Create context for agents
            from refinire.agents.flow import Context
            ctx = Context()
            
            # Run traced operations
            result1 = await agent.run_async(
                "Explain the benefits and challenges of microservices architecture.", ctx
            )
            span.add_event("first-query-completed", {
                "query.type": "architecture-explanation",
                "result.length": len(str(result1.result))
            })
            
            result2 = await agent.run_async(
                "What are the key considerations for implementing observability in distributed systems?", ctx
            )
            span.add_event("second-query-completed", {
                "query.type": "observability-question", 
                "result.length": len(str(result2.result))
            })
            
            print(f"First result evaluation: {result1.evaluation_result}")
            print(f"Second result evaluation: {result2.evaluation_result}")
            
            # Mark workflow completion
            span.set_attribute("workflow.status", "completed")
            span.add_event("workflow-finished")
    
    print("\n✅ Advanced workflow with custom spans completed")
    
    # Disable tracing
    disable_opentelemetry_tracing()


async def multi_agent_tracing_example():
    """
    Example with multiple agents and complex workflow tracing
    """
    print("\n=== Multi-Agent Tracing Example ===\n")
    
    if not is_openinference_available():
        print("❌ OpenInference instrumentation not available.")
        return
    
    # Enable tracing
    enable_opentelemetry_tracing(
        service_name="multi-agent-system",
        console_output=True,
        resource_attributes={
            "system.type": "multi-agent",
            "agents.count": "3"
        }
    )
    
    # Create specialized agents
    analyzer = RefinireAgent(
        name="content_analyzer",
        generation_instructions="Analyze the input and categorize it as: technical, business, or general.",
        model="gpt-4o-mini"
    )
    
    technical_expert = RefinireAgent(
        name="technical_expert", 
        generation_instructions="Provide detailed technical explanations with examples and best practices.",
        model="gpt-4o-mini"
    )
    
    business_expert = RefinireAgent(
        name="business_expert",
        generation_instructions="Provide business-focused analysis with ROI and strategic considerations.", 
        model="gpt-4o-mini"
    )
    
    tracer = get_tracer("multi-agent-tracer")
    
    if tracer:
        with tracer.start_as_current_span("multi-agent-pipeline") as span:
            user_query = "How should we implement CI/CD pipelines for our development team?"
            span.set_attribute("user.query", user_query)
            
            # Create context for agents
            from refinire.agents.flow import Context
            ctx = Context()
            
            # Step 1: Analyze content type
            with tracer.start_as_current_span("content-analysis") as analysis_span:
                analysis_result = await analyzer.run_async(user_query, ctx)
                analysis_span.set_attribute("analysis.result", str(analysis_result.result))
                print(f"Analysis: {analysis_result.result}")
            
            # Step 2: Route to appropriate expert
            if "technical" in str(analysis_result.result).lower():
                with tracer.start_as_current_span("technical-response") as tech_span:
                    expert_result = await technical_expert.run_async(user_query, ctx)
                    tech_span.set_attribute("expert.type", "technical")
                    tech_span.set_attribute("response.length", len(str(expert_result.result)))
                    print(f"Technical Expert Response: {str(expert_result.result)[:200]}...")
            else:
                with tracer.start_as_current_span("business-response") as biz_span:
                    expert_result = await business_expert.run_async(user_query, ctx)
                    biz_span.set_attribute("expert.type", "business")
                    biz_span.set_attribute("response.length", len(str(expert_result.result)))
                    print(f"Business Expert Response: {str(expert_result.result)[:200]}...")
            
            span.set_attribute("pipeline.status", "completed")
    
    print("\n✅ Multi-agent pipeline with tracing completed")
    
    # Disable tracing
    disable_opentelemetry_tracing()


def check_openinference_status():
    """
    Check if OpenInference instrumentation is available and provide setup instructions
    """
    print("=== OpenInference Availability Check ===\n")
    
    available = is_openinference_available()
    print(f"OpenInference available: {available}")
    
    if available:
        print("✅ OpenInference instrumentation is installed and ready to use!")
        print("\nAvailable functions:")
        print("- enable_opentelemetry_tracing()")
        print("- disable_opentelemetry_tracing()")
        print("- is_opentelemetry_enabled()")
        print("- get_tracer()")
    else:
        print("❌ OpenInference instrumentation not available")
        print("\nTo install:")
        print("pip install refinire[openinference-instrumentation]")
        print("\nOr install manually:")
        print("pip install openinference-instrumentation openinference-instrumentation-openai")


async def main():
    """
    Main function to run all examples
    """
    # Check availability first
    check_openinference_status()
    
    if is_openinference_available():
        # Run examples
        await basic_opentelemetry_example()
        await advanced_opentelemetry_example() 
        await multi_agent_tracing_example()
    else:
        print("\n⚠️  Skipping examples - OpenInference not available")
        print("Install with: pip install refinire[openinference-instrumentation]")


if __name__ == "__main__":
    asyncio.run(main())