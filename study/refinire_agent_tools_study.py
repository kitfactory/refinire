#!/usr/bin/env python3
"""
RefinireAgent Tools Study - Advanced tool usage examples
RefinireAgentツール学習 - 高度なツール使用例

This study demonstrates advanced tool usage with RefinireAgent including:
この学習では、RefinireAgentでの高度なツール使用を示します：

- Multiple tool types / 複数のツールタイプ
- Tool management / ツール管理
- Error handling in tools / ツールでのエラーハンドリング
- Dynamic tool addition/removal / 動的なツール追加/削除
"""

import json
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any
from refinire import RefinireAgent, create_tool_enabled_agent

try:
    from agents import function_tool
except ImportError:
    # Fallback if function_tool is not available
    def function_tool(func):
        return func


# ============================================================================
# Tool Function Definitions
# ツール関数定義
# ============================================================================

@function_tool
def get_weather(location: str, unit: str = "celsius") -> str:
    """
    Get weather information for a location
    指定された場所の天気情報を取得する
    
    Args:
        location: City and state / 都市と州
        unit: Temperature unit / 温度単位
        
    Returns:
        Weather information string / 天気情報文字列
    """
    # Simulate weather data / 天気データをシミュレート
    weather_data = {
        "Tokyo": {"temp": 22, "condition": "Sunny", "humidity": 65},
        "New York": {"temp": 18, "condition": "Cloudy", "humidity": 70},
        "London": {"temp": 15, "condition": "Rainy", "humidity": 80},
        "Paris": {"temp": 20, "condition": "Partly Cloudy", "humidity": 60}
    }
    
    if location in weather_data:
        data = weather_data[location]
        temp = data["temp"]
        if unit == "fahrenheit":
            temp = (temp * 9/5) + 32
            
        return f"Weather in {location}: {temp}°{unit[0].upper()}, {data['condition']}, Humidity: {data['humidity']}%"
    else:
        return f"Weather data not available for {location}. Available cities: {', '.join(weather_data.keys())}"


@function_tool
def calculate(expression: str) -> str:
    """
    Calculate mathematical expression
    数学式を計算する
    
    Args:
        expression: Mathematical expression / 数学式
        
    Returns:
        Calculation result / 計算結果
    """
    try:
        # Safe evaluation with limited operations / 制限された操作での安全な評価
        allowed_names = {
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'sum': sum, 'len': len, 'int': int, 'float': float
        }
        
        # Remove any potentially dangerous operations / 潜在的に危険な操作を削除
        expression = expression.replace('__', '').replace('import', '').replace('eval', '')
        
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"Result of {expression} = {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"


@function_tool
def translate_text(text: str, target_language: str, source_language: str = "auto") -> str:
    """
    Translate text between languages
    テキストを言語間で翻訳する
    
    Args:
        text: Text to translate / 翻訳するテキスト
        target_language: Target language code / ターゲット言語コード
        source_language: Source language code / ソース言語コード
        
    Returns:
        Translated text / 翻訳されたテキスト
    """
    # Simple translation simulation / 簡単な翻訳シミュレーション
    translations = {
        "ja": {
            "hello": "こんにちは",
            "goodbye": "さようなら",
            "thank you": "ありがとうございます",
            "how are you": "お元気ですか"
        },
        "es": {
            "hello": "hola",
            "goodbye": "adiós",
            "thank you": "gracias",
            "how are you": "¿cómo estás?"
        },
        "fr": {
            "hello": "bonjour",
            "goodbye": "au revoir",
            "thank you": "merci",
            "how are you": "comment allez-vous?"
        }
    }
    
    if target_language in translations:
        text_lower = text.lower()
        if text_lower in translations[target_language]:
            return f"'{text}' translated to {target_language}: {translations[target_language][text_lower]}"
        else:
            return f"Translation not available for '{text}' to {target_language}. Available words: {', '.join(translations[target_language].keys())}"
    else:
        return f"Language {target_language} not supported. Available languages: {', '.join(translations.keys())}"


