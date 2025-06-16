#!/usr/bin/env python3
"""
Test AgentPipeline implementation (deprecated).

非推奨のAgentPipelineの実装をテストします。
"""

import pytest
import warnings
from unittest.mock import Mock, patch, MagicMock

from refinire.agents.pipeline.pipeline import (
    AgentPipeline, EvaluationResult, Comment, CommentImportance
)


class TestComment:
    """Test cases for Comment class."""
    
    def test_comment_creation(self):
        """Test Comment creation."""
        comment = Comment(
            importance=CommentImportance.SERIOUS,
            content="This is a serious comment"
        )
        
        assert comment.importance == CommentImportance.SERIOUS
        assert comment.content == "This is a serious comment"
    
    def test_comment_importance_levels(self):
        """Test CommentImportance enum values."""
        assert CommentImportance.SERIOUS.value == "serious"
        assert CommentImportance.NORMAL.value == "normal"
        assert CommentImportance.MINOR.value == "minor"


class TestEvaluationResult:
    """Test cases for EvaluationResult class."""
    
    def test_evaluation_result_creation(self):
        """Test EvaluationResult creation."""
        comments = [
            Comment(CommentImportance.SERIOUS, "Serious issue"),
            Comment(CommentImportance.NORMAL, "Normal comment")
        ]
        
        result = EvaluationResult(score=85, comment=comments)
        
        assert result.score == 85
        assert len(result.comment) == 2
        assert result.comment[0].importance == CommentImportance.SERIOUS
        assert result.comment[1].importance == CommentImportance.NORMAL


