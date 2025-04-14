import asyncio
import os
from agents import Agent, Runner
from agents_sdk_models import LlmModel


async def main():
    # Initialize the LlmModel model (Example uses Ollama's llama3)
    # You can change the provider and model as needed.
    # Supported providers: "openai", "google", "anthropic", "ollama"
    model = LlmModel(
        provider="ollama",  # Change provider here
        model="llama3",  # Change model name here
        temperature=0.7,
        # api_key=os.environ.get("YOUR_API_KEY_ENV_VAR") # Uncomment and set if using OpenAI, Google, or Anthropic
    )

    # Create an agent with the model
    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant.",
        model=model,
    )

    # Run the agent
    print("Running Ollama example...")
    response = await Runner.run(agent, "What is your name and what can you do?")
    print(response.final_output)

    # --- Example with OpenAI --- (Requires OPENAI_API_KEY environment variable)
    # Uncomment the following lines to run the OpenAI example
    # print("\nRunning OpenAI example...")
    # openai_api_key = os.environ.get("OPENAI_API_KEY")
    # if openai_api_key:
    #     model_openai = LlmModel(
    #         provider="openai",
    #         model="gpt-4o-mini",
    #         temperature=0.7,
    #         api_key=openai_api_key
    #     )
    #     agent_openai = Agent(
    #         name="Assistant",
    #         instructions="You are a helpful assistant.",
    #         model=model_openai
    #     )
    #     response_openai = await Runner.run(agent_openai, "What is your name and what can you do?")
    #     print(response_openai.final_output)
    # else:
    #     print("OPENAI_API_KEY not found. Skipping OpenAI example.")

    # --- Example with Google Gemini --- (Requires GOOGLE_API_KEY environment variable)
    # Uncomment the following lines to run the Google Gemini example
    # print("\nRunning Google Gemini example...")
    # google_api_key = os.environ.get("GOOGLE_API_KEY")
    # if google_api_key:
    #     model_gemini = LlmModel(
    #         provider="google",
    #         model="gemini-1.5-pro",
    #         temperature=0.7,
    #         api_key=google_api_key
    #     )
    #     agent_gemini = Agent(
    #         name="Assistant",
    #         instructions="You are a helpful assistant.",
    #         model=model_gemini
    #     )
    #     response_gemini = await Runner.run(agent_gemini, "What is your name and what can you do?")
    #     print(response_gemini.final_output)
    # else:
    #     print("GOOGLE_API_KEY not found. Skipping Google Gemini example.")

    # --- Example with Anthropic Claude --- (Requires ANTHROPIC_API_KEY environment variable)
    # Uncomment the following lines to run the Anthropic Claude example
    # print("\nRunning Anthropic Claude example...")
    # anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    # if anthropic_api_key:
    #     model_claude = LlmModel(
    #         provider="anthropic",
    #         model="claude-3-sonnet-20240229",
    #         temperature=0.7,
    #         api_key=anthropic_api_key
    #     )
    #     agent_claude = Agent(
    #         name="Assistant",
    #         instructions="You are a helpful assistant.",
    #         model=model_claude
    #     )
    #     response_claude = await Runner.run(agent_claude, "What is your name and what can you do?")
    #     print(response_claude.final_output)
    # else:
    #     print("ANTHROPIC_API_KEY not found. Skipping Anthropic Claude example.")


if __name__ == "__main__":
    asyncio.run(main()) 