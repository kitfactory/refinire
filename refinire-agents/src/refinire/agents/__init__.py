"""
Agents module for the Agents SDK Models.

This module provides specialized agent implementations that extend the base Step class
to provide specific functionality patterns commonly used in AI workflows.

Agents are categorized into several types:
- Processing Agents: Transform, extract, validate, and aggregate data
- Decision Agents: Route, classify, and make decisions
- Communication Agents: Handle notifications, chat, and interviews
- Data Agents: Collect, cache, and search data
- Control Agents: Orchestrate, monitor, and schedule tasks
- Security Agents: Handle authentication and auditing

All agents inherit from the Step class and can be used within Flow workflows.
"""

# Core workflow functionality
from .context import Context
from .step import (
    Step,
    FunctionStep,
    ConditionStep,
    ParallelStep,
    AgentPipelineStep,
    UserInputStep,
    ForkStep,
    JoinStep,
    DebugStep
)
from .flow import Flow, FlowExecutionError
from .pipeline import AgentPipeline, EvaluationResult, Comment, CommentImportance

# Import implemented agents
from .router import (
    RouterAgent,
    RouterConfig,
    RouteClassifier,
    LLMClassifier,
    RuleBasedClassifier,
    create_intent_router,
    create_content_type_router
)

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

from .clarify_agent import (
    ClarifyAgent,
    ClarificationResult,
    ClarificationQuestion,
    ClarifyBase,
    Clarify,
    create_simple_clarify_agent,
    create_evaluated_clarify_agent
)

from .gen_agent import (
    GenAgent,
    create_simple_gen_agent,
    create_evaluated_gen_agent
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
__version__ = "0.1.0"

# Public API - will be populated as agents are implemented
__all__ = [
    # Core workflow functionality
    "Context", 
    "Step",
    "FunctionStep",
    "ConditionStep", 
    "ParallelStep",
    "AgentPipelineStep",
    "UserInputStep",
    "ForkStep",
    "JoinStep",
    "DebugStep",
    "Flow",
    "FlowExecutionError",
    "AgentPipeline",
    "EvaluationResult",
    "Comment",
    "CommentImportance",
    
    # Base classes and utilities
    "RouteClassifier",
    "LLMClassifier", 
    "RuleBasedClassifier",
    
    # Core Agent Pipeline functionality
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
    "ClarifyAgent",
    "ClarificationResult",
    "ClarificationQuestion", 
    "ClarifyBase",
    "Clarify",
    "create_simple_clarify_agent",
    "create_evaluated_clarify_agent",
    "GenAgent",
    "create_simple_gen_agent",
    "create_evaluated_gen_agent",
    
    # Processing Agents
    # "TransformerAgent",
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
    # "AggregatorAgent",
    
    # Decision Agents
    "RouterAgent",
    "RouterConfig",
    "create_intent_router",
    "create_content_type_router",
    # "ClassifierAgent", 
    # "DecisionAgent",
    # "PrioritizerAgent",
    
    # Communication Agents
    # "NotificationAgent",
    # "ChatbotAgent",
    # "InterviewAgent",
    
    # Data Agents
    # "CollectorAgent",
    # "CacheAgent",
    # "SearchAgent",
    
    # Control Agents
    # "OrchestratorAgent",
    # "MonitorAgent", 
    # "SchedulerAgent",
    
    # Security Agents
    # "AuthAgent",
    # "AuditAgent",
] 
