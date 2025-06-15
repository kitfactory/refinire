"""Test GenAgent - Modern LLM-based Step using LLMPipeline"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Optional

from src.refinire.agents.gen_agent import (
    GenAgent, create_simple_gen_agent, create_evaluated_gen_agent
)
from refinire import Context, LLMResult

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = object


# Test data models  
class OutputModel(BaseModel):
    result: str
    confidence: float


class TestGenAgent:
    """Test GenAgent functionality"""

    def test_gen_agent_initialization(self):
        """Test GenAgent initialization with basic parameters"""
        agent = GenAgent(
            name="test_agent",
            generation_instructions="Generate helpful responses",
            model="gpt-4o-mini",
            threshold=80.0,
            max_retries=2,
            next_step="next_test_step"
        )
        
        assert agent.name == "test_agent"
        assert agent.next_step == "next_test_step"
        assert agent.store_result_key == "test_agent_result"
        assert agent.llm_pipeline.generation_instructions == "Generate helpful responses"
        assert agent.llm_pipeline.model == "gpt-4o-mini"
        assert agent.llm_pipeline.threshold == 80.0
        assert agent.llm_pipeline.max_retries == 2

    def test_gen_agent_initialization_with_evaluation(self):
        """Test GenAgent initialization with evaluation"""
        agent = GenAgent(
            name="eval_agent",
            generation_instructions="Generate responses",
            evaluation_instructions="Evaluate quality",
            evaluation_model="gpt-4",
            store_result_key="custom_result_key"
        )
        
        assert agent.llm_pipeline.evaluation_instructions == "Evaluate quality"
        assert agent.llm_pipeline.evaluation_model == "gpt-4"
        assert agent.store_result_key == "custom_result_key"

    def test_gen_agent_initialization_with_structured_output(self):
        """Test GenAgent initialization with structured output"""
        agent = GenAgent(
            name="structured_agent",
            generation_instructions="Generate structured data",
            output_model=OutputModel
        )
        
        assert agent.llm_pipeline.output_model == OutputModel

    @pytest.mark.asyncio
    async def test_run_success_with_user_input(self):
        """Test successful run with user input"""
        # Mock LLMPipeline run method
        mock_llm_result = LLMResult(
            content="Generated response",
            success=True,
            attempts=1
        )
        
        agent = GenAgent(
            name="test_agent",
            generation_instructions="Generate responses",
            next_step="next_step"
        )
        
        with patch.object(agent.llm_pipeline, 'run', return_value=mock_llm_result):
            ctx = Context()
            result_ctx = await agent.run("Test input", ctx)
            
            # Verify context updates
            assert result_ctx.current_step == "test_agent"
            assert result_ctx.shared_state["test_agent_result"] == "Generated response"
            assert result_ctx.prev_outputs["test_agent"] == "Generated response"
            assert result_ctx.next_label == "next_step"
            
            # Verify messages
            assistant_messages = [msg for msg in result_ctx.messages if msg.role == "assistant"]
            system_messages = [msg for msg in result_ctx.messages if msg.role == "system"]
            
            assert len(assistant_messages) == 1
            assert assistant_messages[0].content == "Generated response"
            assert any("Pipeline executed successfully" in msg.content for msg in system_messages)

    @pytest.mark.asyncio
    async def test_run_success_with_context_input(self):
        """Test successful run using context's last user input"""
        mock_llm_result = LLMResult(
            content="Context response",
            success=True,
            attempts=1
        )
        
        agent = GenAgent(
            name="context_agent",
            generation_instructions="Generate responses"
        )
        
        with patch.object(agent.llm_pipeline, 'run', return_value=mock_llm_result):
            ctx = Context()
            ctx.last_user_input = "Context input text"
            
            result_ctx = await agent.run(None, ctx)
            
            assert result_ctx.shared_state["context_agent_result"] == "Context response"
            assert result_ctx.prev_outputs["context_agent"] == "Context response"

    @pytest.mark.asyncio
    async def test_run_no_input_available(self):
        """Test run with no input available"""
        agent = GenAgent(
            name="no_input_agent",
            generation_instructions="Generate responses"
        )
        
        ctx = Context()
        result_ctx = await agent.run(None, ctx)
        
        # Verify no execution occurred
        assert result_ctx.shared_state["no_input_agent_result"] is None
        assert result_ctx.prev_outputs["no_input_agent"] is None
        
        # Verify system message about no input
        system_messages = [msg for msg in result_ctx.messages if msg.role == "system"]
        assert any("No input available" in msg.content for msg in system_messages)

    @pytest.mark.asyncio
    async def test_run_pipeline_failure(self):
        """Test run when pipeline execution fails"""
        # Mock failed LLMPipeline result
        mock_llm_result = LLMResult(
            content=None,
            success=False,
            metadata={"error": "Evaluation threshold not met"},
            attempts=3
        )
        
        agent = GenAgent(
            name="fail_agent",
            generation_instructions="Generate responses"
        )
        
        with patch.object(agent.llm_pipeline, 'run', return_value=mock_llm_result):
            ctx = Context()
            result_ctx = await agent.run("Test input", ctx)
            
            # Verify failure handling
            assert result_ctx.shared_state["fail_agent_result"] is None
            assert result_ctx.prev_outputs["fail_agent"] is None
            
            # Verify failure message
            system_messages = [msg for msg in result_ctx.messages if msg.role == "system"]
            assert any("Pipeline execution failed" in msg.content for msg in system_messages)

    @pytest.mark.asyncio
    async def test_run_with_exception(self):
        """Test run when pipeline raises exception"""
        agent = GenAgent(
            name="error_agent",
            generation_instructions="Generate responses"
        )
        
        with patch.object(agent.llm_pipeline, 'run', side_effect=Exception("Test error")):
            ctx = Context()
            result_ctx = await agent.run("Test input", ctx)
            
            # Verify error handling
            assert result_ctx.shared_state["error_agent_result"] is None
            assert result_ctx.prev_outputs["error_agent"] is None
            
            # Verify error message
            system_messages = [msg for msg in result_ctx.messages if msg.role == "system"]
            assert any("execution error: Test error" in msg.content for msg in system_messages)

    @pytest.mark.asyncio
    async def test_run_with_structured_output(self):
        """Test run with structured output model"""
        # Create structured output
        structured_output = OutputModel(result="Structured data", confidence=0.95)
        mock_llm_result = LLMResult(
            content=structured_output,
            success=True,
            attempts=1
        )
        
        agent = GenAgent(
            name="structured_agent",
            generation_instructions="Generate structured data",
            output_model=OutputModel
        )
        
        with patch.object(agent.llm_pipeline, 'run', return_value=mock_llm_result):
            ctx = Context()
            result_ctx = await agent.run("Test input", ctx)
            
            # Verify structured output handling
            stored_result = result_ctx.shared_state["structured_agent_result"]
            assert isinstance(stored_result, OutputModel)
            assert stored_result.result == "Structured data"
            assert stored_result.confidence == 0.95

    def test_get_pipeline_history(self):
        """Test getting pipeline history"""
        agent = GenAgent(
            name="history_agent",
            generation_instructions="Generate responses"
        )
        
        # Mock pipeline history
        mock_history = [{"user_input": "test", "result": "response"}]
        
        with patch.object(agent.llm_pipeline, 'get_history', return_value=mock_history):
            history = agent.get_pipeline_history()
            assert history == mock_history

    def test_get_session_history(self):
        """Test getting session history"""
        agent = GenAgent(
            name="session_agent",
            generation_instructions="Generate responses"
        )
        
        # Set mock session history
        agent.llm_pipeline.session_history = ["User: input", "Assistant: response"]
        
        history = agent.get_session_history()
        assert history == ["User: input", "Assistant: response"]

    def test_update_instructions(self):
        """Test updating pipeline instructions"""
        agent = GenAgent(
            name="update_agent",
            generation_instructions="Original generation",
            evaluation_instructions="Original evaluation"
        )
        
        with patch.object(agent.llm_pipeline, 'update_instructions') as mock_update:
            agent.update_instructions(
                generation_instructions="New generation",
                evaluation_instructions="New evaluation"
            )
            
            mock_update.assert_called_once_with("New generation", "New evaluation")

    def test_clear_history(self):
        """Test clearing pipeline history"""
        agent = GenAgent(
            name="clear_agent",
            generation_instructions="Generate responses"
        )
        
        with patch.object(agent.llm_pipeline, 'clear_history') as mock_clear:
            agent.clear_history()
            mock_clear.assert_called_once()

    def test_set_threshold(self):
        """Test setting evaluation threshold"""
        agent = GenAgent(
            name="threshold_agent",
            generation_instructions="Generate responses"
        )
        
        with patch.object(agent.llm_pipeline, 'set_threshold') as mock_set:
            agent.set_threshold(90.0)
            mock_set.assert_called_once_with(90.0)

    def test_str_and_repr(self):
        """Test string representations"""
        agent = GenAgent(
            name="repr_agent",
            generation_instructions="Test instructions",
            model="gpt-4o-mini"
        )
        
        str_repr = str(agent)
        assert "GenAgent" in str_repr
        assert "repr_agent" in str_repr
        assert "gpt-4o-mini" in str_repr
        assert str(agent) == repr(agent)

    def test_create_simple_gen_agent(self):
        """Test utility function for creating simple GenAgent"""
        agent = create_simple_gen_agent(
            name="simple_test",
            instructions="Simple instructions",
            model="gpt-3.5-turbo",
            next_step="next_step",
            threshold=80.0,
            retries=2
        )
        
        assert isinstance(agent, GenAgent)
        assert agent.name == "simple_test"
        assert agent.llm_pipeline.generation_instructions == "Simple instructions"
        assert agent.llm_pipeline.model == "gpt-3.5-turbo"
        assert agent.next_step == "next_step"
        assert agent.llm_pipeline.threshold == 80.0
        assert agent.llm_pipeline.max_retries == 2

    def test_create_evaluated_gen_agent(self):
        """Test utility function for creating evaluated GenAgent"""
        agent = create_evaluated_gen_agent(
            name="evaluated_test",
            generation_instructions="Generation instructions",
            evaluation_instructions="Evaluation instructions",
            model="gpt-4",
            evaluation_model="gpt-4-turbo",
            next_step="eval_next",
            threshold=90.0,
            retries=3
        )
        
        assert isinstance(agent, GenAgent)
        assert agent.name == "evaluated_test"
        assert agent.llm_pipeline.generation_instructions == "Generation instructions"
        assert agent.llm_pipeline.evaluation_instructions == "Evaluation instructions"
        assert agent.llm_pipeline.model == "gpt-4"
        assert agent.llm_pipeline.evaluation_model == "gpt-4-turbo"
        assert agent.next_step == "eval_next"
        assert agent.llm_pipeline.threshold == 90.0
        assert agent.llm_pipeline.max_retries == 3

    @pytest.mark.asyncio
    async def test_integration_with_flow_context(self):
        """Test integration with Flow context sharing"""
        # Create multiple agents that share context
        agent1 = GenAgent(
            name="agent1",
            generation_instructions="Process input",
            next_step="agent2"
        )
        
        agent2 = GenAgent(
            name="agent2", 
            generation_instructions="Process result from agent1"
        )
        
        # Mock results
        mock_result1 = LLMResult(content="Result from agent1", success=True)
        mock_result2 = LLMResult(content="Result from agent2", success=True)
        
        with patch.object(agent1.llm_pipeline, 'run', return_value=mock_result1), \
             patch.object(agent2.llm_pipeline, 'run', return_value=mock_result2):
            
            # Run first agent
            ctx = Context()
            ctx = await agent1.run("Initial input", ctx)
            
            # Verify first agent's results
            assert ctx.shared_state["agent1_result"] == "Result from agent1"
            assert ctx.next_label == "agent2"
            
            # Run second agent (simulating Flow execution)
            ctx.current_step = "agent2"
            ctx.next_label = None
            # Set some context input for agent2 to process
            ctx.last_user_input = "Process the result from agent1"
            ctx = await agent2.run(None, ctx)  # No new input, uses context
            
            # Verify second agent's results
            assert ctx.shared_state["agent2_result"] == "Result from agent2"
            assert ctx.prev_outputs["agent1"] == "Result from agent1"
            assert ctx.prev_outputs["agent2"] == "Result from agent2" 
