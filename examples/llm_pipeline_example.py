"""
RefinireAgent and GenAgentV2 Example - Modern AI agent development
RefinireAgentとGenAgentV2の例 - モダンなAIエージェント開発
"""

import asyncio
from typing import Optional
from pydantic import BaseModel

from refinire import (
    RefinireAgent, GenAgentV2, Flow, Context,
    create_simple_agent, create_evaluated_agent,
    create_simple_gen_agent_v2, create_evaluated_gen_agent_v2,
    create_tool_enabled_agent, create_calculator_agent,
    create_web_search_agent
)


# Example data models for structured output
# 構造化出力用のサンプルデータモデル
class TaskAnalysis(BaseModel):
    """Task analysis result / タスク分析結果"""
    task_type: str
    complexity: str
    estimated_time: str
    requirements: list[str]


class TaskPlan(BaseModel):
    """Task execution plan / タスク実行計画"""
    steps: list[str]
    resources: list[str]
    timeline: str
    success_criteria: str


def example_basic_refinire_agent():
    """
    Basic RefinireAgent usage example
    基本的なRefinireAgentの使用例
    """
    print("🔧 Basic RefinireAgent Example")
    print("=" * 50)
    
    # Create simple agent
    # シンプルなエージェントを作成
    agent = create_simple_agent(
        name="task_helper",
        instructions="You are a helpful task planning assistant. Analyze user requests and provide structured guidance.",
        model="gpt-4o-mini"
    )
    
    # Example usage
    # 使用例
    user_input = "I need to organize a team meeting for 10 people next week"
    
    print(f"📝 User Input: {user_input}")
    print("\n🤖 Processing...")
    
    # Note: This would require actual OpenAI API key to run
    # 注意：実際に実行するにはOpenAI APIキーが必要です
    try:
        result = pipeline.run(user_input)
        
        if result.success:
            print(f"✅ Success! Generated response:")
            print(f"📄 Content: {result.content}")
            print(f"🔄 Attempts: {result.attempts}")
        else:
            print(f"❌ Failed: {result.metadata.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"⚠️  Note: This example requires OpenAI API key. Error: {e}")
    
    print("\n" + "=" * 50)


def example_evaluated_llm_pipeline():
    """
    LLMPipeline with evaluation example
    評価機能付きLLMPipelineの例
    """
    print("🔍 Evaluated LLMPipeline Example")
    print("=" * 50)
    
    # Create pipeline with evaluation
    # 評価機能付きパイプラインを作成
    pipeline = create_evaluated_llm_pipeline(
        name="quality_writer",
        generation_instructions="""
        You are a professional content writer. Create high-quality, engaging content 
        based on user requests. Focus on clarity, structure, and value.
        """,
        evaluation_instructions="""
        Evaluate the generated content on:
        1. Clarity and readability (0-25 points)
        2. Structure and organization (0-25 points)  
        3. Value and usefulness (0-25 points)
        4. Engagement and style (0-25 points)
        
        Provide a total score out of 100 and brief feedback.
        """,
        model="gpt-4o-mini",
        threshold=80.0,
        max_retries=2
    )
    
    user_input = "Write a brief guide on effective remote work practices"
    
    print(f"📝 User Input: {user_input}")
    print(f"🎯 Quality Threshold: {pipeline.threshold}%")
    print("\n🤖 Processing with evaluation...")
    
    try:
        result = pipeline.run(user_input)
        
        if result.success:
            print(f"✅ Success! High-quality content generated:")
            print(f"📄 Content: {result.content[:200]}...")
            print(f"⭐ Evaluation Score: {result.evaluation_score}%")
            print(f"🔄 Attempts: {result.attempts}")
        else:
            print(f"❌ Failed to meet quality threshold: {result.metadata.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"⚠️  Note: This example requires OpenAI API key. Error: {e}")
    
    print("\n" + "=" * 50)


def example_structured_output_pipeline():
    """
    LLMPipeline with structured output example
    構造化出力付きLLMPipelineの例
    """
    print("📊 Structured Output LLMPipeline Example")
    print("=" * 50)
    
    # Create pipeline with structured output
    # 構造化出力付きパイプラインを作成
    pipeline = LLMPipeline(
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
        result = pipeline.run(user_input)
        
        if result.success and isinstance(result.content, TaskAnalysis):
            analysis = result.content
            print(f"✅ Structured Analysis Complete:")
            print(f"📋 Task Type: {analysis.task_type}")
            print(f"⚡ Complexity: {analysis.complexity}")
            print(f"⏱️  Estimated Time: {analysis.estimated_time}")
            print(f"📝 Requirements:")
            for req in analysis.requirements:
                print(f"   • {req}")
        else:
            print(f"❌ Failed to generate structured output")
            
    except Exception as e:
        print(f"⚠️  Note: This example requires OpenAI API key. Error: {e}")
    
    print("\n" + "=" * 50)


async def example_gen_agent_v2_in_flow():
    """
    GenAgentV2 in Flow workflow example
    FlowワークフローでのGenAgentV2の例
    """
    print("🔄 GenAgentV2 in Flow Example")
    print("=" * 50)
    
    # Create GenAgentV2 steps
    # GenAgentV2ステップを作成
    analyzer = create_simple_gen_agent_v2(
        name="task_analyzer",
        instructions="""
        Analyze the user's task request and identify key requirements, 
        complexity, and initial planning considerations.
        """,
        next_step="planner"
    )
    
    planner = create_evaluated_gen_agent_v2(
        name="task_planner", 
        generation_instructions="""
        Based on the task analysis, create a detailed execution plan with
        specific steps, required resources, timeline, and success criteria.
        """,
        evaluation_instructions="""
        Evaluate the plan on:
        1. Completeness and detail (0-30 points)
        2. Feasibility and practicality (0-30 points)
        3. Clear timeline and milestones (0-20 points)
        4. Success criteria definition (0-20 points)
        
        Provide total score out of 100.
        """,
        threshold=85.0,
        next_step="reviewer"
    )
    
    reviewer = create_simple_gen_agent_v2(
        name="plan_reviewer",
        instructions="""
        Review the task analysis and execution plan. Provide final 
        recommendations, potential risks, and optimization suggestions.
        """
    )
    
    # Create Flow
    # Flowを作成
    flow = Flow(
        name="task_planning_flow",
        steps=[analyzer, planner, reviewer],
        max_steps=10
    )
    
    print("🏗️  Created task planning workflow with 3 GenAgentV2 steps")
    print("📋 Steps: Analyzer → Planner → Reviewer")
    
    # Example execution (would require API key)
    # 実行例（APIキーが必要）
    user_input = "Plan a company retreat for 50 employees"
    
    print(f"\n📝 User Input: {user_input}")
    print("🤖 Processing through workflow...")
    
    try:
        # Create context and run flow
        # コンテキストを作成してFlowを実行
        ctx = Context()
        ctx.last_user_input = user_input
        
        # Note: This would require actual OpenAI API key
        # 注意：実際のOpenAI APIキーが必要
        # result_ctx = await flow.run(ctx)
        
        print("✅ Workflow would execute:")
        print("   1. 🔍 Analyzer: Analyze retreat requirements")
        print("   2. 📋 Planner: Create detailed execution plan") 
        print("   3. 👀 Reviewer: Review and optimize plan")
        print("\n💡 Each step uses LLMPipeline internally (no async issues!)")
        
    except Exception as e:
        print(f"⚠️  Note: This example requires OpenAI API key. Error: {e}")
    
    print("\n" + "=" * 50)


def example_pipeline_features():
    """
    Demonstrate advanced LLMPipeline features
    LLMPipelineの高度な機能のデモ
    """
    print("⚙️  Advanced LLMPipeline Features")
    print("=" * 50)
    
    # Input guardrails
    # 入力ガードレール
    def content_filter(text: str) -> bool:
        """Filter inappropriate content / 不適切なコンテンツをフィルタ"""
        blocked_words = ["spam", "inappropriate"]
        return not any(word in text.lower() for word in blocked_words)
    
    def length_filter(text: str) -> bool:
        """Filter overly long inputs / 長すぎる入力をフィルタ"""
        return len(text) <= 500
    
    # Output guardrails  
    # 出力ガードレール
    def quality_filter(text: str) -> bool:
        """Ensure minimum quality output / 最低品質の出力を保証"""
        return len(text) > 10 and not text.lower().startswith("i cannot")
    
    # Create pipeline with guardrails
    # ガードレール付きパイプラインを作成
    pipeline = LLMPipeline(
        name="guarded_assistant",
        generation_instructions="Provide helpful and appropriate responses to user queries.",
        input_guardrails=[content_filter, length_filter],
        output_guardrails=[quality_filter],
        history_size=5,
        max_retries=2,
        model="gpt-4o-mini"
    )
    
    print("🛡️  Created pipeline with guardrails:")
    print("   • Input: Content filter + Length limit")
    print("   • Output: Quality assurance")
    print("   • History: Last 5 interactions")
    print("   • Retries: Up to 2 attempts")
    
    # Test guardrails
    # ガードレールをテスト
    test_inputs = [
        "What is machine learning?",  # Valid
        "This is spam content",       # Blocked by content filter
        "a" * 600                     # Blocked by length filter
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n🧪 Test {i}: {test_input[:50]}{'...' if len(test_input) > 50 else ''}")
        
        try:
            # Simulate validation (without actual API call)
            # 検証をシミュレート（実際のAPI呼び出しなし）
            input_valid = all(guard(test_input) for guard in pipeline.input_guardrails)
            
            if input_valid:
                print("   ✅ Input passed guardrails")
            else:
                print("   ❌ Input blocked by guardrails")
                
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    
    print("\n" + "=" * 50)


def example_tool_enabled_pipeline():
    """
    Tool-enabled LLMPipeline example
    tool機能付きLLMPipelineの例
    """
    print("🛠️  Tool-Enabled LLMPipeline Example")
    print("=" * 50)
    
    # Define custom tools
    # カスタムtoolを定義
    def get_weather(city: str) -> str:
        """Get the current weather for a city"""
        # Simulated weather data
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
    
    def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
        """Convert currency (simplified rates)"""
        # Simplified exchange rates
        rates = {
            ("USD", "JPY"): 150.0,
            ("USD", "EUR"): 0.85,
            ("EUR", "JPY"): 160.0,
            ("JPY", "USD"): 1/150.0,
            ("EUR", "USD"): 1/0.85,
            ("JPY", "EUR"): 1/160.0
        }
        
        rate = rates.get((from_currency, to_currency), 1.0)
        converted = amount * rate
        return f"{amount} {from_currency} = {converted:.2f} {to_currency}"
    
    # Create pipeline with tools
    # tool付きパイプラインを作成
    pipeline = create_tool_enabled_llm_pipeline(
        name="multi_tool_assistant",
        instructions="""
        You are a helpful assistant with access to multiple tools:
        - get_weather: Get weather information for cities
        - calculate_age: Calculate age from birth year
        - convert_currency: Convert between currencies
        
        Use these tools when users ask relevant questions.
        """,
        tools=[get_weather, calculate_age, convert_currency],
        model="gpt-4o-mini"
    )
    
    # Test complex query requiring multiple tools
    # 複数toolが必要な複雑なクエリをテスト
    user_input = "I was born in 1990, what's my age? Also, what's the weather in Tokyo and how much is 100 USD in JPY?"
    
    print(f"📝 User Input: {user_input}")
    print(f"🛠️  Available Tools: {pipeline.list_tools()}")
    print("\n🤖 Processing with tools...")
    
    try:
        result = pipeline.run(user_input)
        
        if result.success:
            print(f"✅ Success! AI used tools automatically:")
            print(f"📄 Response: {result.content}")
            print(f"🔄 Attempts: {result.attempts}")
            print(f"📊 Metadata: {result.metadata}")
        else:
            print(f"❌ Failed: {result.metadata.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"⚠️  Note: This example requires OpenAI API key. Error: {e}")
    
    print("\n" + "=" * 50)


def example_calculator_pipeline():
    """
    Calculator pipeline example  
    計算機パイプラインの例
    """
    print("🧮 Calculator LLMPipeline Example")
    print("=" * 50)
    
    # Create calculator pipeline
    # 計算機パイプラインを作成
    pipeline = create_calculator_pipeline(
        name="math_assistant",
        model="gpt-4o-mini"
    )
    
    user_input = "Calculate the area of a circle with radius 5, and then find the square root of that result"
    
    print(f"📝 User Input: {user_input}")
    print(f"🛠️  Available Tools: {pipeline.list_tools()}")
    print("\n🤖 Processing mathematical query...")
    
    try:
        result = pipeline.run(user_input)
        
        if result.success:
            print(f"✅ Success! Mathematical calculation completed:")
            print(f"📄 Response: {result.content}")
        else:
            print(f"❌ Failed: {result.metadata.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"⚠️  Note: This example requires OpenAI API key. Error: {e}")
    
    print("\n" + "=" * 50)


def example_web_search_pipeline():
    """
    Web search pipeline example
    Web検索パイプラインの例
    """
    print("🔍 Web Search LLMPipeline Example")
    print("=" * 50)
    
    # Create web search pipeline
    # Web検索パイプラインを作成
    pipeline = create_web_search_pipeline(
        name="search_assistant",
        model="gpt-4o-mini"
    )
    
    user_input = "What are the latest developments in AI technology?"
    
    print(f"📝 User Input: {user_input}")
    print(f"🛠️  Available Tools: {pipeline.list_tools()}")
    print("\n🤖 Processing search query...")
    
    try:
        result = pipeline.run(user_input)
        
        if result.success:
            print(f"✅ Success! Search completed:")
            print(f"📄 Response: {result.content}")
            print("💡 Note: This uses a placeholder search implementation")
        else:
            print(f"❌ Failed: {result.metadata.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"⚠️  Note: This example requires OpenAI API key. Error: {e}")
    
    print("\n" + "=" * 50)


def example_manual_tool_management():
    """
    Manual tool management example
    手動tool管理の例
    """
    print("⚙️  Manual Tool Management Example")
    print("=" * 50)
    
    # Create basic pipeline
    # 基本パイプラインを作成
    pipeline = LLMPipeline(
        name="custom_assistant",
        generation_instructions="You are a helpful assistant with access to tools.",
        model="gpt-4o-mini",
        tools=[]  # Start with no tools
    )
    
    # Define and add tools manually
    # toolを手動で定義・追加
    def greet_user(name: str) -> str:
        """Greet a user by name"""
        return f"Hello, {name}! Nice to meet you!"
    
    def get_time() -> str:
        """Get the current time"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Add tools one by one
    # toolを一つずつ追加
    pipeline.add_function_tool(greet_user)
    pipeline.add_function_tool(get_time)
    
    print(f"🛠️  Added Tools: {pipeline.list_tools()}")
    
    user_input = "Greet me as Alice and tell me the current time"
    
    print(f"📝 User Input: {user_input}")
    print("\n🤖 Processing with manually added tools...")
    
    try:
        result = pipeline.run(user_input)
        
        if result.success:
            print(f"✅ Success! Tools executed:")
            print(f"📄 Response: {result.content}")
        else:
            print(f"❌ Failed: {result.metadata.get('error', 'Unknown error')}")
    
        # Demonstrate tool removal
        # tool削除をデモ
        print(f"\n🗑️  Removing 'greet_user' tool...")
        removed = pipeline.remove_tool("greet_user")
        print(f"   Removed: {removed}")
        print(f"🛠️  Remaining Tools: {pipeline.list_tools()}")
            
    except Exception as e:
        print(f"⚠️  Note: This example requires OpenAI API key. Error: {e}")
    
    print("\n" + "=" * 50)


def main():
    """
    Run all examples
    全ての例を実行
    """
    print("🚀 LLMPipeline & GenAgentV2 Examples")
    print("Modern replacement for deprecated AgentPipeline")
    print("非推奨のAgentPipelineに代わるモダンな実装\n")
    
    # Basic examples
    # 基本例
    example_basic_llm_pipeline()
    example_evaluated_llm_pipeline()
    example_structured_output_pipeline()
    
    # Advanced features
    # 高度な機能
    example_pipeline_features()
    
    # Flow integration
    # Flow統合
    print("🔄 Running async Flow example...")
    asyncio.run(example_gen_agent_v2_in_flow())
    
    # New examples
    # 新しい例
    example_tool_enabled_pipeline()
    example_calculator_pipeline()
    example_web_search_pipeline()
    example_manual_tool_management()
    
    print("\n🎉 All examples completed!")
    print("\n💡 Key Benefits of New Implementation:")
    print("   ✅ No dependency on deprecated AgentPipeline")
    print("   ✅ No async event loop conflicts")
    print("   ✅ Direct OpenAI Python SDK usage")
    print("   ✅ Full Flow/Step architecture support")
    print("   ✅ Comprehensive testing coverage")
    print("   ✅ Future-proof design")


if __name__ == "__main__":
    main() 
