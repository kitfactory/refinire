"""
Example: Grafana Tempo Tracing with Refinire

This example demonstrates how to send OpenTelemetry traces from Refinire agents
to a Grafana Tempo server for advanced observability and monitoring.

Prerequisites:
    pip install refinire[openinference-instrumentation]

Grafana Tempo Setup:
    - Ensure Grafana Tempo is running on 192.168.11.15:4317
    - Or update the OTLP endpoint to your Tempo server

English: Shows how to configure Refinire for Grafana Tempo tracing integration.
日本語: RefinireとGrafana Tempoトレーシング統合の設定方法を示します。
"""

import asyncio
import os
import logging
from refinire import (
    RefinireAgent,
    enable_opentelemetry_tracing,
    disable_opentelemetry_tracing,
    is_openinference_available,
    is_opentelemetry_enabled,
    get_tracer
)

# Configure logging to see OpenTelemetry info
logging.basicConfig(level=logging.INFO)


async def basic_tempo_tracing_example():
    """
    Basic example of sending traces to Grafana Tempo
    """
    print("=== Grafana Tempo Tracing Example ===\n")
    
    # Check if OpenInference is available
    if not is_openinference_available():
        print("❌ OpenInference instrumentation not available.")
        print("Install with: pip install refinire[openinference-instrumentation]")
        return
    
    # Configure Grafana Tempo endpoint
    # Using localhost for WSL to Windows access
    tempo_endpoint = "http://localhost:4317"
    
    # Enable OpenTelemetry tracing with Tempo export
    success = enable_opentelemetry_tracing(
        service_name="refinire-tempo-demo",
        service_version="1.0.0",
        otlp_endpoint=tempo_endpoint,
        console_output=True,  # Also output to console for debugging
        resource_attributes={
            "environment": "development",
            "team": "ai-research",
            "demo.type": "grafana-tempo"
        }
    )
    
    if not success:
        print("❌ Failed to enable OpenTelemetry tracing")
        return
    
    print(f"✅ OpenTelemetry tracing enabled with Tempo endpoint: {tempo_endpoint}")
    
    # Create agent that will be traced
    agent = RefinireAgent(
        name="tempo_traced_agent",
        generation_instructions="""
        You are a knowledgeable AI assistant specializing in cloud infrastructure and observability.
        Provide detailed, technical responses with practical examples.
        """,
        model="gpt-4o-mini"
    )
    
    # Run some operations that will be traced and sent to Tempo
    print("\n--- Running operations (traces sent to Grafana Tempo) ---")
    
    from refinire.agents.flow import Context
    ctx = Context()
    
    queries = [
        "What are the benefits of using Grafana for observability?",
        "How does distributed tracing help in microservices debugging?",
        "Explain the role of Tempo in the Grafana observability stack.",
        "What are best practices for OpenTelemetry instrumentation?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        result = await agent.run_async(query, ctx)
        print(f"📝 Response length: {len(str(result.result))} characters")
        print(f"📊 First 100 chars: {str(result.result)[:100]}...")
    
    print(f"\n✅ All traces sent to Grafana Tempo at {tempo_endpoint}")
    print("🔗 Check your Grafana Tempo UI to view the traces!")
    
    # Disable tracing
    disable_opentelemetry_tracing()
    print(f"\n✅ OpenTelemetry tracing disabled")


async def advanced_tempo_workflow_example():
    """
    Advanced example with custom spans and workflow tracing
    """
    print("\n=== Advanced Grafana Tempo Workflow Example ===\n")
    
    if not is_openinference_available():
        print("❌ OpenInference instrumentation not available.")
        return
    
    # Enable tracing with environment-specific configuration
    enable_opentelemetry_tracing(
        service_name="refinire-advanced-workflow",
        otlp_endpoint="http://localhost:4317",
        console_output=False,  # Only send to Tempo, no console output
        resource_attributes={
            "environment": "development",
            "workflow.type": "multi-agent-pipeline",
            "infrastructure.region": "local"
        }
    )
    
    # Get tracer for custom spans
    tracer = get_tracer("advanced-workflow-tracer")
    
    if not tracer:
        print("❌ Failed to get tracer")
        return
    
    print("✅ Advanced tracing enabled - traces sent to Tempo only")
    
    # Create specialized agents for workflow
    analyzer_agent = RefinireAgent(
        name="infrastructure_analyzer",
        generation_instructions="""
        You are an infrastructure analysis expert. Analyze technical questions
        and categorize them as: monitoring, alerting, deployment, or general.
        Respond with just the category.
        """,
        model="gpt-4o-mini"
    )
    
    monitoring_expert = RefinireAgent(
        name="monitoring_expert",
        generation_instructions="""
        You are a monitoring and observability expert. Provide detailed
        technical guidance on monitoring, metrics, and alerting solutions.
        """,
        model="gpt-4o-mini"
    )
    
    deployment_expert = RefinireAgent(
        name="deployment_expert", 
        generation_instructions="""
        You are a deployment and CI/CD expert. Provide guidance on
        deployment strategies, automation, and infrastructure as code.
        """,
        model="gpt-4o-mini"
    )
    
    # Run workflow with custom tracing
    with tracer.start_as_current_span("infrastructure-consultation-workflow") as workflow_span:
        workflow_span.set_attribute("workflow.name", "infrastructure-consultation")
        workflow_span.set_attribute("workflow.version", "v2.0")
        
        user_questions = [
            "How should we set up monitoring for our Kubernetes cluster?",
            "What's the best way to implement blue-green deployments?",
            "How can we improve our alerting strategy for microservices?"
        ]
        
        from refinire.agents.flow import Context
        
        for i, question in enumerate(user_questions, 1):
            with tracer.start_as_current_span(f"question-{i}-processing") as question_span:
                question_span.set_attribute("question.text", question)
                question_span.set_attribute("question.index", i)
                
                ctx = Context()
                
                # Step 1: Analyze question type
                with tracer.start_as_current_span("analysis-phase") as analysis_span:
                    analysis_result = await analyzer_agent.run_async(question, ctx)
                    category = str(analysis_result.result).lower().strip()
                    analysis_span.set_attribute("analysis.category", category)
                    question_span.set_attribute("question.category", category)
                
                # Step 2: Route to appropriate expert
                if "monitoring" in category or "alerting" in category:
                    with tracer.start_as_current_span("monitoring-expert-response") as expert_span:
                        expert_result = await monitoring_expert.run_async(question, ctx)
                        expert_span.set_attribute("expert.type", "monitoring")
                        expert_span.set_attribute("response.length", len(str(expert_result.result)))
                        question_span.set_attribute("expert.assigned", "monitoring")
                elif "deployment" in category:
                    with tracer.start_as_current_span("deployment-expert-response") as expert_span:
                        expert_result = await deployment_expert.run_async(question, ctx)
                        expert_span.set_attribute("expert.type", "deployment")
                        expert_span.set_attribute("response.length", len(str(expert_result.result)))
                        question_span.set_attribute("expert.assigned", "deployment")
                else:
                    with tracer.start_as_current_span("general-response") as expert_span:
                        expert_result = await monitoring_expert.run_async(question, ctx)
                        expert_span.set_attribute("expert.type", "general")
                        expert_span.set_attribute("response.length", len(str(expert_result.result)))
                        question_span.set_attribute("expert.assigned", "general")
                
                question_span.set_attribute("processing.status", "completed")
                print(f"✅ Question {i} processed and traced")
        
        workflow_span.set_attribute("workflow.questions_processed", len(user_questions))
        workflow_span.set_attribute("workflow.status", "completed")
    
    print(f"\n🚀 Advanced workflow completed - all traces sent to Grafana Tempo")
    print("📊 Check Tempo UI for detailed span hierarchy and timing information")
    
    disable_opentelemetry_tracing()


async def environment_variable_example():
    """
    Example using environment variables for configuration
    """
    print("\n=== Environment Variable Configuration Example ===\n")
    
    # Set environment variables programmatically for demo
    # In practice, these would be set in your shell or deployment environment
    os.environ["REFINIRE_TRACE_OTLP_ENDPOINT"] = "http://localhost:4317"
    os.environ["REFINIRE_TRACE_SERVICE_NAME"] = "refinire-env-demo"
    os.environ["REFINIRE_TRACE_RESOURCE_ATTRIBUTES"] = "environment=staging,team=devops,region=local"
    
    print("Environment variables set:")
    print(f"  REFINIRE_TRACE_OTLP_ENDPOINT: {os.getenv('REFINIRE_TRACE_OTLP_ENDPOINT')}")
    print(f"  REFINIRE_TRACE_SERVICE_NAME: {os.getenv('REFINIRE_TRACE_SERVICE_NAME')}")
    print(f"  REFINIRE_TRACE_RESOURCE_ATTRIBUTES: {os.getenv('REFINIRE_TRACE_RESOURCE_ATTRIBUTES')}")
    
    if not is_openinference_available():
        print("❌ OpenInference instrumentation not available.")
        return
    
    # Enable tracing - configuration will be read from environment variables
    success = enable_opentelemetry_tracing(
        console_output=True  # Still enable console for demo
    )
    
    if not success:
        print("❌ Failed to enable OpenTelemetry tracing")
        return
    
    print("\n✅ Tracing enabled using environment variable configuration")
    
    # Create and run agent
    agent = RefinireAgent(
        name="env_configured_agent",
        generation_instructions="You are a helpful assistant demonstrating environment-based configuration.",
        model="gpt-4o-mini"
    )
    
    from refinire.agents.flow import Context
    ctx = Context()
    
    result = await agent.run_async(
        "Explain the advantages of using environment variables for configuration in containerized applications.",
        ctx
    )
    
    print(f"✅ Traced response: {str(result.result)[:150]}...")
    print("\n🔗 Trace sent to Grafana Tempo with environment-based configuration!")
    
    # Clean up environment variables
    del os.environ["REFINIRE_TRACE_OTLP_ENDPOINT"]
    del os.environ["REFINIRE_TRACE_SERVICE_NAME"] 
    del os.environ["REFINIRE_TRACE_RESOURCE_ATTRIBUTES"]
    
    disable_opentelemetry_tracing()


def check_tempo_connectivity():
    """
    Check if Grafana Tempo endpoint is accessible
    """
    print("=== Grafana Tempo Connectivity Check ===\n")
    
    import socket
    
    tempo_host = "localhost"
    tempo_port = 4317
    
    try:
        # Test TCP connection to Tempo OTLP gRPC endpoint
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((tempo_host, tempo_port))
        sock.close()
        
        if result == 0:
            print(f"✅ Successfully connected to Grafana Tempo at {tempo_host}:{tempo_port}")
            print("🚀 Ready to send traces!")
            return True
        else:
            print(f"❌ Cannot connect to Grafana Tempo at {tempo_host}:{tempo_port}")
            print("📋 Please ensure:")
            print("   - Grafana Tempo is running")
            print("   - OTLP gRPC receiver is enabled on port 4317")
            print("   - Network connectivity is available")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


async def main():
    """
    Main function to run all Grafana Tempo examples
    """
    # Check Tempo connectivity first
    tempo_available = check_tempo_connectivity()
    
    if not tempo_available:
        print("\n⚠️  Tempo connectivity issues detected")
        print("Examples will still run but traces may not reach Tempo server")
        print("Update the endpoint in the examples if your Tempo is on a different host/port")
    
    print(f"\nOpenInference available: {is_openinference_available()}")
    
    if is_openinference_available():
        # Run examples
        await basic_tempo_tracing_example()
        await advanced_tempo_workflow_example()
        await environment_variable_example()
        
        print("\n🎉 All Grafana Tempo tracing examples completed!")
        print("📊 Check your Grafana Tempo UI to explore the traces")
        print("🔍 Look for services: refinire-tempo-demo, refinire-advanced-workflow, refinire-env-demo")
        
    else:
        print("\n⚠️  Skipping examples - OpenInference not available")
        print("Install with: pip install refinire[openinference-instrumentation]")


if __name__ == "__main__":
    asyncio.run(main())