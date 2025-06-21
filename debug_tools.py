#!/usr/bin/env python3
"""
Debug script for tool addition
ツール追加のデバッグ用スクリプト
"""

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

def main():
    print("🔍 Debugging tool addition...")
    
    # Create agent
    agent = RefinireAgent(
        name="debug_agent",
        generation_instructions="You are a helpful assistant.",
        model="gpt-4o-mini"
    )
    
    print("\n📝 Adding weather tool...")
    agent.add_function_tool(get_weather)
    
    print("\n📝 Adding calculator tool...")
    agent.add_function_tool(calculate)
    
    print("\n✅ Tool addition completed!")

if __name__ == "__main__":
    main() 