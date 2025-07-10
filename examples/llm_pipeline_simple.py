#!/usr/bin/env python3
"""
Simple LLMPipeline Example - Modern RefinireAgent usage
シンプルなLLMPipelineの例 - 現代的なRefinireAgentの使用法

This demonstrates basic RefinireAgent usage with current API.
これは、現在のAPIでの基本的なRefinireAgentの使用方法を示しています。
"""

import os
from pydantic import BaseModel
from refinire import RefinireAgent, Context, disable_tracing


class TaskAnalysis(BaseModel):
    """Task analysis result / タスク分析結果"""
    task_type: str
    complexity: str
    estimated_time: str
    requirements: list[str]


def example_basic_agent():
    """
    Basic RefinireAgent example
    基本的なRefinireAgentの例
    """
    print("🔧 Basic RefinireAgent Example")
    print("=" * 50)
    
    # Create simple agent
    # シンプルなエージェントを作成
    agent = RefinireAgent(
        name="task_helper",
        generation_instructions="You are a helpful task planning assistant. Analyze user requests and provide structured guidance.",
        model="gpt-4o-mini"
    )
    
    user_input = "I need to organize a team meeting for 10 people next week"
    
    print(f"📝 User Input: {user_input}")
    print("\n🤖 Processing...")
    
    try:
        context = Context()
        result_context = agent.run(user_input, context)
        result = result_context.shared_state.get('task_helper_result')
        
        if result:
            print(f"✅ Success! Generated response:")
            print(f"📄 Content: {result}")
        else:
            print(f"❌ No result generated")
            
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    print("\n" + "=" * 50)


def example_structured_output():
    """
    RefinireAgent with structured output example
    構造化出力付きRefinireAgentの例
    """
    print("📊 Structured Output RefinireAgent Example")
    print("=" * 50)
    
    # Create agent with structured output
    # 構造化出力付きエージェントを作成
    agent = RefinireAgent(
        name="task_analyzer",
        generation_instructions="""
        Analyze the given task and provide structured analysis.
        Return your response as JSON with the following structure:
        {
            "task_type": "category of the task",
            "complexity": "low/medium/high",
            "estimated_time": "time estimate",
            "requirements": ["list", "of", "requirements"]
        }
        """,
        output_model=TaskAnalysis,
        model="gpt-4o-mini"
    )
    
    user_input = "Create a mobile app for expense tracking"
    
    print(f"📝 User Input: {user_input}")
    print("\n🤖 Analyzing task structure...")
    
    try:
        context = Context()
        result_context = agent.run(user_input, context)
        result = result_context.shared_state.get('task_analyzer_result')
        
        if result and isinstance(result, TaskAnalysis):
            print(f"✅ Structured Analysis Complete:")
            print(f"📋 Task Type: {result.task_type}")
            print(f"⚡ Complexity: {result.complexity}")
            print(f"⏱️  Estimated Time: {result.estimated_time}")
            print(f"📝 Requirements:")
            for req in result.requirements:
                print(f"   • {req}")
        else:
            print(f"❌ Failed to generate structured output")
            
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    print("\n" + "=" * 50)


def example_with_tools():
    """
    RefinireAgent with tools example
    ツール付きRefinireAgentの例
    """
    print("🛠️  Tool-Enabled RefinireAgent Example")
    print("=" * 50)
    
    # Define simple tools
    # シンプルなツールを定義
    def get_weather(city: str) -> str:
        """Get the current weather for a city"""
        weather_data = {
            "Tokyo": "Sunny, 22°C",
            "London": "Rainy, 15°C", 
            "New York": "Cloudy, 18°C",
            "Paris": "Partly cloudy, 20°C"
        }
        return weather_data.get(city, f"Weather data not available for {city}")
    
    def calculate_age(birth_year: int) -> int:
        """Calculate age from birth year"""
        from datetime import datetime
        current_year = datetime.now().year
        return current_year - birth_year
    
    # Create agent with tools
    # ツール付きエージェントを作成
    agent = RefinireAgent(
        name="tool_assistant",
        generation_instructions="""
        You are a helpful assistant with access to tools:
        - get_weather: Get weather information for cities
        - calculate_age: Calculate age from birth year
        
        Use these tools when users ask relevant questions.
        """,
        tools=[get_weather, calculate_age],
        model="gpt-4o-mini"
    )
    
    user_input = "I was born in 1990, what's my age? Also, what's the weather in Tokyo?"
    
    print(f"📝 User Input: {user_input}")
    print("🛠️  Available Tools: get_weather, calculate_age")
    print("\n🤖 Processing with tools...")
    
    try:
        context = Context()
        result_context = agent.run(user_input, context)
        result = result_context.shared_state.get('tool_assistant_result')
        
        if result:
            print(f"✅ Success! AI used tools automatically:")
            print(f"📄 Response: {result}")
        else:
            print(f"❌ No result generated")
            
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    print("\n" + "=" * 50)


def main():
    """
    Run all examples
    全ての例を実行
    """
    print("🚀 Simple RefinireAgent Examples")
    print("Modern AI agent development with current API")
    print("現在のAPIでのモダンなAIエージェント開発\n")
    
    # Note: Tracing enabled by default for better observability
    # 注意: デフォルトでトレーシングが有効になっており、より良いオブザーバビリティを提供します
    
    # Check API key
    # APIキーをチェック
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Please set OPENAI_API_KEY environment variable.")
        return
    
    # Run examples
    # 例を実行
    example_basic_agent()
    example_structured_output()
    example_with_tools()
    
    print("\n🎉 All examples completed!")
    print("\n💡 Key Benefits:")
    print("   ✅ Uses current RefinireAgent API")
    print("   ✅ Clean output with disable_tracing()")
    print("   ✅ Structured output support")
    print("   ✅ Tool integration")
    print("   ✅ Simple and reliable")


if __name__ == "__main__":
    main()