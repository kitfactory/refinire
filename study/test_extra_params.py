#!/usr/bin/env python3
"""
Test Extra Parameters for Timeout - Using ModelSettings extra_* parameters
タイムアウト用追加パラメータテスト - ModelSettingsのextra_*パラメータを使用

This tests if timeout can be configured via extra_headers, extra_body, or extra_query.
extra_headers、extra_body、extra_queryでタイムアウトが設定できるかテストします。
"""

import os
import asyncio
from agents import Agent, Runner, RunConfig, ModelSettings


async def test_extra_timeout_params():
    """
    Test timeout configuration via ModelSettings extra parameters
    ModelSettingsの追加パラメータでタイムアウト設定をテスト
    """
    print("🔍 Testing Extra Parameters for Timeout Configuration")
    print("=" * 60)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        return
    
    # Test 1: extra_headers with timeout
    print("\n📋 Test 1: extra_headers with timeout")
    try:
        model_settings = ModelSettings(
            extra_headers={"X-Request-Timeout": "120"}
        )
        agent = Agent(
            name="timeout_test_headers",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        run_config = RunConfig(model_settings=model_settings)
        result = await Runner.run(agent, "Hi", run_config=run_config)
        print(f"   ✅ Success with extra_headers: {result.final_output[:30]}...")
    except Exception as e:
        print(f"   ❌ Failed with extra_headers: {e}")
    
    # Test 2: extra_body with timeout
    print("\n📋 Test 2: extra_body with timeout")
    try:
        model_settings = ModelSettings(
            extra_body={"timeout": 120}
        )
        agent = Agent(
            name="timeout_test_body",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        run_config = RunConfig(model_settings=model_settings)
        result = await Runner.run(agent, "Hi", run_config=run_config)
        print(f"   ✅ Success with extra_body: {result.final_output[:30]}...")
    except Exception as e:
        print(f"   ❌ Failed with extra_body: {e}")
    
    # Test 3: extra_query with timeout
    print("\n📋 Test 3: extra_query with timeout")
    try:
        model_settings = ModelSettings(
            extra_query={"timeout": "120"}
        )
        agent = Agent(
            name="timeout_test_query",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        run_config = RunConfig(model_settings=model_settings)
        result = await Runner.run(agent, "Hi", run_config=run_config)
        print(f"   ✅ Success with extra_query: {result.final_output[:30]}...")
    except Exception as e:
        print(f"   ❌ Failed with extra_query: {e}")
    
    # Test 4: Check if we can access underlying OpenAI client configuration
    print("\n📋 Test 4: OpenAI Client Timeout Investigation")
    try:
        # Create agent and try to access internal client
        agent = Agent(
            name="client_investigation",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        
        print(f"   Agent type: {type(agent)}")
        print(f"   Agent attributes: {[attr for attr in dir(agent) if not attr.startswith('_') and 'client' in attr.lower()]}")
        
        # Check if agent has model attribute
        if hasattr(agent, 'model'):
            model = agent.model
            print(f"   Agent.model type: {type(model)}")
            print(f"   Agent.model attributes: {[attr for attr in dir(model) if not attr.startswith('_') and ('client' in attr.lower() or 'timeout' in attr.lower())]}")
            
            # Check if model has openai client
            if hasattr(model, 'openai_client'):
                client = model.openai_client
                print(f"   OpenAI client type: {type(client)}")
                print(f"   OpenAI client timeout-related: {[attr for attr in dir(client) if 'timeout' in attr.lower()]}")
                
        # Check if we can modify agent/model after creation
        if hasattr(agent, 'model') and hasattr(agent.model, 'openai_client'):
            try:
                # Try to set timeout on the client
                agent.model.openai_client.timeout = 120
                print(f"   ✅ Successfully set timeout on OpenAI client")
                
                # Test with modified client
                result = await Runner.run(agent, "Hi")
                print(f"   ✅ Agent works with modified timeout: {result.final_output[:30]}...")
                
            except Exception as e:
                print(f"   ❌ Failed to modify client timeout: {e}")
    
    except Exception as e:
        print(f"   ❌ Client investigation failed: {e}")
    
    # Test 5: Environment variable approach
    print("\n📋 Test 5: Environment Variable Approach")
    try:
        # Set OpenAI timeout environment variables
        original_timeout = os.environ.get('OPENAI_TIMEOUT')
        os.environ['OPENAI_TIMEOUT'] = '120'
        
        agent = Agent(
            name="env_timeout_test",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        result = await Runner.run(agent, "Hi")
        print(f"   ✅ Success with OPENAI_TIMEOUT env var: {result.final_output[:30]}...")
        
        # Restore original value
        if original_timeout is None:
            os.environ.pop('OPENAI_TIMEOUT', None)
        else:
            os.environ['OPENAI_TIMEOUT'] = original_timeout
            
    except Exception as e:
        print(f"   ❌ Failed with environment variable: {e}")
        # Restore original value on error
        if original_timeout is None:
            os.environ.pop('OPENAI_TIMEOUT', None)
        else:
            os.environ['OPENAI_TIMEOUT'] = original_timeout


if __name__ == "__main__":
    asyncio.run(test_extra_timeout_params())