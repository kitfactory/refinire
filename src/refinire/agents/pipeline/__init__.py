"""
Refinire Agent - AI agent framework with evaluation and tool support

This module provides AI agent functionality for the Refinire platform:
- RefinireAgent with built-in evaluation and tool support
- InteractiveAgent for multi-turn conversations
- Factory functions for common configurations
"""

# Refinire Agent (recommended)
from .llm_pipeline import (
    RefinireAgent,
    LLMResult,
    EvaluationResult as LLMEvaluationResult,
    InteractiveAgent,
    InteractionResult,
    InteractionQuestion,
    create_simple_agent,
    create_evaluated_agent,
    create_tool_enabled_agent,
    create_web_search_agent,
    create_calculator_agent,
    create_simple_interactive_agent,
    create_evaluated_interactive_agent
)

# Legacy AgentPipeline (deprecated - removed)
# from .pipeline import AgentPipeline, EvaluationResult, Comment, CommentImportance

__all__ = [
    # Refinire Agent (recommended)
    "RefinireAgent",
    "LLMResult", 
    "LLMEvaluationResult",
    "InteractiveAgent",
    "InteractionResult",
    "InteractionQuestion",
    "create_simple_agent",
    "create_evaluated_agent",
    "create_tool_enabled_agent",
    "create_web_search_agent",
    "create_calculator_agent",
    "create_simple_interactive_agent",
    "create_evaluated_interactive_agent"
]