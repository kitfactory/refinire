#!/usr/bin/env python3
"""
Debug Raw Exception - OpenAI Agents SDK Level Exception Analysis
生の例外デバッグ - OpenAI Agents SDKレベル例外分析

This temporarily disables Refinire's exception handling to see the original SDK exception.
これは一時的にRefinireの例外処理を無効化して、元のSDK例外を確認します。
"""

import os
import asyncio
from refinire import RefinireAgent


async def debug_raw_exception():
    """
    Debug raw OpenAI Agents SDK exception
    生のOpenAI Agents SDK例外をデバッグ
    """
    print("🔍 Debug Raw Exception Analysis")
    print("=" * 40)
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        return
    
    try:
        # Create agent
        agent = RefinireAgent(
            name="debug_agent",
            generation_instructions="You are a helpful assistant.",
            model="gpt-4o-mini",
            timeout=5  # Very short timeout to trigger error quickly
        )
        
        # Access the internal _run_standalone method directly
        # 内部の_run_standaloneメソッドに直接アクセス
        print("🚀 Calling _run_standalone directly...")
        llm_result = await agent._run_standalone("Hello! Please introduce yourself.")
        
        print(f"✅ Result: {llm_result}")
        print(f"📄 Content: {llm_result.content}")
        print(f"🎯 Success: {llm_result.success}")
        print(f"📊 Metadata: {llm_result.metadata}")
        
    except Exception as e:
        print(f"🚨 Raw OpenAI Agents SDK Exception Caught!")
        print(f"📛 Exception Type: {type(e).__name__}")
        print(f"📍 Exception Module: {type(e).__module__}")
        print(f"📝 Exception Message: {str(e)}")
        print(f"📋 Exception Args: {e.args}")
        
        # Check for specific exception types
        print(f"\n🔍 Exception Analysis:")
        
        import httpx
        from openai import OpenAIError
        
        if isinstance(e, OpenAIError):
            print(f"   - OpenAI SDK Exception: {type(e).__name__}")
        elif isinstance(e, httpx.TimeoutException):
            print(f"   - HTTPX Timeout Exception: {type(e).__name__}")
        elif isinstance(e, httpx.ConnectError):
            print(f"   - HTTPX Connection Exception: {type(e).__name__}")
        elif isinstance(e, httpx.RequestError):
            print(f"   - HTTPX Request Exception: {type(e).__name__}")
        else:
            print(f"   - Other Exception Type: {type(e).__name__}")
        
        # Full traceback
        import traceback
        print(f"\n🗂️  Full Traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_raw_exception())