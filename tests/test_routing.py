"""
Tests for routing functionality in RefinireAgent.
RefinireAgent のルーティング機能のテスト
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import BaseModel, Field
from src.refinire.core.routing import (
    RoutingResult, 
    RoutingConstraints, 
    create_routing_result_model,
    DEFAULT_ROUTING_INSTRUCTIONS
)
from src.refinire.agents.pipeline.llm_pipeline import RefinireAgent
from src.refinire.agents.flow.context import Context


class TestRoutingResult:
    """Test RoutingResult data class."""
    
    def test_routing_result_creation(self):
        """Test creating a RoutingResult instance."""
        result = RoutingResult(
            content="Test content",
            next_route="test_route",
            confidence=0.85,
            reasoning="This is a test routing decision"
        )
        
        assert result.content == "Test content"
        assert result.next_route == "test_route"
        assert result.confidence == 0.85
        assert result.reasoning == "This is a test routing decision"
    
    def test_routing_result_with_custom_content(self):
        """Test RoutingResult with custom content type."""
        custom_content = {"task": "completed", "score": 0.9}
        result = RoutingResult(
            content=custom_content,
            next_route="complete",
            confidence=0.9,
            reasoning="Task completed successfully"
        )
        
        assert result.content == custom_content
        assert result.next_route == "complete"
    
    def test_routing_result_validation_invalid_route(self):
        """Test RoutingResult validation with invalid route name."""
        with pytest.raises(ValueError, match="Invalid route name format"):
            RoutingResult(
                content="Test content",
                next_route="123invalid",  # Invalid: starts with number
                confidence=0.85,
                reasoning="Test reasoning"
            )
    
    def test_routing_result_validation_invalid_confidence(self):
        """Test RoutingResult validation with invalid confidence."""
        with pytest.raises(ValueError):
            RoutingResult(
                content="Test content",
                next_route="test_route",
                confidence=1.5,  # Invalid: > 1.0
                reasoning="Test reasoning"
            )
    
    def test_routing_result_validation_invalid_reasoning(self):
        """Test RoutingResult validation with invalid reasoning."""
        with pytest.raises(ValueError, match="Reasoning too short"):
            RoutingResult(
                content="Test content",
                next_route="test_route",
                confidence=0.85,
                reasoning="Too short"  # Invalid: < 10 characters
            )


class TestRoutingConstraints:
    """Test RoutingConstraints utility class."""
    
    def test_is_valid_route_name(self):
        """Test route name validation."""
        assert RoutingConstraints.is_valid_route_name("valid_route") is True
        assert RoutingConstraints.is_valid_route_name("valid-route") is True
        assert RoutingConstraints.is_valid_route_name("validRoute123") is True
        assert RoutingConstraints.is_valid_route_name("123invalid") is False
        assert RoutingConstraints.is_valid_route_name("") is False
        assert RoutingConstraints.is_valid_route_name("a" * 51) is False  # Too long
    
    def test_is_valid_confidence(self):
        """Test confidence validation."""
        assert RoutingConstraints.is_valid_confidence(0.0) is True
        assert RoutingConstraints.is_valid_confidence(0.5) is True
        assert RoutingConstraints.is_valid_confidence(1.0) is True
        assert RoutingConstraints.is_valid_confidence(-0.1) is False
        assert RoutingConstraints.is_valid_confidence(1.1) is False
    
    def test_is_valid_reasoning(self):
        """Test reasoning validation."""
        assert RoutingConstraints.is_valid_reasoning("This is a valid reasoning with enough characters") is True
        assert RoutingConstraints.is_valid_reasoning("Too short") is False
        assert RoutingConstraints.is_valid_reasoning("") is False
        assert RoutingConstraints.is_valid_reasoning("a" * 501) is False  # Too long


class TestCreateRoutingResultModel:
    """Test dynamic RoutingResult model creation."""
    
    def test_create_routing_result_model_with_custom_type(self):
        """Test creating a RoutingResult model with custom content type."""
        class CustomContent(BaseModel):
            task: str = Field(description="Task description")
            score: float = Field(description="Task score")
        
        DynamicRoutingResult = create_routing_result_model(CustomContent)
        
        # Create instance with custom content
        custom_content = CustomContent(task="test task", score=0.9)
        result = DynamicRoutingResult(
            content=custom_content,
            next_route="complete",
            confidence=0.95,
            reasoning="Task completed with high score"
        )
        
        assert isinstance(result.content, CustomContent)
        assert result.content.task == "test task"
        assert result.content.score == 0.9
        assert result.next_route == "complete"


class TestRefinireAgentRouting:
    """Test RefinireAgent routing functionality."""
    
    def test_routing_parameters_initialization(self):
        """Test RefinireAgent initialization with routing parameters."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content",
            routing_instruction="Route based on quality",
            routing_mode="accurate_routing"
        )
        
        assert agent.routing_instruction == "Route based on quality"
        assert agent.routing_mode == "accurate_routing"
    
    def test_routing_mode_validation(self):
        """Test routing_mode validation."""
        with pytest.raises(ValueError, match="Invalid routing_mode"):
            RefinireAgent(
                name="test_agent",
                generation_instructions="Generate content",
                routing_mode="invalid_mode"
            )
    
    def test_create_routing_output_model_with_output_model(self):
        """Test _create_routing_output_model with output_model specified."""
        class TaskResult(BaseModel):
            task: str
            score: float
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content",
            output_model=TaskResult,
            routing_instruction="Route based on score"
        )
        
        routing_model = agent._create_routing_output_model()
        
        # Should create a dynamic model with TaskResult as content type
        assert routing_model is not RoutingResult  # Different model
        
        # Test creating instance
        task_result = TaskResult(task="test", score=0.8)
        routing_result = routing_model(
            content=task_result,
            next_route="continue",
            confidence=0.9,
            reasoning="Good score, continue processing"
        )
        
        assert routing_result.content.task == "test"
        assert routing_result.content.score == 0.8
        assert routing_result.next_route == "continue"
    
    def test_create_routing_output_model_without_output_model(self):
        """Test _create_routing_output_model without output_model."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content",
            routing_instruction="Route based on content"
        )
        
        routing_model = agent._create_routing_output_model()
        
        # Should use standard RoutingResult
        assert routing_model is RoutingResult
    
    def test_build_routing_prompt(self):
        """Test _build_routing_prompt method."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content",
            routing_instruction="Route based on quality score"
        )
        
        content = "This is test content"
        prompt = agent._build_routing_prompt(content, agent.routing_instruction)
        
        assert "生成されたコンテンツを分析し" in prompt
        assert "This is test content" in prompt
        assert "Route based on quality score" in prompt
    
    @patch.object(RefinireAgent, 'run')
    def test_execute_accurate_routing(self, mock_run):
        """Test _execute_accurate_routing method."""
        # Mock the routing agent run result
        mock_routing_result = Mock()
        mock_routing_result.success = True
        mock_routing_result.content = RoutingResult(
            content="Test content",
            next_route="complete",
            confidence=0.9,
            reasoning="High quality content"
        )
        mock_run.return_value = mock_routing_result
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content",
            routing_instruction="Route based on quality",
            routing_mode="accurate_routing"
        )
        
        # Mock the model name
        agent.model_name = "gpt-4o-mini"
        
        result = agent._execute_accurate_routing(
            content="Test content",
            routing_output_model=RoutingResult
        )
        
        assert result is not None
        assert result.content == "Test content"
        assert result.next_route == "complete"
        assert result.confidence == 0.9
    
    def test_execute_fast_routing(self):
        """Test _execute_fast_routing method."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content",
            routing_instruction="Route based on quality",
            routing_mode="fast_routing"
        )
        
        result = agent._execute_fast_routing(
            content="Test content",
            routing_output_model=RoutingResult
        )
        
        assert result is not None
        assert result.content == "Test content"
        assert result.next_route == "continue"
        assert result.confidence == 0.8
        assert "Fast routing mode" in result.reasoning
    
    def test_execute_routing_without_routing_instruction(self):
        """Test _execute_routing when routing_instruction is None."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content"
            # No routing_instruction
        )
        
        result = agent._execute_routing(content="Test content")
        
        assert result is None
    
    @patch('src.refinire.agents.pipeline.llm_pipeline.RefinireAgent._execute_accurate_routing')
    def test_execute_routing_accurate_mode(self, mock_accurate_routing):
        """Test _execute_routing with accurate_routing mode."""
        mock_accurate_routing.return_value = RoutingResult(
            content="Test content",
            next_route="complete",
            confidence=0.9,
            reasoning="High quality"
        )
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content",
            routing_instruction="Route based on quality",
            routing_mode="accurate_routing"
        )
        
        result = agent._execute_routing(content="Test content")
        
        assert result is not None
        assert result.next_route == "complete"
        mock_accurate_routing.assert_called_once()
    
    @patch('src.refinire.agents.pipeline.llm_pipeline.RefinireAgent._execute_fast_routing')
    def test_execute_routing_fast_mode(self, mock_fast_routing):
        """Test _execute_routing with fast_routing mode."""
        mock_fast_routing.return_value = RoutingResult(
            content="Test content",
            next_route="continue",
            confidence=0.8,
            reasoning="Fast routing"
        )
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content",
            routing_instruction="Route based on quality",
            routing_mode="fast_routing"
        )
        
        result = agent._execute_routing(content="Test content")
        
        assert result is not None
        assert result.next_route == "continue"
        mock_fast_routing.assert_called_once()


