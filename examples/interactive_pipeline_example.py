"""
Interactive Pipeline Example - Demonstrating the new InteractivePipeline functionality
対話的パイプライン例 - 新しいInteractivePipeline機能のデモンストレーション

This example shows how to use InteractivePipeline for:
この例では、以下の用途でInteractivePipelineを使用する方法を示します：
1. Simple interactive conversations / シンプルな対話的会話
2. Requirements clarification / 要件明確化
3. Multi-step data collection / 複数ステップのデータ収集
"""

import os
from typing import Any
from refinire import (
    create_simple_interactive_pipeline,
    create_evaluated_interactive_pipeline,
    InteractivePipeline,
    InteractionResult,
    InteractionQuestion
)

# Set OpenAI API key (required for actual execution)
# OpenAI APIキーを設定（実際の実行に必要）
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"


def example_1_simple_interactive_conversation():
    """
    Example 1: Simple interactive conversation that continues until user says "done"
    例1: ユーザーが「done」と言うまで続くシンプルな対話的会話
    """
    print("=== Example 1: Simple Interactive Conversation ===")
    print("=== 例1: シンプルな対話的会話 ===")
    
    def completion_check(result: Any) -> bool:
        """Check if user wants to end the conversation"""
        return "done" in str(result).lower() or "終了" in str(result)
    
    # Create interactive pipeline
    # 対話的パイプラインを作成
    pipeline = create_simple_interactive_pipeline(
        name="simple_chat",
        instructions="You are a helpful assistant. Have a conversation with the user. When they say 'done' or want to end, acknowledge and say goodbye.",
        completion_check=completion_check,
        max_turns=10,
        model="gpt-4o-mini"
    )
    
    print(f"Pipeline created: {pipeline.name}")
    print(f"Max turns: {pipeline.max_turns}")
    print(f"Current turn: {pipeline.current_turn}")
    
    # Simulate conversation (without actual API calls)
    # 会話をシミュレート（実際のAPI呼び出しなし）
    print("\n--- Simulated Conversation ---")
    print("User: Hello, how are you?")
    print("Assistant: [Would respond with greeting and ask how to help]")
    print("User: I need help with Python")
    print("Assistant: [Would ask what specific Python help is needed]")
    print("User: done")
    print("Assistant: [Would say goodbye and mark conversation as complete]")
    
    return pipeline


def example_2_requirements_clarification():
    """
    Example 2: Requirements clarification for a software project
    例2: ソフトウェアプロジェクトの要件明確化
    """
    print("\n=== Example 2: Requirements Clarification ===")
    print("=== 例2: 要件明確化 ===")
    
    def completion_check(result: Any) -> bool:
        """Check if requirements are sufficiently clarified"""
        result_str = str(result).lower()
        return ("requirements are clear" in result_str or 
                "all information collected" in result_str or
                "要件が明確" in result_str)
    
    def custom_question_format(response: str, turn: int, remaining: int) -> str:
        """Custom formatting for clarification questions"""
        return f"[要件明確化 ターン{turn}/{turn + remaining}] {response}"
    
    # Create requirements clarification pipeline
    # 要件明確化パイプラインを作成
    pipeline = InteractivePipeline(
        name="requirements_clarification",
        generation_instructions="""
        You are a business analyst helping to clarify software requirements.
        Ask specific questions to understand:
        1. What the software should do
        2. Who will use it
        3. What platforms it should run on
        4. Any specific constraints or requirements
        
        When you have enough information, say "Requirements are clear" to complete.
        """,
        completion_check=completion_check,
        question_format=custom_question_format,
        max_turns=8,
        model="gpt-4o-mini"
    )
    
    print(f"Pipeline created: {pipeline.name}")
    print(f"Max turns: {pipeline.max_turns}")
    
    # Simulate requirements gathering
    # 要件収集をシミュレート
    print("\n--- Simulated Requirements Gathering ---")
    print("User: I want to build a web application")
    print("Assistant: [要件明確化 ターン1/8] What kind of web application? What should it do?")
    print("User: A task management system")
    print("Assistant: [要件明確化 ターン2/7] Who will be the primary users? Individual users or teams?")
    print("User: Teams of 5-20 people")
    print("Assistant: [要件明確化 ターン3/6] What features are most important? Task creation, assignment, deadlines?")
    print("User: All of those, plus progress tracking")
    print("Assistant: Requirements are clear - Team task management with creation, assignment, deadlines, and progress tracking.")
    
    return pipeline


