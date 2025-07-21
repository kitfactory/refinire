#!/usr/bin/env python3
"""
Debug Timeout Configuration - OpenAI Agents SDK Timeout Analysis
タイムアウト設定デバッグ - OpenAI Agents SDKタイムアウト分析

This investigates how to properly set timeout in OpenAI Agents SDK.
OpenAI Agents SDKでのタイムアウト設定方法を調査します。
"""

import os
import asyncio
from agents import Agent, Runner, RunConfig, ModelSettings


async def test_timeout_configurations():
    """
    Test various timeout configuration methods
    様々なタイムアウト設定方法をテスト
    """
    print("🔍 Testing OpenAI Agents SDK Timeout Configurations")
    print("=" * 60)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        return
    
    # Test 1: Basic ModelSettings without extra_args
    print("\n📋 Test 1: Basic ModelSettings")
    try:
        agent = Agent(
            name="timeout_test_1",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        
        model_settings = ModelSettings(max_tokens=50)  # Use a valid parameter
        run_config = RunConfig(model_settings=model_settings)
        
        print("✅ Agent and RunConfig created successfully")
        print(f"   - ModelSettings created with max_tokens: {model_settings.max_tokens}")
        
        # Try very short message to test quickly
        result = await Runner.run(agent, "Hi", run_config=run_config)
        print(f"✅ Success: {result.final_output[:50]}...")
        
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
    
    # Test 2: Try different timeout parameter names
    print("\n📋 Test 2: Different timeout parameter names")
    timeout_params = [
        {"request_timeout": 120},
        {"timeout": 120}, 
        {"read_timeout": 120},
        {"connect_timeout": 120},
        {"total_timeout": 120}
    ]
    
    for i, params in enumerate(timeout_params):
        try:
            print(f"   Testing params: {params}")
            model_settings = ModelSettings(extra_args=params)
            run_config = RunConfig(model_settings=model_settings)
            
            agent = Agent(
                name=f"timeout_test_2_{i}",
                instructions="You are a helpful assistant.",
                model="gpt-4o-mini"
            )
            
            result = await Runner.run(agent, "Say hello quickly", run_config=run_config)
            print(f"   ✅ Success with {params}: {result.final_output[:30]}...")
            break  # If one works, we found it
            
        except Exception as e:
            print(f"   ❌ Failed with {params}: {e}")
    
    # Test 3: Check OpenAI client configuration
    print("\n📋 Test 3: OpenAI Client Investigation")
    try:
        from refinire.core.llm import get_llm
        model = get_llm(provider='openai', model='gpt-4o-mini')
        
        print(f"   - Model type: {type(model)}")
        print(f"   - Model attributes: {[attr for attr in dir(model) if not attr.startswith('_')]}")
        
        # Try to access internal OpenAI client
        if hasattr(model, 'openai_client'):
            client = model.openai_client
            print(f"   - Client type: {type(client)}")
            print(f"   - Client timeout: {getattr(client, 'timeout', 'Not found')}")
            if hasattr(client, '_client'):
                print(f"   - Internal client: {type(client._client)}")
                inner_client = client._client
                if hasattr(inner_client, 'timeout'):
                    print(f"   - Inner client timeout: {inner_client.timeout}")
        
    except Exception as e:
        print(f"   ❌ Client investigation failed: {e}")
    
    # Test 4: Check if the issue is network-specific
    print("\n📋 Test 4: Network connectivity test")
    try:
        import httpx
        
        # Test direct HTTP request to OpenAI
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get("https://api.openai.com/v1/models", 
                                      headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"})
            print(f"   ✅ Direct OpenAI API access: Status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Direct API test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_timeout_configurations())