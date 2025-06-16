"""
Example of using OllamaModel with OpenAI Agents v0.0.4
OpenAI Agents v0.0.4でOllamaModelを使用する例
"""

import asyncio
from agents.agent import Agent
from agents.run import Runner
from agents.items import ItemHelpers
from refinire.core import OllamaModel

async def main():
    # Initialize the Ollama model
    # Ollamaモデルを初期化
    model = OllamaModel(
        model="phi4-mini:latest",
        temperature=0.3
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