@function_tool
def file_operation(operation: str, filename: str, content: str = "") -> str:
    """
    Perform file operations
    ファイル操作を実行する
    
    Args:
        operation: File operation type / ファイル操作タイプ
        filename: Name of the file / ファイル名
        content: Content to write / 書き込む内容
        
    Returns:
        Operation result / 操作結果
    """
    try:
        if operation == "read":
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return f"File content of {filename}:\n{f.read()}"
            else:
                return f"File {filename} does not exist"
                
        elif operation == "write":
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote content to {filename}"
            
        elif operation == "append":
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully appended content to {filename}"
            
        else:
            return f"Unsupported operation: {operation}"
            
    except Exception as e:
        return f"Error performing {operation} on {filename}: {str(e)}"


@function_tool
def analyze_business_data(data_type: str, time_period: str = "recent", metrics: str = "") -> str:
    """
    Analyze business data and provide insights
    ビジネスデータを分析して洞察を提供する
    
    Args:
        data_type: Type of business data / ビジネスデータのタイプ
        time_period: Time period for analysis / 分析期間
        metrics: Specific metrics to analyze / 分析する特定のメトリクス
        
    Returns:
        Analysis result / 分析結果
    """
    # Simulate business data analysis / ビジネスデータ分析をシミュレート
    analysis_results = {
        "sales": {
            "trend": "Increasing by 15% month-over-month",
            "top_products": ["Product A", "Product B", "Product C"],
            "revenue": "$125,000",
            "recommendations": ["Focus on Product A marketing", "Expand to new markets"]
        },
        "customer": {
            "satisfaction": "4.2/5.0",
            "retention_rate": "87%",
            "new_customers": "1,250",
            "recommendations": ["Improve customer support", "Launch loyalty program"]
        },
        "inventory": {
            "turnover_rate": "8.5 times/year",
            "stockout_rate": "3%",
            "carrying_cost": "$12,000/month",
            "recommendations": ["Optimize reorder points", "Reduce slow-moving items"]
        },
        "financial": {
            "profit_margin": "23%",
            "cash_flow": "Positive",
            "debt_ratio": "0.35",
            "recommendations": ["Increase pricing", "Reduce operational costs"]
        }
    }
    
    if data_type in analysis_results:
        data = analysis_results[data_type]
        result = f"Business Analysis - {data_type.upper()} ({time_period}):\n"
        for key, value in data.items():
            if isinstance(value, list):
                result += f"  {key.replace('_', ' ').title()}: {', '.join(value)}\n"
            else:
                result += f"  {key.replace('_', ' ').title()}: {value}\n"
        return result
    else:
        return f"Data type '{data_type}' not supported. Available types: {', '.join(analysis_results.keys())}"


# ============================================================================
# Tool Implementation Functions
# ツール実装関数
# ============================================================================

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


def translation_tool():
    """
    Define a translation tool function schema for OpenAI
    OpenAI用の翻訳ツール関数スキーマを定義する
    """
    return {
        "type": "function",
        "function": {
            "name": "translate_text",
            "description": "Translate text between languages",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to translate"
                    },
                    "source_language": {
                        "type": "string",
                        "description": "Source language code (e.g., 'en', 'ja', 'es')"
                    },
                    "target_language": {
                        "type": "string",
                        "description": "Target language code (e.g., 'en', 'ja', 'es')"
                    }
                },
                "required": ["text", "target_language"]
            }
        }
    }


def file_operation_tool():
    """
    Define a file operation tool function schema for OpenAI
    OpenAI用のファイル操作ツール関数スキーマを定義する
    """
    return {
        "type": "function",
        "function": {
            "name": "file_operation",
            "description": "Perform file operations like read, write, append",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["read", "write", "append"],
                        "description": "File operation to perform"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Name of the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write (for write/append operations)"
                    }
                },
                "required": ["operation", "filename"]
            }
        }
    }


def business_analysis_tool():
    """
    Define a business analysis tool function schema for OpenAI
    OpenAI用のビジネス分析ツール関数スキーマを定義する
    """
    return {
        "type": "function",
        "function": {
            "name": "analyze_business_data",
            "description": "Analyze business data and provide insights",
            "parameters": {
                "type": "object",
                "properties": {
                    "data_type": {
                        "type": "string",
                        "enum": ["sales", "customer", "inventory", "financial"],
                        "description": "Type of business data to analyze"
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Time period for analysis (e.g., 'last_month', 'q1_2024')"
                    },
                    "metrics": {
                        "type": "string",
                        "description": "Specific metrics to analyze (comma-separated)"
                    }
                },
                "required": ["data_type"]
            }
        }
    }


