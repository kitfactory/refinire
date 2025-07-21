#!/usr/bin/env python3
"""
Test script to verify flow termination with routing instructions
ルーティング指示によるフロー終了を検証するテストスクリプト
"""

import sys
import os
import asyncio

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Flow


def test_simple_termination():
    """Test simple flow termination with routing instruction"""
    print("=== Testing Simple Flow Termination ===")
    
    # Agent that should always return _FLOW_END_
    termination_agent = RefinireAgent(
        name="termination_test",
        generation_instructions="""
You are a test agent. Always respond with a simple message and then indicate termination.
        """.strip(),
        model="gpt-4o-mini",
        routing_instruction="""
タスクが完了しました。

フローを終了するため、次のステップを "_FLOW_END_" にしてください。

JSON形式で以下のように返してください:
{
    "content": "タスク完了",
    "next_route": "_FLOW_END_",
    "confidence": 1.0,
    "reasoning": "タスクが完了したため"
}

重要: next_routeは必ず "_FLOW_END_" にしてください。
        """.strip()
    )
    
    # Simple flow with just one step
    flow = Flow(
        name="termination_test_flow",
        start="termination_test",
        steps={
            "termination_test": termination_agent
        }
    )
    
    async def run_test():
        print("\n--- Starting Flow ---")
        result = await flow.run("Test input")
        print(f"\n--- Flow Result ---")
        if result and hasattr(result, 'result'):
            print(f"Result: {result.result}")
        print(f"Flow finished: {flow.finished}")
        print(f"Context finished: {flow.context.is_finished()}")
        if flow.context.routing_result:
            print(f"Final routing result: {flow.context.routing_result}")
        return flow.finished
    
    try:
        return asyncio.run(run_test())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_flow_with_loop_step():
    """Test flow that might loop but should terminate"""
    print("\n=== Testing Flow With Potential Loop ===")
    
    # Agent with explicit termination condition
    loop_agent = RefinireAgent(
        name="loop_test",
        generation_instructions="""
You are a conversation agent. Respond briefly to the user.
        """.strip(),
        model="gpt-4o-mini",
        routing_instruction="""
ユーザーからの入力に応答しました。

常にフローを終了してください。次のステップは "_FLOW_END_" です。

JSON形式:
{
    "content": "応答完了",
    "next_route": "_FLOW_END_",
    "confidence": 1.0,
    "reasoning": "応答が完了したため終了"
}
        """.strip()
    )
    
    # Flow that could potentially loop
    flow = Flow(
        name="loop_test_flow", 
        start="loop_test",
        steps={
            "loop_test": loop_agent
        }
    )
    
    async def run_test():
        print("\n--- Starting Flow ---")
        result = await flow.run("Hello, how are you?")
        print(f"\n--- Flow Result ---")
        if result and hasattr(result, 'result'):
            print(f"Result: {result.result}")
        print(f"Flow finished: {flow.finished}")
        print(f"Context finished: {flow.context.is_finished()}")
        if flow.context.routing_result:
            print(f"Final routing result: {flow.context.routing_result}")
        return flow.finished
    
    try:
        return asyncio.run(run_test())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all termination tests"""
    print("Testing Flow Termination with Routing Instructions")
    print("=" * 50)
    
    test1_result = test_simple_termination()
    test2_result = test_flow_with_loop_step()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"✅ Simple termination test: {'PASSED' if test1_result else 'FAILED'}")
    print(f"✅ Loop prevention test: {'PASSED' if test2_result else 'FAILED'}")
    
    if all([test1_result, test2_result]):
        print("\n🎉 ALL TESTS PASSED!")
        print("Flow termination is working correctly.")
    else:
        print("\n❌ Some tests failed.")
        print("Flow termination needs attention.")


if __name__ == "__main__":
    main()