#!/usr/bin/env python3
"""
Debug script to investigate when goto() changes are lost.
goto()の変更がいつ失われるかを調査するデバッグスクリプト。

Focuses on the exact timing of next_label changes.
next_label変更の正確なタイミングに焦点を当てる。
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


# Cannot monkey patch Pydantic models, so we'll use direct calls with logging


async def step1_with_tracking(user_input: str, context: Context) -> Context:
    """Step 1 with detailed next_label tracking"""
    
    print(f"📍 STEP1 START: next_label = {context.next_label}")
    
    # Add some data
    # データを追加
    context.shared_state['step1_done'] = True
    context.add_system_message("Step 1 executed")
    
    print(f"📍 STEP1 BEFORE GOTO: next_label = {context.next_label}")
    
    # Set next step with detailed logging
    # 詳細ログ付きで次ステップを設定
    print(f"🔄 CALLING context.goto('step2') (was: {context.next_label})")
    context.goto("step2")
    print(f"🔄 GOTO COMPLETED: next_label = {context.next_label}")
    
    print(f"📍 STEP1 AFTER GOTO: next_label = {context.next_label}")
    print(f"📍 STEP1 RETURNING CONTEXT ID: {id(context)}")
    
    return context


async def step2_with_tracking(user_input: str, context: Context) -> Context:
    """Step 2 with tracking"""
    
    print(f"📍 STEP2 START: next_label = {context.next_label}")
    print(f"📍 STEP2 GOT CONTEXT ID: {id(context)}")
    
    # Check data from step1
    # step1からのデータをチェック
    step1_done = context.shared_state.get('step1_done', False)
    print(f"📍 STEP2 SEES step1_done: {step1_done}")
    
    # Add our data
    # データを追加
    context.shared_state['step2_done'] = True
    context.add_system_message("Step 2 executed")
    
    print(f"📍 STEP2 BEFORE FINISH: next_label = {context.next_label}")
    
    # Finish flow with detailed logging
    # 詳細ログ付きでフローを終了
    print(f"🏁 CALLING context.finish() (was: {context.next_label})")
    context.finish()
    print(f"🏁 FINISH COMPLETED: next_label = {context.next_label}")
    
    print(f"📍 STEP2 AFTER FINISH: next_label = {context.next_label}")
    print(f"📍 STEP2 RETURNING CONTEXT ID: {id(context)}")
    
    return context


async def debug_goto_timing():
    """Debug goto timing issues"""
    
    print("Goto Timing Debug")
    print("=" * 50)
    
    # Create Flow
    # Flowを作成
    flow = Flow(
        start="step1", 
        steps={
            "step1": FunctionStep("step1", step1_with_tracking),
            "step2": FunctionStep("step2", step2_with_tracking)
        },
        name="GotoTimingTest"
    )
    
    # No tracker needed, using direct logging in functions
    # トラッカーは不要、関数内で直接ログ記録
    
    print(f"🚀 FLOW START: context_id = {id(flow.context)}, next_label = {flow.context.next_label}")
    
    try:
        final_context = await flow.run("Test input")
        
        print(f"🏁 FLOW END: context_id = {id(final_context)}, next_label = {final_context.next_label}")
        print(f"🏁 FINAL SHARED STATE: {final_context.shared_state}")
        
        # Check what actually got executed
        # 実際に実行されたものをチェック
        step1_done = final_context.shared_state.get('step1_done', False)
        step2_done = final_context.shared_state.get('step2_done', False)
        
        print(f"\n📊 EXECUTION SUMMARY:")
        print(f"   Step1 executed: {step1_done}")
        print(f"   Step2 executed: {step2_done}")
        print(f"   Context same object: {id(flow.context) == id(final_context)}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_goto_timing())