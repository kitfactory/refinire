"""
Refinire Agents - Comprehensive AI agent and workflow framework

This module provides the complete agent framework including:
- Workflow orchestration (Flow, Step, Context)
- Pipeline functionality (LLMPipeline, InteractivePipeline)
- Specialized agent implementations for specific tasks

Components are organized into:
- Flow: Workflow orchestration engine and step implementations
- Pipeline: LLM pipeline and execution frameworks
- Specialized Agents: Task-specific agent implementations
"""

# Import flow and pipeline functionality
from .flow import (
    Flow,
    FlowExecutionError,
    Step,
    FunctionStep,
    ConditionStep,
    ParallelStep,
    UserInputStep,
    AgentPipelineStep,
    DebugStep,
    ForkStep,
    JoinStep,
    Context,
    Message,
    create_simple_flow,
    create_conditional_flow,
    create_simple_condition,
    create_lambda_step
)

from .pipeline import (
    LLMPipeline,
    LLMResult,
    InteractivePipeline,
    InteractionResult,
    InteractionQuestion,
    create_simple_llm_pipeline,
    create_evaluated_llm_pipeline,
    create_tool_enabled_llm_pipeline,
    create_simple_interactive_pipeline,
    create_evaluated_interactive_pipeline,
    # Legacy pipeline (deprecated)
    AgentPipeline,
    EvaluationResult,
    Comment,
    CommentImportance
)

# Import implemented agents
from .gen_agent import (
    GenAgent,
    create_simple_gen_agent,
    create_evaluated_gen_agent
)

from .clarify_agent import (
    ClarifyAgent,
    ClarificationResult,
    ClarificationQuestion,
    ClarifyBase,
    Clarify,
    create_simple_clarify_agent,
    create_evaluated_clarify_agent
)

from .extractor import (
    ExtractorAgent,
    ExtractorConfig,
    ExtractionRule,
    ExtractionResult,
    RegexExtractionRule,
    EmailExtractionRule,
    PhoneExtractionRule,
    URLExtractionRule,
    DateExtractionRule,
    HTMLExtractionRule,
    JSONExtractionRule,
    LLMExtractionRule,
    CustomFunctionExtractionRule,
    create_contact_extractor,
    create_html_extractor,
    create_json_extractor,
)

from .validator import (
    ValidatorAgent,
    ValidatorConfig,
    ValidationRule,
    ValidationResult,
    RequiredRule,
    EmailFormatRule,
    LengthRule,
    RangeRule,
    RegexRule,
    CustomFunctionRule,
    create_email_validator,
    create_required_validator,
    create_length_validator,
    create_custom_validator,
)

from .router import (
    RouterAgent,
    RouterConfig,
    RouteClassifier,
    LLMClassifier,
    RuleBasedClassifier,
    create_intent_router,
    create_content_type_router
)

from .notification import (
    NotificationAgent,
    NotificationConfig,
    NotificationChannel,
    NotificationResult,
    LogChannel,
    EmailChannel,
    WebhookChannel,
    SlackChannel,
    TeamsChannel,
    FileChannel,
    create_log_notifier,
    create_file_notifier,
    create_webhook_notifier,
    create_slack_notifier,
    create_teams_notifier,
    create_multi_channel_notifier,
)

# Version information
__version__ = "0.2.0"

# Public API
__all__ = [
    # Workflow orchestration
    "Flow",
    "FlowExecutionError",
    "Step",
    "FunctionStep",
    "ConditionStep",
    "ParallelStep",
    "UserInputStep",
    "AgentPipelineStep",
    "DebugStep",
    "ForkStep",
    "JoinStep",
    "Context",
    "Message",
    "create_simple_flow",
    "create_conditional_flow",
    "create_simple_condition",
    "create_lambda_step",
    
    # Pipeline functionality
    "LLMPipeline",
    "LLMResult",
    "InteractivePipeline",
    "InteractionResult",
    "InteractionQuestion",
    "create_simple_llm_pipeline",
    "create_evaluated_llm_pipeline",
    "create_tool_enabled_llm_pipeline",
    "create_simple_interactive_pipeline",
    "create_evaluated_interactive_pipeline",
    "AgentPipeline",
    "EvaluationResult",
    "Comment",
    "CommentImportance",
    
    # Generation Agents
    "GenAgent",
    "create_simple_gen_agent", 
    "create_evaluated_gen_agent",
    
    # Clarification Agents
    "ClarifyAgent",
    "ClarificationResult",
    "ClarificationQuestion", 
    "ClarifyBase",
    "Clarify",
    "create_simple_clarify_agent",
    "create_evaluated_clarify_agent",
    
    # Processing Agents
    "ExtractorAgent",
    "ExtractorConfig",
    "ExtractionRule",
    "ExtractionResult",
    "RegexExtractionRule",
    "EmailExtractionRule",
    "PhoneExtractionRule",
    "URLExtractionRule",
    "DateExtractionRule",
    "HTMLExtractionRule",
    "JSONExtractionRule",
    "LLMExtractionRule",
    "CustomFunctionExtractionRule",
    "create_contact_extractor",
    "create_html_extractor",
    "create_json_extractor",
    
    "ValidatorAgent",
    "ValidatorConfig",
    "ValidationRule",
    "ValidationResult",
    "RequiredRule",
    "EmailFormatRule",
    "LengthRule",
    "RangeRule",
    "RegexRule",
    "CustomFunctionRule",
    "create_email_validator",
    "create_required_validator",
    "create_length_validator",
    "create_custom_validator",
    
    # Decision Agents
    "RouterAgent",
    "RouterConfig",
    "RouteClassifier",
    "LLMClassifier",
    "RuleBasedClassifier",
    "create_intent_router",
    "create_content_type_router",
    
    # Communication Agents
    "NotificationAgent",
    "NotificationConfig",
    "NotificationChannel",
    "NotificationResult",
    "LogChannel",
    "EmailChannel",
    "WebhookChannel",
    "SlackChannel",
    "TeamsChannel",
    "FileChannel",
    "create_log_notifier",
    "create_file_notifier",
    "create_webhook_notifier",
    "create_slack_notifier",
    "create_teams_notifier",
    "create_multi_channel_notifier",
]