class TestDefaultRoutingInstructions:
    """Test default routing instructions."""
    
    def test_default_routing_instructions_exist(self):
        """Test that default routing instructions are defined."""
        assert "simple" in DEFAULT_ROUTING_INSTRUCTIONS
        assert "quality_based" in DEFAULT_ROUTING_INSTRUCTIONS
        assert "complexity_based" in DEFAULT_ROUTING_INSTRUCTIONS
        assert "content_type_based" in DEFAULT_ROUTING_INSTRUCTIONS
    
    def test_default_routing_instructions_content(self):
        """Test that default routing instructions have meaningful content."""
        for key, instruction in DEFAULT_ROUTING_INSTRUCTIONS.items():
            assert isinstance(instruction, str)
            assert len(instruction) > 0
            assert len(instruction.strip()) > 10  # Meaningful content


class TestRoutingIntegration:
    """Test routing integration with RefinireAgent execution."""
    
    @patch.object(RefinireAgent, '_execute_routing')
    @patch.object(RefinireAgent, '_run_standalone')
    def test_routing_integration_in_execute_with_context(self, mock_run_standalone, mock_execute_routing):
        """Test routing integration in _execute_with_context."""
        # Mock LLM execution
        mock_llm_result = Mock()
        mock_llm_result.success = True
        mock_llm_result.content = "Generated content"
        mock_run_standalone.return_value = mock_llm_result
        
        # Mock routing execution
        mock_routing_result = RoutingResult(
            content="Generated content",
            next_route="complete",
            confidence=0.9,
            reasoning="High quality content"
        )
        mock_execute_routing.return_value = mock_routing_result
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content",
            routing_instruction="Route based on quality"
        )
        
        ctx = Context()
        
        # This would normally be async, but for testing we'll mock it
        import asyncio
        
        async def test_execution():
            result_ctx = await agent._execute_with_context("Test input", ctx)
            return result_ctx
        
        # Run the async function
        result_ctx = asyncio.run(test_execution())
        
        # Verify routing was executed
        mock_execute_routing.assert_called_once_with("Generated content", ctx)
        
        # Verify context was updated with routing result
        assert hasattr(result_ctx, 'routing_result')
        assert result_ctx.routing_result['next_route'] == "complete"
        assert result_ctx.routing_result['confidence'] == 0.9
        assert result_ctx.routing_result['reasoning'] == "High quality content"
        
        # Verify the result is the routing result
        assert result_ctx.result == mock_routing_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])