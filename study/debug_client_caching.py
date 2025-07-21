#!/usr/bin/env python3
"""
Debug Client Caching - Check if OpenAI client is cached
クライアントキャッシュデバッグ - OpenAIクライアントがキャッシュされているかチェック

This investigates if the OpenAI client is cached and preventing timeout changes.
OpenAIクライアントがキャッシュされてタイムアウト変更を阻害しているか調査します。
"""

import os
import asyncio
from refinire import RefinireAgent


async def debug_client_caching():
    """
    Debug OpenAI client caching behavior
    OpenAIクライアントキャッシュ動作をデバッグ
    """
    print("🔍 Debug Client Caching")
    print("=" * 30)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        return
    
    # Test 1: Check if client is created immediately when agent is created
    print("\n📋 Test 1: Agent Creation and Client State")
    try:
        from agents.models import openai_provider
        
        # Check initial state
        print(f"   Initial _http_client: {getattr(openai_provider, '_http_client', 'No _http_client attr')}")
        
        # Create agent
        agent = RefinireAgent(
            name="cache_test",
            generation_instructions="You are a helpful assistant.",
            model="gpt-4o-mini",
            timeout=120
        )
        
        print(f"   After agent creation _http_client: {getattr(openai_provider, '_http_client', 'No _http_client attr')}")
        
        # Check if SDK agent has cached client
        if hasattr(agent, '_sdk_agent') and agent._sdk_agent:
            print(f"   SDK agent exists: {type(agent._sdk_agent)}")
            
    except Exception as e:
        print(f"   ❌ Test 1 failed: {e}")
    
    # Test 2: Try to force client recreation
    print("\n📋 Test 2: Force Client Recreation")
    try:
        from agents.models import openai_provider
        
        # Reset the global HTTP client
        if hasattr(openai_provider, '_http_client'):
            print(f"   Resetting global _http_client: {openai_provider._http_client}")
            openai_provider._http_client = None
        
        # Create new agent after reset
        agent = RefinireAgent(
            name="reset_test",
            generation_instructions="You are a helpful assistant.",
            model="gpt-4o-mini",
            timeout=120
        )
        
        # Monitor client creation
        call_count = [0]
        original_shared_http_client = openai_provider.shared_http_client
        
        def monitor_client_creation():
            call_count[0] += 1
            print(f"   🔧 shared_http_client called #{call_count[0]}")
            client = original_shared_http_client()
            print(f"      Created client type: {type(client)}")
            print(f"      Created client timeout: {getattr(client, 'timeout', 'No timeout')}")
            return client
        
        openai_provider.shared_http_client = monitor_client_creation
        
        try:
            # Try to trigger client creation
            result = await agent._run_standalone("Hi")
            print(f"   Result: {result.success}")
        except Exception as e:
            print(f"   Exception: {e}")
        finally:
            openai_provider.shared_http_client = original_shared_http_client
            
        print(f"   Client creation calls: {call_count[0]}")
        
    except Exception as e:
        print(f"   ❌ Test 2 failed: {e}")
    
    # Test 3: Check if there are other client caches
    print("\n📋 Test 3: Look for Other Client Caches")
    try:
        from agents.models import openai_provider
        
        # Check if OpenAIProvider has cached clients
        from agents import RunConfig
        run_config = RunConfig()
        
        if hasattr(run_config, 'model_provider'):
            provider = run_config.model_provider
            print(f"   RunConfig model_provider: {type(provider)}")
            
            if hasattr(provider, '_client'):
                print(f"   Provider _client: {getattr(provider, '_client', 'None')}")
            
            # Try to get a model to see if client is created
            model = provider.get_model("gpt-4o-mini")
            print(f"   Model type: {type(model)}")
            
            if hasattr(model, '_client'):
                client = model._client
                print(f"   Model _client: {type(client)}")
                print(f"   Model client timeout: {getattr(client, 'timeout', 'No timeout')}")
        
    except Exception as e:
        print(f"   ❌ Test 3 failed: {e}")


if __name__ == "__main__":
    asyncio.run(debug_client_caching())