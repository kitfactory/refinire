#!/usr/bin/env python3
"""
Flow Tracing Example
フロートレーシングの例

This demonstrates unified trace ID across Flow steps and observability features.
これは、フローステップ間での統一されたトレースIDと観測性機能を示しています。
"""

import os
import asyncio
from refinire import (
    Flow, Context, FunctionStep, ConditionStep, 
    RefinireAgent
)
from agents.tracing import trace


def create_data_processing_flow():
    """
    Create a data processing workflow with multiple steps
    複数のステップを持つデータ処理ワークフローを作成
    """
    print("=== Creating Data Processing Flow ===")
    
    # Step 1: Data validation
    # ステップ1: データ検証
    def validate_data(user_input, context):
        """Validate input data"""
        print(f"📝 Validating data: {user_input}")
        
        # Simple validation logic
        # シンプルな検証ロジック
        if not user_input or len(user_input.strip()) < 3:
            context.shared_state["validation_result"] = "invalid"
            context.shared_state["error"] = "Input too short"
        else:
            context.shared_state["validation_result"] = "valid"
            context.shared_state["processed_data"] = user_input.strip().upper()
        
        return context
    
    # Step 2: Route based on validation
    # ステップ2: 検証結果に基づくルーティング
    def is_valid(context):
        """Check if data is valid"""
        return context.shared_state.get("validation_result") == "valid"
    
    # Step 3a: Process valid data
    # ステップ3a: 有効なデータの処理
    def process_valid_data(user_input, context):
        """Process valid data"""
        data = context.shared_state.get("processed_data", "")
        print(f"✅ Processing valid data: {data}")
        
        # Simulate processing
        # 処理をシミュレート
        result = f"PROCESSED: {data} (Length: {len(data)})"
        context.shared_state["final_result"] = result
        context.finish()
        return context
    
    # Step 3b: Handle invalid data
    # ステップ3b: 無効なデータの処理
    def handle_invalid_data(user_input, context):
        """Handle invalid data"""
        error = context.shared_state.get("error", "Unknown error")
        print(f"❌ Handling invalid data: {error}")
        
        context.shared_state["final_result"] = f"ERROR: {error}"
        context.finish()
        return context
    
    # Create flow steps
    # フローステップを作成
    validate_step = FunctionStep("validate", validate_data, next_step="route")
    route_step = ConditionStep("route", is_valid, "process_valid", "handle_invalid")
    process_step = FunctionStep("process_valid", process_valid_data)
    error_step = FunctionStep("handle_invalid", handle_invalid_data)
    
    # Create flow with trace ID
    # トレースID付きフローを作成
    flow = Flow(
        name="DataProcessingFlow",
        start="validate",
        steps={
            "validate": validate_step,
            "route": route_step,
            "process_valid": process_step,
            "handle_invalid": error_step
        }
    )
    
    print(f"Created flow with trace ID: {flow.trace_id}")
    return flow


def create_ai_agent_flow():
    """
    Create a flow with AI agents
    AIエージェント付きフローを作成
    """
    print("\n=== Creating AI Agent Flow ===")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Skipping AI agent flow (no API key)")
        return None
    
    # AI Agent for text analysis
    # テキスト分析用AIエージェント
    analyzer = RefinireAgent(
        name="text_analyzer",
        generation_instructions="""
        Analyze the given text and provide:
        1. Sentiment (positive/negative/neutral)
        2. Main topics
        3. Word count
        
        Respond in JSON format.
        """,
        model="gpt-4o-mini"
    )
    
    # Post-processing step
    # 後処理ステップ
    def summarize_analysis(user_input, context):
        """Summarize the analysis result"""
        analysis = context.shared_state.get("text_analyzer_result", "No analysis")
        print(f"📊 Analysis completed: {analysis[:100]}...")
        
        context.shared_state["summary"] = f"Analysis of '{user_input}' completed"
        context.finish()
        return context
    
    # Create AI agent flow
    # AIエージェントフローを作成
    summary_step = FunctionStep("summarize", summarize_analysis)
    
    flow = Flow(
        name="TextAnalysisFlow",
        start="text_analyzer",
        steps={
            "text_analyzer": analyzer,
            "summarize": summary_step
        }
    )
    
    print(f"Created AI flow with trace ID: {flow.trace_id}")
    return flow


async def test_flow_tracing():
    """
    Test flow tracing with unified trace IDs
    統一されたトレースIDでフロートレーシングをテスト
    """
    print("\n=== Testing Flow Tracing ===")
    
    # Test 1: Data processing flow
    # テスト1: データ処理フロー
    print("\n--- Test 1: Valid Data ---")
    data_flow = create_data_processing_flow()
    
    # Use trace context for unified tracing
    # 統一されたトレーシング用のトレースコンテキストを使用
    with trace("data_processing_test"):
        result_context = await data_flow.run("Hello World Test Data")
        result = result_context.shared_state.get("final_result")
        print(f"🎯 Result: {result}")
        print(f"📋 Trace ID: {data_flow.trace_id}")
        print(f"📋 Context Trace ID: {result_context.trace_id}")
    
    print("\n--- Test 2: Invalid Data ---")
    data_flow2 = create_data_processing_flow()
    
    with trace("data_processing_invalid_test"):
        result_context2 = await data_flow2.run("Hi")  # Too short
        result2 = result_context2.shared_state.get("final_result")
        print(f"🎯 Result: {result2}")
        print(f"📋 Trace ID: {data_flow2.trace_id}")
    
    # Test 3: AI agent flow (if API key available)
    # テスト3: AIエージェントフロー（APIキーが利用可能な場合）
    ai_flow = create_ai_agent_flow()
    if ai_flow:
        print("\n--- Test 3: AI Agent Flow ---")
        with trace("ai_analysis_test"):
            result_context3 = await ai_flow.run("I love using AI tools for development!")
            summary = result_context3.shared_state.get("summary")
            print(f"🎯 Summary: {summary}")
            print(f"📋 AI Flow Trace ID: {ai_flow.trace_id}")


def main():
    """
    Main function demonstrating flow tracing
    フロートレーシングを示すメイン関数
    """
    print("🔍 Flow Tracing and Observability Example")
    print("=" * 60)
    
    # Note: Tracing enabled by default for observability
    # 注意: オブザーバビリティのためデフォルトでトレーシングが有効
    
    # Run flow tracing tests
    # フロートレーシングテストを実行
    asyncio.run(test_flow_tracing())
    
    print("\n" + "=" * 60)
    print("🎉 Flow tracing demonstration completed!")
    print("\n💡 Key Features Demonstrated:")
    print("   ✅ Unified trace IDs across flow steps")
    print("   ✅ Color-coded console tracing output")
    print("   ✅ Step-by-step execution visibility")
    print("   ✅ Context state tracking")
    print("   ✅ AI agent integration with tracing")


if __name__ == "__main__":
    main()