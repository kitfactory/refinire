import asyncio
import os
from agents import Agent, Runner
from refinire import get_llm


async def main():
    # Initialize the model using get_llm (Example uses Ollama's llama3)
    # get_llm を使用してモデルを初期化 (例は Ollama の llama3 を使用)
    # You can change the provider and model as needed.
    # 必要に応じてプロバイダーとモデルを変更できます。
    # Supported providers: "openai", "google", "anthropic", "ollama"
    # サポートされているプロバイダー: "openai", "google", "anthropic", "ollama"
    model = get_llm(
        provider="openai",  # Change provider here / プロバイダーをここで変更
        model="gpt-4o-mini",  # Change model name here / モデル名をここで変更
        # api_key=os.environ.get("YOUR_API_KEY_ENV_VAR") # Uncomment and set if using OpenAI, Google, or Anthropic
        # OpenAI、Google、または Anthropic を使用する場合はコメント解除して設定
    )

    print(model.__class__)

    # Create an agent with the model
    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant.",
        model=model,
    )

    # Run the agent
    print("Running OpenAI example...")
    response = await Runner.run(agent, "What is your name and what can you do?")
    print(response.final_output)


if __name__ == "__main__":
    asyncio.run(main()) 
