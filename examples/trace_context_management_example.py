#!/usr/bin/env python3
"""
Trace Context Management Example - トレースコンテキスト管理の例

English: This example demonstrates how the new trace context management works to avoid nested trace warnings.
日本語: この例では、ネストしたトレース警告を回避する新しいトレースコンテキスト管理の動作を実演します。
"""

import asyncio
import os
from refinire import RefinireAgent, has_active_trace_context
from refinire.agents.flow import SimpleFlow, simple_step, Context


async def trace_management_demo():
    """
    Demonstrate intelligent trace context management
    インテリジェントなトレースコンテキスト管理を実演
    """
    print("🔍 Trace Context Management Demo")
    print("🔍 トレースコンテキスト管理デモ")
    print("=" * 50)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        print("❌ OPENAI_API_KEY環境変数を設定してください。")
        return
    
    # Test 1: Single RefinireAgent (creates new trace)
    # テスト1: 単一のRefinireAgent（新しいトレースを作成）
    print("\n🧪 Test 1: Single RefinireAgent")
    print("🧪 テスト1: 単一のRefinireAgent")
    print(f"   Active trace before: {has_active_trace_context()}")
    print(f"   実行前のアクティブトレース: {has_active_trace_context()}")
    
    agent = RefinireAgent(
        name="single_agent",
        generation_instructions="Respond helpfully and concisely.",
        model="gpt-4o-mini"
    )
    
    result1 = await agent.run_async("Hello from single agent!")
    print(f"   ✅ Single agent result: {result1.content[:50]}...")
    print(f"   ✅ 単一エージェント結果: {result1.content[:50]}...")
    
    # Test 2: Flow with RefinireAgent (shares trace context)
    # テスト2: RefinireAgent付きFlow（トレースコンテキストを共有）
    print("\n🧪 Test 2: Flow with RefinireAgent (should share trace)")
    print("🧪 テスト2: RefinireAgent付きFlow（トレースを共有すべき）")
    
    async def flow_step_function(user_input: str, context: Context) -> Context:
        """Step function that uses RefinireAgent"""
        print(f"   🔄 Inside flow step - Active trace: {has_active_trace_context()}")
        print(f"   🔄 フローステップ内 - アクティブトレース: {has_active_trace_context()}")
        
        # This agent will detect the existing trace and not create a new one
        # このエージェントは既存のトレースを検出し、新しいものを作成しません
        flow_agent = RefinireAgent(
            name="flow_agent",
            generation_instructions="Respond helpfully and mention you're running in a flow.",
            model="gpt-4o-mini"
        )
        
        result = await flow_agent.run_async(user_input)
        context.shared_state['flow_result'] = result.content
        return context
    
    # Create and run flow
    # フローを作成して実行
    flow = SimpleFlow([
        simple_step("agent_step", flow_step_function)
    ], name="trace_demo_flow")
    
    print(f"   Active trace before flow: {has_active_trace_context()}")
    print(f"   フロー実行前のアクティブトレース: {has_active_trace_context()}")
    
    result2 = await flow.run("Hello from flow!")
    
    print(f"   ✅ Flow result: {result2.shared_state.get('flow_result', '')[:50]}...")
    print(f"   ✅ フロー結果: {result2.shared_state.get('flow_result', '')[:50]}...")
    
    # Test 3: Nested flows (still share context)
    # テスト3: ネストしたフロー（依然としてコンテキストを共有）
    print("\n🧪 Test 3: Nested Flow execution")
    print("🧪 テスト3: ネストしたフロー実行")
    
    async def nested_flow_step(user_input: str, context: Context) -> Context:
        """Step that creates another SimpleFlow"""
        print(f"   🔄 In nested step - Active trace: {has_active_trace_context()}")
        print(f"   🔄 ネストステップ内 - アクティブトレース: {has_active_trace_context()}")
        
        # Create inner flow
        # 内部フローを作成
        async def inner_step(inner_input: str, inner_context: Context) -> Context:
            agent = RefinireAgent(
                name="nested_agent",
                generation_instructions="You are in a nested flow. Be brief.",
                model="gpt-4o-mini"
            )
            result = await agent.run_async(inner_input)
            inner_context.shared_state['nested_result'] = result.content
            return inner_context
        
        inner_flow = SimpleFlow([
            simple_step("nested_step", inner_step)
        ], name="nested_flow")
        
        inner_result = await inner_flow.run("Nested hello!")
        context.shared_state['nested_flow_result'] = inner_result.shared_state.get('nested_result', '')
        return context
    
    outer_flow = SimpleFlow([
        simple_step("outer_step", nested_flow_step)
    ], name="outer_flow")
    
    result3 = await outer_flow.run("Outer input")
    
    print(f"   ✅ Nested flow result: {result3.shared_state.get('nested_flow_result', '')[:50]}...")
    print(f"   ✅ ネストフロー結果: {result3.shared_state.get('nested_flow_result', '')[:50]}...")
    
    print("\n🎉 Trace Context Management Demo completed!")
    print("🎉 トレースコンテキスト管理デモ完了！")
    print("\n💡 Key Benefits:")
    print("💡 主要な利点:")
    print("   ✅ No 'Trace already exists' warnings")
    print("   ✅ 「Trace already exists」警告なし")
    print("   ✅ Single trace per workflow execution")  
    print("   ✅ ワークフロー実行ごとに単一トレース")
    print("   ✅ Automatic trace context detection")
    print("   ✅ 自動トレースコンテキスト検出")
    print("   ✅ Works with both Flow and SimpleFlow")
    print("   ✅ FlowとSimpleFlowの両方で動作")


if __name__ == "__main__":
    asyncio.run(trace_management_demo())