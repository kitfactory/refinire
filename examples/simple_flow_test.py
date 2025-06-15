#!/usr/bin/env python3
"""
Simple Flow Test
シンプルなFlowテスト

Test basic Flow functionality to debug execution issues.
基本的なFlow機能をテストして実行問題をデバッグします。
"""

import asyncio
from refinire import Flow, FunctionStep, DebugStep


async def main():
    """Test basic Flow execution"""
    print("Simple Flow Test")
    print("=" * 40)
    
    # Create a simple function that returns context
    def simple_function(user_input, ctx):
        print(f"Executing simple_function with input: {user_input}")
        ctx.add_assistant_message("Function executed successfully")
        # Finish the flow since this is the last step
        ctx.finish()
        print(f"Context after function: finished={ctx.is_finished()}, next_label={ctx.next_label}")
        return ctx
    
    # Create a simple flow with one step
    step1 = FunctionStep("step1", simple_function)
    
    flow = Flow(
        name="simple_test",
        start="step1",
        steps={"step1": step1}
    )
    
    print(f"Flow created: {flow.flow_name}")
    print(f"Flow ID: {flow.flow_id}")
    print(f"Start step: {flow.start}")
    print(f"Steps: {list(flow.steps.keys())}")
    
    try:
        print("\nRunning flow...")
        result = await flow.run("test input")
        print(f"Flow completed successfully!")
        print(f"Final context finished: {result.is_finished()}")
        print(f"Messages: {len(result.messages)}")
        for msg in result.messages:
            print(f"  {msg.role}: {msg.content}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 
