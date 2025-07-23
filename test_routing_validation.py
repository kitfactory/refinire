#!/usr/bin/env python3
"""
Test script for routing parameter validation
ルーティングパラメータ検証のテストスクリプト
"""

from src.refinire.agents.pipeline.llm_pipeline import RefinireAgent
from src.refinire.agents.flow.flow import Flow

def test_routing_instruction_without_destinations():
    """Test that providing routing_instruction without routing_destinations raises ValueError"""
    print("=== Testing routing_instruction without routing_destinations ===")
    
    try:
        # This should raise ValueError
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content",
            routing_instruction="Make routing decisions",
            # routing_destinations is missing
            model="gpt-4o-mini"
        )
        print("❌ ERROR: No exception was raised!")
        return False
    except ValueError as e:
        expected_message = "routing_destinations is required when routing_instruction is provided"
        if expected_message in str(e):
            print(f"✅ SUCCESS: Correct ValueError raised: {e}")
            return True
        else:
            print(f"❌ ERROR: Wrong error message: {e}")
            return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected exception type: {type(e).__name__}: {e}")
        return False

def test_routing_destinations_without_instruction():
    """Test that providing routing_destinations without routing_instruction raises ValueError"""
    print("\n=== Testing routing_destinations without routing_instruction ===")
    
    try:
        # This should raise ValueError
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content",
            # routing_instruction is missing
            routing_destinations=["enhance", "validate", Flow.END],
            model="gpt-4o-mini"
        )
        print("❌ ERROR: No exception was raised!")
        return False
    except ValueError as e:
        expected_message = "routing_instruction is required when routing_destinations is provided"
        if expected_message in str(e):
            print(f"✅ SUCCESS: Correct ValueError raised: {e}")
            return True
        else:
            print(f"❌ ERROR: Wrong error message: {e}")
            return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected exception type: {type(e).__name__}: {e}")
        return False

def test_both_routing_parameters_provided():
    """Test that providing both routing parameters works correctly"""
    print("\n=== Testing both routing parameters provided ===")
    
    try:
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content",
            routing_instruction="Make routing decisions",
            routing_destinations=["enhance", "validate", Flow.END],
            model="gpt-4o-mini"
        )
        print("✅ SUCCESS: Agent created successfully with both parameters")
        print(f"  - Has routing instruction: {agent.routing_instruction is not None}")
        print(f"  - Has routing destinations: {agent.routing_destinations is not None}")
        print(f"  - Routing destinations: {agent.routing_destinations}")
        return True
    except Exception as e:
        print(f"❌ ERROR: Unexpected exception: {type(e).__name__}: {e}")
        return False

def test_neither_routing_parameter_provided():
    """Test that providing neither routing parameter works correctly"""
    print("\n=== Testing neither routing parameter provided ===")
    
    try:
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content",
            # Neither routing_instruction nor routing_destinations provided
            model="gpt-4o-mini"
        )
        print("✅ SUCCESS: Agent created successfully without routing parameters")
        print(f"  - Routing instruction: {agent.routing_instruction}")
        print(f"  - Routing destinations: {agent.routing_destinations}")
        return True
    except Exception as e:
        print(f"❌ ERROR: Unexpected exception: {type(e).__name__}: {e}")
        return False

def test_empty_routing_destinations():
    """Test that providing empty routing_destinations with routing_instruction works"""
    print("\n=== Testing empty routing_destinations list ===")
    
    try:
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content",
            routing_instruction="Make routing decisions",
            routing_destinations=[],  # Empty list
            model="gpt-4o-mini"
        )
        print("✅ SUCCESS: Agent created successfully with empty routing_destinations")
        print(f"  - Routing destinations: {agent.routing_destinations}")
        return True
    except Exception as e:
        print(f"❌ ERROR: Unexpected exception: {type(e).__name__}: {e}")
        return False

def main():
    """Run all validation tests"""
    print("Starting routing parameter validation tests...\n")
    
    results = []
    
    # Test all scenarios
    results.append(test_routing_instruction_without_destinations())
    results.append(test_routing_destinations_without_instruction())
    results.append(test_both_routing_parameters_provided())
    results.append(test_neither_routing_parameter_provided())
    results.append(test_empty_routing_destinations())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All validation tests passed!")
        print("RefinireAgentのルーティングパラメータ検証が正常に動作しています。")
    else:
        print("❌ Some validation tests failed.")
    
    return passed == total

if __name__ == "__main__":
    main()