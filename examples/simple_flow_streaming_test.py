#!/usr/bin/env python3
"""
Simple Flow Streaming Test
シンプルなFlowストリーミングテスト
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Flow, FunctionStep

async def test_flow_streaming():
    """Test basic Flow streaming functionality"""
    print("🧪 Testing Flow Streaming...")
    
    try:
        # Create a simple function step
        def greet(user_input, context):
            context.result = f"Hello {user_input}!"
            return context
        
        # Create an agent step
        agent = RefinireAgent(
            name="TestAgent",
            generation_instructions="Respond briefly and helpfully",
            model="gpt-4o-mini"
        )
        
        # Create Flow with mixed steps
        flow = Flow(
            start="greet",
            steps={
                "greet": FunctionStep("greet", greet, "agent"),
                "agent": agent
            },
            name="test_flow"
        )
        
        print("User: World")
        print("Flow: ", end="", flush=True)
        
        chunks = []
        async for chunk in flow.run_streamed("World"):
            print(chunk, end="", flush=True)
            chunks.append(chunk)
        
        print(f"\n\n✅ Flow streaming successful!")
        print(f"📊 Received {len(chunks)} chunks")
        
    except Exception as e:
        print(f"❌ Flow streaming failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_flow_streaming())