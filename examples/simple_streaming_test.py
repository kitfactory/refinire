#!/usr/bin/env python3
"""
Simple RefinireAgent Streaming Test
シンプルなRefinireAgentストリーミングテスト
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent

async def test_streaming():
    """Test basic streaming functionality"""
    print("🧪 Testing RefinireAgent Streaming...")
    
    try:
        agent = RefinireAgent(
            name="StreamingTestAgent",
            generation_instructions="Respond briefly with 'Hello from streaming agent'",
            model="gpt-4o-mini"
        )
        
        print("User: Hello")
        print("Assistant: ", end="", flush=True)
        
        chunks = []
        async for chunk in agent.run_streamed("Hello"):
            print(chunk, end="", flush=True)
            chunks.append(chunk)
        
        print(f"\n\n✅ Streaming successful!")
        print(f"📊 Received {len(chunks)} chunks")
        print(f"📏 Total content: {''.join(chunks)}")
        
    except Exception as e:
        print(f"❌ Streaming failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_streaming())