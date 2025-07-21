#!/usr/bin/env python3
"""
Test clearer routing instructions
より明確なルーティング指示のテスト
"""

import asyncio
import sys
import os

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent
from refinire.agents.flow.context import Context


async def test_clearer_routing():
    """Test routing agent with clearer instructions"""
    print("=== Testing Clearer Routing Instructions ===")
    
    # Create agent with clearer routing instructions
    agent = RefinireAgent(
        name="test_clearer",
        generation_instructions="Collect user information and respond appropriately.",
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 10}
        ],
        routing_instruction="""
CRITICAL: Your job is ONLY to analyze the conversation history for completeness, NOT to consider what questions are being asked.

Check if these 4 pieces of information have been provided by the user:
1. Name - specific name or nickname
2. Age - age information  
3. Personality - character traits
4. Hobbies - interests or hobbies

IGNORE what questions are being asked to the user.
IGNORE if more details could be gathered.
ONLY check if the 4 basic pieces of information above exist.

If ALL 4 pieces exist: "create_introduction"
If ANY piece is missing: "additional_input"  
If user wants to quit: "_FLOW_END_"

Decision rule: Count the 4 pieces. If count = 4, return "create_introduction". Otherwise return "additional_input".
"""
    )
    
    # Build up conversation
    ctx = Context()
    
    print("\n--- Building conversation ---")
    await agent.run_async("My name is Alice", ctx)
    await agent.run_async("I am 25 years old", ctx) 
    await agent.run_async("I am friendly and outgoing", ctx)
    result = await agent.run_async("My hobby is reading", ctx)
    
    print(f"Final response: {result.content}")
    print(f"Final routing: {result.routing_result}")
    
    if result.routing_result:
        next_route = result.routing_result.get('next_route')
        reasoning = result.routing_result.get('reasoning')
        print(f"\n✅ Final decision: {next_route}")
        print(f"✅ Reasoning: {reasoning}")
        
        if next_route == "create_introduction":
            print("🎉 SUCCESS: All information recognized as complete!")
        else:
            print(f"⚠️ Still not working: {next_route}")


if __name__ == "__main__":
    asyncio.run(test_clearer_routing())