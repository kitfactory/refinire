#!/usr/bin/env python3
"""
Debug orchestration mode issues
オーケストレーション・モードの問題をデバッグ
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
    
    result = agent.run("Analyze this simple test data")
    
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    
    if isinstance(result, dict):
        print("✅ Orchestration mode working - returned dict")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Result: {result.get('result', 'none')}")
    else:
        print("❌ Orchestration mode not working - returned Context")
        print(f"Context result: {result.result}")

def test_structured_orchestration():
    """Test orchestration with structured output"""
    print("\nTesting structured orchestration mode...")
    
    agent = RefinireAgent(
        name="structured_test_agent",
        generation_instructions="Generate structured test output",
        orchestration_mode=True,
        output_model=TestOutput,
        model="gpt-4o-mini"
    )
    
    result = agent.run("Generate a test message with score 0.8")
    
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    
    if isinstance(result, dict):
        print("✅ Structured orchestration working - returned dict")
        print(f"Status: {result.get('status', 'unknown')}")
        result_data = result.get('result')
        print(f"Result data type: {type(result_data)}")
        print(f"Result data: {result_data}")
        
        if isinstance(result_data, TestOutput):
            print("✅ Output model parsing worked")
            print(f"Message: {result_data.message}")
            print(f"Score: {result_data.score}")
        else:
            print("❌ Output model parsing failed")
    else:
        print("❌ Structured orchestration not working - returned Context")

if __name__ == "__main__":
    test_basic_orchestration()
    test_structured_orchestration()