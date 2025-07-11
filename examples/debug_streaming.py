#!/usr/bin/env python3
"""
Debug Streaming Implementation
ストリーミング実装のデバッグ
"""

import asyncio
import sys
import os
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent
from agents import Runner

async def debug_streaming_events():
    """Debug what stream events are actually received"""
    print("🔧 Debugging Streaming Events")
    print("=" * 40)
    
    agent = RefinireAgent(
        name="DebugAgent",
        generation_instructions="Say hello briefly",
        model="gpt-4o-mini"
    )
    
    try:
        # Build prompt using agent's internal method
        full_prompt = agent._build_prompt("Hello", include_instructions=False)
        
        # Set agent instructions
        original_instructions = agent._sdk_agent.instructions
        agent._sdk_agent.instructions = agent.generation_instructions
        
        print("📡 Starting stream...")
        stream_result = Runner.run_streamed(agent._sdk_agent, full_prompt)
        
        event_count = 0
        async for stream_event in stream_result.stream_events():
            event_count += 1
            print(f"\n🔍 Event #{event_count}:")
            print(f"   Type: {getattr(stream_event, 'type', 'No type attribute')}")
            print(f"   Event: {type(stream_event)}")
            print(f"   Attributes: {dir(stream_event)}")
            
            if hasattr(stream_event, 'data'):
                print(f"   Data type: {type(stream_event.data)}")
                print(f"   Data attributes: {dir(stream_event.data)}")
                
                if hasattr(stream_event.data, 'chunk'):
                    chunk = stream_event.data.chunk
                    print(f"   Chunk type: {type(chunk)}")
                    print(f"   Chunk attributes: {dir(chunk)}")
                    print(f"   Chunk content: {chunk}")
            
            # Check for various content sources
            content = None
            if hasattr(stream_event, 'content'):
                content = stream_event.content
                print(f"   Direct content: {content}")
            
            if content:
                print(f"✅ Found content: {content}")
        
        print(f"\n📊 Total events received: {event_count}")
        
        # Restore instructions
        agent._sdk_agent.instructions = original_instructions
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

async def debug_non_streaming():
    """Compare with non-streaming execution"""
    print("\n🔧 Debugging Non-Streaming for Comparison")
    print("=" * 40)
    
    agent = RefinireAgent(
        name="DebugAgent",
        generation_instructions="Say hello briefly",
        model="gpt-4o-mini"
    )
    
    try:
        # Use regular run_async
        from refinire import Context
        ctx = Context()
        result = await agent.run_async("Hello", ctx)
        
        print(f"✅ Non-streaming result: {result.result}")
        print(f"   Result type: {type(result.result)}")
        
    except Exception as e:
        print(f"❌ Non-streaming debug failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await debug_non_streaming()
    await debug_streaming_events()

if __name__ == "__main__":
    asyncio.run(main())