#!/usr/bin/env python3
"""
Debug Context methods for conversation history
会話履歴用Contextメソッドのデバッグ
"""

import asyncio
import sys
import os

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent
from refinire.agents.flow.context import Context


async def debug_context_methods():
    """Debug Context methods for extracting conversation"""
    print("=== Debug Context Methods ===")
    
    agent = RefinireAgent(
        name="debug_agent",
        generation_instructions="Respond briefly.",
        model="gpt-4o-mini"
    )
    
    ctx = Context()
    
    # Build conversation
    await agent.run_async("Hello, my name is Alice", ctx)
    await agent.run_async("I am 25 years old", ctx)
    
    print("\n--- Available Context methods ---")
    context_methods = [method for method in dir(ctx) if not method.startswith('_') and callable(getattr(ctx, method))]
    for method in context_methods:
        print(f"  {method}")
    
    print("\n--- Trying get_conversation_text ---")
    if hasattr(ctx, 'get_conversation_text'):
        try:
            conversation = ctx.get_conversation_text()
            print(f"get_conversation_text(): {conversation}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n--- Trying get_last_messages ---")
    if hasattr(ctx, 'get_last_messages'):
        try:
            last_messages = ctx.get_last_messages(5)
            print(f"get_last_messages(5): {last_messages}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n--- Checking last_user_input ---")
    if hasattr(ctx, 'last_user_input'):
        print(f"last_user_input: {ctx.last_user_input}")
    
    print("\n--- Checking messages content ---")
    for i, msg in enumerate(ctx.messages):
        print(f"Message {i}: role={msg.role}")
        # Try to extract actual text content
        if hasattr(msg, 'content'):
            content_str = str(msg.content)
            if 'LLMResult' in content_str and 'content=' in content_str:
                # Try to extract the actual text from LLMResult
                start = content_str.find("content='") + 9
                if start > 8:
                    end = content_str.find("'", start)
                    if end > start:
                        actual_content = content_str[start:end]
                        print(f"  Extracted content: {actual_content[:50]}...")


if __name__ == "__main__":
    asyncio.run(debug_context_methods())