"""
Example of using ClaudeModel with streaming responses in OpenAI Agents
OpenAI Agentsでストリーミングレスポンスを使用したClaudeモデルの例
"""

import asyncio
import os
import sys
from openai.types.responses import ResponseTextDeltaEvent
from agents.agent import Agent
from agents.run import Runner
from refinire.core import ClaudeModel

async def main():
    """
    Main function to demonstrate streaming with Claude
    Claudeでのストリーミングを実演するメイン関数
    """
    # Get API key from environment variable
    # 環境変数からAPIキーを取得
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    
    # Initialize the Claude model
    # Claudeモデルを初期化
    model = ClaudeModel(
        model="claude-3-sonnet-20240229",  # or "claude-3-haiku-20240307", "claude-3-opus-20240229"
        temperature=0.3,
        api_key=api_key,
        thinking=True  # Enable thinking for complex reasoning
    )
    
    # Create an agent with the model
    # モデルを使用してエージェントを作成
    agent = Agent(
        name="Japanese Streaming Assistant",
        instructions="You are a helpful assistant that always responds in Japanese.",
        model=model
    )
    
    # Get user input or use default
    # ユーザー入力を取得するか、デフォルトを使用
    user_input = sys.argv[1] if len(sys.argv) > 1 else "あなたの名前と、できることを教えてください。"
    
    print(f"User: {user_input}")
    print("Assistant: ", end="", flush=True)
    
    # Run the agent with streaming enabled
    # ストリーミングを有効にしてエージェントを実行
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
    # Disable tracing since we're not using OpenAI's API
    # OpenAIのAPIを使用しないのでトレースを無効化
    from agents import set_tracing_disabled
    set_tracing_disabled(True)
    
    asyncio.run(main()) 
