#!/usr/bin/env python3
"""
Tool Migration Example - Comparing old vs new tool approaches
ツール移行例 - 古いアプローチと新しいアプローチの比較

This example demonstrates how to migrate from the OpenAI Agents SDK function_tool
to the new Refinire @tool decorator for cleaner imports and better user experience.
この例は、より簡潔なインポートと優れたユーザー体験のために、
OpenAI Agents SDKのfunction_toolから新しいRefinire @toolデコレータに移行する方法を示します。
"""

import asyncio


def demonstrate_old_approach():
    """Demonstrate the old approach with direct OpenAI Agents SDK imports"""
    print("🔧 Old Approach - Direct OpenAI Agents SDK imports:")
    print("=" * 60)
    
    # Old approach - requires knowledge of OpenAI Agents SDK
    # 古いアプローチ - OpenAI Agents SDKの知識が必要
    from agents import function_tool
    from refinire import RefinireAgent
    
    @function_tool
    def old_calculate(expression: str) -> str:
        """Calculate mathematical expressions (old style)"""
        try:
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @function_tool  
    def old_weather(city: str) -> str:
        """Get weather for a city (old style)"""
        weather_data = {
            "Tokyo": "Sunny, 22°C",
            "Paris": "Cloudy, 18°C"
        }
        return weather_data.get(city, f"No weather data for {city}")
    
    print("✅ Code example (old approach):")
    print("""
from agents import function_tool
from refinire import RefinireAgent

@function_tool
def calculate(expression: str) -> str:
    return f"Result: {eval(expression)}"
    
@function_tool
def weather(city: str) -> str:
    return f"Weather in {city}: Sunny"
    
agent = RefinireAgent(
    name="assistant",
    generation_instructions="Help with calculations and weather",
    tools=[calculate, weather],
    model="gpt-4o-mini"
)
""")
    
    print("❌ Issues with old approach:")
    print("  - Requires importing from external 'agents' package")
    print("  - Users need to know OpenAI Agents SDK specifics")
    print("  - Less intuitive for Refinire users")
    print("  - SDK API changes can break user code")
    
    return [old_calculate, old_weather]


def demonstrate_new_approach():
    """Demonstrate the new approach with Refinire @tool decorator"""
    print("\n🎯 New Approach - Refinire @tool decorator:")
    print("=" * 60)
    
    # New approach - clean Refinire imports only
    # 新しいアプローチ - クリーンなRefinireインポートのみ
    from refinire import tool, RefinireAgent, get_tool_info
    
    @tool
    def calculate(expression: str) -> str:
        """Calculate mathematical expressions (new style)"""
        try:
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @tool(name="weather_checker", description="Get weather information for cities")
    def weather(city: str) -> str:
        """Get weather for a city (new style)"""
        weather_data = {
            "Tokyo": "Sunny, 22°C",
            "Paris": "Cloudy, 18°C"
        }
        return weather_data.get(city, f"No weather data for {city}")
    
    print("✅ Code example (new approach):")
    print("""
from refinire import tool, RefinireAgent

@tool
def calculate(expression: str) -> str:
    return f"Result: {eval(expression)}"
    
@tool(name="weather_checker", description="Get weather info")
def weather(city: str) -> str:
    return f"Weather in {city}: Sunny"
    
agent = RefinireAgent(
    name="assistant", 
    generation_instructions="Help with calculations and weather",
    tools=[calculate, weather],
    model="gpt-4o-mini"
)
""")
    
    print("✅ Benefits of new approach:")
    print("  - Single 'from refinire import tool' - no external SDK knowledge needed")
    print("  - Intuitive decorator usage familiar to Python developers")
    print("  - Enhanced debugging with tool metadata")
    print("  - Future-proof against SDK changes")
    print("  - Backward compatible with existing function_tool decorators")
    
    # Demonstrate enhanced features
    # 拡張機能を実演
    print("\n🔍 Enhanced Tool Information:")
    for tool_func in [calculate, weather]:
        info = get_tool_info(tool_func)
        print(f"  - {info['name']}: {info['description']}")
        print(f"    Refinire Tool: {info['is_refinire_tool']}")
    
    return [calculate, weather]


async def demonstrate_agent_usage():
    """Demonstrate both approaches working with RefinireAgent"""
    print("\n🤖 Agent Usage Demonstration:")
    print("=" * 60)
    
    from refinire import tool, RefinireAgent
    
    @tool
    def demo_calculate(expression: str) -> str:
        """Demo calculation tool"""
        try:
            result = eval(expression)
            return f"Calculation result: {result}"
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    # Test both calling the function directly and via agent
    # 関数の直接呼び出しとエージェント経由の両方をテスト
    print("📞 Direct function call:")
    print(f"  calculate('2 + 3'): {demo_calculate('2 + 3')}")
    
    print("\n🤖 Agent-based usage:")
    agent = RefinireAgent(
        name="demo_agent",
        generation_instructions="You are a helpful calculator. Use the available tool to perform calculations when asked.",
        tools=[demo_calculate],
        model="gpt-4o-mini"
    )
    
    try:
        result = await agent.run_async("What is 15 + 27?")
        print(f"  Agent response: {result.content}")
        print(f"  Success: {result.success}")
    except Exception as e:
        print(f"  Agent error: {e}")


def demonstrate_migration_strategy():
    """Show migration strategy for existing code"""
    print("\n📋 Migration Strategy:")
    print("=" * 60)
    
    print("🔄 Step-by-step migration:")
    print("1. Add Refinire tool import: from refinire import tool")
    print("2. Replace @function_tool with @tool")
    print("3. Remove agents import: from agents import function_tool")
    print("4. Optionally add custom names/descriptions: @tool(name='...', description='...')")
    print("5. Test to ensure everything works")
    
    print("\n🔀 Compatibility options:")
    print("- Use function_tool_compat for gradual migration")
    print("- Mix old and new tools in the same agent")
    print("- RefinireAgent automatically handles both formats")
    
    print("\n✨ Advanced features with new @tool:")
    print("- get_tool_info() for debugging")
    print("- list_tools() for tool inventory")
    print("- Enhanced metadata for better error messages")


async def main():
    """Main demonstration function"""
    print("🛠️  Refinire Tool Migration Example")
    print("=" * 80)
    
    # Demonstrate approaches
    # アプローチを実演
    old_tools = demonstrate_old_approach()
    new_tools = demonstrate_new_approach()
    
    # Show practical usage
    # 実用例を表示
    await demonstrate_agent_usage()
    
    # Migration guidance
    # 移行ガイダンス
    demonstrate_migration_strategy()
    
    print("\n🎉 Migration Complete!")
    print("=" * 80)
    print("Your Refinire tools are now more intuitive and future-proof!")
    print("Visit the documentation for more advanced features and examples.")


if __name__ == "__main__":
    asyncio.run(main())