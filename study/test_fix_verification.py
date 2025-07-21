#!/usr/bin/env python3
"""
Test Fix Verification - Verify that the provider detection fix works completely
修正検証テスト - プロバイダー検出修正が完全に機能することを検証

This verifies that RefinireAgent now correctly uses OpenAI for gpt models.
RefinireAgentがgptモデルでOpenAIを正しく使用することを検証します。
"""

import os
import asyncio


async def test_fix_verification():
    """
    Verify the provider detection fix works correctly
    プロバイダー検出修正が正しく機能することを検証
    """
    print("🔍 Fix Verification Tests")
    print("=" * 30)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        return
    
    # Test 1: Verify RefinireAgent now uses OpenAI
    print("\n📋 Test 1: RefinireAgent Provider Verification")
    try:
        from refinire import RefinireAgent
        
        agent = RefinireAgent(
            name="provider_test",
            generation_instructions="You are a helpful assistant.",
            model="gpt-4o-mini",
            timeout=60
        )
        
        print(f"   Agent model type: {type(agent.model)}")
        print(f"   Agent model: {agent.model}")
        
        # Check if it's an OpenAI model now
        is_openai = "openai" in str(type(agent.model)).lower()
        print(f"   Is OpenAI model: {is_openai}")
        
        if hasattr(agent, '_sdk_agent') and agent._sdk_agent:
            sdk_agent = agent._sdk_agent
            print(f"   SDK agent model: {sdk_agent.model}")
            print(f"   SDK agent model type: {type(sdk_agent.model)}")
        
    except Exception as e:
        print(f"   ❌ Provider verification failed: {e}")
    
    # Test 2: Test actual functionality
    print("\n📋 Test 2: Functionality Test")
    try:
        from refinire import RefinireAgent
        
        agent = RefinireAgent(
            name="function_test",
            generation_instructions="You are a helpful assistant.",
            model="gpt-4o-mini",
            timeout=60
        )
        
        result = await agent._run_standalone("What is 2+2?")
        print(f"   Success: {result.success}")
        print(f"   Content: {result.content}")
        
    except Exception as e:
        print(f"   ❌ Functionality test failed: {e}")
    
    # Test 3: Test different OpenAI models
    print("\n📋 Test 3: Different OpenAI Models")
    openai_models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
    
    for model in openai_models:
        try:
            from refinire import RefinireAgent
            
            agent = RefinireAgent(
                name=f"test_{model.replace('-', '_')}",
                generation_instructions="Say hello.",
                model=model,
                timeout=60
            )
            
            model_type = str(type(agent.model))
            is_openai = "openai" in model_type.lower()
            print(f"   {model}: {'✅ OpenAI' if is_openai else '❌ Not OpenAI'} ({model_type})")
            
        except Exception as e:
            print(f"   {model}: ❌ Error - {e}")
    
    # Test 4: Test that non-OpenAI models still work correctly  
    print("\n📋 Test 4: Non-OpenAI Models (should not use OpenAI)")
    non_openai_models = ["claude-3-opus", "gemini-pro"]
    
    for model in non_openai_models:
        try:
            from refinire import RefinireAgent
            
            agent = RefinireAgent(
                name=f"test_{model.replace('-', '_')}",
                generation_instructions="Say hello.",
                model=model,
                timeout=60
            )
            
            model_type = str(type(agent.model))
            is_openai = "openai" in model_type.lower()
            expected_provider = "anthropic" if "claude" in model else "google"
            has_expected = expected_provider in model_type.lower()
            
            print(f"   {model}: {'✅ Correct' if has_expected else '❌ Wrong'} provider ({model_type})")
            
        except Exception as e:
            print(f"   {model}: ❌ Error - {e}")


if __name__ == "__main__":
    asyncio.run(test_fix_verification())