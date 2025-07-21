#!/usr/bin/env python3
"""
Detailed routing debug script
詳細なルーティングデバッグスクリプト
"""

import sys
import os
import asyncio

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent
from refinire.agents.flow.context import Context


async def debug_routing_detailed():
    """Debug RefinireAgent routing in detail"""
    print("=== Detailed Routing Debug ===")
    
    # Agent with simple routing instruction
    agent = RefinireAgent(
        name="test_routing",
        generation_instructions="Always respond with 'Task completed successfully.'",
        model="gpt-4o-mini",
        routing_instruction="""
You need to determine the next route. Always return "_FLOW_END_" as the next route.
Return a JSON with: content, next_route, confidence, reasoning.
"""
    )
    
    print(f"Agent routing_mode: {agent.routing_mode}")
    print(f"Agent routing_instruction exists: {agent.routing_instruction is not None}")
    
    # Create context
    ctx = Context()
    
    # Test 1: Check if conditions are met for routing
    print("\n--- Test 1: Run standalone first ---")
    llm_result = await agent._run_standalone("Test input", ctx)
    
    print(f"LLM Result success: {llm_result.success}")
    print(f"LLM Result content: '{llm_result.content}'")
    print(f"Content length: {len(llm_result.content) if llm_result.content else 0}")
    
    # Test 2: Manual routing execution
    print(f"\n--- Test 2: Manual routing execution ---")
    print(f"Routing condition check:")
    print(f"  agent.routing_instruction: {agent.routing_instruction is not None}")
    print(f"  llm_result.success: {llm_result.success}")  
    print(f"  llm_result.content: {llm_result.content is not None and len(llm_result.content) > 0}")
    
    routing_should_execute = (agent.routing_instruction and 
                            llm_result.success and 
                            llm_result.content)
    print(f"  --> Should execute routing: {routing_should_execute}")
    
    if routing_should_execute:
        print(f"\n--- Test 3: Direct routing call ---")
        try:
            routing_result = await agent._execute_routing(llm_result.content, ctx)
            print(f"Routing result: {routing_result}")
            if routing_result:
                print(f"Routing success!")
                print(f"  next_route: {routing_result.next_route}")
                print(f"  confidence: {routing_result.confidence}")
                print(f"  reasoning: {routing_result.reasoning}")
            else:
                print(f"Routing returned None")
        except Exception as e:
            print(f"Routing execution failed with exception: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\nSkipping routing - conditions not met")
    
    # Test 3: Full agent execution
    print(f"\n--- Test 4: Full agent execution ---")
    try:
        result_ctx = await agent.run_async("Test input", Context())
        print(f"Final result context:")
        print(f"  result: {result_ctx.result}")
        print(f"  routing_result: {result_ctx.routing_result}")
        print(f"  next_label: {result_ctx.next_label}")
        print(f"  is_finished: {result_ctx.is_finished()}")
    except Exception as e:
        print(f"Full execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_routing_detailed())