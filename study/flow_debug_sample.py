#!/usr/bin/env python3
"""
Flow Debug Sample - Debug Flow execution
フロー実行デバッグ用サンプル
"""

import asyncio
import os
from refinire.agents.flow import Flow, FunctionStep, Context
from refinire import RefinireAgent


async def flow_debug_demo():
    """Debug Flow execution"""
    print("🔍 Flow Debug Sample")
    print("🔍 フローデバッグサンプル")
    print("=" * 40)
    
    # Simple test function / シンプルなテスト関数
    async def simple_test(user_input: str, context: Context) -> Context:
        print(f"   📝 simple_test called with user_input: {user_input}, context: {type(context)}")
        topic = context.shared_state.get('topic', 'test topic')
        result = f"Processed: {topic}"
        context.shared_state['result'] = result
        print(f"   📝 simple_test result: {result}")
        return context
    
    # Second test function / 第2テスト関数
    async def second_test(user_input: str, context: Context) -> Context:
        print(f"   📝 second_test called with user_input: {user_input}, context: {type(context)}")
        prev_result = context.shared_state.get('result', '')
        result = f"Extended: {prev_result}"
        context.shared_state['final_result'] = result
        print(f"   📝 second_test result: {result}")
        return context
    
    # Create simple workflow / シンプルなワークフローを作成
    steps = {
        "step1": FunctionStep("step1", simple_test, next_step="step2"),
        "step2": FunctionStep("step2", second_test)  # Last step
    }
    workflow = Flow(start="step1", steps=steps)
    
    print("🚀 Starting debug workflow...")
    print("🚀 デバッグワークフロー開始...")
    
    context = Context()
    context.shared_state['topic'] = 'Debug Test Topic'
    
    try:
        print("📋 Before workflow execution:")
        print(f"   📄 Context: {context.shared_state}")
        
        result = await workflow.run()
        
        print("📋 After workflow execution:")
        print(f"   ✅ Success: {result is not None}")
        print(f"   📄 Final context shared_state: {result.shared_state}")
        print(f"   📄 Final messages count: {len(result.messages)}")
        
        # Show messages if any
        for i, msg in enumerate(result.messages):
            print(f"   📝 Message {i}: {msg.role} - {msg.content[:100]}...")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("🎉 Debug demo completed!")


if __name__ == "__main__":
    asyncio.run(flow_debug_demo())