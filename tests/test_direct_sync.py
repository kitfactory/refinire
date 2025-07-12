#!/usr/bin/env python3
"""
Test orchestration directly without async context
非同期コンテキストなしで直接オーケストレーションをテスト
"""

from refinire import RefinireAgent
from pydantic import BaseModel, Field

class TestOutput(BaseModel):
    message: str = Field(description="Test message")
    score: float = Field(description="Test score")

def test_basic_orchestration():
    """Test basic orchestration mode"""
    print("Testing basic orchestration mode...")
    
    agent = RefinireAgent(
        name="test_agent",
        generation_instructions="Provide a simple analysis",
        orchestration_mode=True,
        model="gpt-4o-mini"
    )
    
    result = agent.run("Analyze this test data: sales increased by 30%")
    
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    
    if isinstance(result, dict):
        print("✅ Orchestration mode working - returned dict")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Result: {result.get('result', 'none')}")
        if result.get('status') == 'completed':
            print("✅ SUCCESS: Basic orchestration working")
            return True
        else:
            print("❌ FAILED: Status not completed")
            return False
    else:
        print("❌ Orchestration mode not working - returned Context")
        return False

def test_structured_orchestration():
    """Test orchestration with structured output"""
    print("\nTesting structured orchestration mode...")
    
    agent = RefinireAgent(
        name="structured_test_agent",
        generation_instructions="Generate structured test output with the requested message and score",
        orchestration_mode=True,
        output_model=TestOutput,
        model="gpt-4o-mini"
    )
    
    result = agent.run("Generate a test message 'Hello World' with score 0.8")
    
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    
    if isinstance(result, dict):
        print("✅ Structured orchestration working - returned dict")
        print(f"Status: {result.get('status', 'unknown')}")
        result_data = result.get('result')
        print(f"Result data type: {type(result_data)}")
        print(f"Result data: {result_data}")
        
        if result.get('status') == 'completed' and isinstance(result_data, TestOutput):
            print("✅ SUCCESS: Structured orchestration working")
            print(f"Message: {result_data.message}")
            print(f"Score: {result_data.score}")
            return True
        else:
            print("❌ FAILED: Status not completed or wrong result type")
            return False
    else:
        print("❌ Structured orchestration not working - returned Context")
        return False

if __name__ == "__main__":
    basic_success = test_basic_orchestration()
    structured_success = test_structured_orchestration()
    
    print(f"\n{'='*50}")
    print(f"SUMMARY:")
    print(f"Basic orchestration: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"Structured orchestration: {'✅ PASS' if structured_success else '❌ FAIL'}")
    print(f"{'='*50}")