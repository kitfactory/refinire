#!/usr/bin/env python3
"""
Debug Patch Application - Check if RefinireAgent applies the HTTP client patch
パッチ適用デバッグ - RefinireAgentがHTTPクライアントパッチを適用するかチェック

This debugs whether the HTTP client patch is actually being applied.
HTTPクライアントパッチが実際に適用されているかデバッグします。
"""

import os
import asyncio
from refinire import RefinireAgent


# Monkey patch to add debug logging to llm_pipeline
def debug_run_standalone(original_method):
    """Wrap _run_standalone to add debug logging"""
    async def wrapper(self, prompt):
        print(f"\n🔍 _run_standalone called")
        print(f"   Agent timeout: {self.timeout}")
        
        # Check if patching logic executes
        if self.timeout and self.timeout != 30.0:
            print(f"   ✅ Timeout condition met: {self.timeout} != 30.0")
        else:
            print(f"   ❌ Timeout condition NOT met: {self.timeout}")
        
        try:
            result = await original_method(self, prompt)
            print(f"   Result: {type(result)} - {getattr(result, 'success', 'No success attr')}")
            return result
        except Exception as e:
            print(f"   Exception in _run_standalone: {e}")
            raise
    
    return wrapper


async def debug_patch_application():
    """
    Debug patch application in RefinireAgent
    RefinireAgentでのパッチ適用をデバッグ
    """
    print("🔍 Debug Patch Application")
    print("=" * 40)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        return
    
    # Apply debug wrapper
    original_run_standalone = RefinireAgent._run_standalone
    RefinireAgent._run_standalone = debug_run_standalone(original_run_standalone)
    
    try:
        print("🔧 Creating RefinireAgent with timeout=120...")
        agent = RefinireAgent(
            name="debug_test",
            generation_instructions="You are a helpful assistant.",
            model="gpt-4o-mini",
            timeout=120
        )
        
        print(f"🔧 Agent created with timeout: {agent.timeout}")
        
        # Monitor HTTP client function during execution
        from agents.models import openai_provider
        original_shared_http_client = openai_provider.shared_http_client
        
        patch_calls = [0]
        def monitor_shared_http_client():
            patch_calls[0] += 1
            print(f"   🔧 shared_http_client called #{patch_calls[0]}")
            client = original_shared_http_client()
            print(f"      Client type: {type(client)}")
            print(f"      Client timeout: {getattr(client, 'timeout', 'No timeout attr')}")
            return client
        
        openai_provider.shared_http_client = monitor_shared_http_client
        
        try:
            print("\n🚀 Running agent...")
            result = await agent._run_standalone("Hi")
            print(f"✅ Success: {result.content}")
        except Exception as e:
            print(f"❌ Failed: {e}")
        finally:
            # Restore
            openai_provider.shared_http_client = original_shared_http_client
            
        print(f"\n📊 shared_http_client was called {patch_calls[0]} times")
        
    finally:
        # Restore original method
        RefinireAgent._run_standalone = original_run_standalone


if __name__ == "__main__":
    asyncio.run(debug_patch_application())