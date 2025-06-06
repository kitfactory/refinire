"""Tests for InteractivePipeline - Generic interactive conversation pipeline
対話的パイプラインのテスト - 汎用対話パイプライン
"""

import pytest
from unittest.mock import Mock, patch
from typing import Any

from agents_sdk_models import (
    InteractivePipeline, InteractionResult, InteractionQuestion,
    create_simple_interactive_pipeline, create_evaluated_interactive_pipeline,
    LLMResult
)

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object


class TestInteractivePipeline:
    """Test cases for InteractivePipeline"""
    
    def test_interactive_pipeline_initialization(self):
        """Test InteractivePipeline can be initialized correctly"""
        
        def completion_check(result: Any) -> bool:
            return hasattr(result, 'done') and result.done
        
        pipeline = InteractivePipeline(
            name="test_interactive",
            generation_instructions="You are a helpful assistant.",
            completion_check=completion_check,
            max_turns=10
        )
        
        assert pipeline.name == "test_interactive"
        assert pipeline.max_turns == 10
        assert pipeline.current_turn == 0
        assert pipeline.remaining_turns == 10
        assert not pipeline.is_complete
        assert pipeline.interaction_history == []
    
    def test_interactive_pipeline_completion_check(self):
        """Test completion check function works correctly"""
        
        def completion_check(result: Any) -> bool:
            return str(result).lower().startswith("done")
        
        pipeline = InteractivePipeline(
            name="test_completion",
            generation_instructions="Complete when user says done.",
            completion_check=completion_check,
            max_turns=5
        )
        
        # Mock the LLMPipeline run method (super().run)
        with patch('agents_sdk_models.llm_pipeline.LLMPipeline.run') as mock_run:
            mock_run.return_value = LLMResult(
                content="I understand your request.",
                success=True
            )
            
            # First interaction - not complete
            result = pipeline.run_interactive("help me")
            assert isinstance(result, InteractionResult)
            assert not result.is_complete
            assert result.turn == 1
            
            # Mock completion response
            mock_run.return_value = LLMResult(
                content="Done! Task completed.",
                success=True
            )
            
            # Second interaction - complete
            result = pipeline.continue_interaction("done")
            assert isinstance(result, InteractionResult)
            assert result.is_complete
            assert result.turn == 2
    
    def test_max_turns_limit(self):
        """Test pipeline respects max turns limit"""
        
        def never_complete(result: Any) -> bool:
            return False  # Never complete
        
        pipeline = InteractivePipeline(
            name="test_max_turns",
            generation_instructions="Never complete.",
            completion_check=never_complete,
            max_turns=2
        )
        
        with patch('agents_sdk_models.llm_pipeline.LLMPipeline.run') as mock_run:
            mock_run.return_value = LLMResult(
                content="Continue asking",
                success=True
            )
            
            # First turn
            result = pipeline.run_interactive("hello")
            assert not result.is_complete
            assert result.turn == 1
            assert result.remaining_turns == 1
            
            # Second turn - reaches max
            result = pipeline.continue_interaction("more")
            assert result.is_complete  # Force complete due to max turns
            assert result.turn == 2
            assert result.remaining_turns == 0
    
    def test_question_formatting(self):
        """Test custom question formatting works"""
        
        def completion_check(result: Any) -> bool:
            return False
        
        def custom_format(response: str, turn: int, remaining: int) -> str:
            return f"Q{turn}: {response} (あと{remaining}ターン)"
        
        pipeline = InteractivePipeline(
            name="test_format",
            generation_instructions="Ask questions.",
            completion_check=completion_check,
            max_turns=3,
            question_format=custom_format
        )
        
        with patch('agents_sdk_models.llm_pipeline.LLMPipeline.run') as mock_run:
            mock_run.return_value = LLMResult(
                content="What do you need?",
                success=True
            )
            
            result = pipeline.run_interactive("help")
            assert isinstance(result.content, InteractionQuestion)
            assert "Q1: What do you need? (あと2ターン)" in str(result.content.question)
    
    def test_error_handling(self):
        """Test pipeline handles errors gracefully"""
        
        def completion_check(result: Any) -> bool:
            return False
        
        pipeline = InteractivePipeline(
            name="test_error",
            generation_instructions="Test error handling.",
            completion_check=completion_check,
            max_turns=5
        )
        
        with patch('agents_sdk_models.llm_pipeline.LLMPipeline.run') as mock_run:
            mock_run.return_value = LLMResult(
                content=None,
                success=False,
                metadata={"error": "API failure"}
            )
            
            result = pipeline.run_interactive("test")
            assert isinstance(result, InteractionResult)
            assert not result.success
            assert not result.is_complete
            assert isinstance(result.content, InteractionQuestion)
            assert "error" in result.content.question.lower()
    
    def test_conversation_history(self):
        """Test conversation history is tracked correctly"""
        
        def completion_check(result: Any) -> bool:
            return False
        
        pipeline = InteractivePipeline(
            name="test_history",
            generation_instructions="Track conversation.",
            completion_check=completion_check,
            max_turns=3
        )
        
        with patch('agents_sdk_models.llm_pipeline.LLMPipeline.run') as mock_run:
            mock_run.return_value = LLMResult(
                content="Response 1",
                success=True
            )
            
            # First interaction
            pipeline.run_interactive("Input 1")
            history = pipeline.interaction_history
            assert len(history) == 1
            assert history[0]['user_input'] == "Input 1"
            assert history[0]['ai_result']['content'] == "Response 1"
            
            mock_run.return_value = LLMResult(
                content="Response 2",
                success=True
            )
            
            # Second interaction
            pipeline.continue_interaction("Input 2")
            history = pipeline.interaction_history
            assert len(history) == 2
            assert history[1]['user_input'] == "Input 2"
            assert history[1]['ai_result']['content'] == "Response 2"
    
    def test_reset_interaction(self):
        """Test reset functionality works correctly"""
        
        def completion_check(result: Any) -> bool:
            return False
        
        pipeline = InteractivePipeline(
            name="test_reset",
            generation_instructions="Test reset.",
            completion_check=completion_check,
            max_turns=5
        )
        
        with patch('agents_sdk_models.llm_pipeline.LLMPipeline.run') as mock_run:
            mock_run.return_value = LLMResult(
                content="Response",
                success=True
            )
            
            # Make some interactions
            pipeline.run_interactive("test")
            pipeline.continue_interaction("more")
            
            assert pipeline.current_turn == 2
            assert len(pipeline.interaction_history) == 2
            
            # Reset
            pipeline.reset_interaction()
            
            assert pipeline.current_turn == 0
            assert pipeline.remaining_turns == 5
            assert not pipeline.is_complete
            assert len(pipeline.interaction_history) == 0
    
    def test_create_simple_interactive_pipeline(self):
        """Test simple pipeline creation utility"""
        
        def completion_check(result: Any) -> bool:
            return "finished" in str(result).lower()
        
        pipeline = create_simple_interactive_pipeline(
            name="simple_test",
            instructions="Simple instructions",
            completion_check=completion_check,
            max_turns=15,
            model="gpt-3.5-turbo"
        )
        
        assert isinstance(pipeline, InteractivePipeline)
        assert pipeline.name == "simple_test"
        assert pipeline.max_turns == 15
        assert pipeline.model == "gpt-3.5-turbo"
    
    def test_create_evaluated_interactive_pipeline(self):
        """Test evaluated pipeline creation utility"""
        
        def completion_check(result: Any) -> bool:
            return True
        
        pipeline = create_evaluated_interactive_pipeline(
            name="evaluated_test",
            generation_instructions="Generation instructions",
            evaluation_instructions="Evaluation instructions",
            completion_check=completion_check,
            max_turns=8,
            threshold=90.0,
            model="gpt-4"
        )
        
        assert isinstance(pipeline, InteractivePipeline)
        assert pipeline.name == "evaluated_test"
        assert pipeline.max_turns == 8
        assert pipeline.threshold == 90.0
        assert pipeline.evaluation_instructions == "Evaluation instructions"