# ============================================================================
# Study Functions
# 学習関数
# ============================================================================

def study_basic_tool_usage():
    """
    Study basic tool usage with RefinireAgent
    RefinireAgentでの基本的なツール使用を学習する
    """
    print("🔧 Study 1: Basic Tool Usage")
    print("学習1: 基本的なツール使用")
    print("=" * 50)
    
    # Create tools list with callable functions
    # 呼び出し可能な関数付きツールリストを作成
    tools = [get_weather, calculate]
    
    # Create RefinireAgent with tools
    # ツール付きRefinireAgentを作成
    agent = RefinireAgent(
        name="basic_tool_agent",
        generation_instructions="You are a helpful assistant with access to weather and calculator tools. When users ask for weather information or calculations, use the appropriate tools to provide accurate information.",
        tools=tools,
        model="gpt-4o-mini"
    )
    
    # Test weather query
    print("\n📍 Testing weather query:")
    result = agent.run("What's the weather like in Tokyo?")
    print(f"Input: What's the weather like in Tokyo?")
    print(f"Output: {result.content}")
    print(f"Success: {result.success}")
    
    # Test calculation query
    print("\n🧮 Testing calculation query:")
    result = agent.run("Calculate 15 * 24 + 100")
    print(f"Input: Calculate 15 * 24 + 100")
    print(f"Output: {result.content}")
    print(f"Success: {result.success}")


def study_advanced_tool_usage():
    """
    Study advanced tool usage with multiple tools
    複数のツールを使用した高度なツール使用を学習する
    """
    print("\n🚀 Study 2: Advanced Tool Usage")
    print("学習2: 高度なツール使用")
    print("=" * 50)
    
    # Create comprehensive tools list
    # 包括的なツールリストを作成
    tools = [get_weather, calculate, translate_text, analyze_business_data]
    
    # Create RefinireAgent with advanced tools
    # 高度なツール付きRefinireAgentを作成
    agent = RefinireAgent(
        name="advanced_tool_agent",
        generation_instructions="""You are a comprehensive business assistant with access to multiple tools:
- Weather information for travel planning
- Calculator for financial calculations
- Translation tools for international communication
- Business analysis tools for data insights

Use the appropriate tools when users request specific information or calculations.""",
        tools=tools,
        model="gpt-4o-mini",
        temperature=0.3
    )
    
    # Test complex query
    print("\n🌍 Testing complex multi-tool query:")
    result = agent.run("I'm planning a business trip to Tokyo. What's the weather like there, and can you translate 'thank you' to Japanese? Also, analyze our recent sales data.")
    print(f"Input: I'm planning a business trip to Tokyo. What's the weather like there, and can you translate 'thank you' to Japanese? Also, analyze our recent sales data.")
    print(f"Output: {result.content}")
    print(f"Success: {result.success}")


