#!/usr/bin/env python3
"""
Debug the routing result success attribute
ルーティング結果のsuccess属性をデバッグ
"""

import sys
import os
import asyncio

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent
from refinire.agents.flow.context import Context


async def debug_success_attribute():
    """Debug routing result success attribute"""
    print("=== Debug Routing Result Success ===")
    
    agent = RefinireAgent(
        name="test_routing",
        generation_instructions="Always respond with 'Task completed successfully.'",
        model="gpt-4o-mini",
        routing_mode="accurate_routing",
        routing_instruction="""
You need to determine the next route. Always return "_FLOW_END_" as the next route.
Return a JSON with: content, next_route, confidence, reasoning.
"""
    )
    
    ctx = Context()
    llm_result = await agent._run_standalone("Test input", ctx)
    
    # Manual accurate routing debug
    print("--- Manual Accurate Routing Debug ---")
    
    try:
        routing_output_model = agent._create_routing_output_model()
        routing_prompt = agent._build_routing_prompt(llm_result.content, agent.routing_instruction)
        
        routing_agent = RefinireAgent(
            name=f"{agent.name}_router_debug",
            generation_instructions=routing_prompt,
            output_model=routing_output_model,
            model=agent.model_name,
            temperature=0.1,
            namespace=agent.namespace
        )
        
        routing_result = await routing_agent.run_async("Please analyze the content and determine the next route.", ctx)
        
        print(f"Routing result type: {type(routing_result)}")
        print(f"Routing result: {routing_result}")
        
        if routing_result:
            print(f"Has success attribute: {hasattr(routing_result, 'success')}")
            if hasattr(routing_result, 'success'):
                print(f"Success value: {routing_result.success}")
            
            print(f"Has content attribute: {hasattr(routing_result, 'content')}")
            if hasattr(routing_result, 'content'):
                print(f"Content value: '{routing_result.content}'")
                print(f"Content type: {type(routing_result.content)}")
            
            # Check all available attributes
            print(f"All attributes: {dir(routing_result)}")
            
    except Exception as e:
        print(f"Debug failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_success_attribute())