"""
Example: Using oneenv for OpenTelemetry tracing configuration

This example demonstrates how to use oneenv templates to manage
OpenTelemetry tracing environment variables for Refinire.

Prerequisites:
    pip install refinire[openinference-instrumentation]
    pip install oneenv

English: Shows how to use oneenv templates for tracing configuration.
日本語: トレーシング設定にoneenvテンプレートを使用する方法を示します。
"""

import asyncio
import os
from refinire import (
    RefinireAgent,
    enable_opentelemetry_tracing,
    disable_opentelemetry_tracing,
    is_openinference_available
)


def setup_oneenv_tracing_demo():
    """
    Demonstrate oneenv template usage for tracing configuration
    """
    print("=== OneEnv Tracing Configuration Demo ===\n")
    
    print("1. Install oneenv and refinire:")
    print("   pip install oneenv refinire[openinference-instrumentation]\n")
    
    print("2. Initialize oneenv with Refinire tracing template:")
    print("   oneenv init --template refinire.tracing\n")
    
    print("3. This creates a .env file with these variables:")
    print("   REFINIRE_TRACE_OTLP_ENDPOINT=")
    print("   REFINIRE_TRACE_SERVICE_NAME=refinire-agent")
    print("   REFINIRE_TRACE_RESOURCE_ATTRIBUTES=\n")
    
    print("4. Configure your tracing settings:")
    print("   REFINIRE_TRACE_OTLP_ENDPOINT=http://localhost:4317")
    print("   REFINIRE_TRACE_SERVICE_NAME=my-application")
    print("   REFINIRE_TRACE_RESOURCE_ATTRIBUTES=environment=production,team=ai\n")
    
    print("5. Use in your application:")
    print("   from oneenv import load_env")
    print("   load_env()  # Loads .env file automatically\n")
    
    # Demonstrate programmatic setup
    print("=== Programmatic Configuration Demo ===\n")
    
    # Simulate oneenv loading environment variables
    os.environ["REFINIRE_TRACE_OTLP_ENDPOINT"] = "http://localhost:4317"
    os.environ["REFINIRE_TRACE_SERVICE_NAME"] = "oneenv-demo-app"
    os.environ["REFINIRE_TRACE_RESOURCE_ATTRIBUTES"] = "environment=development,tool=oneenv,demo=true"
    
    print("Environment variables loaded:")
    print(f"  REFINIRE_TRACE_OTLP_ENDPOINT: {os.getenv('REFINIRE_TRACE_OTLP_ENDPOINT')}")
    print(f"  REFINIRE_TRACE_SERVICE_NAME: {os.getenv('REFINIRE_TRACE_SERVICE_NAME')}")
    print(f"  REFINIRE_TRACE_RESOURCE_ATTRIBUTES: {os.getenv('REFINIRE_TRACE_RESOURCE_ATTRIBUTES')}")


async def oneenv_tracing_example():
    """
    Example using environment variables configured via oneenv
    """
    print("\n=== OneEnv + Refinire Tracing Example ===\n")
    
    if not is_openinference_available():
        print("❌ OpenInference instrumentation not available.")
        print("Install with: pip install refinire[openinference-instrumentation]")
        return
    
    # In a real application, you would use:
    # from oneenv import load_env
    # load_env()
    
    # Environment variables would be loaded by oneenv in real usage
    # Here we simulate having them set
    if not os.getenv("REFINIRE_TRACE_OTLP_ENDPOINT"):
        print("⚠️  No tracing endpoint configured")
        print("Use 'oneenv init --template refinire.tracing' to set up configuration")
        print("Then add 'from oneenv import load_env; load_env()' to your code")
        return
    
    # Enable tracing - will use environment variables automatically
    success = enable_opentelemetry_tracing(
        console_output=True  # Enable console output for demo
    )
    
    if not success:
        print("❌ Failed to enable OpenTelemetry tracing")
        return
    
    print("✅ OpenTelemetry tracing enabled using oneenv configuration")
    
    # Create agent
    agent = RefinireAgent(
        name="oneenv_agent",
        generation_instructions="You are a helpful assistant demonstrating oneenv integration.",
        model="gpt-4o-mini"
    )
    
    # Run traced operation
    from refinire.agents.flow import Context
    ctx = Context()
    
    result = await agent.run_async(
        "Explain the benefits of using environment variable management tools like oneenv.",
        ctx
    )
    
    print(f"\n📝 Agent response: {str(result.result)[:200]}...")
    print("\n✅ Trace sent using oneenv-configured settings!")
    
    # Clean up
    disable_opentelemetry_tracing()


def show_template_info():
    """
    Show information about available oneenv templates
    """
    print("\n=== Refinire OneEnv Templates ===\n")
    
    print("Available templates:")
    print("📦 refinire.core     - Core LLM provider configuration")
    print("📊 refinire.tracing  - OpenTelemetry tracing configuration")
    print("🤖 refinire.agents   - Agent-specific settings")
    print("🔧 refinire.development - Development environment settings\n")
    
    print("Usage:")
    print("  oneenv init --template refinire.tracing")
    print("  # Edit .env file with your settings")
    print("  # In your Python code: from oneenv import load_env; load_env()")
    print("  python your_app.py\n")
    
    print("Template variables (refinire.tracing):")
    print("  REFINIRE_TRACE_OTLP_ENDPOINT - OTLP endpoint for trace export")
    print("  REFINIRE_TRACE_SERVICE_NAME - Service name for traces")
    print("  REFINIRE_TRACE_RESOURCE_ATTRIBUTES - Additional resource attributes")


async def main():
    """
    Main function demonstrating oneenv integration
    """
    # Show template information
    show_template_info()
    
    # Setup demo
    setup_oneenv_tracing_demo()
    
    # Run example if tracing is available
    if is_openinference_available():
        await oneenv_tracing_example()
    else:
        print("\n⚠️  Skipping tracing example - OpenInference not available")
        print("Install with: pip install refinire[openinference-instrumentation]")
    
    # Clean up demo environment variables
    for key in ["REFINIRE_TRACE_OTLP_ENDPOINT", "REFINIRE_TRACE_SERVICE_NAME", "REFINIRE_TRACE_RESOURCE_ATTRIBUTES"]:
        if key in os.environ:
            del os.environ[key]


if __name__ == "__main__":
    asyncio.run(main())