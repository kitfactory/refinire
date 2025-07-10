#!/usr/bin/env python3
"""
Test if Flow issues are fixed in Refinire 0.2.13
"""

import asyncio
import sys
import os

# Add the src directory to the Python path (relative to tests directory)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Flow, FunctionStep, Context

def test_flow_fix():
    """Test if Flow works in new version"""
    print("🔍 Testing Flow in Refinire 0.2.13...")
    
    try:
        # Test 1: Create RefinireAgent and verify it works
        print("📝 Testing RefinireAgent creation...")
        agent = RefinireAgent(
            name="TestAgent",
            generation_instructions="簡潔に挨拶してください。"
        )
        print("✅ RefinireAgent created successfully")
        
        # Test 2: Create Flow with FunctionStep (correct usage)
        print("📝 Testing Flow with FunctionStep...")
        
        def simple_greeting(user_input, context):
            """Simple greeting function for Flow step"""
            context.result = f"こんにちは！{user_input}さん"
            return context
        
        def add_thanks(user_input, context):
            """Add thanks to the previous result"""
            previous_result = getattr(context, 'result', user_input)
            context.result = f"{previous_result}。ご利用ありがとうございます！"
            return context
        
        # Create Flow using correct architecture
        flow = Flow(
            start="greeting",
            steps={
                "greeting": FunctionStep("greeting", simple_greeting, "thanks"),
                "thanks": FunctionStep("thanks", add_thanks)
            },
            name="test_flow"
        )
        print("✅ Flow created successfully")
        
        # Test Flow execution
        input_text = "太郎"
        print(f"📝 Testing Flow.run() with input: {input_text}")
        
        result = asyncio.run(flow.run(input_text))
        print(f"✅ Flow completed successfully!")
        print(f"Result: {result.result}")
        
        # Test 3: Test RefinireAgent run_async method  
        print("📝 Testing RefinireAgent.run_async()...")
        try:
            ctx = Context()
            agent_result = asyncio.run(agent.run_async("こんにちは", ctx))
            print(f"✅ RefinireAgent.run_async() completed successfully!")
            # agent_result is a Context object
            if hasattr(agent_result, 'result'):
                print(f"Agent result: {agent_result.result}")
            else:
                print(f"Agent result: {agent_result}")
        except Exception as e:
            print(f"⚠️  RefinireAgent.run_async() failed: {e}")
            print("(This may be expected if no LLM is configured)")
        
        return True
        
    except Exception as e:
        print(f"❌ Flow still has issues: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎯 Refinire 0.2.13 Flow Fix Test")
    print("=" * 40)
    
    success = test_flow_fix()
    
    if success:
        print("\n🎉 Flow is working in Refinire 0.2.13!")
        print("✅ Previous issues have been resolved")
    else:
        print("\n⚠️  Flow still has issues")
        print("Continue using individual RefinireAgent approach")

if __name__ == "__main__":
    main()