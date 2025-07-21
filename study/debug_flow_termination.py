#!/usr/bin/env python3
"""
Debug script for flow termination issues
フロー終了問題のデバッグスクリプト
"""

import sys
import os
import asyncio

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Flow


def debug_flow_termination():
    """Debug flow termination step by step"""
    print("=== Debugging Flow Termination ===")
    
    # Simple termination agent
    agent = RefinireAgent(
        name="debug_agent",
        generation_instructions="Always respond with 'Task completed.'",
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
        """.strip()
    )
    
    # Simple flow
    flow = Flow(
        name="debug_flow",
        start="debug_agent",
        steps={"debug_agent": agent}
    )
    
    async def debug_run():
        print("\n--- Starting Flow Debug ---")
        print(f"Initial flow.finished: {flow.finished}")
        print(f"Initial context.is_finished(): {flow.context.is_finished()}")
        print(f"Initial routing_result: {flow.context.routing_result}")
        
        # Execute single step manually
        step_count = 0
        max_steps = 5  # Limit for debug
        
        while not flow.finished and step_count < max_steps:
            step_count += 1
            print(f"\n--- Step {step_count} ---")
            
            step_name = flow.context.next_label
            print(f"Current step_name: {step_name}")
            print(f"Flow finished before step: {flow.finished}")
            print(f"Context is_finished before step: {flow.context.is_finished()}")
            
            if step_name in (flow.TERMINATE, flow.END, flow.FINISH):
                print(f"✅ Termination constant detected: {step_name}")
                flow.context.finish()
                break
            
            if not step_name or step_name not in flow.steps:
                print(f"❌ Invalid step_name: {step_name}")
                flow.context.finish()
                break
            
            step = flow.steps[step_name]
            print(f"Executing step: {step.name}")
            
            # Execute step
            try:
                await flow._execute_step(step, "Test input")
                print(f"Step executed successfully")
                
                # Check agent routing instruction
                print(f"Agent has routing_instruction: {hasattr(step, 'routing_instruction') and step.routing_instruction is not None}")
                if hasattr(step, 'routing_instruction'):
                    print(f"Routing instruction length: {len(step.routing_instruction) if step.routing_instruction else 0}")
                
                # Check state after execution
                next_step_name = flow.context.next_label
                print(f"Next step after execution: {next_step_name}")
                print(f"Routing result: {flow.context.routing_result}")
                print(f"Flow finished after step: {flow.finished}")
                print(f"Context is_finished after step: {flow.context.is_finished()}")
                
                # Check for termination constants after step execution  
                if next_step_name in (flow.TERMINATE, flow.END, flow.FINISH):
                    print(f"✅ Termination constant detected after execution: {next_step_name}")
                    flow.context.finish()
                    break
                else:
                    print(f"⚠️ No termination constant detected, next_step: {next_step_name}")
                
            except Exception as e:
                print(f"❌ Error executing step: {e}")
                break
        
        print(f"\n--- Final State ---")
        print(f"Step count: {step_count}")
        print(f"Flow finished: {flow.finished}")
        print(f"Context is_finished: {flow.context.is_finished()}")
        print(f"Final routing_result: {flow.context.routing_result}")
        
        if step_count >= max_steps:
            print("❌ Reached maximum steps - likely infinite loop")
        else:
            print("✅ Flow terminated normally")
    
    try:
        asyncio.run(debug_run())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_flow_termination()