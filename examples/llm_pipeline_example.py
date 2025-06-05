"""
LLMPipeline and GenAgentV2 Example - Modern replacement for deprecated AgentPipeline
LLMPipelineとGenAgentV2の例 - 非推奨のAgentPipelineに代わるモダンな実装
"""

import asyncio
from typing import Optional
from pydantic import BaseModel

from agents_sdk_models import (
    LLMPipeline, GenAgentV2, Flow, Context,
    create_simple_llm_pipeline, create_evaluated_llm_pipeline,
    create_simple_gen_agent_v2, create_evaluated_gen_agent_v2
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


def example_basic_llm_pipeline():
    """
    Basic LLMPipeline usage example
    基本的なLLMPipelineの使用例
    """
    print("🔧 Basic LLMPipeline Example")
    print("=" * 50)
    
    # Create simple pipeline
    # シンプルなパイプラインを作成
    pipeline = create_simple_llm_pipeline(
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