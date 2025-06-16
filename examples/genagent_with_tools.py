"""
GenAgent example with tools for enhanced generation
ツールを使用した拡張生成のGenAgentの例

This example demonstrates how to use GenAgent with tools (Flow/Step architecture).
この例は、ツール機能付きGenAgent（Flow/Stepアーキテクチャ）の使用方法を示しています。
"""

import asyncio
from refinire import GenAgent, create_simple_flow
from agents import function_tool

@function_tool
def search_web(query: str) -> str:
    """
    Search the web for information.
    Webで情報を検索します。

    Args:
        query: The search query / 検索クエリ
    """
    # 実際のWeb検索APIを呼ぶ場合はここを実装
    # In real implementation, call actual web search API here
    return f"Search results for: {query}"

@function_tool
def get_weather(location: str) -> str:
    """
    Get current weather for a location.
    指定した場所の現在の天気を取得します。

    Args:
        location: The location to get weather for / 天気を取得する場所
    """
    # 実際の天気APIを呼ぶ場合はここを実装
    # In real implementation, call actual weather API here
    return f"Weather in {location}: Sunny, 25°C"

@function_tool
def calculate_math(expression: str) -> str:
    """
    Calculate a mathematical expression.
    数式を計算します。

    Args:
        expression: The mathematical expression to calculate / 計算する数式
    """
    try:
        # 安全な数式計算（実装例）
        # Safe mathematical calculation (example implementation)
        result = eval(expression)
        return f"Result: {result}"
    except:
        return f"Error: Could not calculate {expression}"

async def main():
    """
    Main function demonstrating GenAgent with tools
    ツール付きGenAgentをデモンストレーションするメイン関数
    """
    
    # Define tools for the pipeline
    # パイプライン用のツールを定義
    tools = [search_web, get_weather, calculate_math]

    print("=== GenAgent with Tools Example ===")
    
    # Method 1: Using GenAgent directly with tools
    # 方法1: ツール付きGenAgentを直接使用
    gen_agent = GenAgent(
        name="tooled_generator",
        generation_instructions="""
        You are a helpful assistant that can use tools to gather information and perform calculations.
        あなたは情報を収集し、計算を実行するためにツールを使用できる役立つアシスタントです。

        You have access to the following tools:
        以下のツールにアクセスできます：

        1. search_web: Search the web for information
           search_web: 情報をWebで検索する
        2. get_weather: Get current weather for a location
           get_weather: 場所の現在の天気を取得する
        3. calculate_math: Calculate mathematical expressions
           calculate_math: 数式を計算する

        Please use these tools when appropriate to provide accurate information.
        適切な場合は、これらのツールを使用して正確な情報を提供してください。
        """,
        model="gpt-4o",
        generation_tools=tools,
        store_result_key="tooled_result"
    )

    # Create and run flow
    # フローを作成して実行
    flow = create_simple_flow(gen_agent)
    
    test_inputs = [
        "What's the weather like in Tokyo?",
        "Search for information about the latest AI developments", 
        "Calculate 15 * 7 + 23"
    ]

    for user_input in test_inputs:
        print(f"\n--- Input: {user_input} ---")
        try:
            result = await flow.run(input_data=user_input)
            response = result.get_result("tooled_result")
            print("Response:")
            print(response)
        except Exception as e:
            print(f"Error: {e}")
    
    # Method 2: Multi-Agent Flow with different specialized tools
    # 方法2: 異なる専門ツールを持つマルチエージェントフロー
    print("\n\n=== Multi-Agent Flow with Specialized Tools ===")
    
    from refinire import Flow
    
    # Weather specialist agent
    # 天気専門エージェント
    weather_agent = GenAgent(
        name="weather_specialist",
        generation_instructions="""
        You are a weather specialist. Use the get_weather tool to provide detailed weather information.
        あなたは天気の専門家です。get_weatherツールを使用して詳細な天気情報を提供してください。
        """,
        model="gpt-4o-mini",
        generation_tools=[get_weather],
        store_result_key="weather_info"
    )
    
    # Search specialist agent
    # 検索専門エージェント
    search_agent = GenAgent(
        name="search_specialist", 
        generation_instructions="""
        You are a research specialist. Use the search_web tool to find relevant information.
        あなたは調査の専門家です。search_webツールを使用して関連情報を見つけてください。
        """,
        model="gpt-4o-mini",
        generation_tools=[search_web],
        store_result_key="search_info"
    )
    
    # Calculator specialist agent
    # 計算専門エージェント
    calc_agent = GenAgent(
        name="calc_specialist",
        generation_instructions="""
        You are a calculation specialist. Use the calculate_math tool for mathematical operations.
        あなたは計算の専門家です。calculate_mathツールを使用して数学的操作を実行してください。
        """,
        model="gpt-4o-mini", 
        generation_tools=[calculate_math],
        store_result_key="calc_result"
    )
    
    # Create specialized flow
    # 専門フローを作成
    specialized_flow = Flow("specialized_tools_flow")
    specialized_flow.add_step(weather_agent)
    specialized_flow.add_step(search_agent)
    specialized_flow.add_step(calc_agent)
    
    # Test with different types of requests
    # 異なるタイプのリクエストでテスト
    specialized_inputs = [
        "Tokyo weather forecast",
        "Latest developments in renewable energy",
        "Calculate the compound interest: 1000 * (1.05^10)"
    ]
    
    for i, user_input in enumerate(specialized_inputs):
        print(f"\n--- Specialized Input {i+1}: {user_input} ---")
        try:
            result = await specialized_flow.run(input_data=user_input)
            
            # Show results from all agents
            # すべてのエージェントからの結果を表示
            weather_result = result.get_result("weather_info")
            search_result = result.get_result("search_info") 
            calc_result = result.get_result("calc_result")
            
            print(f"Weather Agent: {weather_result}")
            print(f"Search Agent: {search_result}")
            print(f"Calculator Agent: {calc_result}")
            
        except Exception as e:
            print(f"Error: {e}")

def sync_main():
    """
    Synchronous wrapper for the async main function
    非同期main関数の同期ラッパー
    """
    asyncio.run(main())

if __name__ == "__main__":
    sync_main() 
