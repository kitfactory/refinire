"""
Example script demonstrating how to get available models from different providers.

English:
Example script demonstrating how to get available models from different providers.

日本語:
異なるプロバイダーから利用可能なモデルを取得する方法を示すサンプルスクリプト。
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire.llm import get_available_models, get_available_models_async


async def main():
    """
    Main function to demonstrate getting available models.
    
    English:
    Main function to demonstrate getting available models.
    
    日本語:
    利用可能なモデルの取得を実演するメイン関数。
    """
    print("🚀 Getting available models from different providers...")
    print("=" * 60)
    
    # Example 1: Get models from all providers
    print("\n📋 Example 1: Getting models from all providers")
    try:
        all_providers = ["openai", "google", "anthropic", "ollama"]
        models = await get_available_models_async(all_providers)
        
        for provider, model_list in models.items():
            print(f"\n🔹 {provider.upper()} Models:")
            if model_list:
                for model in model_list:
                    print(f"  • {model}")
            else:
                print(f"  ⚠️  No models available (provider may be offline)")
    except Exception as e:
        print(f"❌ Error getting all models: {e}")
    
    # Example 2: Get models from specific providers only
    print("\n📋 Example 2: Getting models from OpenAI and Google only")
    try:
        specific_providers = ["openai", "google"]
        models = await get_available_models_async(specific_providers)
        
        for provider, model_list in models.items():
            print(f"\n🔹 {provider.upper()} Models:")
            for model in model_list:
                print(f"  • {model}")
    except Exception as e:
        print(f"❌ Error getting specific models: {e}")
    
    # Example 3: Get Ollama models with custom base URL
    print("\n📋 Example 3: Getting Ollama models with custom base URL")
    try:
        custom_ollama_url = "http://localhost:11434"  # Default Ollama URL
        models = await get_available_models_async(["ollama"], ollama_base_url=custom_ollama_url)
        
        print(f"\n🔹 OLLAMA Models (from {custom_ollama_url}):")
        if models["ollama"]:
            for model in models["ollama"]:
                print(f"  • {model}")
        else:
            print("  ⚠️  No Ollama models found (Ollama may not be running)")
    except Exception as e:
        print(f"❌ Error getting Ollama models: {e}")
    
    # Example 4: Using synchronous version
    print("\n📋 Example 4: Using synchronous version")
    try:
        models = get_available_models(["openai"])
        print(f"\n🔹 OPENAI Models (sync):")
        for model in models["openai"]:
            print(f"  • {model}")
    except Exception as e:
        print(f"❌ Error getting models synchronously: {e}")
    
    print("\n✅ Examples completed!")


def sync_example():
    """
    Synchronous example for users who prefer sync code.
    
    English:
    Synchronous example for users who prefer sync code.
    
    日本語:
    同期コードを好むユーザー向けの同期例。
    """
    print("\n🔄 Synchronous Example")
    print("=" * 30)
    
    try:
        # Get models from multiple providers synchronously
        providers = ["openai", "google", "anthropic"]
        models = get_available_models(providers)
        
        for provider, model_list in models.items():
            print(f"\n🔹 {provider.upper()} Models:")
            for model in model_list:
                print(f"  • {model}")
                
    except Exception as e:
        print(f"❌ Error in sync example: {e}")


if __name__ == "__main__":
    print("🎯 Available Models Example")
    print("This example demonstrates how to get available models from different LLM providers.")
    print("このサンプルは、異なる LLM プロバイダーから利用可能なモデルを取得する方法を示します。")
    
    # Run async examples
    asyncio.run(main())
    
    # Run sync example
    sync_example()
    
    print("\n💡 Tips:")
    print("  • For Ollama, make sure the Ollama server is running")
    print("  • You can set OLLAMA_BASE_URL environment variable for custom Ollama URLs")
    print("  • Use the sync version if you're working in a non-async context")
    print("\n💡 ヒント:")
    print("  • Ollama の場合、Ollama サーバーが実行されていることを確認してください")
    print("  • カスタム Ollama URL には OLLAMA_BASE_URL 環境変数を設定できます")
    print("  • 非同期でないコンテキストで作業している場合は、同期版を使用してください") 
