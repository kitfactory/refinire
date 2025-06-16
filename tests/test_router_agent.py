"""
Tests for RouterAgent functionality.

RouterAgent機能のテスト。
"""

import pytest
from unittest.mock import Mock, patch
from typing import Any, Dict

from refinire.agents.router import (
    RouterAgent,
    RouterConfig,
    LLMClassifier,
    RuleBasedClassifier,
    RouteClassifier,
    create_intent_router,
    create_content_type_router
)
from refinire import Context, RefinireAgent


class TestRouteClassifier:
    """Test the abstract RouteClassifier and its implementations."""
    
    def test_route_classifier_is_abstract(self):
        """Test that RouteClassifier cannot be instantiated directly."""
        with pytest.raises(TypeError):
            RouteClassifier()


class TestLLMClassifier:
    """Test LLM-based classification functionality."""
    
    @pytest.fixture
    def mock_pipeline(self):
        """Create a mock LLM pipeline."""
        pipeline = Mock(spec=RefinireAgent)
        return pipeline
    
    @pytest.fixture
    def classifier(self, mock_pipeline):
        """Create an LLM classifier instance."""
        return LLMClassifier(
            pipeline=mock_pipeline,
            classification_prompt="Classify the input",
            routes=["route1", "route2", "route3"],
            examples={
                "route1": ["example 1", "example 2"],
                "route2": ["example 3", "example 4"]
            }
        )
    
    def test_classifier_initialization(self, classifier, mock_pipeline):
        """Test classifier initialization."""
        assert classifier.pipeline == mock_pipeline
        assert classifier.classification_prompt == "Classify the input"
        assert classifier.routes == ["route1", "route2", "route3"]
        assert "route1" in classifier.examples
        assert "route2" in classifier.examples
    
    def test_classify_exact_match(self, classifier, mock_pipeline):
        """Test classification with exact route match."""
        mock_pipeline.run.return_value = "route2"
        context = Context()
        
        result = classifier.classify("test input", context)
        
        assert result == "route2"
        mock_pipeline.run.assert_called_once()
        
        # Check that the prompt contains expected elements
        call_args = mock_pipeline.run.call_args[0]
        prompt = call_args[0]
        assert "Classify the input" in prompt
        assert "route1, route2, route3" in prompt
        assert "test input" in prompt
        assert "example 1" in prompt  # Examples should be included
    
    def test_classify_case_insensitive_match(self, classifier, mock_pipeline):
        """Test classification with case insensitive matching."""
        mock_pipeline.run.return_value = "ROUTE2"
        context = Context()
        
        result = classifier.classify("test input", context)
        
        assert result == "route2"
    
    def test_classify_partial_match(self, classifier, mock_pipeline):
        """Test classification with partial matching."""
        mock_pipeline.run.return_value = "I think it's route2 based on analysis"
        context = Context()
        
        result = classifier.classify("test input", context)
        
        assert result == "route2"
    
    def test_classify_no_match_fallback(self, classifier, mock_pipeline):
        """Test classification fallback when no match found."""
        mock_pipeline.run.return_value = "unknown_route"
        context = Context()
        
        result = classifier.classify("test input", context)
        
        assert result is None  # None for RouterAgent to handle fallback
    
    def test_classify_error_fallback(self, classifier, mock_pipeline):
        """Test classification fallback when error occurs."""
        mock_pipeline.run.side_effect = Exception("LLM error")
        context = Context()
        
        result = classifier.classify("test input", context)
        
        assert result is None  # None for RouterAgent to handle fallback
    
    def test_classify_without_examples(self, mock_pipeline):
        """Test classification without examples."""
        classifier = LLMClassifier(
            pipeline=mock_pipeline,
            classification_prompt="Classify the input",
            routes=["route1", "route2"]
        )
        
        mock_pipeline.run.return_value = "route1"
        context = Context()
        
        result = classifier.classify("test input", context)
        
        assert result == "route1"
        
        # Check that prompt doesn't contain examples section
        call_args = mock_pipeline.run.call_args[0]
        prompt = call_args[0]
        assert "Examples:\n" not in prompt


