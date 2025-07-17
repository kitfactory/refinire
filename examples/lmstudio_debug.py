#!/usr/bin/env python3
"""
LMStudio Connection Debug Script

English: Debug script to diagnose LMStudio connection issues.
日本語: LMStudio 接続問題を診断するデバッグスクリプト。
"""

import os
import sys
import httpx
from refinire import RefinireAgent, Context, disable_tracing


def test_direct_api():
    """Test direct API call to LMStudio"""
    print("=== Testing Direct API Call ===")
    
    base_url = os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234')
    print(f"Base URL: {base_url}")
    
    try:
        # Test models endpoint
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{base_url}/v1/models")
            print(f"Models endpoint status: {response.status_code}")
            if response.status_code == 200:
                models = response.json()
                print(f"Available models: {[m['id'] for m in models.get('data', [])]}")
            
        # Test chat completion
        with httpx.Client(timeout=10.0) as client:
            response = client.post(f"{base_url}/v1/chat/completions", json={
                "model": "mistralai/devstral-small-2507",
                "messages": [{"role": "user", "content": "Hello"}],
                "temperature": 0.7,
                "max_tokens": 50
            })
            print(f"Chat completion status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Direct API response: {result['choices'][0]['message']['content']}")
                return True
            else:
                print(f"Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"Direct API test failed: {e}")
        return False


def test_refinire_agent():
    """Test RefinireAgent with LMStudio"""
    print("\n=== Testing RefinireAgent ===")
    
    disable_tracing()
    
    try:
        # Create agent
        agent = RefinireAgent(
            name="debug_agent",
            generation_instructions="You are a helpful assistant.",
            model="mistralai/devstral-small-2507"
        )
        
        print("Agent created successfully")
        
        # Test simple query
        context = Context()
        print("Running agent with simple query...")
        
        # Try with timeout
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Agent run timed out")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)  # 30 second timeout
        
        try:
            result_context = agent.run("Hello", context)
            signal.alarm(0)  # Cancel timeout
            
            print(f"Agent run completed")
            print(f"Shared state keys: {list(result_context.shared_state.keys())}")
            print(f"Full shared state: {result_context.shared_state}")
            
            # Try to get result
            result = result_context.shared_state.get('debug_agent_result')
            print(f"Result: {result}")
            
        except TimeoutError:
            print("Agent run timed out after 30 seconds")
            return False
        finally:
            signal.alarm(0)
            
    except Exception as e:
        print(f"RefinireAgent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Run all diagnostic tests"""
    print("LMStudio Connection Diagnostic")
    print("=" * 50)
    
    # Test 1: Direct API call
    api_ok = test_direct_api()
    
    # Test 2: RefinireAgent
    if api_ok:
        agent_ok = test_refinire_agent()
        
        if not agent_ok:
            print("\n❌ RefinireAgent connection failed")
            print("This suggests an issue with RefinireAgent's LMStudio integration")
    else:
        print("\n❌ Direct API test failed")
        print("Check that LMStudio is running and the model is loaded")
    
    print("\n" + "=" * 50)


if __name__ == '__main__':
    main()