"""
Example of using UnifiedModel with OpenAI Agents
OpenAI AgentsでUnifiedModelを使用する例
"""

import asyncio
import os
import sys
from agents.agent import Agent
from agents.run import Runner
from agents_sdk_models import UnifiedModel

async def main():
    """
    Main function to demonstrate using the UnifiedModel
    UnifiedModelの使用法を実演するメイン関数
    """
    # Get provider from command line or use default
    # コマンドラインからプロバイダーを取得するか、デフォルトを使用
    provider = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Get model from command line or let UnifiedModel use default
    # コマンドラインからモデルを取得するか、UnifiedModelにデフォルトを使用させる
    model = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Get API key based on provider
    # プロバイダーに基づいてAPIキーを取得
    api_key = None
    # Use provider or default to "openai" for API key lookup
    # APIキー検索のためにプロバイダーを使用するか、デフォルトで "openai" を使用
    provider_for_key = provider if provider else "openai"
    
    if provider_for_key == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
    elif provider_for_key == "gemini":
        api_key = os.environ.get("GOOGLE_API_KEY")
    elif provider_for_key == "claude":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    # Check if API key is needed and available
    # APIキーが必要かつ利用可能かチェック
    if provider_for_key in ["openai", "gemini", "claude"] and not api_key:
        raise ValueError(f"API key for {provider_for_key} is required")
    
    # Initialize the unified model
    # 統合モデルを初期化
    model_args = {
        "temperature": 0.3
    }
    
    # Add provider if specified
    # 指定されている場合はプロバイダーを追加
    if provider:
        model_args["provider"] = provider
    
    # Add model if specified
    # 指定されている場合はモデルを追加
    if model:
        model_args["model"] = model
    
    # Add API key if needed
    # 必要に応じてAPIキーを追加
    if api_key:
        model_args["api_key"] = api_key
    
    # Add thinking for Claude
    # Claudeの場合は拡張思考を追加
    if provider_for_key == "claude":
        model_args["thinking"] = True
    
    # Create the unified model
    # 統合モデルを作成
    unified_model = UnifiedModel(**model_args)
    
    # Create an agent with the unified model
    # 統合モデルでエージェントを作成
    agent = Agent(
        name="Unified Assistant",
        instructions="""You are a helpful assistant that responds in Japanese.
あなたは日本語で応答する親切なアシスタントです。""",
        model=unified_model
    )
    
    # Get user input or use default
    # ユーザー入力を取得するか、デフォルトを使用
    user_input = sys.argv[3] if len(sys.argv) > 3 else "あなたの名前と、できることを教えてください。"
    
    print(f"Provider: {unified_model.provider}")
    print(f"Model: {unified_model.model}")
    print(f"User: {user_input}")
    print("Assistant: ", end="", flush=True)
    
    # Run the agent with streaming enabled
    # ストリーミングを有効にしてエージェントを実行
    from openai.types.responses import ResponseTextDeltaEvent
    result = Runner.run_streamed(agent, input=user_input)
    
    # Process the streaming events
    # ストリーミングイベントを処理
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
    
    # Print newline at the end
    # 最後に改行を出力
    print()

if __name__ == "__main__":
    # Disable tracing for non-OpenAI providers
    # OpenAI以外のプロバイダーの場合はトレースを無効化
    provider = sys.argv[1] if len(sys.argv) > 1 else "openai"
    if provider != "openai":
        from agents import set_tracing_disabled
        set_tracing_disabled(True)
    
    asyncio.run(main()) 