class MockCompletionModel(BaseModel):
    """Mock model for testing completion"""
    is_complete: bool = False
    result: str = ""


class TestInteractivePipelineWithStructuredOutput:
    """Test InteractivePipeline with structured output models"""
    
    def test_structured_output_completion(self):
        """Test completion with structured output"""
        
        def completion_check(result: Any) -> bool:
            return hasattr(result, 'is_complete') and result.is_complete
        
        pipeline = InteractivePipeline(
            name="structured_test",
            generation_instructions="Return structured output.",
            completion_check=completion_check,
            output_model=MockCompletionModel,
            max_turns=5
        )
        
        with patch('agents_sdk_models.llm_pipeline.LLMPipeline.run') as mock_run:
            # First - not complete
            mock_run.return_value = LLMResult(
                content=MockCompletionModel(is_complete=False, result="Not done yet"),
                success=True
            )
            
            result = pipeline.run_interactive("start")
            assert not result.is_complete
            
            # Second - complete
            mock_run.return_value = LLMResult(
                content=MockCompletionModel(is_complete=True, result="Task finished"),
                success=True
            )
            
            result = pipeline.continue_interaction("finish")
            assert result.is_complete
            assert hasattr(result.content, 'result')
            assert result.content.result == "Task finished"


if __name__ == "__main__":
    pytest.main([__file__]) 