#!/usr/bin/env python3
"""
Test HTTP Client Patch - Verify the HTTP client timeout patch works
HTTPクライアントパッチテスト - HTTPクライアントタイムアウトパッチが機能するか検証

This tests if the HTTP client patching approach works for timeout configuration.
HTTPクライアントパッチアプローチでタイムアウト設定が機能するかテストします。
"""

import os
import asyncio
import httpx
from refinire import RefinireAgent


async def test_http_client_patch():
    """
    Test HTTP client patching approach for timeout
    タイムアウト用HTTPクライアントパッチアプローチをテスト
    """
    print("🔍 Testing HTTP Client Patch for Timeout")
    print("=" * 50)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        return
    
    # Test 1: Check if the patching approach works with direct agents SDK
    print("\n📋 Test 1: Direct HTTP Client Patching Test")
    try:
        from agents import Agent, Runner
        from agents.models import openai_provider
        
        # Store original function
        original_shared_http_client = openai_provider.shared_http_client
        print(f"   Original shared_http_client: {original_shared_http_client}")
        
        # Create custom HTTP client with 120 second timeout
        def custom_shared_http_client():
            print("   🔧 Custom HTTP client created with 120s timeout")
            return httpx.AsyncClient(timeout=120.0)
        
        # Patch the function
        openai_provider.shared_http_client = custom_shared_http_client
        
        # Test with patched function
        agent = Agent(
            name="patch_test",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        
        print("   🚀 Running with patched HTTP client...")
        result = await Runner.run(agent, "Hi")
        print(f"   ✅ Success: {result.final_output}")
        
        # Restore original
        openai_provider.shared_http_client = original_shared_http_client
        
    except Exception as e:
        print(f"   ❌ Direct patch test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Test RefinireAgent with timeout
    print("\n📋 Test 2: RefinireAgent Timeout Test")
    try:
        agent = RefinireAgent(
            name="timeout_test",
            generation_instructions="You are a helpful assistant.",
            model="gpt-4o-mini",
            timeout=120  # 2 minutes
        )
        
        print(f"   Agent timeout setting: {agent.timeout}")
        
        # Add debug to see if patch is applied
        from agents.models import openai_provider
        original_func = openai_provider.shared_http_client
        
        # Wrap the function to see if it gets called
        call_count = [0]
        def debug_wrapper():
            call_count[0] += 1
            print(f"   🔧 shared_http_client called {call_count[0]} times")
            result = original_func()
            print(f"      HTTP client timeout: {getattr(result, 'timeout', 'Not found')}")
            return result
        
        openai_provider.shared_http_client = debug_wrapper
        
        try:
            result = await agent._run_standalone("Hi")
            print(f"   ✅ RefinireAgent success: {result.content}")
        except Exception as e:
            print(f"   ❌ RefinireAgent failed: {e}")
        finally:
            # Restore original
            openai_provider.shared_http_client = original_func
        
    except Exception as e:
        print(f"   ❌ RefinireAgent test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Check what timeout value is actually being used
    print("\n📋 Test 3: Timeout Value Investigation")
    try:
        from agents.models import openai_provider
        
        # Create client and check its timeout
        client = openai_provider.shared_http_client()
        print(f"   Default client type: {type(client)}")
        print(f"   Default client timeout: {getattr(client, 'timeout', 'Not found')}")
        
        # Test with custom timeout
        custom_client = httpx.AsyncClient(timeout=120.0)
        print(f"   Custom client timeout: {custom_client.timeout}")
        
    except Exception as e:
        print(f"   ❌ Timeout investigation failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_http_client_patch())