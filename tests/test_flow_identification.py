#!/usr/bin/env python3
"""
Tests for Flow identification and tracing features
Flow識別とトレース機能のテスト
"""

import pytest
import asyncio
from datetime import datetime
from refinire import (
    Flow, Context, FunctionStep, DebugStep, UserInputStep,
    create_simple_flow, create_conditional_flow
)


class TestFlowIdentification:
    """Test Flow identification features"""
    
    def test_flow_name_property(self):
        """Test flow name property"""
        flow = Flow(name="test_flow", steps=[FunctionStep("step1", lambda u, c: c)])
        assert flow.flow_name == "test_flow"
        assert flow.name == "test_flow"
    
    def test_flow_id_property(self):
        """Test flow ID property"""
        flow = Flow(name="test_flow", steps=[FunctionStep("step1", lambda u, c: c)])
        assert flow.flow_id == flow.trace_id
        assert flow.flow_id.startswith("test_flow_")
    
    def test_automatic_trace_id_generation(self):
        """Test automatic trace ID generation"""
        import time
        
        flow = Flow(name="my_workflow", steps=[FunctionStep("step1", lambda u, c: c)])
        
        # Should contain flow name and timestamp
        assert "my_workflow" in flow.trace_id
        assert len(flow.trace_id) > len("my_workflow")
        
        # Should be unique for different flows
        time.sleep(0.001)  # Small delay to ensure different timestamps
        flow2 = Flow(name="my_workflow", steps=[FunctionStep("step1", lambda u, c: c)])
        assert flow.trace_id != flow2.trace_id
    
    def test_custom_trace_id(self):
        """Test custom trace ID"""
        custom_id = "custom_trace_12345"
        flow = Flow(
            name="test_flow",
            trace_id=custom_id,
            steps=[FunctionStep("step1", lambda u, c: c)]
        )
        
        assert flow.trace_id == custom_id
        assert flow.flow_id == custom_id
    
    def test_trace_id_without_name(self):
        """Test trace ID generation without flow name"""
        flow = Flow(steps=[FunctionStep("step1", lambda u, c: c)])
        
        assert flow.flow_name is None
        assert flow.trace_id.startswith("flow_")
        assert len(flow.trace_id) > len("flow_")
    
    def test_trace_id_with_special_characters(self):
        """Test trace ID generation with special characters in name"""
        flow = Flow(
            name="test-flow_with@special#chars!",
            steps=[FunctionStep("step1", lambda u, c: c)]
        )
        
        # Should sanitize special characters
        assert "test-flow_with_special_chars_" in flow.trace_id
        assert "@" not in flow.trace_id
        assert "#" not in flow.trace_id
        assert "!" not in flow.trace_id
    
    @pytest.mark.asyncio
    async def test_context_trace_id_propagation(self):
        """Test that trace ID is propagated to context"""
        def test_function(user_input, ctx):
            assert ctx.trace_id == "test_trace_123"
            return ctx
        
        flow = Flow(
            name="test_flow",
            trace_id="test_trace_123",
            steps=[FunctionStep("step1", test_function)]
        )
        
        result = await flow.run("test")
        assert result.trace_id == "test_trace_123"
    
    def test_flow_summary_identification(self):
        """Test flow summary includes identification information"""
        flow = Flow(
            name="summary_test",
            trace_id="summary_trace_456",
            steps=[FunctionStep("step1", lambda u, c: c)]
        )
        
        summary = flow.get_flow_summary()
        
        assert summary["flow_name"] == "summary_test"
        assert summary["flow_id"] == "summary_trace_456"
        assert summary["trace_id"] == "summary_trace_456"
        assert "execution_history" in summary
        assert "start_step" in summary
    
    @pytest.mark.asyncio
    async def test_multiple_flows_unique_ids(self):
        """Test that multiple flows have unique IDs"""
        flows = []
        for i in range(5):
            flow = Flow(
                name=f"flow_{i}",
                steps=[FunctionStep("step1", lambda u, c: c)]
            )
            flows.append(flow)
        
        # All trace IDs should be unique
        trace_ids = [flow.trace_id for flow in flows]
        assert len(set(trace_ids)) == len(trace_ids)
        
        # All should contain their respective names
        for i, flow in enumerate(flows):
            assert f"flow_{i}" in flow.trace_id
    
    def test_create_simple_flow_with_name(self):
        """Test create_simple_flow with name parameter"""
        def step_func(u, c):
            return c
        
        flow = create_simple_flow(
            steps=[
                ("step1", FunctionStep("step1", step_func)),
                ("step2", FunctionStep("step2", step_func))
            ],
            name="simple_test"
        )
        
        assert flow.flow_name == "simple_test"
        assert "simple_test" in flow.trace_id
    
    def test_create_conditional_flow_with_name(self):
        """Test create_conditional_flow with name parameter"""
        def step_func(u, c):
            return c
        
        def condition_func(c):
            return True
        
        initial_step = FunctionStep("initial", step_func)
        condition_step = FunctionStep("condition", step_func)  # Simplified for test
        true_branch = [FunctionStep("true1", step_func)]
        false_branch = [FunctionStep("false1", step_func)]
        
        flow = create_conditional_flow(
            name="conditional_test",
            initial_step=initial_step,
            condition_step=condition_step,
            true_branch=true_branch,
            false_branch=false_branch
        )
        
        assert flow.flow_name == "conditional_test"
        assert "conditional_test" in flow.trace_id


