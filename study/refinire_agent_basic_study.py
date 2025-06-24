#!/usr/bin/env python3
"""
RefinireAgent Basic Study - Fundamental usage examples
RefinireAgent基本学習 - 基本的な使用例

This study demonstrates the fundamental usage of RefinireAgent including:
この学習では、RefinireAgentの基本的な使用方法を示します：

- Basic generation / 基本的な生成
- Evaluation and retry / 評価とリトライ
- Tool integration / ツール統合
- Error handling / エラーハンドリング
"""

import asyncio
import warnings
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass
from typing import Dict, Any
from refinire import RefinireAgent, create_simple_agent, create_evaluated_agent, enable_console_tracing
from agents import Agent, Runner, function_tool

# ============================================================================
# Tool Functions for OpenAI Agents SDK
# OpenAI Agents SDK用のツール関数
# ============================================================================

@function_tool
def get_weather_sdk(location: str) -> str:
    """
    Get weather information for a location
    場所の天気情報を取得する
    """
    print(f"Getting weather for: {location}")
    weather_data = {
        "Tokyo": "Sunny, 22°C",
        "New York": "Cloudy, 18°C",
        "London": "Rainy, 15°C",
        "Paris": "Partly Cloudy, 20°C"
    }
    return weather_data.get(location, f"Weather data not available for {location}")

@function_tool
def calculate_sdk(expression: str) -> str:
    """
    Perform mathematical calculations
    数学的計算を実行する
    """
    try:
        print(f"Calculating: {expression}")
        # Safe evaluation with limited operations
        allowed_names = {'abs': abs, 'round': round, 'min': min, 'max': max}
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# Tool Functions for RefinireAgent
# RefinireAgent用のツール関数
# ============================================================================

def get_weather(location: str) -> str:
    """
    Simple weather tool function
    シンプルな天気ツール関数
    """
    print(f"🔍 DEBUG: get_weather called with location: {location}")
    weather_data = {
        "Tokyo": "Sunny, 22°C",
        "New York": "Cloudy, 18°C",
        "London": "Rainy, 15°C",
        "Paris": "Partly Cloudy, 20°C"
    }
    result = weather_data.get(location, f"Weather data not available for {location}")
    print(f"🔍 DEBUG: get_weather returning: {result}")
    return result


def calculate(expression: str) -> str:
    """
    Simple calculator tool function
    シンプルな計算機ツール関数
    """
    try:
        print(f"🔍 DEBUG: calculate called with expression: {expression}")
        # Safe evaluation with limited operations
        allowed_names = {'abs': abs, 'round': round, 'min': min, 'max': max}
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        output = f"Result: {result}"
        print(f"🔍 DEBUG: calculate returning: {output}")
        return output
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"🔍 DEBUG: calculate error: {error_msg}")
        return error_msg


# ============================================================================
# Basic Generation Study
# 基本的な生成学習
# ============================================================================

async def study_basic_generation():
    """
    Study basic content generation with RefinireAgent
    RefinireAgentでの基本的なコンテンツ生成を学習する
    """
    print("📝 Study 1: Basic Generation")
    print("学習1: 基本的な生成")
    print("=" * 50)
    
    # Create a simple RefinireAgent
    # シンプルなRefinireAgentを作成
    agent = RefinireAgent(
        name="basic_agent",
        generation_instructions="You are a helpful assistant that provides clear and concise answers.",
        model="gpt-4o",
        temperature=0.3,
    )
    
    # Test basic generation
    # 基本的な生成をテスト
    print("\n🤖 Testing basic generation:")
    result = await agent.run_async("What is artificial intelligence?")
    print(f"Input: What is artificial intelligence?")
    print(f"Output: {result.content}")
    print(f"Success: {result.success}")
    print(f"Metadata: {result.metadata}")


# ============================================================================
# Tool Integration Study
# ツール統合学習
# ============================================================================

async def study_tool_integration():
    """
    Study tool integration with RefinireAgent
    RefinireAgentでのツール統合を学習する
    """
    print("\n🔧 Study 3: Tool Integration")
    print("学習3: ツール統合")
    print("=" * 50)
    
    # Create agent with tools
    # ツール付きでエージェントを作成
    tool_agent = RefinireAgent(
        name="tool_agent",
        generation_instructions=(
            "You are a helpful assistant with access to weather and calculator tools. "
            "For any question about weather or calculation, you MUST use the appropriate tool. "
            "Do not answer directly, always call the tool for those topics."
        ),
        model="gpt-4o",
        tools=[get_weather_sdk, calculate_sdk]  # Use the same tools as Study 5
    )
    
    # Test tool usage
    # ツール使用をテスト
    print("run_async about to be called (weather tool)")
    try:
        result = await tool_agent.run_async("What's the weather like in Tokyo?")
        print(f"Input: What's the weather like in Tokyo?")
        print(f"Output: {result.content}")
        print(f"Success: {result.success}")
        if not result.success:
            print(f"Error metadata: {result.metadata}")
    except Exception as e:
        print(f"Error in weather tool test: {e}")
        import traceback
        traceback.print_exc()
    
    print("run_async about to be called (calculator tool)")
    print("\n🧮 Testing calculator tool:")
    try:
        result = await tool_agent.run_async("Calculate 15 * 24 + 100")
        print(f"Input: Calculate 15 * 24 + 100")
        print(f"Output: {result.content}")
        print(f"Success: {result.success}")
        if not result.success:
            print(f"Error metadata: {result.metadata}")
    except Exception as e:
        print(f"Error in calculator tool test: {e}")
        import traceback
        traceback.print_exc()

