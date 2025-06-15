"""
Example of using OpenAI Agents with streaming responses from Ollama
OllamaからのストリーミングレスポンスをOpenAI Agentsで使用する例
"""

import asyncio
import sys
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner
from refinire import OllamaModel

async def main():
    """
    Main function to demonstrate streaming with Ollama
    Ollamaでのストリーミングを実演するメイン関数
    """
    # Create an agent with the Ollama model
    # OllamaモデルでAgentを作成
    agent = Agent(
        name="Streaming Assistant",
        instructions="""You are a helpful assistant that responds in Japanese.
あなたは日本語で応答する親切なアシスタントです。""",
        model=OllamaModel(
            model="phi4-mini:latest",
            temperature=0.3
        )
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
    asyncio.run(main()) 