class TestRuleBasedClassifier:
    """Test rule-based classification functionality."""
    
    def test_rule_based_classifier_initialization(self):
        """Test rule-based classifier initialization."""
        rules = {
            "route1": lambda x, ctx: "test" in str(x),
            "route2": lambda x, ctx: len(str(x)) > 10
        }
        
        classifier = RuleBasedClassifier(rules)
        assert classifier.rules == rules
    
    def test_classify_first_matching_rule(self):
        """Test classification returns first matching rule."""
        rules = {
            "route1": lambda x, ctx: "hello" in str(x),
            "route2": lambda x, ctx: "world" in str(x),
            "route3": lambda x, ctx: True  # Always matches
        }
        
        classifier = RuleBasedClassifier(rules)
        context = Context()
        
        result = classifier.classify("hello world", context)
        
        assert result == "route1"  # First matching rule
    
    def test_classify_no_rules_match(self):
        """Test classification when no rules match."""
        rules = {
            "route1": lambda x, ctx: False,
            "route2": lambda x, ctx: False
        }
        
        classifier = RuleBasedClassifier(rules)
        context = Context()
        
        result = classifier.classify("test input", context)
        
        assert result == "route1"  # First route as fallback
    
    def test_classify_rule_error_continues(self):
        """Test classification continues when a rule throws error."""
        def error_rule(x, ctx):
            raise ValueError("Rule error")
        
        rules = {
            "route1": error_rule,
            "route2": lambda x, ctx: True
        }
        
        classifier = RuleBasedClassifier(rules)
        context = Context()
        
        result = classifier.classify("test input", context)
        
        assert result == "route2"  # Second rule should work
    
    def test_classify_all_rules_error(self):
        """Test classification when all rules throw errors."""
        def error_rule(x, ctx):
            raise ValueError("Rule error")
        
        rules = {
            "route1": error_rule,
            "route2": error_rule
        }
        
        classifier = RuleBasedClassifier(rules)
        context = Context()
        
        result = classifier.classify("test input", context)
        
        assert result == "route1"  # First route as fallback


class TestRouterConfig:
    """Test RouterConfig validation and configuration."""
    
    def test_valid_config(self):
        """Test valid router configuration."""
        config = RouterConfig(
            name="test_router",
            routes={"route1": "step1", "route2": "step2"},
            classifier_type="llm"
        )
        
        assert config.name == "test_router"
        assert config.routes == {"route1": "step1", "route2": "step2"}
        assert config.classifier_type == "llm"
    
    def test_empty_routes_validation(self):
        """Test validation fails with empty routes."""
        with pytest.raises(ValueError, match="Routes cannot be empty"):
            RouterConfig(
                name="test_router",
                routes={},
                classifier_type="llm"
            )
    
    def test_invalid_default_route(self):
        """Test validation fails with invalid default route."""
        with pytest.raises(ValueError, match="Default route .* must exist in routes"):
            RouterConfig(
                name="test_router",
                routes={"route1": "step1"},
                classifier_type="llm",
                default_route="invalid_route"
            )
    
    def test_valid_default_route(self):
        """Test validation passes with valid default route."""
        config = RouterConfig(
            name="test_router",
            routes={"route1": "step1", "route2": "step2"},
            classifier_type="llm",
            default_route="route1"
        )
        
        assert config.default_route == "route1"


