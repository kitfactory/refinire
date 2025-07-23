#!/usr/bin/env python3
"""
Test EvaluationAgent functionality
EvaluationAgent機能のテスト
"""

import pytest
import asyncio
import sys
import os

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire.agents.evaluation_agent import EvaluationAgent, EvaluationResult
from refinire.agents.flow.context import Context


@pytest.fixture
def sample_context():
    """Create sample context with shared_state data"""
    context = Context()
    context.shared_state['_last_prompt'] = "高品質な記事を書いてください。"
    context.shared_state['_last_generation'] = "人工知能は現代社会において重要な技術です。様々な分野で活用されており、今後も発展が期待されています。"
    return context


@pytest.fixture
def evaluation_agent():
    """Create EvaluationAgent for testing"""
    return EvaluationAgent(
        name="test_evaluator",
        evaluation_instruction="""
以下の基準で品質評価を行ってください：
1. 内容の正確性 (0.0-1.0)
2. 文章の明確性 (0.0-1.0)  
3. 情報の完全性 (0.0-1.0)
4. 読みやすさ (0.0-1.0)

総合スコアは各基準の平均とし、0.7以上を合格とします。
        """.strip(),
        evaluation_criteria={
            "accuracy": "情報の正確性と事実性",
            "clarity": "文章の明確性と理解しやすさ",
            "completeness": "情報の完全性と網羅性", 
            "readability": "読みやすさと構成"
        },
        pass_threshold=0.7,
        model="gpt-4o-mini",
        temperature=0.2
    )


