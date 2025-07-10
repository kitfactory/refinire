#!/usr/bin/env python3
"""
Debug Flow validation 
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Flow, FunctionStep

def test_debug():
    """Debug Flow with RefinireAgent"""
    
    print("Creating RefinireAgent...")
    agent = RefinireAgent(
        name="TestAgent",
        generation_instructions="Say hello"
    )
    
    print(f"Agent type: {type(agent)}")
    print(f"Agent has name: {hasattr(agent, 'name')}")
    print(f"Agent has generation_instructions: {hasattr(agent, 'generation_instructions')}")
    
    print("Creating Flow with RefinireAgent...")
    try:
        flow = Flow(steps=[agent])
        print(f"Flow created successfully: {flow}")
    except Exception as e:
        print(f"Flow creation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_debug()