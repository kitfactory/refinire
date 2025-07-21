#!/usr/bin/env python3
"""
Test Custom Client - Test if custom OpenAI client with timeout works
カスタムクライアントテスト - タイムアウト付きカスタムOpenAIクライアントが機能するかテスト

This tests if creating a custom OpenAI client with timeout works.
タイムアウト付きカスタムOpenAIクライアントの作成が機能するかテストします。
"""

import os
import asyncio
import httpx


async def test_custom_client():
    """
    Test custom OpenAI client with timeout
    タイムアウト付きカスタムOpenAIクライアントをテスト
    """
    print("🔍 Testing Custom OpenAI Client with Timeout")
    print("=" * 50)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        return
    
    # Test 1: Custom OpenAI client with timeout
    print("\n📋 Test 1: Custom OpenAI Client")
    try:
        from openai import AsyncOpenAI
        from agents import Agent, Runner, RunConfig
        from agents.models.openai_provider import OpenAIProvider
        
        # Create custom client with 120 second timeout
        custom_client = AsyncOpenAI(
            timeout=httpx.Timeout(timeout=120.0)
        )
        
        print(f"   Custom client timeout: {custom_client.timeout}")
        
        # Create custom provider
        custom_provider = OpenAIProvider(openai_client=custom_client)
        
        # Create agent
        agent = Agent(
            name="custom_client_test",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        
        # Create RunConfig with custom provider
        run_config = RunConfig(model_provider=custom_provider)
        
        print("   🚀 Running with custom client...")
        result = await Runner.run(agent, "Hi", run_config=run_config)
        print(f"   ✅ Success: {result.final_output}")
        
    except Exception as e:
        print(f"   ❌ Custom client test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Check if the custom client is actually used
    print("\n📋 Test 2: Verify Client Usage")
    try:
        from openai import AsyncOpenAI
        from agents import Agent, Runner, RunConfig
        from agents.models.openai_provider import OpenAIProvider
        
        # Create custom client with timeout
        custom_client = AsyncOpenAI(
            timeout=httpx.Timeout(timeout=120.0)
        )
        
        # Create custom provider
        custom_provider = OpenAIProvider(openai_client=custom_client)
        
        # Get model from provider
        model = custom_provider.get_model("gpt-4o-mini")
        print(f"   Model type: {type(model)}")
        
        # Check if model uses our custom client
        if hasattr(model, '_client'):
            client = model._client
            print(f"   Model client: {type(client)}")
            print(f"   Model client timeout: {client.timeout}")
            print(f"   Same client: {client is custom_client}")
        
        # Test with agent
        agent = Agent(
            name="verify_test",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        
        run_config = RunConfig(model_provider=custom_provider)
        result = await Runner.run(agent, "Hi", run_config=run_config)
        print(f"   ✅ Verification success: {result.final_output}")
        
    except Exception as e:
        print(f"   ❌ Verification test failed: {e}")
    
    # Test 3: Compare default vs custom timeouts
    print("\n📋 Test 3: Timeout Comparison")
    try:
        from openai import AsyncOpenAI
        
        # Default client
        default_client = AsyncOpenAI()
        print(f"   Default client timeout: {default_client.timeout}")
        
        # Custom client with 120s timeout
        custom_client = AsyncOpenAI(timeout=httpx.Timeout(timeout=120.0))
        print(f"   Custom client timeout: {custom_client.timeout}")
        
        # Custom client with 30s timeout (to test if this is the issue)
        short_timeout_client = AsyncOpenAI(timeout=httpx.Timeout(timeout=30.0))
        print(f"   Short timeout client: {short_timeout_client.timeout}")
        
    except Exception as e:
        print(f"   ❌ Timeout comparison failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_custom_client())