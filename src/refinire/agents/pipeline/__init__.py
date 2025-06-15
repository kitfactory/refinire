"""
Refinire Pipeline - LLM pipeline and execution frameworks

This module provides pipeline functionality for the Refinire AI agent platform:
- Modern LLM pipeline with PromptStore integration
- Legacy AgentPipeline (deprecated)
- Interactive pipeline for multi-turn conversations
"""

# Modern LLM Pipeline (recommended)
from .llm_pipeline import (
    LLMPipeline,
    LLMResult,
    EvaluationResult as LLMEvaluationResult,
    InteractivePipeline,
    InteractionResult,
    InteractionQuestion,
    create_simple_llm_pipeline,
    create_evaluated_llm_pipeline,
    create_tool_enabled_llm_pipeline,
    create_web_search_pipeline,
    create_calculator_pipeline,
    create_simple_interactive_pipeline,
    create_evaluated_interactive_pipeline
)

# Legacy AgentPipeline (deprecated)
from .pipeline import AgentPipeline, EvaluationResult, Comment, CommentImportance

__all__ = [
    # Modern LLM Pipeline (recommended)
    "LLMPipeline",
    "LLMResult", 
    "LLMEvaluationResult",
    "InteractivePipeline",
    "InteractionResult",
    "InteractionQuestion",
    "create_simple_llm_pipeline",
    "create_evaluated_llm_pipeline",
    "create_tool_enabled_llm_pipeline",
    "create_web_search_pipeline",
    "create_calculator_pipeline",
    "create_simple_interactive_pipeline",
    "create_evaluated_interactive_pipeline",
    
    # Legacy AgentPipeline (deprecated)
    "AgentPipeline",
    "EvaluationResult",
    "Comment",
    "CommentImportance"
]