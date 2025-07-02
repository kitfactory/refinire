"""Test evaluation result access through Context.evaluation_result"""

import pytest
from refinire import RefinireAgent, Context, create_evaluated_agent, create_simple_agent


class TestEvaluationResultAccess:
    """Test cases for evaluation result access via ctx.evaluation_result"""
    
    def test_simple_agent_no_evaluation_result(self):
        """Test that simple agent without evaluation has no evaluation_result"""
        agent = create_simple_agent(
            name="simple_test",
            instructions="You are a helpful assistant."
        )
        
        ctx = Context()
        result_ctx = agent.run("Hello", ctx)
        
        # No evaluation should be performed
        assert result_ctx.evaluation_result is None
        assert result_ctx.result is not None  # But result should exist
    
    def test_evaluated_agent_has_evaluation_result(self):
        """Test that evaluated agent produces evaluation_result"""
        agent = create_evaluated_agent(
            name="eval_test",
            generation_instructions="Respond helpfully.",
            evaluation_instructions="Rate helpfulness 0-100",
            threshold=70
        )
        
        ctx = Context()
        result_ctx = agent.run("What is AI?", ctx)
        
        # Evaluation should be performed
        assert result_ctx.evaluation_result is not None
        assert "score" in result_ctx.evaluation_result
        assert "passed" in result_ctx.evaluation_result
        assert "feedback" in result_ctx.evaluation_result
        assert "metadata" in result_ctx.evaluation_result
        
        # Score should be a float
        assert isinstance(result_ctx.evaluation_result["score"], float)
        assert 0 <= result_ctx.evaluation_result["score"] <= 100
        
        # Passed should be a boolean
        assert isinstance(result_ctx.evaluation_result["passed"], bool)
    
    def test_evaluation_threshold_logic(self):
        """Test that evaluation threshold logic works correctly"""
        # Test with low threshold (should pass)
        low_threshold_agent = create_evaluated_agent(
            name="low_threshold",
            generation_instructions="Respond helpfully.",
            evaluation_instructions="Rate helpfulness 0-100",
            threshold=50  # Low threshold
        )
        
        ctx1 = Context()
        result_ctx1 = low_threshold_agent.run("Hello", ctx1)
        
        # Should likely pass with low threshold
        assert result_ctx1.evaluation_result["passed"] == (
            result_ctx1.evaluation_result["score"] >= 50
        )
        
        # Test with high threshold (should fail)
        high_threshold_agent = create_evaluated_agent(
            name="high_threshold", 
            generation_instructions="Respond helpfully.",
            evaluation_instructions="Rate helpfulness 0-100",
            threshold=95  # High threshold
        )
        
        ctx2 = Context()
        result_ctx2 = high_threshold_agent.run("Hi", ctx2)
        
        # Should likely fail with high threshold
        assert result_ctx2.evaluation_result["passed"] == (
            result_ctx2.evaluation_result["score"] >= 95
        )
    
    def test_evaluation_result_structure(self):
        """Test that evaluation_result has the correct structure"""
        agent = create_evaluated_agent(
            name="structure_test",
            generation_instructions="Respond helpfully.",
            evaluation_instructions="Rate helpfulness 0-100"
        )
        
        ctx = Context()
        result_ctx = agent.run("Test input", ctx)
        
        eval_result = result_ctx.evaluation_result
        assert eval_result is not None
        
        # Check required fields
        required_fields = ["score", "passed", "feedback", "metadata"]
        for field in required_fields:
            assert field in eval_result, f"Missing required field: {field}"
        
        # Check data types
        assert isinstance(eval_result["score"], (int, float))
        assert isinstance(eval_result["passed"], bool)
        assert isinstance(eval_result["feedback"], str)
        assert isinstance(eval_result["metadata"], dict)
    
    def test_context_preserves_evaluation_result(self):
        """Test that Context properly preserves evaluation_result"""
        agent = create_evaluated_agent(
            name="preserve_test",
            generation_instructions="Respond helpfully.",
            evaluation_instructions="Rate helpfulness 0-100"
        )
        
        ctx = Context()
        original_shared_state = ctx.shared_state.copy()
        
        result_ctx = agent.run("Test", ctx)
        
        # evaluation_result should be set
        assert result_ctx.evaluation_result is not None
        
        # Should be the same context object
        assert result_ctx is ctx
        
        # Other context data should be preserved
        for key, value in original_shared_state.items():
            assert ctx.shared_state[key] == value