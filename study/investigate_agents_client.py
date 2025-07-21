#!/usr/bin/env python3
"""
Investigate OpenAI Agents SDK Client Configuration
OpenAI Agents SDKクライアント設定の調査

This investigates how OpenAI Agents SDK creates and configures its OpenAI client.
OpenAI Agents SDKがOpenAIクライアントをどのように作成・設定するかを調査します。
"""

import os
import asyncio
from agents import Agent, Runner


async def investigate_agents_client():
    """
    Investigate OpenAI Agents SDK client configuration
    OpenAI Agents SDKクライアント設定を調査
    """
    print("🔍 Investigating OpenAI Agents SDK Client Configuration")
    print("=" * 60)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        return
    
    # Test 1: Create agent and examine internal structure
    print("\n📋 Test 1: Agent Internal Structure")
    try:
        agent = Agent(
            name="client_investigation",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        
        print(f"   Agent type: {type(agent)}")
        print(f"   Agent attributes: {[attr for attr in dir(agent) if not attr.startswith('_')]}")
        
        # Look for model-related attributes
        model_attrs = [attr for attr in dir(agent) if 'model' in attr.lower()]
        print(f"   Model-related attributes: {model_attrs}")
        
        # Check if agent has internal model object after initialization
        if hasattr(agent, 'model'):
            print(f"   agent.model: {agent.model} (type: {type(agent.model)})")
        
        # Check for private attributes that might contain model object
        private_attrs = [attr for attr in dir(agent) if attr.startswith('_') and 'model' in attr.lower()]
        print(f"   Private model attributes: {private_attrs}")
        
        for attr in private_attrs:
            try:
                value = getattr(agent, attr)
                print(f"   {attr}: {value} (type: {type(value)})")
            except Exception:
                print(f"   {attr}: <unable to access>")
        
    except Exception as e:
        print(f"   ❌ Agent investigation failed: {e}")
    
    # Test 2: Check RunConfig model_provider settings
    print("\n📋 Test 2: RunConfig ModelProvider Investigation")
    try:
        from agents import RunConfig, ModelProvider
        
        # Check ModelProvider attributes
        print(f"   ModelProvider type: {type(ModelProvider)}")
        print(f"   ModelProvider attributes: {[attr for attr in dir(ModelProvider) if not attr.startswith('_')]}")
        
        # Try to create a ModelProvider
        model_provider = ModelProvider()
        print(f"   ModelProvider instance: {model_provider}")
        print(f"   ModelProvider instance attributes: {[attr for attr in dir(model_provider) if not attr.startswith('_')]}")
        
        # Check if ModelProvider has timeout-related methods
        timeout_attrs = [attr for attr in dir(model_provider) if 'timeout' in attr.lower()]
        print(f"   ModelProvider timeout attributes: {timeout_attrs}")
        
    except Exception as e:
        print(f"   ❌ ModelProvider investigation failed: {e}")
    
    # Test 3: Check if we can access the model during execution
    print("\n📋 Test 3: Runtime Model Access Investigation")
    
    # Create a custom Runner subclass to intercept model access
    class DebugRunner(Runner):
        @classmethod
        async def _get_new_response(cls, *args, **kwargs):
            print(f"      🔍 _get_new_response called with args: {len(args)}")
            print(f"      🔍 kwargs keys: {list(kwargs.keys())}")
            
            # Try to find model object in arguments
            for i, arg in enumerate(args):
                if hasattr(arg, 'get_response') or 'model' in str(type(arg)).lower():
                    print(f"      🔍 Found potential model at args[{i}]: {type(arg)}")
                    print(f"         Attributes: {[attr for attr in dir(arg) if not attr.startswith('_')][:10]}")  # First 10
                    
                    # Check for OpenAI client
                    if hasattr(arg, '_get_client'):
                        try:
                            client = arg._get_client()
                            print(f"         Client type: {type(client)}")
                            print(f"         Client timeout: {getattr(client, 'timeout', 'Not found')}")
                        except Exception as e:
                            print(f"         Client access failed: {e}")
            
            # Call original method
            return await super()._get_new_response(*args, **kwargs)
    
    try:
        agent = Agent(
            name="runtime_test",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        
        print("   🚀 Running with debug interceptor...")
        result = await DebugRunner.run(agent, "Hi")
        print(f"   ✅ Success: {result.final_output}")
        
    except Exception as e:
        print(f"   ❌ Runtime investigation failed: {e}")


if __name__ == "__main__":
    asyncio.run(investigate_agents_client())