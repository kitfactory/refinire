#!/usr/bin/env python3
"""
LMStudio Error Investigation

English: Investigate the 'NoneType' object is not iterable error in RefinireAgent.
日本語: RefinireAgent の 'NoneType' object is not iterable エラーを調査する。
"""

import os
import sys
from refinire import RefinireAgent, Context, disable_tracing
from refinire.core.llm import get_llm


def investigate_error():
    """
    Investigate the NoneType error in detail
    NoneType エラーを詳細に調査
    """
    print("=== LMStudio Error Investigation ===")
    
    # Clear environment variables
    if 'OLLAMA_BASE_URL' in os.environ:
        del os.environ['OLLAMA_BASE_URL']
        print("🔧 Cleared OLLAMA_BASE_URL")
    
    # Enable detailed logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Create LLM
    lmstudio_base_url = os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234')
    model_name = "mistralai/devstral-small-2507"
    
    print(f"Creating LLM with base_url: {lmstudio_base_url}")
    
    try:
        llm = get_llm(
            provider="openai",
            model=model_name,
            base_url=lmstudio_base_url,
            api_key="lm-studio"
        )
        print(f"✅ LLM created: {type(llm)}")
        
        # Try to manually call the LLM to test it
        print("\nTesting direct LLM call...")
        try:
            # Check what methods are available
            methods = [m for m in dir(llm) if not m.startswith('_') and callable(getattr(llm, m))]
            print(f"Available methods: {methods}")
            
            # Test the get_response method signature
            import inspect
            if hasattr(llm, 'get_response'):
                sig = inspect.signature(llm.get_response)
                print(f"get_response signature: {sig}")
                
        except Exception as e:
            print(f"Direct LLM test failed: {e}")
            
        # Create agent with error handling
        print("\nCreating RefinireAgent...")
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant.",
            model=llm
        )
        print(f"✅ Agent created: {agent.name}")
        
        # Test with minimal input
        print("\nTesting agent with minimal input...")
        context = Context()
        
        # Monkey patch to catch the error
        original_run = agent.run
        
        def debug_run(user_input, ctx=None):
            print(f"🔍 Agent run called with input: {user_input}")
            try:
                result = original_run(user_input, ctx)
                print(f"🔍 Agent run completed successfully")
                return result
            except Exception as e:
                print(f"🔍 Agent run failed with error: {e}")
                print(f"🔍 Error type: {type(e)}")
                import traceback
                traceback.print_exc()
                raise
        
        agent.run = debug_run
        
        # Test the agent
        try:
            result_context = agent.run("Hello", context)
            print(f"Result context: {result_context}")
            print(f"Shared state: {result_context.shared_state}")
        except Exception as e:
            print(f"Agent test failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"Investigation failed: {e}")
        import traceback
        traceback.print_exc()


def test_alternative_approach():
    """
    Test alternative approach to bypass the issue
    問題を回避する代替アプローチをテスト
    """
    print("\n=== Alternative Approach Test ===")
    
    # Clear environment variables
    if 'OLLAMA_BASE_URL' in os.environ:
        del os.environ['OLLAMA_BASE_URL']
    
    try:
        # Try using the lmstudio provider directly
        lmstudio_base_url = os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234')
        model_name = "mistralai/devstral-small-2507"
        
        print("Testing with provider='lmstudio'...")
        
        llm = get_llm(
            provider="lmstudio",
            model=model_name,
            base_url=lmstudio_base_url,
            api_key="lm-studio"
        )
        print(f"✅ LLM created with lmstudio provider: {type(llm)}")
        
        agent = RefinireAgent(
            name="lmstudio_test",
            generation_instructions="You are a helpful assistant.",
            model=llm
        )
        
        context = Context()
        result_context = agent.run("Hello", context)
        
        result = result_context.shared_state.get('lmstudio_test_result')
        print(f"Result from lmstudio provider: {result}")
        
    except Exception as e:
        print(f"Alternative approach failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """
    Run investigation
    調査を実行
    """
    print("LMStudio Error Investigation")
    print("=" * 60)
    
    investigate_error()
    test_alternative_approach()
    
    print("\n" + "=" * 60)
    print("Investigation Complete")


if __name__ == '__main__':
    main()