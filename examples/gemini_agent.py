"""
Example of using GeminiModel with OpenAI Agents
OpenAI AgentsでGeminiModelを使用する例
"""

import asyncio
import os
from agents.agent import Agent
from agents.run import Runner
from refinire.core import GeminiModel

async def main():
    # Get API key from environment variable
    # 環境変数からAPIキーを取得
    api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    
    # Initialize the Gemini model
    # Geminiモデルを初期化
    model = GeminiModel(
        model="gemini-2.0-flash",  # or "gemini-2.0-pro", "gemini-2.0-ultra"
        temperature=0.3,
        api_key=api_key
    )
    
    # Create an agent with the model
    # モデルを使用してエージェントを作成
    agent = Agent(
        name="Japanese Assistant",
        instructions="You are a helpful assistant that always responds in Japanese.",
        model=model
    )
    
    # Run the agent with a simple query using Runner
    # Runnerを使用してエージェントに簡単な質問を実行
    response = await Runner.run(agent, "What is your name and what can you do?")
    
    # Print the final output
    # 最終出力を表示
    print(response.final_output)

if __name__ == "__main__":
    # Disable tracing since we're not using OpenAI's API
    # OpenAIのAPIを使用しないのでトレースを無効化
    from agents import set_tracing_disabled
    set_tracing_disabled(True)
    
    asyncio.run(main()) 