def study_file_operation_tools():
    """
    Study file operation tools with RefinireAgent
    RefinireAgentでのファイル操作ツールを学習する
    """
    print("\n📁 Study 3: File Operation Tools")
    print("学習3: ファイル操作ツール")
    print("=" * 50)
    
    # Create temporary file for testing
    # テスト用の一時ファイルを作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_filename = f.name
        f.write("Initial content for testing.\n")
    
    try:
        # Create tools with file operations
        # ファイル操作付きツールを作成
        tools = [file_operation]
        
        # Create RefinireAgent with file tools
        # ファイルツール付きRefinireAgentを作成
        agent = RefinireAgent(
            name="file_tool_agent",
            generation_instructions="You are a file management assistant. You can read, write, and append content to files. Always be careful with file operations and provide clear feedback.",
            tools=tools,
            model="gpt-4o-mini"
        )
        
        # Test file read operation
        print(f"\n📖 Testing file read operation:")
        result = agent.run(f"Read the content of file: {temp_filename}")
        print(f"Input: Read the content of file: {temp_filename}")
        print(f"Output: {result.content}")
        print(f"Success: {result.success}")
        
        # Test file write operation
        print(f"\n✏️ Testing file write operation:")
        result = agent.run(f"Write 'Hello from RefinireAgent!' to file: {temp_filename}")
        print(f"Input: Write 'Hello from RefinireAgent!' to file: {temp_filename}")
        print(f"Output: {result.content}")
        print(f"Success: {result.success}")
        
        # Test file append operation
        print(f"\n➕ Testing file append operation:")
        result = agent.run(f"Append 'This is appended content.' to file: {temp_filename}")
        print(f"Input: Append 'This is appended content.' to file: {temp_filename}")
        print(f"Output: {result.content}")
        print(f"Success: {result.success}")
        
        # Verify final content
        print(f"\n📄 Final file content:")
        with open(temp_filename, 'r') as f:
            print(f.read())
            
    finally:
        # Clean up temporary file
        # 一時ファイルをクリーンアップ
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def study_tool_enabled_agent_factory():
    """
    Study using create_tool_enabled_agent factory function
    create_tool_enabled_agentファクトリ関数の使用を学習する
    """
    print("\n🏭 Study 4: Tool Enabled Agent Factory")
    print("学習4: ツール有効エージェントファクトリ")
    print("=" * 50)
    
    # Create agent using factory function with Python functions
    # Python関数を使用したファクトリ関数でエージェントを作成
    agent = create_tool_enabled_agent(
        name="factory_tool_agent",
        instructions="You are a helpful assistant with access to weather, calculator, and translation tools. Use them appropriately when users request specific information.",
        tools=[get_weather, calculate, translate_text],
        model="gpt-4o-mini"
    )
    
    # Test multiple tool usage
    print("\n🔄 Testing multiple tool usage:")
    result = agent.run("What's the weather in London, calculate 25 * 4, and translate 'hello' to Spanish")
    print(f"Input: What's the weather in London, calculate 25 * 4, and translate 'hello' to Spanish")
    print(f"Output: {result.content}")
    print(f"Success: {result.success}")
    
    # List available tools
    print(f"\n📋 Available tools: {agent.list_tools()}")


