#!/usr/bin/env python3
"""
Refinire Tools Example - Using the new @tool decorator
Refinireツール例 - 新しい@toolデコレータの使用

This example demonstrates the new @tool decorator that provides
a cleaner import experience compared to the OpenAI Agents SDK function_tool.
この例は、OpenAI Agents SDKのfunction_toolと比較して
よりクリーンなインポート体験を提供する新しい@toolデコレータを実演します。
"""

import asyncio
from refinire import tool, RefinireAgent, get_tool_info, list_tools


@tool
def get_weather(city: str) -> str:
    """Get weather information for a specific city"""
    # Mock weather data for demonstration
    # デモンストレーション用のモック天気データ
    weather_data = {
        "Tokyo": "Sunny, 22°C, humidity 45%",
        "New York": "Cloudy, 18°C, humidity 60%", 
        "London": "Rainy, 15°C, humidity 80%",
        "Paris": "Partly Cloudy, 20°C, humidity 55%",
        "Sydney": "Clear, 25°C, humidity 40%"
    }
    return weather_data.get(city, f"Weather data not available for {city}")


@tool(name="math_calculator", description="Perform mathematical calculations safely")
def calculate(expression: str) -> str:
    """Calculate mathematical expressions with basic safety checks"""
    # Basic safety check - only allow simple arithmetic
    # 基本的な安全チェック - 単純な算術のみ許可
    allowed_chars = set('0123456789+-*/()., ')
    if not all(c in allowed_chars for c in expression):
        return "Error: Only basic arithmetic operations are allowed"
    
    try:
        # Use eval cautiously with cleaned expression
        # クリーンアップされた式でevalを慎重に使用
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"


@tool
def search_info(query: str) -> str:
    """Search for information (mock implementation)"""
    # Mock search results for demonstration
    # デモンストレーション用のモック検索結果
    knowledge_base = {
        "ai": "Artificial Intelligence is the simulation of human intelligence in machines",
        "python": "Python is a high-level programming language known for its simplicity",
        "weather": "Weather refers to atmospheric conditions at a specific time and place",
        "refinire": "Refinire is a unified AI agent development platform"
    }
    
    # Simple keyword matching
    # シンプルなキーワードマッチング
    for keyword, info in knowledge_base.items():
        if keyword.lower() in query.lower():
            return f"Found information about '{keyword}': {info}"
    
    return f"No specific information found for '{query}'. Try asking about AI, Python, weather, or Refinire."


@tool(name="time_converter", description="Convert between different time formats")
def convert_time(time_input: str, from_format: str = "24h", to_format: str = "12h") -> str:
    """Convert time between 12-hour and 24-hour formats"""
    try:
        if from_format == "24h" and to_format == "12h":
            # Convert 24h to 12h format
            # 24時間形式から12時間形式に変換
            hour, minute = map(int, time_input.split(':'))
            if hour == 0:
                return f"12:{minute:02d} AM"
            elif hour < 12:
                return f"{hour}:{minute:02d} AM"
            elif hour == 12:
                return f"12:{minute:02d} PM"
            else:
                return f"{hour-12}:{minute:02d} PM"
        else:
            return f"Conversion from {from_format} to {to_format} not implemented yet"
    except Exception as e:
        return f"Time conversion error: {str(e)}"


async def main():
    """Main demonstration function"""
    print("🛠️  Refinire Tools Example")
    print("=" * 50)
    
    # Display tool information
    # ツール情報を表示
    tools = [get_weather, calculate, search_info, convert_time]
    
    print("\n📋 Available Tools:")
    tool_list = list_tools(tools)
    for i, tool_info in enumerate(tool_list, 1):
        print(f"{i}. {tool_info['name']}: {tool_info['description']}")
    
    print(f"\n🔍 Detailed Tool Info:")
    for tool_func in tools:
        info = get_tool_info(tool_func)
        print(f"  - {info['name']}: {info['description']}")
        print(f"    Refinire Tool: {info['is_refinire_tool']}")
        print()
    
    # Create agent with tools
    # ツール付きエージェントを作成
    agent = RefinireAgent(
        name="multi_tool_assistant",
        generation_instructions="""
        You are a helpful assistant with access to multiple tools:
        - Weather information for cities
        - Mathematical calculations
        - Information search
        - Time format conversion
        
        Always use the appropriate tool for user requests. Be specific about what tool you're using.
        """,
        tools=tools,
        model="gpt-4o-mini"
    )
    
    # Test queries to demonstrate different tools
    # 異なるツールを実演するテストクエリ
    test_queries = [
        "What's the weather like in Tokyo?",
        "Calculate 15 * 23 + 47",
        "Tell me about AI",
        "Convert 14:30 to 12-hour format"
    ]
    
    print("🤖 Agent Responses:")
    print("-" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        try:
            result = await agent.run_async(query)
            print(f"   Response: {result.content}")
            print(f"   Success: {result.success}")
            
            if not result.success:
                print(f"   Error: {result.metadata}")
                
        except Exception as e:
            print(f"   Exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n✨ Example completed!")
    print("\n📝 Benefits of @tool decorator:")
    print("  - Clean import: 'from refinire import tool'")
    print("  - No need to know OpenAI Agents SDK details")
    print("  - Enhanced metadata for debugging")
    print("  - Future-proof against SDK changes")


if __name__ == "__main__":
    asyncio.run(main())