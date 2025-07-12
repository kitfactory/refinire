"""
Refinire - Unified AI Agent Development Platform

Refinire provides a comprehensive platform for building AI agents with three core pillars:

1. **Unified LLM Interface** - Single API across providers (OpenAI, Anthropic, Google, Ollama)
2. **Autonomous Quality Assurance** - Built-in evaluation and improvement
3. **Composable Flow Architecture** - Flexible workflow orchestration

Key Features:
- Multi-provider LLM support with unified interface
- Workflow orchestration with Flow and Step abstractions  
- Specialized agents for common tasks (generation, extraction, validation, etc.)
- Modern AI agents with PromptStore integration
- Built-in tracing and observability
- Interactive multi-turn conversation support
"""

__version__ = "0.2.16"

# Core LLM functionality - most commonly used
from .core import (
    get_llm,
    ProviderType, 
    get_available_models,
    get_available_models_async,
    PromptStore,
    StoredPrompt,
    PromptReference,
    P,
    detect_system_language,
    get_default_storage_dir,
    enable_console_tracing,
    disable_tracing,
    TraceRegistry,
    TraceMetadata,
    get_global_registry,
    set_global_registry,
    enable_opentelemetry_tracing,
    disable_opentelemetry_tracing,
    is_opentelemetry_enabled,
    is_openinference_available,
    get_tracer,
    ClaudeModel,
    GeminiModel,
    OllamaModel,
    get_message,
    DEFAULT_LANGUAGE
)

# Workflow orchestration
from .agents.flow import (
    Flow,
    FlowExecutionError,
    Step,
    FunctionStep,
    ConditionStep,
    ParallelStep,
    UserInputStep,
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

# Modern agent functionality
from .agents.pipeline import (
    RefinireAgent,
    LLMResult,
    InteractiveAgent,
    InteractionResult,
    InteractionQuestion,
    create_simple_agent,
    create_evaluated_agent,
    create_tool_enabled_agent,
    create_simple_interactive_agent,
    create_evaluated_interactive_agent
)

# Specialized agents
from .agents import (
    ClarifyAgent,
    ClarificationResult,
    ClarificationQuestion,
    ExtractorAgent,
    ValidatorAgent,
    RouterAgent,
    NotificationAgent,
    create_simple_clarify_agent,
    create_evaluated_clarify_agent
)

# Tool decorators and utilities
from .tools import (
    tool,
    function_tool_compat,
    get_tool_info,
    list_tools
)

# Environment variable templates
from .templates import core_template

# Most commonly used imports for quick access
__all__ = [
    # Core LLM functionality
    "get_llm",
    "ProviderType",
    "get_available_models", 
    "get_available_models_async",
    "PromptStore",
    "StoredPrompt",
    "PromptReference",
    "P",
    "detect_system_language",
    "get_default_storage_dir",
    "ClaudeModel",
    "GeminiModel", 
    "OllamaModel",
    "get_message",
    "DEFAULT_LANGUAGE",
    
    # Workflow orchestration
    "Flow",
    "FlowExecutionError", 
    "Step",
    "FunctionStep",
    "ConditionStep",
    "ParallelStep",
    "UserInputStep",
    "DebugStep",
    "ForkStep",
    "JoinStep",
    "Context",
    "Message",
    "create_simple_flow",
    "create_conditional_flow",
    "create_simple_condition",
    "create_lambda_step",
    
    # Agent functionality
    "RefinireAgent",
    "LLMResult",
    "InteractiveAgent", 
    "InteractionResult",
    "InteractionQuestion",
    "create_simple_agent",
    "create_evaluated_agent",
    "create_tool_enabled_agent",
    "create_simple_interactive_agent",
    "create_evaluated_interactive_agent",
    
    # Specialized agents
    "ClarifyAgent",
    "ClarificationResult",
    "ClarificationQuestion",
    "ExtractorAgent", 
    "ValidatorAgent",
    "RouterAgent",
    "NotificationAgent",
    "create_simple_clarify_agent",
    "create_evaluated_clarify_agent",
    
    # Tool decorators and utilities
    "tool",
    "function_tool_compat",
    "get_tool_info",
    "list_tools",
    
    # Tracing
    "enable_console_tracing",
    "disable_tracing", 
    "TraceRegistry",
    "TraceMetadata",
    "get_global_registry",
    "set_global_registry",
    "enable_opentelemetry_tracing",
    "disable_opentelemetry_tracing",
    "is_opentelemetry_enabled", 
    "is_openinference_available",
    "get_tracer",
    
    # Environment templates
    "core_template"
]