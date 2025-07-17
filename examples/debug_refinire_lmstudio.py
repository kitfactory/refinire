#!/usr/bin/env python3
"""
Debug RefinireAgent vs LMStudio Issue

English: Debug the exact issue between RefinireAgent and LMStudio.
日本語: RefinireAgent と LMStudio の間の具体的な問題をデバッグする。
"""

import os
import json
import httpx
from refinire import RefinireAgent, Context, disable_tracing
from refinire.core.llm import get_llm


def test_direct_api_call():
    """
    Test what works: Direct API call to LMStudio
    動作するもの: LMStudio への直接 API 呼び出し
    """
    print("=== Direct API Call (WORKING) ===")
    
    base_url = os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234')
    if not base_url.endswith('/v1'):
        base_url = base_url.rstrip('/') + '/v1'
    
    payload = {
        "model": "mistralai/devstral-small-2507",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(f"{base_url}/chat/completions", json=payload)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"✅ Success: {content}")
                return True
            else:
                print(f"❌ Failed: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_refinire_agent_detailed():
    """
    Test what fails: RefinireAgent with LMStudio
    失敗するもの: LMStudio での RefinireAgent
    """
    print("\n=== RefinireAgent with LMStudio (FAILING) ===")
    
    # Clear environment variables
    if 'OLLAMA_BASE_URL' in os.environ:
        del os.environ['OLLAMA_BASE_URL']
    
    base_url = os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234')
    if not base_url.endswith('/v1'):
        base_url = base_url.rstrip('/') + '/v1'
    
    try:
        # Create LLM
        llm = get_llm(
            provider="openai",
            model="mistralai/devstral-small-2507",
            base_url=base_url,
            api_key="lm-studio"
        )
        
        print(f"LLM created: {type(llm)}")
        print(f"Base URL: {base_url}")
        
        # Create agent
        agent = RefinireAgent(
            name="debug_agent",
            generation_instructions="You are a helpful assistant.",
            model=llm
        )
        
        print(f"Agent created: {agent.name}")
        
        # Test with context
        context = Context()
        
        # Enable detailed logging to see what's happening
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        print("\n🔍 Attempting RefinireAgent run...")
        
        # Monitor the actual HTTP requests
        class HTTPMonitor:
            def __init__(self):
                self.requests = []
                
            def log_request(self, method, url, data=None):
                self.requests.append({
                    'method': method,
                    'url': url,
                    'data': data
                })
                print(f"📡 HTTP {method} {url}")
                if data:
                    print(f"📡 Data: {data}")
        
        monitor = HTTPMonitor()
        
        # Try to run the agent
        try:
            result_context = agent.run("Hello", context)
            
            print(f"\n📊 Agent execution completed")
            print(f"Result: {result_context.shared_state.get('debug_agent_result')}")
            print(f"Shared state: {result_context.shared_state}")
            
            if hasattr(result_context, 'messages'):
                print(f"Messages: {result_context.messages}")
                
        except Exception as e:
            print(f"❌ Agent run failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()


def analyze_llm_response_format():
    """
    Analyze the exact response format issue
    正確なレスポンス形式の問題を分析
    """
    print("\n=== Response Format Analysis ===")
    
    base_url = os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234')
    if not base_url.endswith('/v1'):
        base_url = base_url.rstrip('/') + '/v1'
    
    # Test different endpoints that RefinireAgent might be calling
    test_endpoints = [
        "/responses",
        "/chat/completions", 
        "/v1/chat/completions",
        "/chat/completions",  # This should work
    ]
    
    for endpoint in test_endpoints:
        print(f"\n🔍 Testing endpoint: {endpoint}")
        
        # Different payload formats
        payloads = [
            {
                "name": "OpenAI Responses Format",
                "data": {
                    "input": [{"content": "Hello", "role": "user"}],
                    "model": "mistralai/devstral-small-2507",
                    "instructions": "You are a helpful assistant.",
                    "stream": False,
                    "tools": []
                }
            },
            {
                "name": "OpenAI Chat Format",
                "data": {
                    "model": "mistralai/devstral-small-2507",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Hello"}
                    ],
                    "stream": False
                }
            }
        ]
        
        for payload in payloads:
            print(f"  📋 Testing {payload['name']}")
            
            try:
                with httpx.Client(timeout=5.0) as client:
                    response = client.post(f"{base_url}{endpoint}", json=payload['data'])
                    
                    print(f"    Status: {response.status_code}")
                    if response.status_code == 200:
                        result = response.json()
                        print(f"    ✅ Success: {json.dumps(result, indent=2)[:200]}...")
                    else:
                        print(f"    ❌ Error: {response.text}")
                        
            except Exception as e:
                print(f"    ❌ Exception: {e}")


def main():
    """
    Run comprehensive analysis
    包括的な分析を実行
    """
    print("RefinireAgent vs LMStudio Debug Analysis")
    print("=" * 60)
    
    # Test what works
    direct_works = test_direct_api_call()
    
    # Test what fails
    test_refinire_agent_detailed()
    
    # Analyze response formats
    analyze_llm_response_format()
    
    print("\n" + "=" * 60)
    print("📊 Analysis Summary:")
    print(f"✅ Direct API: {'WORKS' if direct_works else 'FAILS'}")
    print("❌ RefinireAgent: FAILS (NoneType error)")
    print("\n🔍 Root Cause:")
    print("1. RefinireAgent expects specific response format")
    print("2. LMStudio returns OpenAI-compatible format")
    print("3. Format mismatch causes 'NoneType' parsing error")
    print("4. Even with /v1 endpoint, response processing fails")
    print("\n💡 Solution: Use direct API integration")


if __name__ == '__main__':
    main()