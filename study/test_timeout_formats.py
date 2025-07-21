#!/usr/bin/env python3
"""
Test Timeout Formats - Test different httpx timeout configurations
タイムアウト形式テスト - 異なるhttpxタイムアウト設定をテスト

This tests different timeout formats and a very simple request to isolate the issue.
異なるタイムアウト形式と非常にシンプルなリクエストをテストして問題を特定します。
"""

import os
import asyncio
import httpx


async def test_timeout_formats():
    """
    Test different timeout formats and simple requests
    異なるタイムアウト形式とシンプルなリクエストをテスト
    """
    print("🔍 Testing Timeout Formats and Simple Requests")
    print("=" * 60)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        return
    
    # Test 1: Different timeout formats
    print("\n📋 Test 1: Different Timeout Formats")
    timeout_formats = [
        httpx.Timeout(timeout=120.0),
        httpx.Timeout(120.0),
        httpx.Timeout(connect=120.0, read=120.0, write=120.0, pool=120.0),
        120.0,  # Simple float
    ]
    
    for i, timeout_format in enumerate(timeout_formats):
        try:
            print(f"   Testing format {i+1}: {timeout_format}")
            
            from openai import AsyncOpenAI
            from agents import Agent, Runner, RunConfig
            from agents.models.openai_provider import OpenAIProvider
            
            # Create client with this timeout format
            custom_client = AsyncOpenAI(timeout=timeout_format)
            print(f"      Client timeout: {custom_client.timeout}")
            
            # Quick test
            custom_provider = OpenAIProvider(openai_client=custom_client)
            agent = Agent(
                name=f"timeout_format_test_{i+1}",
                instructions="You are a helpful assistant.",
                model="gpt-4o-mini"
            )
            run_config = RunConfig(model_provider=custom_provider)
            
            print(f"      🚀 Testing format {i+1}...")
            result = await Runner.run(agent, "Say 'Hi'", run_config=run_config)
            print(f"      ✅ Format {i+1} success: {result.final_output}")
            
        except Exception as e:
            print(f"      ❌ Format {i+1} failed: {e}")
    
    # Test 2: Very simple request to check connectivity
    print("\n📋 Test 2: Simple Connectivity Test")
    try:
        from openai import AsyncOpenAI
        
        # Very simple request with default client
        client = AsyncOpenAI()
        print(f"   Default client timeout: {client.timeout}")
        
        # Extremely simple completion
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5
        )
        
        print(f"   ✅ Simple request success: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"   ❌ Simple request failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test with shorter timeout to confirm timeout behavior
    print("\n📋 Test 3: Very Short Timeout Test")
    try:
        from openai import AsyncOpenAI
        from agents import Agent, Runner, RunConfig
        from agents.models.openai_provider import OpenAIProvider
        
        # Create client with very short timeout (1 second)
        short_timeout_client = AsyncOpenAI(timeout=1.0)
        print(f"   Short timeout client: {short_timeout_client.timeout}")
        
        custom_provider = OpenAIProvider(openai_client=short_timeout_client)
        agent = Agent(
            name="short_timeout_test",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        run_config = RunConfig(model_provider=custom_provider)
        
        print("   🚀 Testing with 1-second timeout (should fail)...")
        result = await Runner.run(agent, "Hi", run_config=run_config)
        print(f"   😮 Unexpected success: {result.final_output}")
        
    except Exception as e:
        print(f"   ✅ Expected timeout with 1s: {e}")
    
    # Test 4: Direct httpx request to OpenAI
    print("\n📋 Test 4: Direct HTTPX Request")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                print(f"   ✅ Direct HTTPX success: {content}")
            else:
                print(f"   ❌ Direct HTTPX failed: {response.status_code} - {response.text}")
        
    except Exception as e:
        print(f"   ❌ Direct HTTPX failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_timeout_formats())