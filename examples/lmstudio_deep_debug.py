#!/usr/bin/env python3
"""
Deep Debug Script for LMStudio RefinireAgent

English: Detailed debugging of RefinireAgent execution with LMStudio.
日本語: LMStudio での RefinireAgent 実行の詳細デバッグ。
"""

import os
from refinire import RefinireAgent, Context, disable_tracing
from refinire.core.llm import get_llm


def test_get_llm():
    """Test the get_llm function directly"""
    print("=== Testing get_llm Function ===")
    
    try:
        # Test with LMStudio configuration
        llm = get_llm(
            provider="openai",  # LMStudio uses OpenAI-compatible API
            model="mistralai/devstral-small-2507",
            base_url=os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234'),
            api_key="lm-studio"
        )
        
        print(f"LLM created: {type(llm)}")
        
        # Test direct call
        print("Testing direct LLM call...")
        print(f"LLM methods: {[method for method in dir(llm) if not method.startswith('_')]}")
        
        # Try get_response method
        try:
            response = llm.get_response("Hello, how are you?")
            print(f"Direct LLM response (get_response): {response}")
        except Exception as e:
            print(f"get_response failed: {e}")
            
        # Try with proper message format
        try:
            from agents.models.messages import Message
            message = Message(content="Hello, how are you?", role="user")
            response = llm.get_response([message])
            print(f"Direct LLM response (with Message): {response}")
        except Exception as e:
            print(f"Message format failed: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"get_llm test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_refinire_agent_detailed():
    """Test RefinireAgent with detailed debugging"""
    print("\n=== Detailed RefinireAgent Test ===")
    
    disable_tracing()
    
    try:
        # Create agent with explicit configuration
        agent = RefinireAgent(
            name="debug_agent",
            generation_instructions="You are a helpful assistant. Respond briefly.",
            model="mistralai/devstral-small-2507",
            store_result_key="debug_result"  # Custom result key
        )
        
        print(f"Agent created: {agent.name}")
        print(f"Agent store_result_key: {agent.store_result_key}")
        
        # Create context
        context = Context()
        print(f"Initial context shared_state: {context.shared_state}")
        
        # Test run method step by step
        print("\nCalling agent.run...")
        
        try:
            result_context = agent.run("Say hello", context)
            
            print(f"Agent run returned")
            print(f"Result context type: {type(result_context)}")
            print(f"Result context.result: {getattr(result_context, 'result', 'No result attribute')}")
            print(f"Result context.shared_state: {result_context.shared_state}")
            print(f"Result context.prev_outputs: {getattr(result_context, 'prev_outputs', 'No prev_outputs')}")
            
            # Check multiple possible result locations
            debug_result = result_context.shared_state.get('debug_result')
            agent_result = result_context.shared_state.get('debug_agent_result')
            generic_result = result_context.shared_state.get('result')
            
            print(f"\nResult check:")
            print(f"  debug_result: {debug_result}")
            print(f"  debug_agent_result: {agent_result}")
            print(f"  generic_result: {generic_result}")
            
            # Check if agent finished successfully
            if hasattr(result_context, 'finished') and result_context.finished:
                print("Agent finished successfully")
            else:
                print("Agent may not have finished properly")
                
        except Exception as e:
            print(f"Error during agent.run: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"Agent creation failed: {e}")
        import traceback
        traceback.print_exc()


def test_simple_agent():
    """Test with simplest possible configuration"""
    print("\n=== Simple Agent Test ===")
    
    disable_tracing()
    
    try:
        # Use minimal configuration
        agent = RefinireAgent(
            name="simple",
            generation_instructions="Reply with just 'OK'",
            model="mistralai/devstral-small-2507"
        )
        
        context = Context()
        result_context = agent.run("test", context)
        
        print(f"Simple test - shared_state: {result_context.shared_state}")
        print(f"Simple test - result: {result_context.shared_state.get('simple_result')}")
        
    except Exception as e:
        print(f"Simple test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all detailed diagnostic tests"""
    print("Deep LMStudio RefinireAgent Diagnostic")
    print("=" * 60)
    
    # Test 1: get_llm function
    llm_ok = test_get_llm()
    
    # Test 2: Detailed RefinireAgent
    if llm_ok:
        test_refinire_agent_detailed()
        
    # Test 3: Simple agent
    test_simple_agent()
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()