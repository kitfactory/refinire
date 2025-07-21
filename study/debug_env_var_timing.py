#!/usr/bin/env python3
"""
Debug Environment Variable Timing - Check if OPENAI_TIMEOUT is set correctly
環境変数タイミングデバッグ - OPENAI_TIMEOUTが正しく設定されているかチェック

This debugs the timing of when OPENAI_TIMEOUT is set in RefinireAgent.
RefinireAgentでOPENAI_TIMEOUTがいつ設定されるかのタイミングをデバッグします。
"""

import os
import asyncio
from refinire import RefinireAgent


# Monkey patch to add debug logging
original_run_standalone = None


async def debug_run_standalone(self, prompt):
    """Debug version of _run_standalone with environment variable logging"""
    print(f"\n🔍 Debug: _run_standalone called")
    print(f"   Agent timeout: {self.timeout}")
    print(f"   OPENAI_TIMEOUT before: {os.environ.get('OPENAI_TIMEOUT', 'Not set')}")
    
    # Call original method
    try:
        result = await original_run_standalone(self, prompt)
        print(f"   OPENAI_TIMEOUT after: {os.environ.get('OPENAI_TIMEOUT', 'Not set')}")
        return result
    except Exception as e:
        print(f"   OPENAI_TIMEOUT after error: {os.environ.get('OPENAI_TIMEOUT', 'Not set')}")
        raise


async def test_env_var_timing():
    """
    Test environment variable timing in RefinireAgent
    RefinireAgentでの環境変数タイミングをテスト
    """
    print("🔍 Testing Environment Variable Timing")
    print("=" * 50)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        return
    
    # Monkey patch for debugging
    global original_run_standalone
    original_run_standalone = RefinireAgent._run_standalone
    RefinireAgent._run_standalone = debug_run_standalone
    
    try:
        print(f"🔧 Initial OPENAI_TIMEOUT: {os.environ.get('OPENAI_TIMEOUT', 'Not set')}")
        
        # Create agent with timeout
        agent = RefinireAgent(
            name="timing_test",
            generation_instructions="You are a helpful assistant.",
            model="gpt-4o-mini",
            timeout=120
        )
        
        print(f"🔧 After agent creation: {os.environ.get('OPENAI_TIMEOUT', 'Not set')}")
        
        # Test execution
        print("\n📋 Testing agent execution...")
        try:
            result = await agent._run_standalone("Hi")
            print(f"✅ Success: {result.content}")
        except Exception as e:
            print(f"❌ Failed: {e}")
            
        print(f"🔧 Final OPENAI_TIMEOUT: {os.environ.get('OPENAI_TIMEOUT', 'Not set')}")
        
    finally:
        # Restore original method
        RefinireAgent._run_standalone = original_run_standalone


async def test_manual_env_setting():
    """
    Test setting OPENAI_TIMEOUT manually before RefinireAgent execution
    RefinireAgent実行前にOPENAI_TIMEOUTを手動設定してテスト
    """
    print("\n🔍 Testing Manual Environment Variable Setting")
    print("=" * 50)
    
    # Store original
    original_timeout = os.environ.get('OPENAI_TIMEOUT')
    
    try:
        # Set manually before agent creation
        os.environ['OPENAI_TIMEOUT'] = '120'
        print(f"🔧 Manually set OPENAI_TIMEOUT: {os.environ.get('OPENAI_TIMEOUT')}")
        
        # Create agent with default timeout (should use env var)
        agent = RefinireAgent(
            name="manual_test",
            generation_instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
            # No timeout parameter - should use environment variable
        )
        
        print(f"🔧 Agent timeout: {agent.timeout}")
        print(f"🔧 Environment variable: {os.environ.get('OPENAI_TIMEOUT')}")
        
        # Test execution
        result = await agent._run_standalone("Hi")
        print(f"✅ Manual env var success: {result.content}")
        
    except Exception as e:
        print(f"❌ Manual env var failed: {e}")
    finally:
        # Restore original
        if original_timeout is None:
            os.environ.pop('OPENAI_TIMEOUT', None)
        else:
            os.environ['OPENAI_TIMEOUT'] = original_timeout


if __name__ == "__main__":
    asyncio.run(test_env_var_timing())
    asyncio.run(test_manual_env_setting())