class TestFlowTracing:
    """Test Flow tracing features"""
    
    @pytest.mark.asyncio
    async def test_execution_history_tracking(self):
        """Test that execution history is tracked"""
        def step1_func(user_input, ctx):
            ctx.add_assistant_message("Step 1 executed")
            return ctx
        
        def step2_func(user_input, ctx):
            ctx.add_assistant_message("Step 2 executed")
            return ctx
        
        step1 = FunctionStep("step1", step1_func)
        step2 = FunctionStep("step2", step2_func)
        debug_step = DebugStep("debug")
        
        step1.next_step = "step2"
        step2.next_step = "debug"
        
        flow = Flow(
            name="history_test",
            start="step1",
            steps={
                "step1": step1,
                "step2": step2,
                "debug": debug_step
            }
        )
        
        result = await flow.run("test input")
        
        # Check that flow completed
        assert result.is_finished()
        assert result.step_count == 3
        
        # Check flow summary
        summary = flow.get_flow_summary()
        assert summary["finished"] is True
        assert summary["step_count"] == 3
        assert summary["flow_name"] == "history_test"
    
    @pytest.mark.asyncio
    async def test_error_scenario_identification(self):
        """Test flow identification in error scenarios"""
        def error_func(user_input, ctx):
            raise ValueError("Test error")
        
        def safe_func(user_input, ctx):
            ctx.add_assistant_message("Safe step executed")
            return ctx
        
        safe_step = FunctionStep("safe", safe_func)
        error_step = FunctionStep("error", error_func)
        
        safe_step.next_step = "error"
        
        flow = Flow(
            name="error_test",
            trace_id="error_trace_789",
            start="safe",
            steps={
                "safe": safe_step,
                "error": error_step
            }
        )
        
        try:
            await flow.run("test")
            assert False, "Should have raised an exception"
        except Exception:
            # Error occurred, check flow state
            summary = flow.get_flow_summary()
            assert summary["flow_name"] == "error_test"
            assert summary["trace_id"] == "error_trace_789"
            # Should have executed at least the safe step
            assert summary["step_count"] >= 1
    
    def test_flow_string_representation(self):
        """Test flow string representation includes identification"""
        flow = Flow(
            name="repr_test",
            steps=[FunctionStep("step1", lambda u, c: c)]
        )
        
        flow_str = str(flow)
        assert "Flow(" in flow_str
        assert "start=" in flow_str
        assert "steps=" in flow_str
        assert "finished=" in flow_str
    
    @pytest.mark.asyncio
    async def test_flow_reset_preserves_identification(self):
        """Test that flow reset preserves identification"""
        flow = Flow(
            name="reset_test",
            trace_id="reset_trace_999",
            steps=[FunctionStep("step1", lambda u, c: c)]
        )
        
        original_name = flow.flow_name
        original_trace_id = flow.trace_id
        
        # Run flow
        await flow.run("test")
        
        # Reset flow
        flow.reset()
        
        # Check that identification is preserved
        assert flow.flow_name == original_name
        assert flow.trace_id == original_trace_id
        assert flow.context.trace_id == original_trace_id
    
    def test_microsecond_precision_in_trace_id(self):
        """Test that trace IDs include microsecond precision for uniqueness"""
        import time
        
        flow1 = Flow(name="timing_test", steps=[FunctionStep("step1", lambda u, c: c)])
        time.sleep(0.001)  # Small delay to ensure different timestamps
        flow2 = Flow(name="timing_test", steps=[FunctionStep("step1", lambda u, c: c)])
        
        # Even with same name and created quickly, should be different
        assert flow1.trace_id != flow2.trace_id
        
        # Both should contain microsecond-level timestamps (6 digits)
        assert len(flow1.trace_id.split('_')[-1]) == 6  # Microseconds
        assert len(flow2.trace_id.split('_')[-1]) == 6


if __name__ == "__main__":
    pytest.main([__file__]) 
