#!/usr/bin/env python3
"""
Investigate Agent model_settings - Check if timeout can be configured there
Agentのmodel_settings調査 - そこでタイムアウト設定ができるかチェック

This investigates the Agent.model_settings attribute for timeout configuration.
Agent.model_settings属性でのタイムアウト設定を調査します。
"""

import os
import asyncio
from agents import Agent, Runner, ModelSettings


async def investigate_agent_model_settings():
    """
    Investigate Agent.model_settings for timeout configuration
    タイムアウト設定のためのAgent.model_settingsを調査
    """
    print("🔍 Investigating Agent.model_settings")
    print("=" * 40)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        return
    
    # Test 1: Default agent model_settings
    print("\n📋 Test 1: Default Agent model_settings")
    try:
        agent = Agent(
            name="default_test",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        
        print(f"   Agent.model_settings: {agent.model_settings}")
        print(f"   Type: {type(agent.model_settings)}")
        
        if agent.model_settings:
            print(f"   Attributes: {[attr for attr in dir(agent.model_settings) if not attr.startswith('_')]}")
        else:
            print("   model_settings is None")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 2: Agent with explicit ModelSettings
    print("\n📋 Test 2: Agent with Explicit ModelSettings")
    try:
        # Try creating ModelSettings with OpenAI timeout parameters
        model_settings = ModelSettings(
            max_tokens=1000,
            temperature=0.7
        )
        
        agent = Agent(
            name="explicit_test",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini",
            model_settings=model_settings
        )
        
        print(f"   Agent.model_settings: {agent.model_settings}")
        print(f"   Type: {type(agent.model_settings)}")
        print(f"   Same object: {agent.model_settings is model_settings}")
        
        # Test if it works
        result = await Runner.run(agent, "Hi")
        print(f"   ✅ Success: {result.final_output}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 3: Try to set timeout via ModelSettings extra parameters
    print("\n📋 Test 3: ModelSettings with Timeout Extra Parameters")
    
    # Based on OpenAI client documentation, try different approaches
    timeout_configs = [
        {"extra_headers": {"timeout": "120"}},
        {"extra_body": {"timeout": 120}},  # This failed before but let's try again
        {"extra_query": {"timeout": "120"}},
    ]
    
    for i, config in enumerate(timeout_configs):
        try:
            print(f"   Testing config {i+1}: {config}")
            
            model_settings = ModelSettings(**config)
            agent = Agent(
                name=f"timeout_test_{i+1}",
                instructions="You are a helpful assistant.",
                model="gpt-4o-mini",
                model_settings=model_settings
            )
            
            result = await Runner.run(agent, "Hi")
            print(f"   ✅ Config {i+1} success: {result.final_output[:30]}...")
            
        except Exception as e:
            print(f"   ❌ Config {i+1} failed: {e}")
    
    # Test 4: Check if we can modify agent.model_settings after creation
    print("\n📋 Test 4: Modify model_settings After Agent Creation")
    try:
        agent = Agent(
            name="modify_test",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        
        print(f"   Before: {agent.model_settings}")
        
        # Try to set model_settings
        agent.model_settings = ModelSettings(
            max_tokens=500,
            temperature=0.5
        )
        
        print(f"   After: {agent.model_settings}")
        
        result = await Runner.run(agent, "Hi")
        print(f"   ✅ Modified settings work: {result.final_output[:30]}...")
        
    except Exception as e:
        print(f"   ❌ Modification failed: {e}")
    
    # Test 5: Check OpenAI client timeout configuration approach
    print("\n📋 Test 5: OpenAI Client Timeout Investigation")
    try:
        # Look for how OpenAI Agents SDK creates OpenAI client
        import inspect
        from agents.models import openai_chatcompletions
        
        # Check if we can find the client creation method
        print(f"   openai_chatcompletions module: {openai_chatcompletions}")
        
        # Look for client-related methods
        for name in dir(openai_chatcompletions):
            if 'client' in name.lower() or 'create' in name.lower():
                obj = getattr(openai_chatcompletions, name)
                if callable(obj):
                    print(f"   Found method: {name}")
                    try:
                        sig = inspect.signature(obj)
                        print(f"     Signature: {sig}")
                    except Exception:
                        print(f"     <unable to get signature>")
        
    except Exception as e:
        print(f"   ❌ Client investigation failed: {e}")


if __name__ == "__main__":
    asyncio.run(investigate_agent_model_settings())