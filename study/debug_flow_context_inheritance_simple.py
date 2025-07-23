#!/usr/bin/env python3
"""
Simplified debug script for investigating Flow Context inheritance.
Context継承を調査するための簡略化デバッグスクリプト。

Focuses specifically on Context object identity and data preservation between steps.
ステップ間でのContextオブジェクト識別とデータ保持に特化。
"""

import asyncio
import sys
import os

# Add src to path for import
# インポートのためのsrcパス追加
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from refinire.agents.flow.flow import Flow
from refinire.agents.flow.step import FunctionStep
from refinire.agents.flow.context import Context
from refinire.agents.pipeline.llm_pipeline import RefinireAgent


def print_context_debug(stage: str, context: Context, step_name: str = ""):
    """Print detailed context debugging information"""
    print(f"\n{'='*60}")
    print(f"CONTEXT DEBUG - {stage}")
    if step_name:
        print(f"Step: {step_name}")
    print(f"{'='*60}")
    print(f"Context ID: {id(context)}")
    print(f"Trace ID: {getattr(context, 'trace_id', 'None')}")
    print(f"Current Step: {context.current_step}")
    print(f"Next Label: {context.next_label}")
    print(f"Step Count: {context.step_count}")
    print(f"Messages: {len(context.messages)}")
    print(f"Shared State Keys: {list(context.shared_state.keys())}")
    print(f"Shared State: {context.shared_state}")
    print(f"Result: {context.result is not None}")
    print(f"Content: {context.content}")
    print(f"Success: {context.success}")
    print(f"Finished: {context.finished}")
    
    if context.messages:
        print("Recent Messages:")
        for i, msg in enumerate(context.messages[-3:]):
            content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            print(f"  {i+1}. [{msg.role}] {content}")
    print(f"{'='*60}")


async def simple_step_1(user_input: str, context: Context) -> Context:
    """First step - stores data in Context"""
    print_context_debug("STEP1_BEFORE", context, "step1")
    
    # Add some data to shared state
    # 共有状態にデータを追加
    context.shared_state['step1_data'] = 'Hello from step 1'
    context.shared_state['step1_counter'] = 1
    context.shared_state['step_sequence'] = ['step1']
    
    # Add a system message
    # システムメッセージを追加
    context.add_system_message("Step 1 completed successfully")
    
    print_context_debug("STEP1_AFTER", context, "step1")
    
    # Route to next step
    # 次ステップにルーティング
    print(f"Step 1: Setting next step to 'step2'. Before: {context.next_label}")
    context.goto("step2")
    print(f"Step 1: After goto: {context.next_label}")
    
    return context


async def simple_step_2(user_input: str, context: Context) -> Context:
    """Second step - tries to access data from Context"""
    print_context_debug("STEP2_BEFORE", context, "step2")
    
    # Check what data is available
    # 利用可能なデータをチェック
    print(f"Step 2: Found shared_state keys: {list(context.shared_state.keys())}")
    print(f"Step 2: step1_data = {context.shared_state.get('step1_data', 'NOT_FOUND')}")
    print(f"Step 2: step1_counter = {context.shared_state.get('step1_counter', 'NOT_FOUND')}")
    print(f"Step 2: step_sequence = {context.shared_state.get('step_sequence', 'NOT_FOUND')}")
    
    # Add our own data
    # 独自のデータを追加
    context.shared_state['step2_data'] = 'Hello from step 2'
    context.shared_state['step2_counter'] = 2
    
    if 'step_sequence' in context.shared_state:
        context.shared_state['step_sequence'].append('step2')
    
    # Add a system message
    # システムメッセージを追加
    context.add_system_message("Step 2 completed successfully")
    
    print_context_debug("STEP2_AFTER", context, "step2")
    
    # Finish the flow
    # フローを終了
    print(f"Step 2: Finishing flow. Before: {context.next_label}")
    context.finish()
    print(f"Step 2: After finish: {context.next_label}")
    
    return context


async def test_context_inheritance():
    """Test Context inheritance between Flow steps"""
    
    print("Context Inheritance Test - Simple Version")
    print("="*80)
    
    # Create Flow with simple function steps
    # シンプルな関数ステップでFlowを作成
    flow = Flow(
        start="step1",
        steps={
            "step1": FunctionStep("step1", simple_step_1),
            "step2": FunctionStep("step2", simple_step_2)
        },
        name="SimpleContextTest"
    )
    
    print_context_debug("INITIAL", flow.context, "flow_init")
    
    # Run the flow
    # フローを実行
    try:
        print("\nStarting Flow execution...")
        initial_input = "Test input for context inheritance"
        
        # Store initial context ID for tracking
        # 追跡のため初期コンテキストIDを保存
        initial_context_id = id(flow.context)
        print(f"Initial Context ID: {initial_context_id}")
        
        # Add debugging to monitor the flow execution process
        # フロー実行プロセスを監視するデバッグを追加
        print(f"Before Flow.run: next_label = {flow.context.next_label}, finished = {flow.context.finished}")
        
        final_context = await flow.run(initial_input)
        
        print(f"After Flow.run: next_label = {final_context.next_label}, finished = {final_context.finished}")
        
        print_context_debug("FINAL", final_context, "flow_final")
        
        # Check if same context object was used throughout
        # 同一コンテキストオブジェクトが全体で使用されたかチェック
        final_context_id = id(final_context)
        print(f"\nContext Object Identity Check:")
        print(f"Initial Context ID: {initial_context_id}")
        print(f"Final Context ID: {final_context_id}")
        print(f"Same Object: {initial_context_id == final_context_id}")
        
        # Check data preservation
        # データ保持をチェック
        print(f"\nData Preservation Check:")
        expected_keys = ['step1_data', 'step1_counter', 'step2_data', 'step2_counter', 'step_sequence']
        for key in expected_keys:
            value = final_context.shared_state.get(key, 'NOT_FOUND')
            print(f"{key}: {value}")
            
        expected_sequence = ['step1', 'step2']
        actual_sequence = final_context.shared_state.get('step_sequence', [])
        print(f"Expected sequence: {expected_sequence}")
        print(f"Actual sequence: {actual_sequence}")
        print(f"Sequence matches: {actual_sequence == expected_sequence}")
        
    except Exception as e:
        print(f"Error during flow execution: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main function"""
    try:
        await test_context_inheritance()
    except Exception as e:
        print(f"Script failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())