def example_3_data_collection():
    """
    Example 3: Multi-step data collection with validation
    例3: 検証付き複数ステップデータ収集
    """
    print("\n=== Example 3: Multi-step Data Collection ===")
    print("=== 例3: 複数ステップデータ収集 ===")
    
    def completion_check(result: Any) -> bool:
        """Check if all required data has been collected"""
        result_str = str(result).lower()
        return ("data collection complete" in result_str or
                "all information gathered" in result_str or
                "データ収集完了" in result_str)
    
    # Create data collection pipeline with evaluation
    # 評価付きデータ収集パイプラインを作成
    pipeline = create_evaluated_interactive_pipeline(
        name="user_profile_collection",
        generation_instructions="""
        You are collecting user profile information. Ask for:
        1. Full name
        2. Email address
        3. Phone number
        4. Preferred contact method
        5. Areas of interest
        
        Validate each piece of information and ask for clarification if needed.
        When all information is collected and validated, say "Data collection complete".
        """,
        evaluation_instructions="""
        Evaluate if the collected information is:
        1. Complete (all 5 items collected)
        2. Valid (email format, phone format, etc.)
        3. Clear and unambiguous
        
        Score 100 if all criteria are met, lower scores for missing or invalid data.
        """,
        completion_check=completion_check,
        max_turns=12,
        threshold=90.0,
        model="gpt-4o-mini"
    )
    
    print(f"Pipeline created: {pipeline.name}")
    print(f"Evaluation threshold: {pipeline.threshold}")
    print(f"Max turns: {pipeline.max_turns}")
    
    # Simulate data collection
    # データ収集をシミュレート
    print("\n--- Simulated Data Collection ---")
    print("User: I want to create a profile")
    print("Assistant: [Turn 1] Great! Let's start with your full name.")
    print("User: John Smith")
    print("Assistant: [Turn 2] Thank you, John. What's your email address?")
    print("User: john@email.com")
    print("Assistant: [Turn 3] Perfect. Could you provide your phone number?")
    print("User: 555-1234")
    print("Assistant: [Turn 4] How would you prefer to be contacted - email or phone?")
    print("User: Email")
    print("Assistant: [Turn 5] What are your main areas of interest?")
    print("User: Technology, AI, programming")
    print("Assistant: Data collection complete - All profile information gathered and validated.")
    
    return pipeline


def example_4_interactive_pipeline_properties():
    """
    Example 4: Demonstrating InteractivePipeline properties and methods
    例4: InteractivePipelineのプロパティとメソッドのデモンストレーション
    """
    print("\n=== Example 4: Pipeline Properties and Methods ===")
    print("=== 例4: パイプラインのプロパティとメソッド ===")
    
    def simple_completion(result: Any) -> bool:
        return False  # Never complete for this demo
    
    pipeline = create_simple_interactive_pipeline(
        name="demo_pipeline",
        instructions="Demo pipeline for showing properties",
        completion_check=simple_completion,
        max_turns=5
    )
    
    print(f"Pipeline name: {pipeline.name}")
    print(f"Max turns: {pipeline.max_turns}")
    print(f"Current turn: {pipeline.current_turn}")
    print(f"Remaining turns: {pipeline.remaining_turns}")
    print(f"Is complete: {pipeline.is_complete}")
    print(f"Interaction history length: {len(pipeline.interaction_history)}")
    
    # Demonstrate reset functionality
    # リセット機能をデモンストレーション
    print("\n--- After Reset ---")
    pipeline.reset_interaction()
    print(f"Current turn: {pipeline.current_turn}")
    print(f"Remaining turns: {pipeline.remaining_turns}")
    print(f"Is complete: {pipeline.is_complete}")
    print(f"Interaction history length: {len(pipeline.interaction_history)}")
    
    return pipeline


def main():
    """
    Main function to run all examples
    全ての例を実行するメイン関数
    """
    print("Interactive Pipeline Examples")
    print("対話的パイプライン例")
    print("=" * 50)
    
    try:
        # Run all examples
        # 全ての例を実行
        example_1_simple_interactive_conversation()
        example_2_requirements_clarification()
        example_3_data_collection()
        example_4_interactive_pipeline_properties()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("全ての例が正常に完了しました！")
        
        print("\nKey Benefits of InteractivePipeline:")
        print("InteractivePipelineの主な利点:")
        print("✅ Generalized interactive conversation pattern")
        print("✅ 汎用的な対話パターン")
        print("✅ Consistent with LLMPipeline design")
        print("✅ LLMPipelineとの設計一貫性")
        print("✅ Flexible completion conditions")
        print("✅ 柔軟な完了条件")
        print("✅ Turn management and history tracking")
        print("✅ ターン管理と履歴追跡")
        print("✅ Customizable question formatting")
        print("✅ カスタマイズ可能な質問フォーマット")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print(f"例の実行中にエラー: {e}")


if __name__ == "__main__":
    main() 
