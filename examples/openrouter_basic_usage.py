#!/usr/bin/env python3
"""
OpenRouter Basic Usage Example
OpenRouter基本使用例

This example demonstrates basic OpenRouter integration with Refinire.
この例は、RefinireでのOpenRouterの基本的な統合を示します。

Before running this example, ensure you have:
この例を実行する前に、以下を確認してください：
1. Set OPENROUTER_API_KEY environment variable
   OPENROUTER_API_KEY環境変数を設定
2. Install refinire: pip install -e .
   refinireをインストール: pip install -e .
"""

import os
import asyncio
from refinire.core.llm import get_llm
from refinire.agents.pipeline.llm_pipeline import RefinireAgent
from refinire.agents.flow.context import Context
from refinire import (
    RefinireConnectionError, RefinireTimeoutError, RefinireAuthenticationError,
    RefinireRateLimitError, RefinireAPIError, RefinireModelError
)

# Clear other provider environment variables to ensure OpenRouter is used
# 他のプロバイダーの環境変数をクリアしてOpenRouterが使用されるようにする
os.environ.pop('OLLAMA_API_KEY', None)
os.environ.pop('LMSTUDIO_API_KEY', None)
os.environ.pop('OLLAMA_BASE_URL', None)
os.environ.pop('LMSTUDIO_BASE_URL', None)

async def basic_openrouter_example():
    """
    Basic OpenRouter usage with different popular models using RefinireAgent
    RefinireAgentを使用した異なる人気モデルでのOpenRouterの基本使用
    """
    print("=== OpenRouter Basic Usage Example ===")
    print("=== OpenRouter基本使用例 ===\n")
    
    # Example 1: Using Meta Llama 3 8B Instruct (cost-effective)
    # 例1: Meta Llama 3 8B Instruct使用（コスト効率的）
    print("1. Using Meta Llama 3 8B Instruct:")
    print("1. Meta Llama 3 8B Instructを使用:")
    
    try:
        agent = RefinireAgent(
            name="openrouter_llama_agent",
            generation_instructions="You are a helpful assistant. Answer questions clearly and concisely.",
            model="openrouter://meta-llama/llama-3-8b-instruct",
            temperature=0.7
        )
        
        ctx = Context()
        result_ctx = await agent.run_async("Explain what OpenRouter is in one sentence.", ctx)
        
        print(f"Response: {result_ctx.result}")
        print(f"Model: meta-llama/llama-3-8b-instruct")
        print()
        
    except RefinireConnectionError as e:
        print(f"Connection failed with Llama 3 8B: {e}")
        print(f"Llama 3 8Bでの接続失敗: {e}")
        print("Check your internet connection and OpenRouter service status.")
        print("インターネット接続とOpenRouterサービスの状態を確認してください。")
    except RefinireTimeoutError as e:
        print(f"Request timed out with Llama 3 8B: {e}")
        print(f"Llama 3 8Bでのリクエストタイムアウト: {e}")
        print("The request took too long. Try again later.")
        print("リクエストに時間がかかりすぎました。後でもう一度お試しください。")
    except RefinireAuthenticationError as e:
        print(f"Authentication failed with Llama 3 8B: {e}")
        print(f"Llama 3 8Bでの認証失敗: {e}")
        print("Check your OPENROUTER_API_KEY environment variable.")
        print("OPENROUTER_API_KEY環境変数を確認してください。")
    except RefinireRateLimitError as e:
        print(f"Rate limit exceeded with Llama 3 8B: {e}")
        print(f"Llama 3 8Bでのレート制限超過: {e}")
        print("Wait before making another request or upgrade your plan.")
        print("次のリクエストまで待つか、プランをアップグレードしてください。")
    except RefinireAPIError as e:
        print(f"API error with Llama 3 8B: {e}")
        print(f"Llama 3 8BでのAPIエラー: {e}")
        print("OpenRouter API service issue. Check status page.")
        print("OpenRouter APIサービスの問題。ステータスページを確認してください。")
    except RefinireModelError as e:
        print(f"Model error with Llama 3 8B: {e}")
        print(f"Llama 3 8Bでのモデルエラー: {e}")
        print("Model may be unavailable or overloaded.")
        print("モデルが利用できないか、過負荷状態の可能性があります。")
    except Exception as e:
        print(f"Unexpected error with Llama 3 8B: {e}")
        print(f"Llama 3 8Bでの予期しないエラー: {e}")
    
    # Example 2: Using OpenAI GPT-4 through OpenRouter
    # 例2: OpenRouter経由でのOpenAI GPT-4使用
    print("2. Using OpenAI GPT-4 through OpenRouter:")
    print("2. OpenRouter経由でのOpenAI GPT-4使用:")
    
    try:
        agent = RefinireAgent(
            name="openrouter_gpt4_agent",
            generation_instructions="You are a helpful assistant. Provide detailed and informative responses.",
            model="openrouter://openai/gpt-4",
            temperature=0.5
        )
        
        ctx = Context()
        result_ctx = await agent.run_async("What are the advantages of using OpenRouter?", ctx)
        
        print(f"Response: {result_ctx.result}")
        print(f"Model: openai/gpt-4")
        print()
        
    except Exception as e:
        print(f"Error with GPT-4: {e}")
        print(f"GPT-4でのエラー: {e}")
    
    # Example 3: Using Anthropic Claude through OpenRouter
    # 例3: OpenRouter経由でのAnthropic Claude使用
    print("3. Using Anthropic Claude through OpenRouter:")
    print("3. OpenRouter経由でのAnthropic Claude使用:")
    
    try:
        agent = RefinireAgent(
            name="openrouter_claude_agent",
            generation_instructions="You are a helpful assistant. Compare and analyze topics objectively.",
            model="openrouter://anthropic/claude-3-haiku",
            temperature=0.3
        )
        
        ctx = Context()
        result_ctx = await agent.run_async("Compare OpenRouter with direct API access.", ctx)
        
        print(f"Response: {result_ctx.result}")
        print(f"Model: anthropic/claude-3-haiku")
        print()
        
    except Exception as e:
        print(f"Error with Claude: {e}")
        print(f"Claudeでのエラー: {e}")

