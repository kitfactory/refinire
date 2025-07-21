#!/usr/bin/env python3
"""
Debug routing with different modes
異なるモードでのルーティングデバッグ
"""

import sys
import os
import asyncio

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent
from refinire.agents.flow.context import Context


async def test_routing_mode(mode: str):
    """Test routing with specific mode"""
    print(f"\n=== Testing routing_mode: {mode} ===")
    
    agent = RefinireAgent(
        name="test_routing",
        generation_instructions="Always respond with 'Task completed successfully.'",
        model="gpt-4o-mini",
        routing_mode=mode,
        routing_instruction="""
You need to determine the next route. Always return "_FLOW_END_" as the next route.
Return a JSON with: content, next_route, confidence, reasoning.
"""
    )
    
    print(f"Agent routing_mode: {agent.routing_mode}")
    
    ctx = Context()
    
    # Run standalone first
    llm_result = await agent._run_standalone("Test input", ctx)
    print(f"LLM success: {llm_result.success}, content: '{llm_result.content}'")
    
    # Test routing execution
    try:
        routing_result = await agent._execute_routing(llm_result.content, ctx)
        print(f"Routing result: {routing_result}")
        print(f"Routing type: {type(routing_result)}")
        
        if routing_result:
            if hasattr(routing_result, 'next_route'):
                print(f"  next_route: {routing_result.next_route}")
            if hasattr(routing_result, 'confidence'):
                print(f"  confidence: {routing_result.confidence}")
            if hasattr(routing_result, 'reasoning'):
                print(f"  reasoning: {routing_result.reasoning}")
        
    except Exception as e:
        print(f"Routing execution failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test full execution
    try:
        result_ctx = await agent.run_async("Test input", Context())
        print(f"Full execution routing_result: {result_ctx.routing_result}")
    except Exception as e:
        print(f"Full execution failed: {e}")


async def main():
    """Test both routing modes"""
    await test_routing_mode("accurate_routing")
    await test_routing_mode("fast_routing")


if __name__ == "__main__":
    asyncio.run(main())