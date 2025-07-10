#!/usr/bin/env python3
"""
Integration tests for tracing independence fixes
トレーシング独立性修正の統合テスト
"""

import asyncio
import sys
import os
import pytest

# Add the src directory to the Python path (relative to tests directory)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire.agents.flow.flow import Flow
from refinire.agents.flow.context import Context
from refinire.agents.flow.step import FunctionStep


def simple_function(user_input, context):
    """Simple test function for Flow steps"""
    context.result = f"Processed: {user_input}"
    return context


class TestTracingIndependence:
    """Test suite for tracing independence fixes"""
    
    @pytest.mark.asyncio
    async def test_flow_without_tracing(self):
        """Test Flow functionality without tracing dependencies"""
        # Create a simple flow
        flow = Flow(
            start="process",
            steps={
                "process": FunctionStep("process", simple_function)
            },
            name="test_flow"
        )
        
        # Verify flow creation
        assert flow is not None
        assert flow.trace_id is not None
        assert flow.context.trace_id is not None
        
        # Test span creation
        span = flow._create_flow_span()
        # Span should be created or None (graceful handling)
        
        # Test flow execution
        result = await flow.run("Hello World")
        assert result is not None
        assert result.result == "Processed: Hello World"

    def test_context_initialization(self):
        """Test Context initialization with various trace_id values"""
        # Test with None trace_id - should auto-generate
        context1 = Context(trace_id=None)
        assert context1.trace_id is not None
        assert isinstance(context1.trace_id, str)
        assert context1.trace_id.startswith("context_")
        
        # Test without trace_id parameter - should auto-generate
        context2 = Context()
        assert context2.trace_id is not None
        assert isinstance(context2.trace_id, str)
        assert context2.trace_id.startswith("context_")
        
        # Test with explicit trace_id - should use provided value
        context3 = Context(trace_id="custom_trace_id")
        assert context3.trace_id == "custom_trace_id"

    def test_context_message_handling(self):
        """Test Context message handling with various input types"""
        context = Context()
        
        # Test normal string message
        context.add_user_message("Hello")
        assert len(context.messages) == 1
        assert context.messages[0].content == "Hello"
        assert context.last_user_input == "Hello"
        
        # Test None message - should be handled gracefully
        context.add_user_message(None)
        assert len(context.messages) == 2
        assert context.messages[1].content == ""
        
        # Test non-string message - should be converted
        context.add_user_message(123)
        assert len(context.messages) == 3
        assert context.messages[2].content == "123"
        
        # Test complex object message - should be converted
        context.add_user_message({"key": "value"})
        assert len(context.messages) == 4
        assert "key" in context.messages[3].content


# Keep the main function for standalone execution
async def main():
    """Run all verification tests (for standalone execution)"""
    print("=== Tracing Independence Fix Verification ===\n")
    
    test_instance = TestTracingIndependence()
    
    results = []
    
    try:
        # Test Flow functionality
        await test_instance.test_flow_without_tracing()
        print("✓ Flow functionality test passed")
        results.append(True)
    except Exception as e:
        print(f"✗ Flow functionality test failed: {e}")
        results.append(False)
    
    try:
        # Test Context initialization
        test_instance.test_context_initialization()
        print("✓ Context initialization test passed")
        results.append(True)
    except Exception as e:
        print(f"✗ Context initialization test failed: {e}")
        results.append(False)
    
    try:
        # Test Context message handling
        test_instance.test_context_message_handling()
        print("✓ Context message handling test passed")
        results.append(True)
    except Exception as e:
        print(f"✗ Context message handling test failed: {e}")
        results.append(False)
    
    # Summary
    print(f"\n=== Test Results ===")
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! The tracing independence fixes are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)