async def structured_output_example():
    """
    Structured output example with OpenRouter using RefinireAgent
    RefinireAgentを使用したOpenRouterでの構造化出力の例
    """
    from pydantic import BaseModel, Field
    
    print("=== Structured Output Example ===")
    print("=== 構造化出力例 ===\n")
    
    class TaskAnalysis(BaseModel):
        task_type: str = Field(description="Type of task (coding, writing, analysis, etc.)")
        difficulty: str = Field(description="Difficulty level (easy, medium, hard)")
        estimated_time: str = Field(description="Estimated completion time")
        requirements: list[str] = Field(description="List of requirements")
    
    try:
        agent = RefinireAgent(
            name="openrouter_structured_agent",
            generation_instructions="You are a project analyst. Analyze tasks and provide structured information about them.",
            model="openrouter://meta-llama/llama-3-8b-instruct",
            output_model=TaskAnalysis,
            temperature=0.2
        )
        
        ctx = Context()
        result_ctx = await agent.run_async("Analyze this task: 'Create a REST API for a todo application with authentication'", ctx)
        
        result = result_ctx.content
        
        print("Task Analysis Result:")
        print("タスク分析結果:")
        print(f"  Task Type: {result.task_type}")
        print(f"  Difficulty: {result.difficulty}")
        print(f"  Estimated Time: {result.estimated_time}")
        print(f"  Requirements: {', '.join(result.requirements)}")
        print()
        
    except Exception as e:
        print(f"Error with structured output: {e}")
        print(f"構造化出力でのエラー: {e}")

async def conversation_example():
    """
    Multi-turn conversation example with OpenRouter using RefinireAgent
    RefinireAgentを使用したOpenRouterでの多ターン会話の例
    """
    print("=== Conversation Example ===")
    print("=== 会話例 ===\n")
    
    try:
        agent = RefinireAgent(
            name="openrouter_conversation_agent",
            generation_instructions="You are a technology consultant. Provide helpful advice about web development technologies.",
            model="openrouter://meta-llama/llama-3-8b-instruct",
            temperature=0.6
        )
        
        # First turn / 最初のターン
        ctx = Context()
        result_ctx1 = await agent.run_async("I'm planning to build a web application. What technology stack would you recommend?", ctx)
        
        print("User: I'm planning to build a web application. What technology stack would you recommend?")
        print("ユーザー: Webアプリケーションを構築予定です。どのテクノロジースタックを推奨しますか？")
        print(f"Assistant: {result_ctx1.result}")
        print()
        
        # Second turn / 2回目のターン
        result_ctx2 = await agent.run_async("The application needs to handle real-time data and have mobile support. Does this change your recommendation?", result_ctx1)
        
        print("User: The application needs to handle real-time data and have mobile support. Does this change your recommendation?")
        print("ユーザー: アプリケーションはリアルタイムデータを扱い、モバイルサポートが必要です。これで推奨事項は変わりますか？")
        print(f"Assistant: {result_ctx2.result}")
        print()
        
    except Exception as e:
        print(f"Error with conversation: {e}")
        print(f"会話でのエラー: {e}")

