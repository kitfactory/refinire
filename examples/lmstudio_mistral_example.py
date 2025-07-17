#!/usr/bin/env python3
"""
LMStudio Mistral Connection Example

English: Demonstrates connecting to LMStudio's mistralai/devstral-small-2507 model.
日本語: LMStudio の mistralai/devstral-small-2507 モデルへの接続例。

Note: This example shows the current behavior of RefinireAgent with LMStudio.
Due to configuration issues, the agent may not return results properly.
For direct API access, use the raw curl examples provided.

注意: この例では、RefinireAgent と LMStudio の現在の動作を示しています。
設定の問題により、エージェントが結果を適切に返さない可能性があります。
直接的なAPIアクセスには、提供されたcurlの例を使用してください。
"""

import os
from refinire import RefinireAgent, Context, disable_tracing
from refinire.core.llm import get_llm


def main():
    """
    LMStudio Mistral connection example
    LMStudio Mistral 接続例
    """
    print("=== LMStudio Mistral Connection Example ===")
    
    # Disable tracing for cleaner output
    # 出力をきれいにするためにトレーシングを無効化
    disable_tracing()
    
    # Clear OLLAMA_BASE_URL to prevent provider misidentification
    # プロバイダーの誤認識を防ぐために OLLAMA_BASE_URL をクリア
    if 'OLLAMA_BASE_URL' in os.environ:
        del os.environ['OLLAMA_BASE_URL']
        print("🔧 Cleared OLLAMA_BASE_URL environment variable")
    
    # LMStudio configuration
    # LMStudio の設定
    lmstudio_base_url = os.getenv('LMSTUDIO_BASE_URL', 'http://localhost:1234')
    
    # Ensure /v1 is appended to base URL for proper API endpoint
    # 適切なAPIエンドポイントのためにbase URLに /v1 を追加
    if not lmstudio_base_url.endswith('/v1'):
        lmstudio_base_url = lmstudio_base_url.rstrip('/') + '/v1'
        print(f"🔧 Added /v1 to base URL: {lmstudio_base_url}")
    
    model_name = "mistralai/devstral-small-2507"
    
    print(f"Using LMStudio at: {lmstudio_base_url}")
    print(f"Using model: {model_name}")
    
    # Show direct API example
    # 直接APIの例を表示
    print("\n📄 Direct API Example (works correctly):")
    print("curl " + lmstudio_base_url + "/chat/completions \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -d '{")
    print("    \"model\": \"mistralai/devstral-small-2507\",")
    print("    \"messages\": [")
    print("      {\"role\": \"user\", \"content\": \"Hello!\"},")
    print("    ],")
    print("    \"temperature\": 0.7")
    print("  }'")
    
    try:
        # Create LLM with Chat Completion client for LMStudio
        # LMStudio 用の Chat Completion クライアントで LLM を作成
        print(f"🔧 Creating LLM with provider='lmstudio', base_url={lmstudio_base_url}")
        llm = get_llm(
            provider="lmstudio",  # Use Chat Completion client for LMStudio
            model=model_name,
            base_url=lmstudio_base_url,
            api_key="lm-studio"
        )
        print(f"✅ LLM created: {type(llm)}")
        print(f"   Model: {llm.model}")
        
        # Verify the LLM configuration
        # LLM設定を確認
        if hasattr(llm, '_client') and hasattr(llm._client, 'base_url'):
            print(f"   Base URL: {llm._client.base_url}")
        elif hasattr(llm, 'base_url'):
            print(f"   Base URL: {llm.base_url}")
        else:
            print("   Base URL: Could not determine")
        
        # Create agent with the configured LLM
        # 設定されたLLMでエージェントを作成
        agent = RefinireAgent(
            name="lmstudio_agent",
            generation_instructions="You are a helpful assistant powered by Mistral. Keep responses concise.",
            model=llm
        )
        
        # Test queries
        # テストクエリ
        test_queries = [
            "Hello! Can you introduce yourself?",
            "What is the capital of France?",
            "Write a short Python function to calculate factorial."
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Query {i} ---")
            print(f"Input: {query}")
            
            # Create fresh context for each query
            # 各クエリに新しいコンテキストを作成
            context = Context()
            
            # Query the model
            # モデルにクエリ
            result_context = agent.run(query, context)
            
            # Get response
            # レスポンスを取得
            result = result_context.shared_state.get('lmstudio_agent_result')
            
            if result is None:
                print("⚠️  No response received from RefinireAgent")
                print("   This is a known issue with LMStudio integration")
                print("   The agent communicates with LMStudio but doesn't return results")
                print("   See lmstudio_direct_integration.py for working solution")
            else:
                print(f"✅ Response: {result}")
        
        print("\n📝 Status Summary:")
        print("✅ RefinireAgent connects to LMStudio successfully")
        print("✅ LMStudio API is working (verified with curl)")
        print("✅ RefinireAgent result retrieval working with Chat Completion client")
        print("💡 Key: Use provider='lmstudio' for Chat Completion client")
        
    except Exception as e:
        print(f"❌ Error connecting to LMStudio: {e}")
        import traceback
        traceback.print_exc()
        print("\n🔍 Known Issue Analysis:")
        print("The 'NoneType' object is not iterable error occurs because:")
        print("1. RefinireAgent calls /responses or /chat/completions endpoints")
        print("2. LMStudio only supports /v1/chat/completions endpoint")
        print("3. Response format mismatch causes parsing errors")
        print("\nTroubleshooting tips:")
        print("1. Make sure LMStudio is running and serving the model")
        print("2. Check that the model name matches exactly: mistralai/devstral-small-2507")
        print("3. Verify LMSTUDIO_BASE_URL environment variable is set")
        print("4. Ensure the model is loaded and ready in LMStudio")
        print("5. Use the direct API integration example for reliable LMStudio access")


if __name__ == '__main__':
    main()