"""
Example of using OpenAI Agents with streaming responses from Ollama
OllamaからのストリーミングレスポンスをOpenAI Agentsで使用する例
"""

import asyncio
from agents import Agent, Runner
from agents_sdk_models import OllamaAIChatCompletionsModel

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
        model=OllamaAIChatCompletionsModel(
            model="phi4-mini:latest",
            temperature=0.3
        )
    )

    # Run the agent and get the response
    # Agentを実行してレスポンスを取得
    response = await Runner.run(
        agent,
        "あなたの名前と、できることを教えてください。"
    )

    # Print the final output
    # 最終出力を表示
    print(response.final_output)

if __name__ == "__main__":
    asyncio.run(main()) 