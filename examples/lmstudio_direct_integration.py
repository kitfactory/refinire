#!/usr/bin/env python3
"""
LMStudio Direct Integration Example

English: Working example of direct LMStudio API integration bypassing RefinireAgent issues.
日本語: RefinireAgent の問題を回避した直接的な LMStudio API 統合の動作例。
"""

import os
import json
import httpx
from typing import Dict, Any, Optional


class LMStudioClient:
    """
    Direct LMStudio API client
    直接的な LMStudio API クライアント
    """
    
    def __init__(self, base_url: str = None, model: str = "mistralai/devstral-small-2507"):
        """
        Initialize LMStudio client
        LMStudio クライアントを初期化
        """
        self.base_url = base_url or os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234')
        self.model = model
        
    def chat_completion(
        self, 
        messages: list, 
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send chat completion request to LMStudio
        LMStudio にチャット補完リクエストを送信
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
                    
        except Exception as e:
            return {
                "error": f"Request failed: {str(e)}"
            }
    
    def simple_chat(self, user_input: str, system_prompt: str = None) -> Optional[str]:
        """
        Simple chat interface
        シンプルなチャットインターフェース
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        messages.append({"role": "user", "content": user_input})
        
        response = self.chat_completion(messages)
        
        if "error" in response:
            print(f"Error: {response['error']}")
            return None
            
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            print(f"Error parsing response: {e}")
            return None


def demonstrate_basic_usage():
    """
    Demonstrate basic LMStudio usage
    基本的な LMStudio 使用法を実演
    """
    print("=== Basic LMStudio Usage ===")
    
    client = LMStudioClient()
    
    # Test queries
    test_queries = [
        {
            "input": "Hello! Can you introduce yourself?",
            "system": "You are a helpful assistant powered by Mistral."
        },
        {
            "input": "What is the capital of France?",
            "system": "You are a knowledgeable geography assistant."
        },
        {
            "input": "Write a short Python function to calculate factorial.",
            "system": "You are a programming assistant. Provide clean, well-commented code."
        }
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"Input: {query['input']}")
        print(f"System: {query['system']}")
        
        response = client.simple_chat(query['input'], query['system'])
        
        if response:
            print(f"Response: {response}")
        else:
            print("❌ No response received")


def demonstrate_advanced_usage():
    """
    Demonstrate advanced LMStudio usage with conversation history
    会話履歴を使った高度な LMStudio 使用法を実演
    """
    print("\n=== Advanced LMStudio Usage (Conversation) ===")
    
    client = LMStudioClient()
    
    # Conversation example
    conversation = [
        {"role": "system", "content": "You are a helpful programming tutor."},
        {"role": "user", "content": "Can you explain what recursion is?"},
    ]
    
    print("Starting conversation...")
    
    # First exchange
    response = client.chat_completion(conversation)
    if "error" not in response:
        assistant_response = response["choices"][0]["message"]["content"]
        print(f"Assistant: {assistant_response}")
        
        # Add to conversation
        conversation.append({"role": "assistant", "content": assistant_response})
        conversation.append({"role": "user", "content": "Can you give me a simple example in Python?"})
        
        # Second exchange
        response = client.chat_completion(conversation)
        if "error" not in response:
            assistant_response = response["choices"][0]["message"]["content"]
            print(f"Assistant: {assistant_response}")
        else:
            print(f"Error in second exchange: {response['error']}")
    else:
        print(f"Error in first exchange: {response['error']}")


def demonstrate_streaming():
    """
    Demonstrate streaming responses (if supported)
    ストリーミング応答を実演（サポートされている場合）
    """
    print("\n=== Streaming Response Test ===")
    
    client = LMStudioClient()
    
    messages = [
        {"role": "system", "content": "You are a storyteller."},
        {"role": "user", "content": "Tell me a short story about a robot learning to paint."}
    ]
    
    response = client.chat_completion(messages, stream=False)  # LMStudio may not support streaming
    
    if "error" not in response:
        story = response["choices"][0]["message"]["content"]
        print(f"Story: {story}")
        
        # Show usage statistics
        usage = response.get("usage", {})
        print(f"\nUsage Statistics:")
        print(f"  Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
        print(f"  Completion tokens: {usage.get('completion_tokens', 'N/A')}")
        print(f"  Total tokens: {usage.get('total_tokens', 'N/A')}")
    else:
        print(f"Error: {response['error']}")


def check_server_status():
    """
    Check LMStudio server status and available models
    LMStudio サーバーの状態と利用可能なモデルを確認
    """
    print("=== Server Status Check ===")
    
    base_url = os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234')
    
    try:
        with httpx.Client(timeout=10.0) as client:
            # Check models endpoint
            response = client.get(f"{base_url}/v1/models")
            
            if response.status_code == 200:
                models = response.json()
                print(f"✅ Server is running at {base_url}")
                print(f"Available models:")
                for model in models.get('data', []):
                    print(f"  - {model['id']}")
            else:
                print(f"❌ Server responded with status {response.status_code}")
                
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        print(f"Make sure LMStudio is running at {base_url}")


def main():
    """
    Run all demonstration functions
    すべての実演関数を実行
    """
    print("LMStudio Direct Integration Example")
    print("=" * 60)
    
    # Check server first
    check_server_status()
    
    # Run demonstrations
    demonstrate_basic_usage()
    demonstrate_advanced_usage()
    demonstrate_streaming()
    
    print("\n" + "=" * 60)
    print("Integration Complete!")
    print("\n💡 Key Points:")
    print("✅ Direct API calls work reliably")
    print("✅ Full conversation history support")
    print("✅ Usage statistics available")
    print("✅ Error handling implemented")
    print("✅ Can be easily integrated into applications")


if __name__ == '__main__':
    main()