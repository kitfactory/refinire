#!/usr/bin/env python3
"""
Simple Flow Tracing Example
シンプルなフロートレーシングの例

This demonstrates basic flow tracing without complex step interactions.
これは、複雑なステップ相互作用なしの基本的なフロートレーシングを示しています。
"""

import os
import asyncio
from refinire import RefinireAgent, Flow, Context
from agents.tracing import trace


def test_basic_flow_tracing():
    """
    Test basic flow tracing with RefinireAgent
    RefinireAgentでの基本的なフロートレーシングをテスト
    """
    print("=== Basic Flow Tracing Test ===")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  No OpenAI API key found. Please set OPENAI_API_KEY environment variable.")
        return
    
    # Create simple RefinireAgent
    # シンプルなRefinireAgentを作成
    agent = RefinireAgent(
        name="simple_processor",
        generation_instructions="Process the user input and provide a helpful response. Be concise.",
        model="gpt-4o-mini",
        history_size=1  # Limit history to prevent loops
    )
    
    # Create flow with single agent
    # 単一エージェントでフローを作成
    flow = Flow(
        name="SimpleProcessingFlow",
        start="simple_processor",
        steps={
            "simple_processor": agent
        }
    )
    
    print(f"Created flow with trace ID: {flow.trace_id}")
    return flow


async def run_tracing_test():
    """
    Run the tracing test
    トレーシングテストを実行
    """
    print("\n=== Running Flow Tracing Test ===")
    
    flow = test_basic_flow_tracing()
    if not flow:
        return
    
    # Test with trace context
    # トレースコンテキストでテスト
    with trace("simple_flow_test"):
        print(f"\n🚀 Starting flow execution...")
        print(f"📋 Flow Trace ID: {flow.trace_id}")
        
        try:
            result_context = await flow.run("Hello! Can you help me understand AI?")
            
            result = result_context.shared_state.get('simple_processor_result')
            print(f"\n✅ Flow completed successfully!")
            print(f"📋 Context Trace ID: {result_context.trace_id}")
            print(f"🎯 Result: {result}")
            
            # Verify trace ID consistency
            # トレースID一貫性を確認
            if flow.trace_id == result_context.trace_id:
                print("✅ Trace ID is consistent across flow and context")
            else:
                print("❌ Trace ID mismatch!")
                print(f"   Flow: {flow.trace_id}")
                print(f"   Context: {result_context.trace_id}")
                
        except Exception as e:
            print(f"❌ Flow execution failed: {e}")


def main():
    """
    Main function demonstrating simple flow tracing
    シンプルなフロートレーシングを示すメイン関数
    """
    print("🔍 Simple Flow Tracing Example")
    print("=" * 50)
    
    # Note: Tracing enabled by default for observability
    # 注意: オブザーバビリティのためデフォルトでトレーシングが有効
    
    # Run simple tracing test
    # シンプルなトレーシングテストを実行
    asyncio.run(run_tracing_test())
    
    print("\n" + "=" * 50)
    print("🎉 Simple flow tracing completed!")
    print("\n💡 Features Demonstrated:")
    print("   ✅ Flow creation with unique trace ID")
    print("   ✅ Trace ID consistency across execution")
    print("   ✅ Color-coded console tracing output")
    print("   ✅ Single-agent flow execution")


if __name__ == "__main__":
    main()