class TestRouterAgent:
    """Test RouterAgent functionality."""
    
    @pytest.fixture
    def mock_pipeline(self):
        """Create a mock LLM pipeline."""
        pipeline = Mock(spec=RefinireAgent)
        return pipeline
    
    @pytest.fixture
    def llm_config(self):
        """Create LLM-based router configuration."""
        return RouterConfig(
            name="test_router",
            routes={"route1": "step1", "route2": "step2"},
            classifier_type="llm",
            classification_prompt="Classify this input"
        )
    
    @pytest.fixture
    def rule_config(self):
        """Create rule-based router configuration."""
        return RouterConfig(
            name="test_router",
            routes={"route1": "step1", "route2": "step2"},
            classifier_type="rule",
            classification_rules={
                "route1": lambda x, ctx: "first" in str(x),
                "route2": lambda x, ctx: "second" in str(x)
            }
        )
    
    def test_llm_router_initialization(self, llm_config, mock_pipeline):
        """Test LLM router initialization."""
        router = RouterAgent(llm_config, mock_pipeline)
        
        assert router.name == "test_router"
        assert router.config == llm_config
        assert isinstance(router.classifier, LLMClassifier)
    
    def test_llm_router_without_pipeline_creates_default(self, llm_config):
        """Test LLM router creates default pipeline if none provided."""
        with patch('refinire.agents.router.create_simple_agent') as mock_create:
            mock_pipeline = Mock(spec=RefinireAgent)
            mock_create.return_value = mock_pipeline
            
            router = RouterAgent(llm_config)
            
            mock_create.assert_called_once()
            assert isinstance(router.classifier, LLMClassifier)
    
    def test_rule_router_initialization(self, rule_config):
        """Test rule-based router initialization."""
        router = RouterAgent(rule_config)
        
        assert router.name == "test_router"
        assert router.config == rule_config
        assert isinstance(router.classifier, RuleBasedClassifier)
    
    def test_rule_router_without_rules_fails(self):
        """Test rule-based router fails without rules."""
        config = RouterConfig(
            name="test_router",
            routes={"route1": "step1"},
            classifier_type="rule"
        )
        
        with pytest.raises(ValueError, match="classification_rules must be provided"):
            RouterAgent(config)
    
    def test_invalid_classifier_type_fails(self):
        """Test router fails with invalid classifier type."""
        with pytest.raises(ValueError, match="Input should be 'llm' or 'rule'"):
            RouterConfig(
                name="test_router",
                routes={"route1": "step1"},
                classifier_type="invalid"
            )
    
    @pytest.mark.asyncio
    async def test_router_run_successful_classification(self, llm_config, mock_pipeline):
        """Test successful routing execution."""
        mock_pipeline.run.return_value = "route2"
        router = RouterAgent(llm_config, mock_pipeline)
        context = Context()
        
        result = await router.run("test input", context)
        
        assert isinstance(result, Context)  # Router now returns Context
        assert result.shared_state.get("test_router_classification") == "route2"
        assert result.shared_state.get("test_router_next_step") == "step2"
        assert result.next_label == "step2"
    
    @pytest.mark.asyncio
    async def test_router_run_with_invalid_route(self, llm_config, mock_pipeline):
        """Test routing with invalid route falls back to default."""
        mock_pipeline.run.return_value = "invalid_route"
        router = RouterAgent(llm_config, mock_pipeline)
        context = Context()
        
        result = await router.run("test input", context)
        
        assert isinstance(result, Context)
        assert result.next_label == "step1"  # First route as fallback
    
    @pytest.mark.asyncio
    async def test_router_run_classification_error(self, llm_config, mock_pipeline):
        """Test routing handles classification errors gracefully."""
        mock_pipeline.run.side_effect = Exception("Classification error")
        router = RouterAgent(llm_config, mock_pipeline)
        context = Context()
        
        result = await router.run("test input", context)
        
        assert isinstance(result, Context)
        assert result.next_label == "step1"  # Fallback route
        assert result.shared_state.get("test_router_classification") == "route1"
        assert "classification failed" in result.shared_state.get("test_router_error", "").lower()
    
    @pytest.mark.asyncio
    async def test_router_run_without_storing_results(self, llm_config, mock_pipeline):
        """Test routing without storing classification results."""
        llm_config.store_classification_result = False
        mock_pipeline.run.return_value = "route2"
        router = RouterAgent(llm_config, mock_pipeline)
        context = Context()
        
        result = await router.run("test input", context)
        
        assert isinstance(result, Context)
        assert result.next_label == "step2"
        assert result.shared_state.get("test_router_classification") is None
        assert result.shared_state.get("test_router_next_step") is None
    
    @pytest.mark.asyncio
    async def test_router_run_with_default_route(self, mock_pipeline):
        """Test routing with configured default route."""
        config = RouterConfig(
            name="test_router",
            routes={"route1": "step1", "route2": "step2"},
            classifier_type="llm",
            default_route="route2"
        )
        
        mock_pipeline.run.return_value = "invalid_route"
        router = RouterAgent(config, mock_pipeline)
        context = Context()
        
        result = await router.run("test input", context)
        
        assert isinstance(result, Context)
        assert result.next_label == "step2"  # Default route


class TestUtilityFunctions:
    """Test utility functions for creating common routers."""
    
    @patch('refinire.agents.router.create_simple_agent')
    def test_create_intent_router_defaults(self, mock_create_pipeline):
        """Test creating intent router with defaults."""
        mock_pipeline = Mock(spec=RefinireAgent)
        mock_create_pipeline.return_value = mock_pipeline
        
        router = create_intent_router()
        
        assert router.name == "intent_router"
        assert "question" in router.config.routes
        assert "request" in router.config.routes
        assert "complaint" in router.config.routes
        assert "other" in router.config.routes
        assert router.config.classifier_type == "llm"
    
    def test_create_intent_router_custom(self):
        """Test creating intent router with custom parameters."""
        custom_intents = {"intent1": "step1", "intent2": "step2"}
        mock_pipeline = Mock(spec=RefinireAgent)
        
        router = create_intent_router(
            name="custom_router",
            intents=custom_intents,
            llm_pipeline=mock_pipeline
        )
        
        assert router.name == "custom_router"
        assert router.config.routes == custom_intents
    
    @patch('refinire.agents.router.create_simple_agent')
    def test_create_content_type_router_defaults(self, mock_create_pipeline):
        """Test creating content type router with defaults."""
        mock_pipeline = Mock(spec=RefinireAgent)
        mock_create_pipeline.return_value = mock_pipeline
        
        router = create_content_type_router()
        
        assert router.name == "content_router"
        assert "document" in router.config.routes
        assert "image" in router.config.routes
        assert "code" in router.config.routes
        assert "data" in router.config.routes
        assert router.config.classifier_type == "llm"
    
    def test_create_content_type_router_custom(self):
        """Test creating content type router with custom parameters."""
        custom_types = {"type1": "processor1", "type2": "processor2"}
        mock_pipeline = Mock(spec=RefinireAgent)
        
        router = create_content_type_router(
            name="custom_content_router",
            content_types=custom_types,
            llm_pipeline=mock_pipeline
        )
        
        assert router.name == "custom_content_router"
        assert router.config.routes == custom_types
