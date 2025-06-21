#!/usr/bin/env python3
"""
Simple test script for RefinireAgent
RefinireAgentのシンプルなテストスクリプト
"""

import asyncio
from refinire import RefinireAgent

def get_weather(location: str) -> str:
    """Get weather information for a location"""
    return f"Weather in {location}: Sunny, 25°C"

def calculate(expression: str) -> str:
    """Calculate mathematical expression"""
    try:
        result = eval(expression)
        return f"Result of {expression} = {result}"
    except:
        return f"Error calculating {expression}"

async def test_basic():
    """Test basic functionality"""
    print("Testing basic RefinireAgent...")
    
    agent = RefinireAgent(
        name="test_agent",
        generation_instructions="You are a helpful assistant.",
        model="gpt-4o-mini"
    )
    
    result = await agent.run_async("What is 2+2?")
    print(f"Basic test result: {result.content}")
    print(f"Success: {result.success}")

async def test_tools():
    """Test tool integration"""
    print("\nTesting tool integration...")
    
    agent = RefinireAgent(
        name="tool_agent",
        generation_instructions="You are a helpful assistant with tools.",
        model="gpt-4o-mini"
    )
    
    agent.add_function_tool(get_weather)
    agent.add_function_tool(calculate)
    
    result = await agent.run_async("What's the weather in Tokyo?")
    print(f"Tool test result: {result.content}")
    print(f"Success: {result.success}")

async def main():
    """Main test function"""
    print("🚀 Starting simple tests...")
    
    try:
        await test_basic()
        await test_tools()
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 