#!/usr/bin/env python3
"""
Debug script for RefinireAgent routing
RefinireAgentルーティングのデバッグスクリプト
"""

import sys
import os
import asyncio

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent
from refinire.agents.flow.context import Context


async def debug_refinire_agent():
    """Debug RefinireAgent routing directly"""
    print("=== Debugging RefinireAgent Routing ===")
    
    # Agent with routing instruction
    agent = RefinireAgent(
        name="test_agent",
        generation_instructions="Always respond with 'Task completed.'",
        model="gpt-4o-mini",
        routing_instruction="""
Always return "_FLOW_END_" as the next route. Return this exact JSON:
{"content": "Done", "next_route": "_FLOW_END_", "confidence": 1.0, "reasoning": "Task complete"}
        """.strip()
    )
    
    print(f"Agent name: {agent.name}")
    print(f"Has routing_instruction: {agent.routing_instruction is not None}")
    print(f"Routing instruction length: {len(agent.routing_instruction) if agent.routing_instruction else 0}")
    print(f"Generation instructions: {agent.generation_instructions[:50]}...")
    print(f"Routing instruction preview: {agent.routing_instruction[:100] if agent.routing_instruction else 'None'}...")
    
    # Create context
    ctx = Context()
    print(f"\nInitial context routing_result: {ctx.routing_result}")
    
    # Run standalone first to check llm_result
    print("\n--- Running _run_standalone ---")
    llm_result = await agent._run_standalone("Test input", ctx)
    
    print(f"\nLLM Result:")
    print(f"LLM Result type: {type(llm_result)}")
    print(f"LLM Result success: {llm_result.success}")
    print(f"LLM Result content: {llm_result.content}")
    
    # Check routing conditions
    print(f"\nRouting Conditions Check:")
    print(f"agent.routing_instruction: {agent.routing_instruction is not None}")
    print(f"llm_result.success: {llm_result.success}")
    print(f"llm_result.content: {bool(llm_result.content)}")
    print(f"All conditions met: {agent.routing_instruction and llm_result.success and llm_result.content}")
    
    # Now run agent completely
    print("\n--- Running Agent Completely ---")
    result = await agent.run_async("Test input", ctx)
    
    print(f"\nAgent execution result:")
    print(f"Result type: {type(result)}")
    if hasattr(result, 'content'):
        print(f"Result content: {result.content}")
    if hasattr(result, 'success'):
        print(f"Result success: {result.success}")
    
    print(f"\nContext after execution:")
    print(f"Routing result: {ctx.routing_result}")
    print(f"Next label: {ctx.next_label}")
    print(f"Is finished: {ctx.is_finished()}")
    
    # Check if routing was executed
    if ctx.routing_result and 'next_route' in ctx.routing_result:
        next_route = ctx.routing_result['next_route']
        print(f"\n✅ Routing executed successfully!")
        print(f"Next route: {next_route}")
        if next_route == "_FLOW_END_":
            print(f"✅ Termination constant detected!")
        else:
            print(f"⚠️ Unexpected next_route: {next_route}")
    else:
        print(f"\n❌ Routing was not executed!")
        print("This indicates a problem with routing instruction execution.")


if __name__ == "__main__":
    asyncio.run(debug_refinire_agent())