class TestAgentPipeline:
    """Test cases for AgentPipeline class."""
    
    def test_agent_pipeline_initialization(self):
        """Test AgentPipeline initialization."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            pipeline = AgentPipeline(
                name="test_pipeline",
                generation_instructions="Generate content",
                evaluation_instructions="Evaluate content",
                threshold=80,
                retries=2
            )
            
            assert pipeline.name == "test_pipeline"
            assert pipeline.generation_instructions == "Generate content"
            assert pipeline.evaluation_instructions == "Evaluate content"
            assert pipeline.threshold == 80
            assert pipeline.retries == 2
    
    def test_agent_pipeline_deprecated_warning(self):
        """Test that AgentPipeline shows deprecation warning."""
        with pytest.warns(DeprecationWarning, match="AgentPipeline is deprecated"):
            AgentPipeline(
                name="test",
                generation_instructions="Generate",
                evaluation_instructions="Evaluate"
            )
    
    def test_agent_pipeline_with_optional_evaluation(self):
        """Test AgentPipeline with None evaluation instructions."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            pipeline = AgentPipeline(
                name="test_pipeline",
                generation_instructions="Generate content",
                evaluation_instructions=None
            )
            
            assert pipeline.evaluation_instructions is None
    
    def test_agent_pipeline_with_guardrails(self):
        """Test AgentPipeline with guardrails."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            input_guardrails = [lambda x: True]
            output_guardrails = [lambda x: True]
            
            pipeline = AgentPipeline(
                name="test_pipeline",
                generation_instructions="Generate content",
                evaluation_instructions="Evaluate content",
                input_guardrails=input_guardrails,
                output_guardrails=output_guardrails
            )
            
            assert pipeline.input_guardrails == input_guardrails
            assert pipeline.output_guardrails == output_guardrails
    
    def test_agent_pipeline_with_tools(self):
        """Test AgentPipeline with tools."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            generation_tools = [{"name": "gen_tool"}]
            evaluation_tools = [{"name": "eval_tool"}]
            
            pipeline = AgentPipeline(
                name="test_pipeline",
                generation_instructions="Generate content",
                evaluation_instructions="Evaluate content",
                generation_tools=generation_tools,
                evaluation_tools=evaluation_tools
            )
            
            assert pipeline.generation_tools == generation_tools
            assert pipeline.evaluation_tools == evaluation_tools
    
    def test_agent_pipeline_with_callbacks(self):
        """Test AgentPipeline with callbacks."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            routing_func = Mock()
            improvement_callback = Mock()
            dynamic_prompt = Mock()
            
            pipeline = AgentPipeline(
                name="test_pipeline",
                generation_instructions="Generate content",
                evaluation_instructions="Evaluate content",
                routing_func=routing_func,
                improvement_callback=improvement_callback,
                dynamic_prompt=dynamic_prompt
            )
            
            assert pipeline.routing_func == routing_func
            assert pipeline.improvement_callback == improvement_callback
            assert pipeline.dynamic_prompt == dynamic_prompt
    
    def test_agent_pipeline_with_session_history(self):
        """Test AgentPipeline with session history."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            history = ["previous interaction"]
            
            pipeline = AgentPipeline(
                name="test_pipeline",
                generation_instructions="Generate content",
                evaluation_instructions="Evaluate content",
                session_history=history,
                history_size=5
            )
            
            assert pipeline.session_history == history
            assert pipeline.history_size == 5
    
    def test_agent_pipeline_locale_settings(self):
        """Test AgentPipeline locale settings."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            pipeline = AgentPipeline(
                name="test_pipeline",
                generation_instructions="Generate content",
                evaluation_instructions="Evaluate content",
                locale="ja"
            )
            
            assert pipeline.locale == "ja"
    
    def test_agent_pipeline_retry_settings(self):
        """Test AgentPipeline retry settings."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            retry_comment_importance = ["serious", "normal"]
            
            pipeline = AgentPipeline(
                name="test_pipeline",
                generation_instructions="Generate content",
                evaluation_instructions="Evaluate content",
                retry_comment_importance=retry_comment_importance
            )
            
            assert pipeline.retry_comment_importance == retry_comment_importance
    
    def test_agent_pipeline_model_settings(self):
        """Test AgentPipeline model settings."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            pipeline = AgentPipeline(
                name="test_pipeline",
                generation_instructions="Generate content",
                evaluation_instructions="Evaluate content",
                model="gpt-4",
                evaluation_model="gpt-3.5-turbo"
            )
            
            assert pipeline.model == "gpt-4"
            assert pipeline.evaluation_model == "gpt-3.5-turbo"
    
    @patch('refinire.agents.pipeline.pipeline.BaseModel')
    def test_agent_pipeline_with_output_model(self, mock_base_model):
        """Test AgentPipeline with output model."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            output_model = mock_base_model
            
            pipeline = AgentPipeline(
                name="test_pipeline",
                generation_instructions="Generate content",
                evaluation_instructions="Evaluate content",
                output_model=output_model
            )
            
            assert pipeline.output_model == output_model
    
    def test_agent_pipeline_string_stripping(self):
        """Test that AgentPipeline strips whitespace from instructions."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            pipeline = AgentPipeline(
                name="test_pipeline",
                generation_instructions="  Generate content  ",
                evaluation_instructions="  Evaluate content  "
            )
            
            assert pipeline.generation_instructions == "Generate content"
            assert pipeline.evaluation_instructions == "Evaluate content"


class TestAgentPipelineDeprecation:
    """Test AgentPipeline deprecation behavior."""
    
    def test_deprecation_warning_message(self):
        """Test deprecation warning message content."""
        with pytest.warns(DeprecationWarning) as warning_info:
            AgentPipeline(
                name="test",
                generation_instructions="Generate",
                evaluation_instructions="Evaluate"
            )
        
        warning_message = str(warning_info[0].message)
        assert "AgentPipeline is deprecated" in warning_message
        assert "GenAgent" in warning_message
        assert "Flow/Step architecture" in warning_message
        assert "docs/deprecation_plan.md" in warning_message
    
    def test_deprecation_warning_can_be_suppressed(self):
        """Test that deprecation warning can be suppressed."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            
            # This should not raise any warnings
            pipeline = AgentPipeline(
                name="test",
                generation_instructions="Generate",
                evaluation_instructions="Evaluate"
            )
            
            assert pipeline.name == "test"


class TestCommentImportanceEnum:
    """Test CommentImportance enum."""
    
    def test_all_importance_levels(self):
        """Test all CommentImportance levels."""
        assert len(CommentImportance) == 3
        
        levels = [importance.value for importance in CommentImportance]
        assert "serious" in levels
        assert "normal" in levels
        assert "minor" in levels
    
    def test_importance_enum_comparison(self):
        """Test CommentImportance enum comparison."""
        serious1 = CommentImportance.SERIOUS
        serious2 = CommentImportance.SERIOUS
        normal = CommentImportance.NORMAL
        
        assert serious1 == serious2
        assert serious1 != normal