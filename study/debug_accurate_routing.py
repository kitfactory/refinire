#!/usr/bin/env python3
"""
Debug accurate routing step by step
accurate routingのステップバイステップデバッグ
"""

import sys
import os
import asyncio

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent
from refinire.agents.flow.context import Context


async def debug_accurate_routing_steps():
    """Debug accurate routing step by step"""
    print("=== Debug Accurate Routing Steps ===")
    
    # Create main agent
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
    print(f"Main agent result: '{llm_result.content}'")
    
    # Now manually replicate what _execute_accurate_routing does
    print("\n--- Replicating _execute_accurate_routing manually ---")
    
    try:
        # Step 1: Create routing output model
        print("Step 1: Creating routing output model...")
        routing_output_model = agent._create_routing_output_model()
        print(f"Routing output model: {routing_output_model}")
        
        # Step 2: Build routing prompt  
        print("Step 2: Building routing prompt...")
        routing_prompt = agent._build_routing_prompt(llm_result.content, agent.routing_instruction)
        print(f"Routing prompt: {routing_prompt[:200]}...")
        
        # Step 3: Create routing agent
        print("Step 3: Creating routing agent...")
        routing_agent = RefinireAgent(
            name=f"{agent.name}_router_manual",
            generation_instructions=routing_prompt,
            output_model=routing_output_model,
            model=agent.model_name,
            temperature=0.1,
            namespace=agent.namespace
        )
        print(f"Routing agent created: {routing_agent.name}")
        
        # Step 4: Execute routing agent
        print("Step 4: Executing routing agent...")
        routing_result = await routing_agent.run_async("", ctx)
        print(f"Routing agent result: {routing_result}")
        print(f"Routing result type: {type(routing_result)}")
        
        if routing_result:
            print(f"Routing result content: {routing_result.content}")
            print(f"Routing result success: {routing_result.success}")
            
            # Check what the content contains
            if hasattr(routing_result, 'content') and routing_result.content:
                print(f"Routing content type: {type(routing_result.content)}")
                print(f"Routing content value: {routing_result.content}")
        
    except Exception as e:
        print(f"Manual routing failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_accurate_routing_steps())