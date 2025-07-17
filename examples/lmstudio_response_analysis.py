#!/usr/bin/env python3
"""
LMStudio Response Analysis

English: Analyze LMStudio API responses to understand integration issues.
日本語: LMStudio API レスポンスを分析して統合問題を理解する。
"""

import os
import json
import httpx
from typing import Dict, Any


def analyze_lmstudio_response():
    """
    Analyze LMStudio API response format
    LMStudio API レスポンス形式を分析
    """
    print("=== LMStudio Response Analysis ===")
    
    base_url = os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234')
    model_name = "mistralai/devstral-small-2507"
    
    print(f"Base URL: {base_url}")
    print(f"Model: {model_name}")
    
    # Test different request formats
    test_cases = [
        {
            "name": "Simple Chat",
            "payload": {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
                "temperature": 0.7,
                "max_tokens": 100
            }
        },
        {
            "name": "With System Message",
            "payload": {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is 2+2?"}
                ],
                "temperature": 0.7,
                "max_tokens": 50
            }
        },
        {
            "name": "Streaming Disabled",
            "payload": {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": "Tell me a joke"}
                ],
                "temperature": 0.7,
                "max_tokens": 100,
                "stream": False
            }
        }
    ]
    
    try:
        with httpx.Client(timeout=30.0) as client:
            for test_case in test_cases:
                print(f"\n--- {test_case['name']} ---")
                
                # Make request
                response = client.post(
                    f"{base_url}/v1/chat/completions",
                    json=test_case['payload']
                )
                
                print(f"Status Code: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"Response Structure:")
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                    
                    # Analyze key fields
                    print(f"\nKey Analysis:")
                    print(f"  ID: {result.get('id', 'N/A')}")
                    print(f"  Object: {result.get('object', 'N/A')}")
                    print(f"  Model: {result.get('model', 'N/A')}")
                    print(f"  Created: {result.get('created', 'N/A')}")
                    
                    choices = result.get('choices', [])
                    if choices:
                        choice = choices[0]
                        print(f"  Choice Index: {choice.get('index', 'N/A')}")
                        print(f"  Finish Reason: {choice.get('finish_reason', 'N/A')}")
                        
                        message = choice.get('message', {})
                        print(f"  Message Role: {message.get('role', 'N/A')}")
                        print(f"  Message Content: {message.get('content', 'N/A')}")
                    
                    usage = result.get('usage', {})
                    if usage:
                        print(f"  Usage: {usage}")
                        
                else:
                    print(f"Error Response: {response.text}")
                
                print("-" * 50)
                
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()


def compare_with_openai_format():
    """
    Compare LMStudio response with expected OpenAI format
    LMStudio レスポンスと期待される OpenAI 形式を比較
    """
    print("\n=== OpenAI Format Comparison ===")
    
    # Expected OpenAI response format
    expected_openai_format = {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-3.5-turbo-0613",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello! How can I assist you today?"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    }
    
    print("Expected OpenAI Format:")
    print(json.dumps(expected_openai_format, indent=2))
    
    # Get actual LMStudio response
    print("\nActual LMStudio Response:")
    base_url = os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234')
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(f"{base_url}/v1/chat/completions", json={
                "model": "mistralai/devstral-small-2507",
                "messages": [{"role": "user", "content": "Hello"}],
                "temperature": 0.7,
                "max_tokens": 50
            })
            
            if response.status_code == 200:
                lmstudio_response = response.json()
                print(json.dumps(lmstudio_response, indent=2, ensure_ascii=False))
                
                # Compare fields
                print("\nField Comparison:")
                expected_fields = ["id", "object", "created", "model", "choices", "usage"]
                
                for field in expected_fields:
                    expected_value = expected_openai_format.get(field)
                    actual_value = lmstudio_response.get(field)
                    
                    if field == "choices" and actual_value:
                        # Compare choice structure
                        exp_choice = expected_value[0] if expected_value else {}
                        act_choice = actual_value[0] if actual_value else {}
                        
                        print(f"  {field}:")
                        print(f"    Expected keys: {list(exp_choice.keys())}")
                        print(f"    Actual keys: {list(act_choice.keys())}")
                        
                        if "message" in act_choice:
                            exp_msg = exp_choice.get("message", {})
                            act_msg = act_choice.get("message", {})
                            print(f"    Message Expected: {list(exp_msg.keys())}")
                            print(f"    Message Actual: {list(act_msg.keys())}")
                    else:
                        print(f"  {field}: Present={field in lmstudio_response}, Type={type(actual_value)}")
                
            else:
                print(f"Failed to get response: {response.status_code}")
                
    except Exception as e:
        print(f"Comparison failed: {e}")


def analyze_request_variations():
    """
    Test different request variations to identify compatibility issues
    互換性問題を特定するために異なるリクエストバリエーションをテスト
    """
    print("\n=== Request Variation Analysis ===")
    
    base_url = os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234')
    model_name = "mistralai/devstral-small-2507"
    
    variations = [
        {
            "name": "Minimal Request",
            "payload": {
                "model": model_name,
                "messages": [{"role": "user", "content": "Hi"}]
            }
        },
        {
            "name": "With All Standard Fields",
            "payload": {
                "model": model_name,
                "messages": [{"role": "user", "content": "Hi"}],
                "temperature": 0.7,
                "max_tokens": 100,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "stream": False
            }
        },
        {
            "name": "With Functions (if supported)",
            "payload": {
                "model": model_name,
                "messages": [{"role": "user", "content": "What's the weather?"}],
                "functions": [
                    {
                        "name": "get_weather",
                        "description": "Get weather information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {"type": "string"}
                            }
                        }
                    }
                ]
            }
        }
    ]
    
    try:
        with httpx.Client(timeout=15.0) as client:
            for variation in variations:
                print(f"\n--- {variation['name']} ---")
                
                try:
                    response = client.post(
                        f"{base_url}/v1/chat/completions",
                        json=variation['payload']
                    )
                    
                    print(f"Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ Success")
                        print(f"Content: {result.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')}")
                        
                        # Check for any special fields
                        special_fields = ['function_call', 'tool_calls', 'logprobs']
                        choice = result.get('choices', [{}])[0]
                        for field in special_fields:
                            if field in choice:
                                print(f"Special field '{field}': {choice[field]}")
                                
                    else:
                        print(f"❌ Failed: {response.text}")
                        
                except Exception as e:
                    print(f"❌ Exception: {e}")
                    
    except Exception as e:
        print(f"Variation analysis failed: {e}")


def main():
    """
    Run all analysis functions
    すべての分析関数を実行
    """
    print("LMStudio API Response Analysis")
    print("=" * 60)
    
    analyze_lmstudio_response()
    compare_with_openai_format()
    analyze_request_variations()
    
    print("\n" + "=" * 60)
    print("Analysis Complete")


if __name__ == '__main__':
    main()