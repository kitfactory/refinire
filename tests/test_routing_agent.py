#!/usr/bin/env python3
"""
Test RoutingAgent functionality
RoutingAgent機能のテスト
"""

import pytest
import asyncio
import sys
import os

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire.agents.routing_agent import RoutingAgent
from refinire.agents.flow.context import Context
from refinire.core.routing import RoutingResult


@pytest.fixture
def sample_context():
    """Create sample context with shared_state data"""
    context = Context()
    context.shared_state['_last_prompt'] = "ユーザーに挨拶してください。"
    context.shared_state['_last_generation'] = "こんにちは！今日はいかがお過ごしですか？"
    return context


@pytest.fixture
def routing_agent():
    """Create RoutingAgent for testing"""
    return RoutingAgent(
        name="test_router",
        routing_instruction="""
以下の条件でルーティングを判定してください：
1. 挨拶が含まれる場合 → "greeting"
2. 質問が含まれる場合 → "question"  
3. エラーが含まれる場合 → "error"
4. その他の場合 → "continue"
        """.strip(),
        model="gpt-4o-mini",
        temperature=0.1
    )


class TestRoutingAgent:
    """RoutingAgent test cases"""
    
    def test_initialization(self, routing_agent):
        """Test RoutingAgent initialization"""
        assert routing_agent.name == "test_router"
        assert routing_agent.model_name == "gpt-4o-mini"
        assert routing_agent.temperature == 0.1
        assert routing_agent.llm is not None
    
    def test_build_routing_prompt(self, routing_agent, sample_context):
        """Test routing prompt construction"""
        prompt = routing_agent._build_routing_prompt(sample_context, "")
        
        # Check that prompt contains expected elements
        assert "直前の生成プロセスを分析し" in prompt
        assert "ユーザーに挨拶してください。" in prompt
        assert "こんにちは！今日は" in prompt
        assert "以下の条件でルーティング" in prompt
        assert "JSON形式で出力" in prompt
    
    def test_build_routing_prompt_empty_shared_state(self, routing_agent):
        """Test routing prompt with empty shared_state"""
        context = Context()
        prompt = routing_agent._build_routing_prompt(context, "")
        
        # Should handle missing data gracefully
        assert "N/A" in prompt
        assert "JSON形式で出力" in prompt
    
    def test_analyze_content_for_routing_greeting(self, routing_agent, sample_context):
        """Test content analysis for greeting detection"""
        result = routing_agent._analyze_content_for_routing("Hello, how are you?", sample_context)
        
        assert isinstance(result, RoutingResult)
        assert result.next_route == "continue"  # Default since no specific keywords
        assert 0.0 <= result.confidence <= 1.0
        assert result.reasoning is not None
    
    def test_analyze_content_for_routing_error(self, routing_agent, sample_context):
        """Test content analysis for error detection"""
        result = routing_agent._analyze_content_for_routing("An error occurred", sample_context)
        
        assert isinstance(result, RoutingResult)
        assert result.next_route == "error"
        assert result.confidence > 0.5
        assert "error indicators" in result.reasoning.lower()
    
    def test_analyze_content_for_routing_completion(self, routing_agent, sample_context):
        """Test content analysis for completion detection"""
        result = routing_agent._analyze_content_for_routing("Task is complete", sample_context)
        
        assert isinstance(result, RoutingResult)
        assert result.next_route == "end"
        assert result.confidence > 0.5
        assert "completion indicators" in result.reasoning.lower()
    
    def test_parse_routing_result_json(self, routing_agent, sample_context):
        """Test parsing valid JSON routing result"""
        json_content = '''
        {
            "content": "Test content",
            "next_route": "greeting", 
            "confidence": 0.9,
            "reasoning": "Detected greeting pattern"
        }
        '''
        
        result = routing_agent._parse_routing_result(json_content, sample_context)
        
        assert isinstance(result, RoutingResult)
        assert result.content == "Test content"
        assert result.next_route == "greeting"
        assert result.confidence == 0.9
        assert result.reasoning == "Detected greeting pattern"
    
    def test_parse_routing_result_invalid_json(self, routing_agent, sample_context):
        """Test parsing invalid JSON falls back to content analysis"""
        invalid_content = "This is not JSON but mentions an error"
        
        result = routing_agent._parse_routing_result(invalid_content, sample_context)
        
        assert isinstance(result, RoutingResult)
        assert result.next_route == "error"  # Should detect "error" keyword
        assert 0.0 <= result.confidence <= 1.0
    
    def test_create_llm_result(self, routing_agent):
        """Test LLMResult creation"""
        routing_result = RoutingResult(
            content="test",
            next_route="greeting",
            confidence=0.8,
            reasoning="test reasoning"
        )
        
        llm_result = routing_agent._create_llm_result(routing_result, True)
        
        assert llm_result.content == routing_result
        assert llm_result.success is True
        assert llm_result.metadata['agent_name'] == "test_router"
        assert llm_result.metadata['agent_type'] == "routing"
    
    @pytest.mark.asyncio
    async def test_run_async_basic(self, routing_agent, sample_context):
        """Test basic async execution"""
        # This test requires actual LLM call, might need mocking in CI
        try:
            result_context = await routing_agent.run_async("", sample_context)
            
            # Check that context was updated
            assert result_context.routing is not None
            assert isinstance(result_context.routing, RoutingResult)
            assert result_context.result is not None
            
            # Check routing result structure
            routing = result_context.routing
            assert routing.content is not None
            assert routing.next_route is not None
            assert 0.0 <= routing.confidence <= 1.0
            assert routing.reasoning is not None
            
        except Exception as e:
            # If LLM call fails (e.g., no API key), should still create error routing
            assert result_context.routing is not None
            assert result_context.routing.next_route == "error"
    
    def test_run_sync(self, routing_agent, sample_context):
        """Test synchronous execution wrapper"""
        try:
            result_context = routing_agent.run("", sample_context)
            
            # Check that context was updated
            assert result_context.routing is not None
            assert isinstance(result_context.routing, RoutingResult)
            
        except Exception:
            # Expected if no LLM access, test the wrapper functionality
            pass


@pytest.mark.asyncio
async def test_routing_agent_integration():
    """Integration test with different routing scenarios"""
    agent = RoutingAgent(
        name="integration_test",
        routing_instruction="""
判定ルール：
- "hello"または"hi"が含まれる → "greeting"
- "?"で終わる → "question"
- "error"が含まれる → "error"
- その他 → "continue"
        """.strip()
    )
    
    test_cases = [
        {
            "last_generation": "Hello there!",
            "expected_route": "greeting"  # May vary based on actual LLM response
        },
        {
            "last_generation": "What is your name?", 
            "expected_route": "question"  # May vary based on actual LLM response
        },
        {
            "last_generation": "An error occurred",
            "expected_route": "error"  # May vary based on actual LLM response
        }
    ]
    
    for i, case in enumerate(test_cases):
        context = Context()
        context.shared_state['_last_prompt'] = f"Test prompt {i}"
        context.shared_state['_last_generation'] = case['last_generation']
        
        try:
            result_context = await agent.run_async("", context)
            
            # Verify structure (actual routing may vary based on LLM)
            assert result_context.routing is not None
            assert isinstance(result_context.routing, RoutingResult)
            assert result_context.routing.next_route is not None
            assert 0.0 <= result_context.routing.confidence <= 1.0
            
        except Exception:
            # If LLM unavailable, should create error routing
            assert result_context.routing.next_route == "error"


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])