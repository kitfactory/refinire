#!/usr/bin/env python3
"""
Compare Direct vs RefinireAgent - Side-by-side comparison
直接比較 vs RefinireAgent - 並行比較

This compares identical requests through direct OpenAI Agents SDK vs RefinireAgent.
直接OpenAI Agents SDKとRefinireAgentで同一リクエストを比較します。
"""

import os
import asyncio
import httpx


async def compare_direct_vs_refinire():
    """
    Compare direct OpenAI Agents SDK vs RefinireAgent with identical configuration
    同一設定で直接OpenAI Agents SDKとRefinireAgentを比較
    """
    print("🔍 Compare Direct vs RefinireAgent")
    print("=" * 50)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        return
    
    # Test 1: Direct OpenAI Agents SDK (we know this works)
    print("\n📋 Test 1: Direct OpenAI Agents SDK with Custom Client")
    try:
        from openai import AsyncOpenAI
        from agents import Agent, Runner, RunConfig
        from agents.models.openai_provider import OpenAIProvider
        
        # Create custom client (same as RefinireAgent creates)
        custom_client = AsyncOpenAI(timeout=httpx.Timeout(timeout=120.0))
        custom_provider = OpenAIProvider(openai_client=custom_client)
        
        # Create agent (same config as RefinireAgent)
        agent = Agent(
            name="direct_test",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        
        run_config = RunConfig(model_provider=custom_provider)
        
        print("   🚀 Running direct OpenAI Agents SDK...")
        result = await Runner.run(agent, "Hello! Please introduce yourself.", run_config=run_config)
        print(f"   ✅ Direct success: {result.final_output}")
        
    except Exception as e:
        print(f"   ❌ Direct failed: {e}")
    
    # Test 2: RefinireAgent with same configuration
    print("\n📋 Test 2: RefinireAgent with Same Configuration")
    try:
        from refinire import RefinireAgent
        
        # Create RefinireAgent with extended timeout
        agent = RefinireAgent(
            name="refinire_test",
            generation_instructions="You are a helpful assistant.",
            model="gpt-4o-mini",
            timeout=120  # Same timeout as above
        )
        
        print("   🚀 Running RefinireAgent...")
        result = await agent._run_standalone("Hello! Please introduce yourself.")
        print(f"   Result success: {result.success}")
        print(f"   Result content: {result.content}")
        
    except Exception as e:
        print(f"   ❌ RefinireAgent failed: {e}")
    
    # Test 3: Compare the actual SDK agents created
    print("\n📋 Test 3: Compare SDK Agent Configuration")
    try:
        from refinire import RefinireAgent
        from agents import Agent
        
        # Create RefinireAgent
        refinire_agent = RefinireAgent(
            name="compare_test",
            generation_instructions="You are a helpful assistant.",
            model="gpt-4o-mini",
            timeout=120
        )
        
        # Compare SDK agents
        direct_agent = Agent(
            name="compare_test",
            instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        
        print(f"   Direct agent type: {type(direct_agent)}")
        print(f"   Direct agent model: {direct_agent.model}")
        print(f"   Direct agent instructions: {direct_agent.instructions}")
        
        if hasattr(refinire_agent, '_sdk_agent') and refinire_agent._sdk_agent:
            sdk_agent = refinire_agent._sdk_agent
            print(f"   RefinireAgent SDK agent type: {type(sdk_agent)}")
            print(f"   RefinireAgent SDK agent model: {sdk_agent.model}")
            print(f"   RefinireAgent SDK agent instructions: {sdk_agent.instructions}")
            
            # Check if they're basically the same
            print(f"   Same model: {direct_agent.model == sdk_agent.model}")
            print(f"   Same instructions: {direct_agent.instructions == sdk_agent.instructions}")
        
    except Exception as e:
        print(f"   ❌ Comparison failed: {e}")
    
    # Test 4: Test with minimal RefinireAgent configuration
    print("\n📋 Test 4: Minimal RefinireAgent Configuration")
    try:
        from refinire import RefinireAgent
        
        # Create very simple RefinireAgent
        agent = RefinireAgent(
            name="minimal_test",
            generation_instructions="Say hello.",
            model="gpt-4o-mini",
            timeout=120
        )
        
        print("   🚀 Running minimal RefinireAgent...")
        result = await agent._run_standalone("Hi")
        print(f"   Minimal result: {result.success} - {result.content}")
        
    except Exception as e:
        print(f"   ❌ Minimal RefinireAgent failed: {e}")


if __name__ == "__main__":
    asyncio.run(compare_direct_vs_refinire())