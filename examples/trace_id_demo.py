#!/usr/bin/env python3
"""
Trace ID Demo
トレースID デモ

This demonstrates trace ID consistency across different components.
これは、異なるコンポーネント間でのトレースID一貫性を示しています。
"""

import os
from refinire import RefinireAgent, Context


def test_trace_id_consistency():
    """
    Test trace ID consistency
    トレースID一貫性をテスト
    """
    print("=== Trace ID Consistency Test ===")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  No OpenAI API key found. Please set OPENAI_API_KEY environment variable.")
        return
    
    # Test 1: Single agent execution
    # テスト1: 単一エージェント実行
    print("\n--- Test 1: Single Agent ---")
    agent = RefinireAgent(
        name="trace_test_agent",
        generation_instructions="Respond briefly to the user input.",
        model="gpt-4o-mini"
    )
    
    context = Context()
    print(f"Initial context trace_id: {context.trace_id}")
    
    result_context = agent.run("Hello", context)
    
    print(f"Result context trace_id: {result_context.trace_id}")
    print(f"Agent result: {result_context.shared_state.get('trace_test_agent_result')}")
    
    # Test 2: Show tracing in action
    # テスト2: トレーシングの動作を表示
    print("\n--- Test 2: Tracing Output ---")
    agent2 = RefinireAgent(
        name="tracing_demo",
        generation_instructions="You are a helpful assistant. Answer in Japanese.",
        model="gpt-4o-mini"
    )
    
    context2 = Context()
    result_context2 = agent2.run("AIとは何ですか？", context2)
    
    print(f"Second agent result: {result_context2.shared_state.get('tracing_demo_result')}")


def main():
    """
    Main demonstration function
    メインデモンストレーション関数
    """
    print("🔍 Trace ID and Console Tracing Demo")
    print("=" * 50)
    
    print("📝 This demo shows:")
    print("   • Default console tracing (colored output)")
    print("   • Trace ID management")
    print("   • RefinireAgent execution tracing")
    
    test_trace_id_consistency()
    
    print("\n" + "=" * 50)
    print("🎉 Trace ID demo completed!")
    print("\n💡 Key Points:")
    print("   ✅ Console tracing is enabled by default")
    print("   ✅ Colored output shows Instruction/Prompt/Output")
    print("   ✅ Each execution has proper trace tracking")
    print("   ✅ For simple examples, use disable_tracing()")


if __name__ == "__main__":
    main()