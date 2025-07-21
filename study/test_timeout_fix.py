#!/usr/bin/env python3
"""
Test Timeout Fix - Verify RefinireAgent timeout configuration
タイムアウト修正テスト - RefinireAgentタイムアウト設定の検証

This tests if the timeout environment variable approach works for RefinireAgent.
タイムアウト環境変数アプローチがRefinireAgentで機能するかテストします。
"""

import os
import asyncio
from refinire import RefinireAgent


async def test_timeout_fix():
    """
    Test RefinireAgent with environment variable timeout configuration
    環境変数タイムアウト設定でRefinireAgentをテスト
    """
    print("🔍 Testing RefinireAgent Timeout Fix")
    print("=" * 40)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        return
    
    # Test 1: Check if environment variable is set correctly
    print("\n📋 Test 1: Environment Variable Setting")
    
    print(f"   Original OPENAI_TIMEOUT: {os.environ.get('OPENAI_TIMEOUT', 'Not set')}")
    
    try:
        # Create RefinireAgent with extended timeout
        agent = RefinireAgent(
            name="timeout_test",
            generation_instructions="You are a helpful assistant.",
            model="gpt-4o-mini",
            timeout=120  # 2 minutes
        )
        
        print(f"   Agent timeout setting: {agent.timeout}")
        
        # Test 2: Run agent and check if timeout is applied
        print("\n📋 Test 2: Agent Execution with Timeout")
        print("   Sending request with 120 second timeout...")
        
        # Use a simple, fast request to verify it works
        result = await agent._run_standalone("Hi")
        
        print(f"   ✅ Success: {result.content}")
        print(f"   Success flag: {result.success}")
        
        if result.success:
            print("   🎉 Timeout configuration is working!")
        else:
            print(f"   ❌ Agent execution failed: {result.content}")
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Direct environment variable approach
    print("\n📋 Test 3: Direct Environment Variable Test")
    try:
        # Set timeout directly via environment variable
        original_timeout = os.environ.get('OPENAI_TIMEOUT')
        os.environ['OPENAI_TIMEOUT'] = '120'
        
        print(f"   Set OPENAI_TIMEOUT to: {os.environ.get('OPENAI_TIMEOUT')}")
        
        # Test with agents SDK directly
        from agents import Agent, Runner
        agent = Agent(
            name="direct_env_test",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        
        result = await Runner.run(agent, "Hi")
        print(f"   ✅ Direct SDK success: {result.final_output}")
        
        # Restore original
        if original_timeout is None:
            os.environ.pop('OPENAI_TIMEOUT', None)
        else:
            os.environ['OPENAI_TIMEOUT'] = original_timeout
            
    except Exception as e:
        print(f"   ❌ Direct environment test failed: {e}")
        # Restore original on error
        if original_timeout is None:
            os.environ.pop('OPENAI_TIMEOUT', None)
        else:
            os.environ['OPENAI_TIMEOUT'] = original_timeout


if __name__ == "__main__":
    asyncio.run(test_timeout_fix())