async def main():
    """
    Main function to run all examples
    全ての例を実行するメイン関数
    """
    # Check if OpenRouter API key is set
    # OpenRouter APIキーが設定されているかチェック
    if not os.getenv('OPENROUTER_API_KEY'):
        print("ERROR: OPENROUTER_API_KEY environment variable not set")
        print("エラー: OPENROUTER_API_KEY環境変数が設定されていません")
        print("Please set it with: export OPENROUTER_API_KEY=your_api_key")
        print("次のコマンドで設定してください: export OPENROUTER_API_KEY=your_api_key")
        return
    
    print("OpenRouter API Key found. Running examples...")
    print("OpenRouter APIキーが見つかりました。例を実行中...")
    print("=" * 50)
    print()
    
    # Run examples / 例を実行
    await basic_openrouter_example()
    await structured_output_example()
    await conversation_example()
    
    print("=" * 50)
    print("All examples completed successfully!")
    print("すべての例が正常に完了しました！")

async def network_error_handling_example():
    """
    Demonstrate network error handling with OpenRouter
    OpenRouterでのネットワークエラーハンドリングを実演
    """
    print("\n=== Network Error Handling Example ===")
    print("=== ネットワークエラーハンドリング例 ===\n")
    
    # Example of comprehensive error handling
    # 包括的なエラーハンドリングの例
    def handle_network_errors(model_name: str, task_description: str):
        """
        Utility function to handle network errors consistently
        ネットワークエラーを一貫して処理するユーティリティ関数
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except RefinireConnectionError as e:
                    print(f"❌ Connection failed for {model_name}: {e}")
                    print(f"❌ {model_name}での接続失敗: {e}")
                    return None
                except RefinireTimeoutError as e:
                    print(f"⏱️ Request timed out for {model_name}: {e}")
                    print(f"⏱️ {model_name}でのリクエストタイムアウト: {e}")
                    return None
                except RefinireAuthenticationError as e:
                    print(f"🔐 Authentication failed for {model_name}: {e}")
                    print(f"🔐 {model_name}での認証失敗: {e}")
                    return None
                except RefinireRateLimitError as e:
                    print(f"⚡ Rate limit exceeded for {model_name}: {e}")
                    print(f"⚡ {model_name}でのレート制限超過: {e}")
                    return None
                except RefinireAPIError as e:
                    print(f"🚫 API error for {model_name}: {e}")
                    print(f"🚫 {model_name}でのAPIエラー: {e}")
                    return None
                except RefinireModelError as e:
                    print(f"🤖 Model error for {model_name}: {e}")
                    print(f"🤖 {model_name}でのモデルエラー: {e}")
                    return None
                except Exception as e:
                    print(f"❓ Unexpected error for {model_name}: {e}")
                    print(f"❓ {model_name}での予期しないエラー: {e}")
                    return None
            return wrapper
        return decorator
    
    # Test with a potentially problematic model to demonstrate error handling
    # エラーハンドリングを実演するために問題のある可能性のあるモデルでテスト
    @handle_network_errors("test-model", "Error handling test")
    async def test_error_handling():
        agent = RefinireAgent(
            name="openrouter_error_test_agent",
            generation_instructions="You are a helpful assistant.",
            model="openrouter://meta-llama/llama-3-8b-instruct",
            temperature=0.7
        )
        
        ctx = Context()
        result_ctx = await agent.run_async("Test message", ctx)
        
        if result_ctx.result:
            print(f"✅ Success: {result_ctx.result[:50]}...")
            print(f"✅ 成功: {result_ctx.result[:50]}...")
        return result_ctx.result
    
    print("Testing error handling with decorator pattern:")
    print("デコレーターパターンでのエラーハンドリングをテスト:")
    
    result = await test_error_handling()
    
    if result:
        print("\n✅ Network error handling test completed successfully!")
        print("✅ ネットワークエラーハンドリングテストが正常に完了しました！")
    else:
        print("\n❌ Network error handling test failed (this is expected for demonstration)")
        print("❌ ネットワークエラーハンドリングテストが失敗しました（実演のため予想されます）")
    
    print("\n💡 Tips for robust error handling:")
    print("💡 堅牢なエラーハンドリングのためのヒント:")
    print("  - Always catch specific Refinire exceptions")
    print("  - 常に特定のRefinire例外をキャッチする")
    print("  - Provide helpful error messages to users")
    print("  - ユーザーに役立つエラーメッセージを提供する")
    print("  - Consider implementing retry logic for transient errors")
    print("  - 一時的なエラーに対するリトライロジックの実装を検討する")
    print("  - Log errors for debugging and monitoring")
    print("  - デバッグと監視のためにエラーをログに記録する")

if __name__ == "__main__":
    async def run_all_examples():
        await main()
        await network_error_handling_example()
    
    asyncio.run(run_all_examples())