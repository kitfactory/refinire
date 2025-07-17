#!/usr/bin/env python3
"""
LMStudio Integration Debug

English: Debug RefinireAgent integration with LMStudio by tracing the execution flow.
日本語: 実行フローをトレースして RefinireAgent の LMStudio 統合をデバッグする。
"""

import os
import sys
from refinire import RefinireAgent, Context
from refinire.core.llm import get_llm


def debug_llm_integration():
    """
    Debug LLM integration step by step
    LLM統合を段階的にデバッグ
    """
    print("=== LLM Integration Debug ===")
    
    # Test get_llm function
    print("\n1. Testing get_llm function")
    try:
        llm = get_llm(
            provider="openai",
            model="mistralai/devstral-small-2507",
            base_url=os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234'),
            api_key="lm-studio"
        )
        print(f"✅ LLM created: {type(llm)}")
        print(f"   Model: {llm.model}")
        print(f"   Available methods: {[m for m in dir(llm) if not m.startswith('_') and callable(getattr(llm, m))]}")
        
        # Test if LLM has necessary attributes
        required_attrs = ['model', 'get_response', 'stream_response']
        for attr in required_attrs:
            if hasattr(llm, attr):
                print(f"   ✅ Has {attr}")
            else:
                print(f"   ❌ Missing {attr}")
                
    except Exception as e:
        print(f"❌ get_llm failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test RefinireAgent creation
    print("\n2. Testing RefinireAgent creation")
    try:
        agent = RefinireAgent(
            name="debug_agent",
            generation_instructions="You are a helpful assistant. Answer briefly.",
            model="mistralai/devstral-small-2507"
        )
        print(f"✅ Agent created: {agent.name}")
        print(f"   Model: {agent.model}")
        print(f"   Store result key: {agent.store_result_key}")
        
        # Check if agent has LLM
        if hasattr(agent, 'llm'):
            print(f"   ✅ Agent has LLM: {type(agent.llm)}")
        else:
            print(f"   ❌ Agent missing LLM")
            
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test agent execution with tracing
    print("\n3. Testing agent execution with detailed tracing")
    try:
        # Enable detailed logging
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        context = Context()
        test_input = "Hello"
        
        print(f"   Input: {test_input}")
        print(f"   Context before: {context.shared_state}")
        
        # Run agent
        result_context = agent.run(test_input, context)
        
        print(f"   Context after: {result_context.shared_state}")
        print(f"   Result: {result_context.shared_state.get('debug_agent_result')}")
        
        # Check if context has result
        if hasattr(result_context, 'result'):
            print(f"   Context.result: {result_context.result}")
            
        # Check if agent stored anything
        all_keys = list(result_context.shared_state.keys())
        print(f"   All shared_state keys: {all_keys}")
        
        for key in all_keys:
            value = result_context.shared_state[key]
            print(f"   {key}: {value} (type: {type(value)})")
            
    except Exception as e:
        print(f"❌ Agent execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def debug_openai_model_integration():
    """
    Debug OpenAI model integration specifically
    OpenAI モデル統合を具体的にデバッグ
    """
    print("\n=== OpenAI Model Integration Debug ===")
    
    try:
        # Import OpenAI model classes
        from agents.models.openai_responses import OpenAIResponsesModel
        from agents.models.model_settings import OpenAIModelSettings
        
        print("✅ OpenAI model classes imported successfully")
        
        # Create model settings
        model_settings = OpenAIModelSettings(
            model="mistralai/devstral-small-2507",
            temperature=0.7,
            max_tokens=100,
            base_url=os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234'),
            api_key="lm-studio"
        )
        
        print(f"✅ Model settings created: {model_settings}")
        
        # Create OpenAI model
        model = OpenAIResponsesModel(model="mistralai/devstral-small-2507")
        print(f"✅ OpenAI model created: {model}")
        
        # Test model response - find correct method signature
        print("\n4. Testing OpenAI model response")
        
        # Check method signature
        import inspect
        sig = inspect.signature(model.get_response)
        print(f"   get_response signature: {sig}")
        
        # Try to call with minimal required parameters
        try:
            # This will likely fail, but will show us what's needed
            result = model.get_response("Hello")
            print(f"   Response: {result}")
        except TypeError as e:
            print(f"   Expected TypeError: {e}")
            print("   This shows us what parameters are required")
            
    except Exception as e:
        print(f"❌ OpenAI model debug failed: {e}")
        import traceback
        traceback.print_exc()


def debug_provider_routing():
    """
    Debug how providers are routed in get_llm
    get_llm でプロバイダーがどのようにルーティングされるかをデバッグ
    """
    print("\n=== Provider Routing Debug ===")
    
    try:
        # Test different provider specifications
        test_cases = [
            {"provider": "openai", "model": "mistralai/devstral-small-2507"},
            {"provider": "lmstudio", "model": "mistralai/devstral-small-2507"},
            {"model": "mistralai/devstral-small-2507"}  # Auto-detect
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n   Test {i}: {case}")
            
            try:
                llm = get_llm(
                    **case,
                    base_url=os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234'),
                    api_key="lm-studio"
                )
                print(f"   ✅ Success: {type(llm)}")
                print(f"   Model: {llm.model}")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                
    except Exception as e:
        print(f"❌ Provider routing debug failed: {e}")


def main():
    """
    Run all debug functions
    すべてのデバッグ関数を実行
    """
    print("LMStudio Integration Debug")
    print("=" * 60)
    
    # Run debug functions
    debug_llm_integration()
    debug_openai_model_integration()
    debug_provider_routing()
    
    print("\n" + "=" * 60)
    print("Debug Complete")


if __name__ == '__main__':
    main()