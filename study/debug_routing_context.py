#!/usr/bin/env python3
"""
Debug routing context provider
ルーティングコンテキストプロバイダーのデバッグ
"""

import asyncio
import sys
import os

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent
from refinire.agents.flow.context import Context


async def debug_routing_context():
    """Debug if routing agent can see conversation history"""
    print("=== Debug Routing Context ===")
    
    # Create agent that asks routing agent to list conversation history
    agent = RefinireAgent(
        name="context_debug",
        generation_instructions="Respond briefly to user input.",
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 10}
        ],
        routing_instruction="""
Please list ALL the conversation messages you can see in the conversation history.
Format your response as:
{
  "content": "Brief summary",
  "next_route": "continue", 
  "confidence": 1.0,
  "reasoning": "List all conversation messages: [message 1], [message 2], etc."
}
"""
    )
    
    # Build up conversation
    ctx = Context()
    
    print("\n--- Message 1 ---")
    result1 = await agent.run_async("Hello, my name is Alice", ctx)
    print(f"Response: {result1.content}")
    if result1.routing_result:
        print(f"Routing reasoning: {result1.routing_result['reasoning']}")
    
    print("\n--- Message 2 ---")
    result2 = await agent.run_async("I am 25 years old", ctx)
    print(f"Response: {result2.content}")
    if result2.routing_result:
        print(f"Routing reasoning: {result2.routing_result['reasoning']}")
    
    print("\n--- Message 3 ---")
    result3 = await agent.run_async("I like to read books", ctx)
    print(f"Response: {result3.content}")
    if result3.routing_result:
        print(f"Routing reasoning: {result3.routing_result['reasoning']}")


if __name__ == "__main__":
    asyncio.run(debug_routing_context())