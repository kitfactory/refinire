#!/usr/bin/env python3
"""
Debug message structure in Context
Contextのメッセージ構造をデバッグ
"""

import asyncio
import sys
import os

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent
from refinire.agents.flow.context import Context


async def debug_message_structure():
    """Debug the structure of messages in Context"""
    print("=== Debug Message Structure ===")
    
    # Create simple agent
    agent = RefinireAgent(
        name="debug_agent",
        generation_instructions="Respond briefly to user input.",
        model="gpt-4o-mini"
    )
    
    ctx = Context()
    
    # Add some messages
    print("\n--- Adding messages ---")
    await agent.run_async("Hello", ctx)
    await agent.run_async("My name is Alice", ctx)
    
    # Examine message structure
    print(f"\n--- Message structure ---")
    print(f"Number of messages: {len(ctx.messages)}")
    
    for i, msg in enumerate(ctx.messages):
        print(f"\nMessage {i}:")
        print(f"  Type: {type(msg)}")
        print(f"  Attributes: {dir(msg)}")
        if hasattr(msg, 'role'):
            print(f"  Role: {msg.role}")
        if hasattr(msg, 'content'):
            print(f"  Content type: {type(msg.content)}")
            print(f"  Content: {str(msg.content)[:100]}...")
            
    # Try to extract conversation history
    print(f"\n--- Extracting conversation history ---")
    history_lines = []
    for msg in ctx.messages:
        if hasattr(msg, 'role') and hasattr(msg, 'content'):
            if msg.role == 'user':
                # Check if content is string or complex object
                if isinstance(msg.content, str):
                    history_lines.append(f"User: {msg.content}")
                else:
                    history_lines.append(f"User: {str(msg.content)}")
            elif msg.role == 'assistant':
                # Check if content is string or complex object
                if isinstance(msg.content, str):
                    history_lines.append(f"Assistant: {msg.content}")
                else:
                    history_lines.append(f"Assistant: {str(msg.content)}")
    
    print("Extracted history:")
    for line in history_lines:
        print(f"  {line}")


if __name__ == "__main__":
    asyncio.run(debug_message_structure())