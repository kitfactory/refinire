#!/usr/bin/env python3
"""
Debug Custom Config - Check if custom RunConfig is created in RefinireAgent
カスタム設定デバッグ - RefinireAgentでカスタムRunConfigが作成されるかチェック

This debugs if the custom RunConfig with timeout is being created and used.
タイムアウト付きカスタムRunConfigが作成・使用されているかデバッグします。
"""

import os
import asyncio
from refinire import RefinireAgent


# Monkey patch to add debug logging
def debug_run_standalone(original_method):
    """Add debug logging to _run_standalone"""
    async def wrapper(self, prompt):
        print(f"\n🔍 _run_standalone called")
        print(f"   Agent timeout: {self.timeout}")
        
        # Check the timeout condition
        if self.timeout and self.timeout != 30.0:
            print(f"   ✅ Timeout condition met: {self.timeout} != 30.0")
            
            # Try to reproduce the custom client creation logic
            try:
                import httpx
                from openai import AsyncOpenAI
                from agents import RunConfig
                from agents.models.openai_provider import OpenAIProvider
                
                print("   🔧 Creating custom client...")
                custom_client = AsyncOpenAI(
                    timeout=httpx.Timeout(timeout=self.timeout)
                )
                print(f"      Custom client timeout: {custom_client.timeout}")
                
                print("   🔧 Creating custom provider...")
                custom_provider = OpenAIProvider(openai_client=custom_client)
                
                print("   🔧 Creating custom RunConfig...")
                custom_run_config = RunConfig(model_provider=custom_provider)
                print(f"      Custom RunConfig created: {type(custom_run_config)}")
                
                # Check if provider is correctly set
                print(f"      RunConfig model_provider: {type(custom_run_config.model_provider)}")
                
                # Test getting a model from the provider
                model = custom_run_config.model_provider.get_model("gpt-4o-mini")
                print(f"      Model from custom provider: {type(model)}")
                if hasattr(model, '_client'):
                    print(f"      Model client timeout: {model._client.timeout}")
                
                print("   ✅ Custom config creation successful")
                
            except Exception as e:
                print(f"   ❌ Custom config creation failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"   ❌ Timeout condition NOT met")
        
        # Call original method
        try:
            result = await original_method(self, prompt)
            print(f"   Result success: {result.success}")
            return result
        except Exception as e:
            print(f"   Exception: {e}")
            raise
    
    return wrapper


async def debug_custom_config():
    """
    Debug custom config creation in RefinireAgent
    RefinireAgentでのカスタム設定作成をデバッグ
    """
    print("🔍 Debug Custom Config Creation")
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
            name="debug_config",
            generation_instructions="You are a helpful assistant.",
            model="gpt-4o-mini",
            timeout=120
        )
        
        print(f"🔧 Agent created with timeout: {agent.timeout}")
        
        print("\n🚀 Running agent...")
        try:
            result = await agent._run_standalone("Hi")
            print(f"✅ Success: {result.content}")
        except Exception as e:
            print(f"❌ Failed: {e}")
        
    finally:
        # Restore original method
        RefinireAgent._run_standalone = original_run_standalone


if __name__ == "__main__":
    asyncio.run(debug_custom_config())