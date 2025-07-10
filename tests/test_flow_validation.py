#!/usr/bin/env python3
"""
Test Flow validation and error handling for common mistakes
Flow検証とよくある間違いに対するエラーハンドリングのテスト
"""

import pytest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Flow, FunctionStep

def test_flow_with_refinire_agent_raises_error():
    """Test that Flow raises a clear error when RefinireAgent is passed instead of Step"""
    
    # Create RefinireAgent (common mistake)
    agent = RefinireAgent(
        name="TestAgent",
        generation_instructions="Say hello"
    )
    
    # This should raise a clear error message
    with pytest.raises(ValueError) as exc_info:
        Flow(steps=[agent])
    
    # Check that the error message is helpful
    error_message = str(exc_info.value)
    assert "appears to be a RefinireAgent, not a Step" in error_message
    assert "FunctionStep" in error_message
    assert "Example:" in error_message

def test_flow_with_invalid_step_type_raises_error():
    """Test that Flow raises error for invalid step types"""
    
    # This should raise an error for invalid type
    with pytest.raises(ValueError) as exc_info:
        Flow(steps=["invalid_step"])
    
    error_message = str(exc_info.value)
    assert "must be a Step instance" in error_message
    assert "FunctionStep, ConditionStep" in error_message

def test_flow_with_empty_steps_raises_error():
    """Test that Flow raises error for empty steps"""
    
    with pytest.raises(ValueError) as exc_info:
        Flow(steps=[])
    
    error_message = str(exc_info.value)
    assert "cannot be empty" in error_message

def test_flow_with_valid_steps_works():
    """Test that Flow works correctly with valid Step instances"""
    
    def test_function(user_input, context):
        context.result = f"Processed: {user_input}"
        return context
    
    # This should work without error
    flow = Flow(
        start="test",
        steps={
            "test": FunctionStep("test", test_function)
        }
    )
    
    assert flow is not None
    assert "test" in flow.steps
    assert flow.start == "test"

if __name__ == "__main__":
    # Run the tests manually
    print("Testing Flow validation...")
    
    try:
        # Create RefinireAgent (common mistake)
        agent = RefinireAgent(
            name="TestAgent",
            generation_instructions="Say hello"
        )
        
        # This should raise a clear error message
        try:
            Flow(steps=[agent])
            print("❌ RefinireAgent error handling test failed: No exception raised")
        except ValueError as e:
            error_message = str(e)
            if "appears to be a RefinireAgent, not a proper Step" in error_message:
                print("✅ RefinireAgent error handling test passed")
            else:
                print(f"❌ RefinireAgent error handling test failed: Wrong error message: {error_message}")
        except Exception as e:
            print(f"❌ RefinireAgent error handling test failed: Wrong exception type: {e}")
    except Exception as e:
        print(f"❌ RefinireAgent error handling test failed: {e}")
    
    try:
        test_flow_with_invalid_step_type_raises_error()
        print("✅ Invalid step type error handling test passed")
    except Exception as e:
        print(f"❌ Invalid step type error handling test failed: {e}")
    
    try:
        test_flow_with_empty_steps_raises_error()
        print("✅ Empty steps error handling test passed")
    except Exception as e:
        print(f"❌ Empty steps error handling test failed: {e}")
    
    try:
        test_flow_with_valid_steps_works()
        print("✅ Valid steps test passed")
    except Exception as e:
        print(f"❌ Valid steps test failed: {e}")
    
    print("All Flow validation tests completed!")