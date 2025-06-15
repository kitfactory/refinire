"""
Refinire Agents - Specialized AI agents for specific tasks

This module provides specialized agent implementations that extend the base Step class
to provide specific functionality patterns commonly used in AI workflows.

Agents are categorized into several types:
- Generation Agents: GenAgent for general-purpose generation
- Processing Agents: ExtractorAgent, ValidatorAgent for data processing  
- Decision Agents: RouterAgent for routing and classification
- Communication Agents: ClarifyAgent for clarification workflows, NotificationAgent for alerts
"""

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