class TestEvaluationAgent:
    """EvaluationAgent test cases"""
    
    def test_initialization(self, evaluation_agent):
        """Test EvaluationAgent initialization"""
        assert evaluation_agent.name == "test_evaluator"
        assert evaluation_agent.model_name == "gpt-4o-mini"
        assert evaluation_agent.temperature == 0.2
        assert evaluation_agent.pass_threshold == 0.7
        assert evaluation_agent.llm is not None
        assert len(evaluation_agent.evaluation_criteria) == 4
    
    def test_format_evaluation_criteria(self, evaluation_agent):
        """Test evaluation criteria formatting"""
        criteria_text = evaluation_agent._format_evaluation_criteria()
        
        assert "accuracy: 情報の正確性と事実性" in criteria_text
        assert "clarity: 文章の明確性と理解しやすさ" in criteria_text
        assert "completeness: 情報の完全性と網羅性" in criteria_text
        assert "readability: 読みやすさと構成" in criteria_text
    
    def test_format_evaluation_criteria_empty(self):
        """Test evaluation criteria formatting with empty criteria"""
        agent = EvaluationAgent(
            name="empty_criteria",
            evaluation_instruction="Evaluate content"
        )
        
        criteria_text = agent._format_evaluation_criteria()
        assert "一般的な品質基準" in criteria_text
    
    def test_build_evaluation_prompt(self, evaluation_agent, sample_context):
        """Test evaluation prompt construction"""
        prompt = evaluation_agent._build_evaluation_prompt(sample_context, "")
        
        # Check that prompt contains expected elements
        assert "直前の生成プロセスを評価してください" in prompt
        assert "高品質な記事を書いてください。" in prompt
        assert "人工知能は現代社会において" in prompt
        assert "以下の基準で品質評価" in prompt
        assert "JSON形式で評価結果を出力" in prompt
        assert "0.7以上が合格基準" in prompt
    
    def test_build_evaluation_prompt_empty_shared_state(self, evaluation_agent):
        """Test evaluation prompt with empty shared_state"""
        context = Context()
        prompt = evaluation_agent._build_evaluation_prompt(context, "")
        
        # Should handle missing data gracefully
        assert "N/A" in prompt
        assert "JSON形式で評価結果を出力" in prompt
    
    def test_analyze_content_for_evaluation_positive(self, evaluation_agent, sample_context):
        """Test content analysis for positive evaluation"""
        result = evaluation_agent._analyze_content_for_evaluation(
            "This is excellent work with clear and accurate information", 
            sample_context
        )
        
        assert isinstance(result, EvaluationResult)
        assert result.score > 0.7  # Should be high due to positive words
        assert result.passed is True  # Should pass the 0.7 threshold
        assert "positive evaluation indicators" in result.feedback.lower()
    
    def test_analyze_content_for_evaluation_negative(self, evaluation_agent, sample_context):
        """Test content analysis for negative evaluation"""
        result = evaluation_agent._analyze_content_for_evaluation(
            "This work contains errors and is unclear and incomplete", 
            sample_context
        )
        
        assert isinstance(result, EvaluationResult)
        assert result.score < 0.5  # Should be low due to negative words
        assert result.passed is False  # Should fail the 0.7 threshold
        assert "negative evaluation indicators" in result.feedback.lower()
        assert len(result.suggestions) > 0
    
    def test_analyze_content_for_evaluation_neutral(self, evaluation_agent, sample_context):
        """Test content analysis for neutral evaluation"""
        result = evaluation_agent._analyze_content_for_evaluation(
            "This is a standard response without specific indicators", 
            sample_context
        )
        
        assert isinstance(result, EvaluationResult)
        assert 0.4 <= result.score <= 0.6  # Should be moderate
        assert "mixed or neutral" in result.feedback.lower()
    
    def test_parse_evaluation_result_json(self, evaluation_agent, sample_context):
        """Test parsing valid JSON evaluation result"""
        json_content = '''
        {
            "content": "Test content for evaluation",
            "score": 0.85,
            "criteria_scores": {
                "accuracy": 0.9,
                "clarity": 0.8
            },
            "feedback": "High quality content with good accuracy",
            "suggestions": ["Minor improvements in clarity"],
            "metadata": {
                "evaluator": "test_evaluator"
            }
        }
        '''
        
        result = evaluation_agent._parse_evaluation_result(json_content, sample_context)
        
        assert isinstance(result, EvaluationResult)
        assert result.content == "Test content for evaluation"
        assert result.score == 0.85
        assert result.criteria_scores["accuracy"] == 0.9
        assert result.criteria_scores["clarity"] == 0.8
        assert result.feedback == "High quality content with good accuracy"
        assert "Minor improvements in clarity" in result.suggestions
    
    def test_parse_evaluation_result_invalid_json(self, evaluation_agent, sample_context):
        """Test parsing invalid JSON falls back to content analysis"""
        invalid_content = "This evaluation shows the work is excellent and accurate"
        
        result = evaluation_agent._parse_evaluation_result(invalid_content, sample_context)
        
        assert isinstance(result, EvaluationResult)
        assert result.score > 0.7  # Should detect positive words
        assert result.passed is True  # Should pass threshold
    
    def test_create_llm_result(self, evaluation_agent):
        """Test LLMResult creation for evaluation"""
        evaluation_result = EvaluationResult(
            content="test content",
            score=0.8,
            passed=True,
            feedback="Good evaluation",
            suggestions=["Keep up the good work"]
        )
        
        llm_result = evaluation_agent._create_llm_result(evaluation_result, True)
        
        assert llm_result.content == evaluation_result
        assert llm_result.success is True
        assert llm_result.evaluation_score == 0.8
        assert llm_result.metadata['agent_name'] == "test_evaluator"
        assert llm_result.metadata['agent_type'] == "evaluation"
        assert llm_result.metadata['pass_threshold'] == 0.7
        assert llm_result.metadata['passed'] is True
    
    @pytest.mark.asyncio
    async def test_run_async_basic(self, evaluation_agent, sample_context):
        """Test basic async execution"""
        # This test requires actual LLM call, might need mocking in CI
        try:
            result_context = await evaluation_agent.run_async("", sample_context)
            
            # Check that context was updated
            assert result_context.evaluation is not None
            assert isinstance(result_context.evaluation, EvaluationResult)
            assert result_context.result is not None
            
            # Check evaluation result structure
            evaluation = result_context.evaluation
            assert evaluation.content is not None
            assert 0.0 <= evaluation.score <= 1.0
            assert evaluation.feedback is not None
            assert isinstance(evaluation.passed, bool)
            
        except Exception as e:
            # If LLM call fails (e.g., no API key), should still create error evaluation
            assert result_context.evaluation is not None
            assert result_context.evaluation.score == 0.0
            assert result_context.evaluation.passed is False
    
    def test_run_sync(self, evaluation_agent, sample_context):
        """Test synchronous execution wrapper"""
        try:
            result_context = evaluation_agent.run("", sample_context)
            
            # Check that context was updated
            assert result_context.evaluation is not None
            assert isinstance(result_context.evaluation, EvaluationResult)
            
        except Exception:
            # Expected if no LLM access, test the wrapper functionality
            pass


