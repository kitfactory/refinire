#!/usr/bin/env python3
"""
Pipeline with Tools Example - Using RefinireAgent with tools
ツール付きパイプライン例 - ツール付きRefinireAgentを使用

This example shows how to use tools with RefinireAgent.
この例は、RefinireAgentでツールを使用する方法を示します。
"""

import asyncio
from refinire import RefinireAgent
from agents import function_tool


@function_tool
def get_weather(location: str) -> str:
    """Get weather information for a location"""
    weather_data = {
        "Tokyo": "Sunny, 22°C",
        "New York": "Cloudy, 18°C",
        "London": "Rainy, 15°C",
        "Paris": "Partly Cloudy, 20°C"
    }
    return weather_data.get(location, f"Weather data not available for {location}")


@function_tool
def search_web(query: str) -> str:
    """Search for information on the web"""
    return f"Search results for '{query}': Found relevant information about {query}"


async def main():
    # RefinireAgentを使用してエージェントを作成（refinire_agent_basic_study.pyと同じ方法）
    agent = RefinireAgent(
        name="tool_agent",
        generation_instructions=(
            "You are a helpful assistant with access to weather and search tools. "
            "For any question about weather or search, you MUST use the appropriate tool. "
            "Do not answer directly, always call the tool for those topics."
        ),
        model="gpt-4o-mini",
        tools=[get_weather, search_web]
    )

    # テストクエリ
    test_queries = [
        "What's the weather like in Tokyo?",
        "Search for information about the latest AI developments"
    ]

    for query in test_queries:
        print(f"\nInput: {query}")
        try:
            result = await agent.run_async(query)
            print(f"Output: {result.content}")
            print(f"Success: {result.success}")
            if not result.success:
                print(f"Error metadata: {result.metadata}")
        except Exception as e:
            print(f"Exception: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 
