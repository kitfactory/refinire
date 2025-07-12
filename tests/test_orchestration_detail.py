#!/usr/bin/env python3
"""
Detailed orchestration mode debugging
オーケストレーション・モードの詳細デバッグ
"""

from refinire import RefinireAgent
from pydantic import BaseModel, Field
import json

class TestOutput(BaseModel):
    message: str = Field(description="Test message")
    score: float = Field(description="Test score")

def test_basic_orchestration_detailed():
    """Test basic orchestration mode with detailed logging"""
    print("Testing basic orchestration mode with detailed logging...")
    
    agent = RefinireAgent(
        name="test_agent",
        generation_instructions="Provide a simple analysis of the input data",
        orchestration_mode=True,
        model="gpt-4o-mini"
    )
    
    # Hook into the agent's _parse_orchestration_result method to see what's happening
    original_parse = agent._parse_orchestration_result
    
    def debug_parse(content):
        print(f"DEBUG: Parsing content type: {type(content)}")
        print(f"DEBUG: Content value: {content}")
        try:
            result = original_parse(content)
            print(f"DEBUG: Parse successful: {result}")
            return result
        except Exception as e:
            print(f"DEBUG: Parse failed: {e}")
            raise
    
    agent._parse_orchestration_result = debug_parse
    
    try:
        result = agent.run("Analyze this test data: sales are up 15%")
        print(f"Final result type: {type(result)}")
        print(f"Final result: {result}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_structured_orchestration_detailed():
    """Test structured orchestration with detailed logging"""
    print("\nTesting structured orchestration with detailed logging...")
    
    agent = RefinireAgent(
        name="structured_test_agent",
        generation_instructions="Generate a test message with the specified score",
        orchestration_mode=True,
        output_model=TestOutput,
        model="gpt-4o-mini"
    )
    
    # Hook into the agent's methods
    original_parse = agent._parse_orchestration_result
    original_structured = agent._parse_structured_output
    
    def debug_parse(content):
        print(f"DEBUG ORCH: Parsing content type: {type(content)}")
        print(f"DEBUG ORCH: Content value: {content}")
        try:
            result = original_parse(content)
            print(f"DEBUG ORCH: Parse successful: {result}")
            return result
        except Exception as e:
            print(f"DEBUG ORCH: Parse failed: {e}")
            raise
    
    def debug_structured(content):
        print(f"DEBUG STRUCT: Parsing content type: {type(content)}")
        print(f"DEBUG STRUCT: Content value: {content}")
        try:
            result = original_structured(content)
            print(f"DEBUG STRUCT: Parse successful: {result}")
            return result
        except Exception as e:
            print(f"DEBUG STRUCT: Parse failed: {e}")
            raise
    
    agent._parse_orchestration_result = debug_parse
    agent._parse_structured_output = debug_structured
    
    try:
        result = agent.run("Generate a test message with score 0.8")
        print(f"Final structured result type: {type(result)}")
        print(f"Final structured result: {result}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_orchestration_detailed()
    test_structured_orchestration_detailed()