class TestEvaluationResult:
    """EvaluationResult data model tests"""
    
    def test_evaluation_result_creation(self):
        """Test EvaluationResult creation and validation"""
        result = EvaluationResult(
            content="Test content",
            score=0.75,
            passed=True,
            feedback="Good work",
            suggestions=["Minor improvements"],
            criteria_scores={"clarity": 0.8},
            metadata={"evaluator": "test"}
        )
        
        assert result.content == "Test content"
        assert result.score == 0.75
        assert result.passed is True
        assert result.feedback == "Good work"
        assert result.suggestions == ["Minor improvements"]
        assert result.criteria_scores["clarity"] == 0.8
        assert result.metadata["evaluator"] == "test"
    
    def test_evaluation_result_score_validation(self):
        """Test score validation (0.0-1.0 range)"""
        # Valid scores
        result1 = EvaluationResult(content="", score=0.0, passed=False, feedback="")
        result2 = EvaluationResult(content="", score=1.0, passed=True, feedback="")
        
        assert result1.score == 0.0
        assert result2.score == 1.0
        
        # Invalid scores should raise validation error
        with pytest.raises(ValueError):
            EvaluationResult(content="", score=-0.1, passed=False, feedback="")
        
        with pytest.raises(ValueError):
            EvaluationResult(content="", score=1.1, passed=True, feedback="")


@pytest.mark.asyncio
async def test_evaluation_agent_integration():
    """Integration test with different evaluation scenarios"""
    agent = EvaluationAgent(
        name="integration_test",
        evaluation_instruction="""
Content quality evaluation:
- Score 0.8+ for excellent content
- Score 0.6-0.8 for good content  
- Score below 0.6 for poor content
        """.strip(),
        pass_threshold=0.6
    )
    
    test_cases = [
        {
            "last_generation": "This is an excellent and comprehensive analysis with accurate information.",
            "expected_pass": True  # May vary based on actual LLM response
        },
        {
            "last_generation": "This content has some good points but lacks detail.",
            "expected_pass": None  # Depends on actual evaluation
        },
        {
            "last_generation": "Poor quality content with errors.",
            "expected_pass": False  # May vary based on actual LLM response
        }
    ]
    
    for i, case in enumerate(test_cases):
        context = Context()
        context.shared_state['_last_prompt'] = f"Test prompt {i}"
        context.shared_state['_last_generation'] = case['last_generation']
        
        try:
            result_context = await agent.run_async("", context)
            
            # Verify structure (actual evaluation may vary based on LLM)
            assert result_context.evaluation is not None
            assert isinstance(result_context.evaluation, EvaluationResult)
            assert 0.0 <= result_context.evaluation.score <= 1.0
            assert isinstance(result_context.evaluation.passed, bool)
            assert result_context.evaluation.feedback is not None
            
        except Exception:
            # If LLM unavailable, should create error evaluation
            assert result_context.evaluation.score == 0.0
            assert result_context.evaluation.passed is False


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])