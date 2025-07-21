#!/usr/bin/env python3
"""
Test fixed self introduction system with routing history
修正した自己紹介システムのルーティング履歴テスト
"""

import asyncio
import sys
import os

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent
from refinire.agents.flow.context import Context


async def test_routing_with_history():
    """Test routing agent with conversation history"""
    print("=== Testing Routing with Conversation History ===")
    
    # Create agent with conversation history
    agent = RefinireAgent(
        name="test_collector",
        generation_instructions="Collect user information and respond appropriately.",
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 10}
        ],
        routing_instruction="""
Based on the conversation history, determine if we have all required information:
1. Name - specific name or nickname
2. Age - age information  
3. Personality - character traits
4. Hobbies - interests or hobbies

If all information is complete: "create_introduction"
If information is missing: "additional_input"
If user wants to quit: "_FLOW_END_"
"""
    )
    
    # Simulate conversation
    ctx = Context()
    
    # Step 1
    print("\n--- Step 1: Name only ---")
    result1 = await agent.run_async("My name is Kitada", ctx)
    print(f"Response: {result1.content}")
    print(f"Routing: {result1.routing_result}")
    
    # Step 2  
    print("\n--- Step 2: Add age ---")
    result2 = await agent.run_async("I am 20 years old", ctx)
    print(f"Response: {result2.content}")
    print(f"Routing: {result2.routing_result}")
    
    # Step 3
    print("\n--- Step 3: Add personality ---")
    result3 = await agent.run_async("I am calm and gentle", ctx)
    print(f"Response: {result3.content}")
    print(f"Routing: {result3.routing_result}")
    
    # Step 4
    print("\n--- Step 4: Add hobby ---")
    result4 = await agent.run_async("My hobby is programming", ctx)
    print(f"Response: {result4.content}")
    print(f"Routing: {result4.routing_result}")
    
    # Check final routing decision
    if result4.routing_result:
        next_route = result4.routing_result.get('next_route')
        print(f"\n✅ Final routing decision: {next_route}")
        if next_route == "create_introduction":
            print("✅ All information collected successfully!")
        else:
            print(f"⚠️ Unexpected routing: {next_route}")
    else:
        print("❌ No routing result")


if __name__ == "__main__":
    asyncio.run(test_routing_with_history())