def study_tool_management():
    """
    Study tool management (adding, removing, listing tools)
    ツール管理（追加、削除、一覧表示）を学習する
    """
    print("\n⚙️ Study 5: Tool Management")
    print("学習5: ツール管理")
    print("=" * 50)
    
    # Create agent without tools initially
    # 最初はツールなしでエージェントを作成
    agent = RefinireAgent(
        name="management_agent",
        generation_instructions="You are a tool management assistant. You can have tools added and removed dynamically.",
        model="gpt-4o-mini"
    )
    
    print(f"Initial tools: {agent.list_tools()}")
    
    # Add tools one by one using add_tool method
    # add_toolメソッドを使用してツールを一つずつ追加
    print("\n➕ Adding tools:")
    
    # Add weather tool
    weather_tool_def = {
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
    agent.add_tool(weather_tool_def, get_weather)
    print(f"Added weather tool: {agent.list_tools()}")
    
    # Add calculator tool
    calculator_tool_def = {
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
    agent.add_tool(calculator_tool_def, calculate)
    print(f"Added calculator tool: {agent.list_tools()}")
    
    # Test with tools
    print("\n🧪 Testing with added tools:")
    result = agent.run("What's the weather in Paris and calculate 10 + 20?")
    print(f"Input: What's the weather in Paris and calculate 10 + 20?")
    print(f"Output: {result.content}")
    print(f"Success: {result.success}")
    
    # Remove a tool
    print("\n➖ Removing weather tool:")
    success = agent.remove_tool("get_weather")
    print(f"Removal successful: {success}")
    print(f"Remaining tools: {agent.list_tools()}")
    
    # Test with remaining tools
    print("\n🧪 Testing with remaining tools:")
    result = agent.run("Calculate 15 * 3")
    print(f"Input: Calculate 15 * 3")
    print(f"Output: {result.content}")
    print(f"Success: {result.success}")


def study_error_handling():
    """
    Study error handling in tool usage
    ツール使用でのエラーハンドリングを学習する
    """
    print("\n⚠️ Study 6: Error Handling")
    print("学習6: エラーハンドリング")
    print("=" * 50)
    
    # Create tools with potential errors
    # 潜在的なエラーがあるツールを作成
    tools = [calculate]
    
    agent = RefinireAgent(
        name="error_handling_agent",
        generation_instructions="You are an assistant that handles errors gracefully. When tools fail, explain the issue and suggest alternatives.",
        tools=tools,
        model="gpt-4o-mini"
    )
    
    # Test invalid calculation
    print("\n❌ Testing invalid calculation:")
    result = agent.run("Calculate invalid_expression")
    print(f"Input: Calculate invalid_expression")
    print(f"Output: {result.content}")
    print(f"Success: {result.success}")
    
    # Test non-existent tool request
    print("\n🔍 Testing non-existent tool request:")
    result = agent.run("Get the weather in Tokyo")
    print(f"Input: Get the weather in Tokyo")
    print(f"Output: {result.content}")
    print(f"Success: {result.success}")
    
    # Test with valid calculation
    print("\n✅ Testing valid calculation:")
    result = agent.run("Calculate 10 + 5 * 2")
    print(f"Input: Calculate 10 + 5 * 2")
    print(f"Output: {result.content}")
    print(f"Success: {result.success}")


def study_basic_generation_without_tools():
    """
    Study basic generation without tools using OpenAI Agents SDK
    OpenAI Agents SDKを使用したツールなしの基本的な生成を学習する
    """
    print("🔧 Study: Basic Generation without Tools using OpenAI Agents SDK")
    print("=" * 70)
    
    # Create agent without tools
    # ツールなしのエージェントを作成
    agent = RefinireAgent(
        name="basic_agent",
        generation_instructions="""
        You are a helpful assistant.
        Provide clear and concise responses to user questions.
        
        あなたは有用なアシスタントです。
        ユーザーの質問に明確で簡潔な回答を提供してください。
        """,
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    # Test queries
    # テストクエリ
    test_queries = [
        "What is the capital of Japan?",
        "Explain photosynthesis in simple terms.",
        "What are the benefits of exercise?",
        "日本の首都はどこですか？",
        "光合成を簡単に説明してください。"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 50)
        
        try:
            result = agent.run(query)
            
            if result.success:
                print(f"✅ Success: {result.content}")
                if result.metadata:
                    print(f"📊 Metadata: {result.metadata}")
            else:
                print(f"❌ Failed: {result.metadata.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"🚨 Exception: {str(e)}")
    
    print("\n" + "=" * 70)


# ============================================================================
# Main Study Function
# メイン学習関数
# ============================================================================

def main():
    """
    Main function to run all studies
    すべての学習を実行するメイン関数
    """
    print("🚀 Starting RefinireAgent Tools Study")
    print("RefinireAgentツール学習を開始")
    print("=" * 60)
    
    try:
        # Test basic generation without tools first
        # まずツールなしの基本的な生成をテスト
        study_basic_generation_without_tools()
        
        # Then test with tools
        # 次にツール付きをテスト
        study_basic_tool_usage()
        study_advanced_tool_usage()
        study_file_operation_tools()
        study_tool_enabled_agent_factory()
        study_tool_management()
        study_error_handling()
        
        print("\n✅ All studies completed successfully!")
        print("すべての学習が正常に完了しました！")
        print("\n📚 Key Takeaways:")
        print("📚 主要なポイント:")
        print("  • RefinireAgent now uses OpenAI Agents SDK for all operations")
        print("  • RefinireAgentはすべての操作でOpenAI Agents SDKを使用します")
        print("  • Tools are properly integrated with strict schema compliance")
        print("  • ツールはstrict schema準拠で適切に統合されています")
        print("  • Pydantic v2 compatibility ensures stable tool execution")
        print("  • Pydantic v2互換性により安定したツール実行が保証されます")
        
    except Exception as e:
        print(f"❌ Study failed with error: {e}")
        print(f"学習がエラーで失敗しました: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Study completed!")
    print("学習完了！")


if __name__ == "__main__":
    main() 