# ============================================================================
# Error Handling Study
# エラーハンドリング学習
# ============================================================================

async def study_error_handling():
    """
    Study error handling in RefinireAgent
    RefinireAgentでのエラーハンドリングを学習する
    """
    print("\n⚠️ Study 4: Error Handling")
    print("学習4: エラーハンドリング")
    print("=" * 50)
    
    # Create agent with low temperature for more predictable responses
    # より予測可能な応答のために低い温度でエージェントを作成
    agent = RefinireAgent(
        name="error_handling_agent",
        generation_instructions="You are a helpful assistant. If you encounter errors or unclear requests, explain the issue clearly and suggest alternatives.",
        model="gpt-4o-mini",
        temperature=0.1
    )
    
    # Test with unclear request
    # 不明確なリクエストでテスト
    print("\n❓ Testing unclear request:")
    result = agent.run("")
    print(f"Input: (empty)")
    print(f"Output: {result.content}")
    print(f"Success: {result.success}")

# =========================================================================
# OpenAI Agents SDK Tool Call Study
# OpenAI Agents SDKによるツールコール学習
# =========================================================================

async def study_open_ai_tool_call():
    """
    Study tool calling using OpenAI Agents SDK
    OpenAI Agents SDKでのツールコールを学習する
    """
    print("\n🤖 Study 5: OpenAI Agents SDK Tool Call")
    print("学習5: OpenAI Agents SDKによるツールコール")
    print("=" * 50)

    # Agentの作成
    # Create agent with tool functions
    agent = Agent(
        name="openai_sdk_agent",
        instructions=(
            "You are a helpful assistant with access to weather and calculator tools. "
            "For any question about weather or calculation, you MUST use the appropriate tool. "
            "Do not answer directly, always call the tool for those topics."
        ),
        tools=[get_weather_sdk, calculate_sdk]
    )

    # 天気ツールのテスト
    print("\n🌤️ Testing weather tool (OpenAI Agents SDK):")
    result = await Runner.run(agent, "What's the weather like in Tokyo?")
    print(f"Input: What's the weather like in Tokyo?")
    print(f"Output: {result.final_output}")
    print(f"Success: {hasattr(result, 'final_output') and result.final_output is not None}")

    # 計算ツールのテスト
    print("\n🧮 Testing calculator tool (OpenAI Agents SDK):")
    result = await Runner.run(agent, "Calculate 15 * 24 + 100")
    print(f"Input: Calculate 15 * 24 + 100")
    print(f"Output: {result.final_output}")
    print(f"Success: {hasattr(result, 'final_output') and result.final_output is not None}")

# ============================================================================
# Main Study Function
# メイン学習関数
# ============================================================================

async def main():
    """
    Main function to run all basic studies
    すべての基本学習を実行するメイン関数
    """
    print("🚀 Starting RefinireAgent Basic Study")
    print("RefinireAgent基本学習を開始")
    print("=" * 60)
    
    # Enable console tracing for RefinireAgent
    # RefinireAgent用にコンソールトレーシングを有効化
    enable_console_tracing()
    
    try:
        # Run all studies
        # すべての学習を実行
        await study_basic_generation()
        # study_factory_functions()
        await study_tool_integration()
        await study_error_handling()
        await study_open_ai_tool_call()
        # study_configuration_options()
        
        print("\n✅ All basic studies completed successfully!")
        print("すべての基本学習が正常に完了しました！")
        print("\n📚 Key Takeaways:")
        print("📚 主要なポイント:")
        print("  • RefinireAgent provides a unified interface for AI agents")
        print("  • RefinireAgentはAIエージェントの統一インターフェースを提供します")
        print("  • Factory functions simplify common configurations")
        print("  • ファクトリ関数は一般的な設定を簡素化します")
        print("  • Tools can be easily integrated for extended functionality")
        print("  • ツールは拡張機能のために簡単に統合できます")
        print("  • Built-in error handling and retry mechanisms")
        print("  • 組み込みのエラーハンドリングとリトライメカニズム")
        print("  • Flexible configuration options for different use cases")
        print("  • 異なるユースケースのための柔軟な設定オプション")
        
    except Exception as e:
        print(f"\n❌ Study failed with error: {e}")
        print(f"学習がエラーで失敗しました: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
 