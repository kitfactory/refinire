#!/usr/bin/env python3
"""
Tools function example for agents-sdk-models
エージェントSDKモデルのツール機能例

This example demonstrates how to use OpenAI tools with GenAgent and ClarifyAgent.
この例では、GenAgentとClarifyAgentでOpenAIツールを使用する方法を示します。
"""

import asyncio
import json
from typing import Optional
from refinire import (
    GenAgent, 
    ClarifyAgent, 
    create_simple_gen_agent, 
    create_simple_clarify_agent,
    Context
)


def get_weather_tool():
    """
    Define a weather tool function schema for OpenAI
    OpenAI用の天気ツール関数スキーマを定義する
    """
    return {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather information for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    }


def calculator_tool():
    """
    Define a calculator tool function schema for OpenAI
    OpenAI用の計算機ツール関数スキーマを定義する
    """
    return {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform basic mathematical calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate, e.g. '2 + 3 * 4'"
                    }
                },
                "required": ["expression"]
            }
        }
    }


async def test_gen_agent_with_tools():
    """
    Test GenAgent with tools functionality
    ツール機能付きGenAgentをテストする
    """
    print("🔧 Testing GenAgent with Tools")
    print("ツール機能付きGenAgentのテスト")
    
    # Define tools
    tools = [get_weather_tool(), calculator_tool()]
    
    # Create GenAgent with tools
    gen_agent = create_simple_gen_agent(
        name="tool_agent",
        instructions="You are a helpful assistant with access to weather and calculator tools. When the user asks for weather or calculations, consider using the appropriate tools.",
        tools=tools
    )
    
    context = Context()
    
    # Test weather query
    print("\n📍 Testing weather query:")
    print("天気クエリテスト:")
    
    result_context = await gen_agent.run(
        "What's the weather like in Tokyo?", 
        context
    )
    
    print(f"Result: {result_context.prev_outputs.get('tool_agent')}")
    
    # Test calculation query
    print("\n🧮 Testing calculation query:")
    print("計算クエリテスト:")
    
    result_context = await gen_agent.run(
        "Calculate 15 * 24 + 100", 
        context
    )
    
    print(f"Result: {result_context.prev_outputs.get('tool_agent')}")


async def test_clarify_agent_with_tools():
    """
    Test ClarifyAgent with tools functionality
    ツール機能付きClarifyAgentをテストする
    """
    print("\n🔍 Testing ClarifyAgent with Tools")
    print("ツール機能付きClarifyAgentのテスト")
    
    # Define tools
    tools = [get_weather_tool()]
    
    # Create ClarifyAgent with tools
    clarify_agent = create_simple_clarify_agent(
        name="clarify_tool_agent",
        instructions="You are helping to clarify weather information requirements. You have access to weather tools.",
        tools=tools,
        max_turns=3
    )
    
    context = Context()
    
    # Test clarification with tool awareness
    print("\n❓ Testing clarification with tool awareness:")
    print("ツール認識を持つ明確化のテスト:")
    
    result_context = await clarify_agent.run(
        "I want weather info", 
        context
    )
    
    print(f"Clarification result: {result_context.prev_outputs.get('clarify_tool_agent')}")


async def test_direct_llm_pipeline_with_tools():
    """
    Test LLMPipeline directly with tools
    LLMPipelineを直接ツールでテストする
    """
    print("\n⚙️ Testing LLMPipeline directly with Tools")
    print("LLMPipelineを直接ツールでテスト")
    
    from refinire import RefinireAgent
    
    tools = [calculator_tool()]
    
    pipeline = RefinireAgent(
        name="direct_pipeline",
        generation_instructions="You are a helpful calculator assistant. When asked to calculate, consider using the calculator tool.",
        tools=tools
    )
    
    result = pipeline.run("What is 123 * 456?")
    
    print(f"Direct pipeline result: {result.content}")
    print(f"Success: {result.success}")


async def main():
    """
    Main function to run all tests
    すべてのテストを実行するメイン関数
    """
    print("🚀 Starting Tools Functionality Tests")
    print("ツール機能テストを開始")
    print("=" * 50)
    
    try:
        await test_gen_agent_with_tools()
        await test_clarify_agent_with_tools()
        await test_direct_llm_pipeline_with_tools()
        
        print("\n✅ All tests completed successfully!")
        print("すべてのテストが正常に完了しました！")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print(f"テストがエラーで失敗しました: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 
