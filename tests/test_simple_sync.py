#!/usr/bin/env python3
"""
Simple sync test without nest_asyncio
nest_asyncioなしでのシンプル同期テスト
"""

from refinire import RefinireAgent
import asyncio

def test_simple_sync():
    """Test simple sync orchestration"""
    print("Testing simple sync orchestration...")
    
    agent = RefinireAgent(
        name="simple_test_agent",
        generation_instructions="Analyze the provided data and summarize",
        orchestration_mode=True,
        model="gpt-4o-mini"
    )
    
    # Test without existing event loop
    try:
        result = agent.run("Analyze this: sales up 40%")
        print(f"RESULT type: {type(result)}")
        print(f"RESULT value: {result}")
        
        if isinstance(result, dict):
            print("✅ SUCCESS: Got dictionary result")
            print(f"Status: {result.get('status')}")
            print(f"Result: {result.get('result')}")
        else:
            print("❌ FAILED: Got non-dictionary result")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

async def test_direct_async():
    """Test direct async call"""
    print("\nTesting direct async call...")
    
    agent = RefinireAgent(
        name="direct_async_agent",
        generation_instructions="Analyze the provided data and summarize",
        orchestration_mode=True,
        model="gpt-4o-mini"
    )
    
    from refinire.agents.flow.context import Context
    ctx = Context()
    
    try:
        result = await agent.run_async("Analyze this: revenue up 50%", ctx)
        print(f"ASYNC RESULT type: {type(result)}")
        print(f"ASYNC RESULT value: {result}")
        
        if isinstance(result, dict):
            print("✅ SUCCESS: Got dictionary result")
            print(f"Status: {result.get('status')}")
            print(f"Result: {result.get('result')}")
        else:
            print("❌ FAILED: Got non-dictionary result")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

async def main():
    # Test sync first
    test_simple_sync()
    
    # Then test async
    await test_direct_async()

if __name__ == "__main__":
    asyncio.run(main())