"""Refinire Agent - A powerful AI agent with built-in evaluation and tool support.

Refinireエージェント - 組み込み評価とツールサポートを備えた強力なAIエージェント。
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Type, Union

from agents import Agent, Runner
from agents import FunctionTool
from pydantic import BaseModel, ValidationError

from ..flow.step import Step
from ..flow.context import Context
from ..context_provider_factory import ContextProviderFactory
from ...core.trace_registry import TraceRegistry
from ...core import PromptReference
from ...core.llm import get_llm
from ...core.exceptions import (
    RefinireNetworkError, RefinireConnectionError, RefinireTimeoutError,
    RefinireAuthenticationError, RefinireRateLimitError, RefinireAPIError,
    RefinireModelError, map_openai_exception, map_httpx_exception
)
from ...core.routing import RoutingResult, create_routing_result_model



@dataclass
class LLMResult:
    """
    Result from LLM generation
    LLM生成結果
    
    Attributes:
        content: Generated content / 生成されたコンテンツ
        success: Whether generation was successful / 生成が成功したか
        metadata: Additional metadata / 追加メタデータ
        evaluation_score: Evaluation score if evaluated / 評価されている場合の評価スコア
        attempts: Number of attempts made / 実行された試行回数
    """
    content: Any
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    evaluation_score: Optional[float] = None
    attempts: int = 1


@dataclass 
class EvaluationResult:
    """
    Result from evaluation process
    評価プロセスの結果
    
    Attributes:
        score: Evaluation score (0-100) / 評価スコア（0-100）
        passed: Whether evaluation passed threshold / 閾値を超えたか
        feedback: Evaluation feedback / 評価フィードバック
        metadata: Additional metadata / 追加メタデータ
    """
    score: float
    passed: bool
    feedback: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class RefinireAgent(Step):
    """
    Refinire Agent - AI agent with automatic evaluation and tool integration
    Refinireエージェント - 自動評価とツール統合を備えたAIエージェント
    
    A powerful AI agent that combines generation, evaluation, and tool calling in a single interface.
    生成、評価、ツール呼び出しを単一のインターフェースで統合した強力なAIエージェント。
    """
    
    def __init__(
        self,
        name: str,
        generation_instructions: str,
        evaluation_instructions: Optional[str] = None,
        *,
        model: str = "gpt-4o-mini",
        evaluation_model: Optional[str] = None,
        output_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: float = 30.0,
        threshold: float = 85.0,
        max_retries: int = 3,
        input_guardrails: Optional[List[Callable[[str], bool]]] = None,
        output_guardrails: Optional[List[Callable[[Any], bool]]] = None,
        session_history: Optional[List[str]] = None,
        history_size: int = 10,
        improvement_callback: Optional[Callable[[LLMResult, EvaluationResult], str]] = None,
        locale: str = "en",
        tools: Optional[List[Callable]] = None,
        mcp_servers: Optional[List[str]] = None,
        context_providers_config: Optional[Union[str, List[Dict[str, Any]]]] = None,
        # Flow integration parameters / Flow統合パラメータ
        next_step: Optional[str] = None,
        store_result_key: Optional[str] = None,
        # Orchestration mode parameter / オーケストレーションモードパラメータ
        orchestration_mode: bool = False,
        # New routing parameters / 新しいルーティングパラメータ
        routing_instruction: Optional[str] = None,
        routing_destinations: Optional[List[str]] = None,
        # Environment variable namespace / 環境変数名前空間
        namespace: Optional[str] = None
    ) -> None:
        """
        Initialize Refinire Agent as a Step
        RefinireエージェントをStepとして初期化する
        
        Args:
            name: Agent name / エージェント名
            generation_instructions: Instructions for generation / 生成用指示
            evaluation_instructions: Instructions for evaluation / 評価用指示
            model: OpenAI model name / OpenAIモデル名
            evaluation_model: Model for evaluation / 評価用モデル
            output_model: Pydantic model for structured output / 構造化出力用Pydanticモデル
            temperature: Sampling temperature / サンプリング温度
            max_tokens: Maximum tokens / 最大トークン数
            timeout: Request timeout / リクエストタイムアウト
            threshold: Evaluation threshold / 評価閾値
            max_retries: Maximum retry attempts / 最大リトライ回数
            input_guardrails: Input validation functions / 入力検証関数
            output_guardrails: Output validation functions / 出力検証関数
            session_history: Session history / セッション履歴
            history_size: History size limit / 履歴サイズ制限
            improvement_callback: Callback for improvement suggestions / 改善提案コールバック
            locale: Locale for messages / メッセージ用ロケール
            tools: OpenAI function tools / OpenAI関数ツール
            mcp_servers: MCP server identifiers / MCPサーバー識別子
            context_providers_config: Configuration for context providers (YAML-like string or dict list) / コンテキストプロバイダーの設定（YAMLライクな文字列または辞書リスト）
            next_step: Next step for Flow integration / Flow統合用次ステップ
            store_result_key: Key to store result in Flow context / Flow context内での結果保存キー
            orchestration_mode: Enable orchestration mode with structured JSON output / 構造化JSON出力付きオーケストレーションモード有効化
            routing_instruction: Instruction for routing decision / ルーティング決定用指示
            routing_destinations: List of possible routing destinations / 可能なルーティング先のリスト
            namespace: Environment variable namespace for oneenv / oneenv用環境変数名前空間
        """
        # Initialize Step base class
        # Step基底クラスを初期化
        super().__init__(name)
        
        # Store namespace for environment variable access
        # 環境変数アクセス用の名前空間を保存
        self.namespace = namespace
        
        # Store routing parameters
        # ルーティングパラメータを保存
        self.routing_instruction = routing_instruction
        self.routing_destinations = routing_destinations
        
        # Initialize dedicated agents (will be created after model setup)
        # 専用エージェントを初期化（モデル設定後に作成）
        self._routing_agent = None
        self._evaluation_agent = None
        
        # Handle PromptReference for generation instructions
        self._generation_prompt_metadata = None
        if PromptReference and isinstance(generation_instructions, PromptReference):
            self._generation_prompt_metadata = generation_instructions.get_metadata()
            self.generation_instructions = str(generation_instructions)
        else:
            self.generation_instructions = generation_instructions
        
        # Handle PromptReference for evaluation instructions
        self._evaluation_prompt_metadata = None
        if PromptReference and isinstance(evaluation_instructions, PromptReference):
            self._evaluation_prompt_metadata = evaluation_instructions.get_metadata()
            self.evaluation_instructions = str(evaluation_instructions)
        else:
            self.evaluation_instructions = evaluation_instructions
        
        # Handle model parameter - convert string to Model instance using get_llm()
        # modelパラメータを処理 - 文字列の場合はget_llm()を使用してModelインスタンスに変換
        if isinstance(model, str):
            # Detect provider from model name to avoid environment override
            # モデル名からプロバイダーを検出して環境オーバーライドを回避
            def detect_provider_from_model_name(model_name: str) -> Optional[str]:
                """Detect provider from model name patterns"""
                if "gpt" in model_name.lower() or "o3" in model_name.lower() or "o4" in model_name.lower():
                    return "openai"
                elif "gemini" in model_name.lower():
                    return "google"
                elif "claude" in model_name.lower():
                    return "anthropic"
                else:
                    return None  # Let get_llm decide
            
            detected_provider = detect_provider_from_model_name(model)
            if detected_provider:
                self.model = get_llm(provider=detected_provider, model=model, temperature=temperature, namespace=namespace)
            else:
                self.model = get_llm(model=model, temperature=temperature, namespace=namespace)
            self.model_name = model
        else:
            # Assume it's already a Model instance
            # 既にModelインスタンスと仮定
            self.model = model
            self.model_name = getattr(model, 'model', 'unknown')
        
        # Handle evaluation_model parameter similarly
        # evaluation_modelパラメータも同様に処理
        if evaluation_model is None:
            self.evaluation_model = self.model
            self.evaluation_model_name = self.model_name
        elif isinstance(evaluation_model, str):
            # Apply same provider detection logic for evaluation model
            # 評価モデルにも同じプロバイダー検出ロジックを適用
            detected_provider = detect_provider_from_model_name(evaluation_model)
            if detected_provider:
                self.evaluation_model = get_llm(provider=detected_provider, model=evaluation_model, temperature=temperature, namespace=namespace)
            else:
                self.evaluation_model = get_llm(model=evaluation_model, temperature=temperature, namespace=namespace)
            self.evaluation_model_name = evaluation_model
        else:
            self.evaluation_model = evaluation_model
            self.evaluation_model_name = getattr(evaluation_model, 'model', 'unknown')
        
        self.output_model = output_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.threshold = threshold
        self.max_retries = max_retries
        self.locale = locale
        
        # Guardrails
        self.input_guardrails = input_guardrails or []
        self.output_guardrails = output_guardrails or []
        
        # History management
        self.session_history = session_history or []
        self.history_size = history_size
        self._pipeline_history: List[Dict[str, Any]] = []
        
        # Callbacks
        self.improvement_callback = improvement_callback
        
        # Flow integration configuration / Flow統合設定
        self.next_step = next_step
        self.store_result_key = store_result_key or f"{name}_result"
        
        # Orchestration mode configuration / オーケストレーションモード設定
        self.orchestration_mode = orchestration_mode
        
        # Tools and MCP support
        self.tools = tools or []
        self.mcp_servers = mcp_servers or []
        self.tool_handlers = {}
        
        # Process tools to extract FunctionTool objects for the SDK
        # ツールを処理してSDK用のFunctionToolオブジェクトを抽出
        sdk_tools = []
        if self.tools:
            for tool in self.tools:
                if hasattr(tool, '_function_tool'):
                    # Refinire @tool or function_tool_compat decorated function
                    # Refinire @toolまたはfunction_tool_compat装飾関数
                    sdk_tools.append(tool._function_tool)
                elif isinstance(tool, FunctionTool):
                    # Already a FunctionTool object
                    # 既にFunctionToolオブジェクト
                    sdk_tools.append(tool)
                else:
                    # Try to create FunctionTool directly (legacy support)
                    # FunctionToolを直接作成を試行（レガシーサポート）
                    from agents import function_tool as agents_function_tool
                    try:
                        function_tool_obj = agents_function_tool(tool)
                        sdk_tools.append(function_tool_obj)
                    except Exception as e:
                        from ...core.exceptions import RefinireError
                        raise RefinireError(f"Failed to convert tool {tool} to FunctionTool: {e}", details={"tool": str(tool), "error": str(e)})
        
        # OpenAI Agents SDK Agentを初期化（Study 5と同じ方法）
        # Initialize OpenAI Agents SDK Agent
        agent_kwargs = {
            "name": f"{name}_sdk_agent",
            "instructions": self.generation_instructions,
            "tools": sdk_tools,
            "model": self.model  # Pass the Model instance to the Agent
        }
        
        # Add timeout setting to SDK agent if specified
        # timeout設定が指定されている場合はSDKエージェントに追加
        if self.timeout and self.timeout != 30.0:  # Only if different from default
            # OpenAI Agents SDK may support timeout in model settings
            # OpenAI Agents SDKはmodel設定でtimeoutをサポートしている可能性
            try:
                # Try to set timeout in model if supported
                # サポートされている場合はモデルにtimeoutを設定
                if hasattr(self.model, 'timeout'):
                    self.model.timeout = self.timeout
                elif hasattr(self.model, 'settings') and hasattr(self.model.settings, 'timeout'):
                    self.model.settings.timeout = self.timeout
            except Exception:
                # If timeout setting fails, continue without it
                # timeout設定が失敗した場合は、それなしで続行
                pass
        
        # Add MCP servers support if specified
        # MCPサーバーが指定されている場合は追加
        if self.mcp_servers:
            agent_kwargs["mcp_servers"] = self.mcp_servers
        
        # Add structured output support if output_model is specified
        # output_modelが指定されている場合は構造化出力サポートを追加
        if self.output_model:
            agent_kwargs["output_type"] = self.output_model
            
        self._sdk_agent = Agent(**agent_kwargs)
        
        # Initialize dedicated routing and evaluation agents
        # 専用のルーティング・評価エージェントを初期化
        self._initialize_dedicated_agents()
        
        # Context providers
        self.context_providers = []
        # Store original config for inheritance by routing agents
        # ルーティングエージェントの継承用に元の設定を保存
        self._original_context_providers_config = context_providers_config
        
        if context_providers_config is None or (isinstance(context_providers_config, str) and not context_providers_config.strip()):
            # Default to conversation history provider
            # デフォルトで会話履歴プロバイダーを使用
            context_providers_config = [
                {"type": "conversation_history", "max_items": 10}
            ]
            # Also update the stored original config
            # 保存されている元の設定も更新
            self._original_context_providers_config = context_providers_config
        
        # Prepare orchestration system instruction template
        # オーケストレーション用システム指示テンプレートを準備
        if self.orchestration_mode:
            self._orchestration_template = self._prepare_orchestration_template()
        
        if context_providers_config:
            # Handle YAML-like string or dict list
            # YAMLライクな文字列または辞書リストを処理
            if isinstance(context_providers_config, str):
                # Parse YAML-like string
                # YAMLライクな文字列を解析
                parsed_configs = ContextProviderFactory.parse_config_string(context_providers_config)
                if not parsed_configs:
                    # If parsing results in empty list, use default
                    # 解析結果が空リストの場合はデフォルトを使用
                    context_providers_config = [
                        {"type": "conversation_history", "max_items": 10}
                    ]
                else:
                    # Convert parsed configs to the format expected by create_providers
                    # 解析された設定をcreate_providersが期待する形式に変換
                    provider_configs = []
                    for parsed_config in parsed_configs:
                        provider_config = {"type": parsed_config["name"]}
                        provider_config.update(parsed_config["config"])
                        provider_configs.append(provider_config)
                    context_providers_config = provider_configs
            
            # Validate configuration before creating providers
            # プロバイダー作成前に設定を検証
            for config in context_providers_config:
                ContextProviderFactory.validate_config(config)
            self.context_providers = ContextProviderFactory.create_providers(context_providers_config)
    
    def _prepare_orchestration_template(self) -> str:
        """
        Prepare orchestration mode system instruction template
        オーケストレーション・モード用システム指示テンプレートを準備
        
        Returns:
            str: Orchestration template / オーケストレーション・テンプレート
        """
        if self.locale == "ja":
            return """あなたは以下のJSON構造で必ず回答してください:
{
  "status": "completed または failed",
  "result": "任務の成果",
  "reasoning": "推論過程",
  "next_hint": {
    "task": "次に推奨される処理種別",
    "confidence": "0-1の信頼度",
    "rationale": "推奨理由（任意）"
  }
}

重要: この形式から逸脱しないでください。"""
        else:
            return """You must respond in the following JSON structure:
{
  "status": "completed or failed",
  "result": "task outcome",
  "reasoning": "reasoning process",
  "next_hint": {
    "task": "recommended next task type",
    "confidence": "confidence level 0-1",
    "rationale": "rationale for recommendation (optional)"
  }
}

IMPORTANT: Do not deviate from this format."""
    
    def run(self, user_input: str, ctx: Optional[Context] = None) -> Context:
        """
        Run the agent synchronously and return Context with result
        エージェントを同期実行し、結果付きContextを返す
        
        Args:
            user_input: User input for the agent / エージェント用ユーザー入力
            ctx: Optional context (creates new if None) / オプションコンテキスト（Noneの場合は新作成）
        
        Returns:
            Context: Context with result in ctx.result / ctx.resultに結果が格納されたContext
        """
        # Create context if not provided / 提供されていない場合はContextを作成
        if ctx is None:
            ctx = Context()
            ctx.add_user_message(user_input)
        
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # If we're in a loop, try to use nest_asyncio or fallback
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                    future = asyncio.ensure_future(self.run_async(user_input, ctx))
                    result_ctx = loop.run_until_complete(future)
                except ImportError:
                    # nest_asyncio not available, cannot run in existing event loop
                    # nest_asyncioが利用できない場合、既存のイベントループでは実行不可
                    raise RuntimeError("Cannot run in existing event loop without nest_asyncio")
            except RuntimeError:
                # No running loop, we can create one
                result_ctx = asyncio.run(self.run_async(user_input, ctx))
            
            # Return orchestration result if in orchestration mode
            # オーケストレーションモードの場合はオーケストレーション結果を返却
            if self.orchestration_mode:
                # Check if result_ctx is already a dict (returned from run_async)
                # result_ctxが既に辞書（run_asyncから返却）の場合をチェック
                if isinstance(result_ctx, dict):
                    return result_ctx
                elif hasattr(result_ctx, 'result') and isinstance(result_ctx.result, dict):
                    return result_ctx.result
                else:
                    # If orchestration mode but no dict result, return error format
                    # オーケストレーションモードだが辞書結果がない場合、エラー形式を返却
                    return {
                        "status": "failed",
                        "result": result_ctx.result if hasattr(result_ctx, 'result') else None,
                        "reasoning": "Orchestration mode enabled but structured output not generated",
                        "next_hint": {
                            "task": "retry",
                            "confidence": 0.3,
                            "rationale": "Retry with clearer instructions or check agent configuration"
                        }
                    }
            return result_ctx
            
        except Exception as e:
            ctx.result = None
            ctx.add_system_message(f"Execution error: {e}")
            
            # Return appropriate error format for orchestration mode
            # オーケストレーションモードの場合は適切なエラー形式を返却
            if self.orchestration_mode:
                return {
                    "status": "failed",
                    "result": None,
                    "reasoning": f"Execution error: {str(e)}",
                    "next_hint": {
                        "task": "retry",
                        "confidence": 0.3,
                        "rationale": "System error occurred, may need retry or different approach"
                    }
                }
            return ctx
    
    async def run_async(self, user_input: Optional[str], ctx: Optional[Context] = None) -> Context:
        """
        Run the agent asynchronously and return Context with result
        エージェントを非同期実行し、結果付きContextを返す
        
        Args:
            user_input: User input for the agent / エージェント用ユーザー入力
            ctx: Optional workflow context (creates new if None) / オプションのワークフローコンテキスト（Noneの場合は新作成）
        
        Returns:
            Context: Updated context with result in ctx.result / ctx.resultに結果が格納された更新Context
        """
        # Create context if not provided / 提供されていない場合はContextを作成
        if ctx is None:
            ctx = Context()
            if user_input:
                ctx.add_user_message(user_input)
        # Create trace context intelligently - only if no active trace exists
        # インテリジェントにトレースコンテキストを作成 - アクティブなトレースが存在しない場合のみ
        try:
            from ...core.trace_context import TraceContextManager
            
            trace_name = f"RefinireAgent({self.name})"
            with TraceContextManager(trace_name):
                result_ctx = await self._execute_with_context(user_input, ctx, None)
                
                # Return orchestration result if in orchestration mode
                # オーケストレーションモードの場合はオーケストレーション結果を返却
                if self.orchestration_mode and isinstance(result_ctx.result, dict):
                    return result_ctx.result
                return result_ctx
        except ImportError:
            # trace_context not available - fallback to original behavior
            # trace_contextが利用できません - 元の動作にフォールバック
            result_ctx = await self._execute_with_context(user_input, ctx, None)
            
            # Return orchestration result if in orchestration mode
            # オーケストレーションモードの場合はオーケストレーション結果を返却
            if self.orchestration_mode and isinstance(result_ctx.result, dict):
                return result_ctx.result
            return result_ctx
        except Exception as e:
            # If there's any issue with trace creation, fall back to no trace
            # トレース作成で問題がある場合は、トレースなしにフォールバック
            # Unable to create trace context, running without trace context
            result_ctx = await self._execute_with_context(user_input, ctx, None)
            
            # Return orchestration result if in orchestration mode
            # オーケストレーションモードの場合はオーケストレーション結果を返却
            if self.orchestration_mode and isinstance(result_ctx.result, dict):
                return result_ctx.result
            return result_ctx
    
    async def run_streamed(self, user_input: str, ctx: Optional[Context] = None, callback: Optional[Callable[[str], None]] = None):
        """
        Run the agent with streaming output (simple implementation)
        エージェントをストリーミング出力で実行（シンプル実装）
        
        Args:
            user_input: User input for the agent / エージェント用ユーザー入力
            ctx: Optional context (creates new if None) / オプションコンテキスト（Noneの場合は新作成）
            callback: Optional callback function for streaming chunks / ストリーミングチャンク用オプションコールバック関数
            
        Yields:
            str: Streaming content chunks / ストリーミングコンテンツチャンク
        """
        # Create context if not provided / 提供されていない場合はContextを作成
        if ctx is None:
            ctx = Context()
            ctx.add_user_message(user_input)
        
        try:
            # Build prompt using existing method / 既存メソッドを使用してプロンプトを構築
            full_prompt = self._build_prompt(user_input, include_instructions=False)
            
            # Apply generation instructions to agent / エージェントに生成指示を適用
            original_instructions = self._sdk_agent.instructions
            self._sdk_agent.instructions = self.generation_instructions
            
            # Use Runner.run_streamed for streaming execution
            # ストリーミング実行のためにRunner.run_streamedを使用
            stream_result = Runner.run_streamed(self._sdk_agent, full_prompt)
            
            full_content = ""
            async for stream_event in stream_result.stream_events():
                # Handle text delta events for streaming content
                # ストリーミングコンテンツのためにテキストデルタイベントを処理
                if hasattr(stream_event, 'type') and stream_event.type == 'raw_response_event':
                    if hasattr(stream_event, 'data'):
                        # Check for ResponseTextDeltaEvent
                        if stream_event.data.__class__.__name__ == 'ResponseTextDeltaEvent':
                            if hasattr(stream_event.data, 'delta') and stream_event.data.delta:
                                chunk = stream_event.data.delta
                                full_content += chunk
                                
                                # Call callback if provided / コールバックが提供されている場合は呼び出し
                                if callback:
                                    callback(chunk)
                                
                                # Yield the chunk / チャンクをyield
                                yield chunk
            
            # Store result in context if provided / 提供されている場合はコンテキストに結果を保存
            if ctx is not None:
                ctx.result = full_content
            
            # Restore original instructions / 元の指示を復元
            self._sdk_agent.instructions = original_instructions
            
        except Exception as e:
            # Restore original instructions on error / エラー時に元の指示を復元
            self._sdk_agent.instructions = original_instructions
            from ...core.exceptions import RefinireError
            raise RefinireError(f"Streaming execution failed: {e}", details={"error": str(e)})
            yield f"Error: {str(e)}"
    
    async def _execute_with_context(self, user_input: Optional[str], ctx: Context, span=None) -> Context:
        """
        Execute agent with context and optional span for metadata
        コンテキストと オプションのスパンでエージェントを実行
        """
        try:
            # Determine input text for agent / エージェント用入力テキストを決定
            input_text = user_input or ctx.last_user_input or ""
            
            # Add span metadata if available
            # スパンが利用可能な場合はメタデータを追加
            if span is not None:
                span.span_data.input = input_text
                span.span_data.instructions = self.generation_instructions
                if self.evaluation_instructions:
                    span.span_data.evaluation_instructions = self.evaluation_instructions
            
            if not input_text:
                # If no input available, set result to None and continue
                # 入力がない場合、結果をNoneに設定して続行
                ctx.result = None
                message = f"RefinireAgent {self.name}: No input available, skipping execution"
                ctx.add_system_message(message)
                if span is not None:
                    span.span_data.output = None
                    span.span_data.error = "No input available"
            else:
                # Save prompt to shared_state before execution for routing/evaluation
                # routing/evaluation用に実行前にプロンプトをshared_stateに保存
                full_prompt = self._build_prompt(input_text, include_instructions=True)
                ctx.shared_state['_last_prompt'] = full_prompt
                
                # Execute RefinireAgent and get LLMResult
                # RefinireAgentを実行してLLMResultを取得
                llm_result = await self._run_standalone(input_text, ctx)
                
                # Save generation result to shared_state for routing/evaluation
                # routing/evaluation用に生成結果をshared_stateに保存
                if llm_result.success and llm_result.content:
                    ctx.shared_state['_last_generation'] = llm_result.content
                
                # Perform evaluation if evaluation_instructions are provided
                # evaluation_instructionsが提供されている場合は評価を実行
                evaluation_result = None
                if self.evaluation_instructions and llm_result.success and llm_result.content:
                    # Preserve _last_prompt and _last_generation during evaluation execution
                    # evaluation実行中の_last_prompt/_last_generation保護
                    preserved_last_prompt = ctx.shared_state.get('_last_prompt') if ctx else None
                    preserved_last_generation = ctx.shared_state.get('_last_generation') if ctx else None
                    
                    try:
                        evaluation_result = await self._execute_evaluation(input_text, llm_result.content, ctx)
                        # Store evaluation result in context
                        # 評価結果をコンテキストに保存
                        ctx.evaluation_result = {
                            "score": evaluation_result.score,
                            "passed": evaluation_result.passed,
                            "feedback": evaluation_result.feedback,
                            "metadata": evaluation_result.metadata
                        }
                        # Update LLMResult with evaluation score
                        # LLMResultを評価スコアで更新
                        llm_result.evaluation_score = evaluation_result.score
                    except Exception as e:
                        # Handle evaluation errors gracefully
                        # 評価エラーを適切に処理
                        ctx.evaluation_result = {
                            "score": 0.0,
                            "passed": False,
                            "feedback": f"Evaluation failed: {str(e)}",
                            "metadata": {"error": str(e)}
                        }
                    finally:
                        # Restore _last_prompt and _last_generation to prevent overwrite
                        # 上書きを防ぐために_last_prompt/_last_generationを復元
                        if ctx:
                            if preserved_last_prompt is not None:
                                ctx.shared_state['_last_prompt'] = preserved_last_prompt
                            if preserved_last_generation is not None:
                                ctx.shared_state['_last_generation'] = preserved_last_generation
                
                # Execute routing if routing_instruction is provided
                # routing_instructionが提供されている場合はルーティングを実行
                routing_result = None
                if self.routing_instruction and llm_result.success and llm_result.content:
                    try:
                        routing_result = await self._execute_routing(llm_result.content, ctx)
                        if routing_result:
                            # Store routing result object in context without overwriting the main result
                            # メイン結果を上書きせずにルーティング結果オブジェクトをコンテキストに保存
                            ctx.routing_result = routing_result
                            # Keep the original LLM result as the main result
                            # 元のLLM結果をメイン結果として保持
                            ctx.result = llm_result
                        else:
                            # Store original result when routing failed
                            # ルーティングが失敗した場合、元の結果を格納
                            ctx.result = llm_result
                    except Exception as e:
                        # Handle routing errors gracefully - store complete LLMResult object
                        # ルーティングエラーを適切に処理 - 完全なLLMResultオブジェクトを格納
                        ctx.result = llm_result
                        from ...core.routing import RoutingResult
                        ctx.routing_result = RoutingResult(
                            content="",
                            next_route="error",
                            confidence=0.0,
                            reasoning=f"Routing failed: {str(e)}"
                        )
                else:
                    # No routing, use original result - store complete LLMResult object
                    # ルーティングなし、元の結果を使用 - 完全なLLMResultオブジェクトを格納
                    ctx.result = llm_result
                
                # Store generated content in shared_state for workflow access
                # ワークフローアクセス用にshared_stateに生成コンテンツを保存
                ctx.shared_state[self.store_result_key] = ctx.content  # Custom key storage
                ctx.shared_state[f"{self.name}_result"] = ctx.content  # Agent name-based storage
                
                # Add span metadata for result
                # 結果のスパンメタデータを追加
                if span is not None:
                    span.span_data.output = ctx.result
                    span.span_data.success = llm_result.success
                    span.span_data.model = self.model_name
                    span.span_data.temperature = self.temperature
                    if evaluation_result:
                        span.span_data.evaluation_score = evaluation_result.score
                        span.span_data.evaluation_passed = evaluation_result.passed
                
                # Add result as assistant message
                # 結果をアシスタントメッセージとして追加
                if ctx.result is not None:
                    ctx.add_assistant_message(str(ctx.result))
                    ctx.add_system_message(f"RefinireAgent {self.name}: Execution successful")
                else:
                    ctx.add_system_message(f"RefinireAgent {self.name}: Execution failed (evaluation threshold not met)")
                
        except Exception as e:
            # Handle execution errors / 実行エラーを処理
            ctx.result = None
            error_msg = f"RefinireAgent {self.name} execution error: {str(e)}"
            ctx.add_system_message(error_msg)
            ctx.shared_state[self.store_result_key] = None
            ctx.shared_state[f"{self.name}_result"] = None
            
            # Add error to span if available
            # スパンが利用可能な場合はエラーを追加
            if span is not None:
                span.span_data.error = str(e)
                span.span_data.success = False
            
            # Log error for debugging / デバッグ用エラーログ
            # RefinireAgent execution error - re-raise to caller
        
        # Set next step if specified / 指定されている場合は次ステップを設定
        if self.next_step:
            ctx.goto(self.next_step)
        
        return ctx
    
    async def _run_standalone(self, user_input: str, ctx: Optional[Context] = None) -> LLMResult:
        """
        Run agent in standalone mode
        スタンドアロンモードでエージェントを実行
        """
        if not self._validate_input(user_input):
            return LLMResult(
                content=None,
                success=False,
                metadata={"error": "Input validation failed", "input": user_input}
            )
        
        # 会話履歴とユーザー入力を含むプロンプトを構築（指示文は除く）
        full_prompt = self._build_prompt(user_input, include_instructions=False, ctx=ctx)
        
        # Store original instructions to restore later
        # 後で復元するために元の指示を保存
        original_instructions = self._sdk_agent.instructions
        
        # Remove retry loop - fail immediately on network errors
        # リトライループを削除 - ネットワークエラーでは即座に失敗
        try:
            # Apply variable substitution to SDK agent instructions if context is available
            # コンテキストが利用可能な場合はSDKエージェントの指示にも変数置換を適用
            if ctx:
                processed_instructions = self._substitute_variables(self.generation_instructions, ctx)
                # Add orchestration template if in orchestration mode
                # オーケストレーション・モードの場合はテンプレートを追加
                if self.orchestration_mode:
                    # Check if orchestration template is already in instructions
                    # オーケストレーション・テンプレートが既に指示に含まれているかチェック
                    if not self._has_orchestration_instruction(processed_instructions):
                        processed_instructions = f"{self._orchestration_template}\n\n{processed_instructions}"
                self._sdk_agent.instructions = processed_instructions
            else:
                # Apply orchestration template without context
                # コンテキストなしでオーケストレーション・テンプレートを適用
                if self.orchestration_mode:
                    instructions = self.generation_instructions
                    if not self._has_orchestration_instruction(instructions):
                        instructions = f"{self._orchestration_template}\n\n{instructions}"
                    self._sdk_agent.instructions = instructions
            
            # full_promptを使用してRunner.runを呼び出し
            # Configure timeout by creating a new OpenAI client with custom timeout
            # カスタムタイムアウトで新しいOpenAIクライアントを作成してタイムアウトを設定
            custom_run_config = None
            
            if self.timeout and self.timeout != 30.0:  # Only if different from default
                try:
                    import httpx
                    from openai import AsyncOpenAI
                    from agents import RunConfig
                    from agents.models.openai_provider import OpenAIProvider
                    
                    # Create a custom OpenAI client with our timeout
                    # 指定されたタイムアウトでカスタムOpenAIクライアントを作成
                    custom_client = AsyncOpenAI(
                        timeout=httpx.Timeout(timeout=self.timeout)
                    )
                    
                    # Create a custom OpenAI provider with our client
                    # カスタムクライアントでカスタムOpenAIプロバイダーを作成
                    custom_provider = OpenAIProvider(openai_client=custom_client)
                    
                    # Create a RunConfig with the custom provider
                    # カスタムプロバイダーでRunConfigを作成
                    custom_run_config = RunConfig(model_provider=custom_provider)
                    
                except Exception:
                    # If custom client creation fails, continue without it
                    # カスタムクライアント作成が失敗した場合は、それなしで続行
                    pass
            
            # Execute with OpenAI Agents SDK using custom timeout if available
            # カスタムタイムアウトが利用可能な場合はそれを使用してOpenAI Agents SDKで実行
            if custom_run_config:
                result = await Runner.run(self._sdk_agent, full_prompt, run_config=custom_run_config)
            else:
                result = await Runner.run(self._sdk_agent, full_prompt)
            content = result.final_output
            if not content and hasattr(result, 'output') and result.output:
                content = result.output
            
            # In orchestration mode, skip structured parsing here - do it later on result field
            # オーケストレーションモードでは、ここでの構造化解析をスキップ - resultフィールドで後で実行
            if self.orchestration_mode:
                parsed_content = content  # Keep raw content for orchestration parsing
            elif self.output_model and content:
                parsed_content = self._parse_structured_output(content)
            else:
                parsed_content = content
            
            # Validate output - fail immediately if validation fails
            # 出力を検証 - 検証が失敗した場合は即座に失敗
            if not self._validate_output(parsed_content):
                # Restore original instructions before returning
                # 戻る前に元の指示を復元
                self._sdk_agent.instructions = original_instructions
                return LLMResult(
                    content=None,
                    success=False,
                    metadata={"error": "Output validation failed", "attempts": 1}
                )
            
            # Build metadata for successful execution
            # 成功実行のメタデータを構築
            metadata = {
                "model": self.model_name,
                "temperature": self.temperature,
                "attempts": 1,
                "sdk": True
            }
            if self._generation_prompt_metadata:
                metadata.update(self._generation_prompt_metadata)
            if self._evaluation_prompt_metadata:
                metadata["evaluation_prompt"] = self._evaluation_prompt_metadata
            
            # Parse orchestration JSON if in orchestration mode
            # オーケストレーション・モードの場合はJSONを解析
            if self.orchestration_mode:
                try:
                    orchestration_result = self._parse_orchestration_result(parsed_content)
                        # Apply output_model parsing to result field if specified
                    # output_modelが指定されている場合はresultフィールドに適用
                    if self.output_model and orchestration_result.get("result") is not None:
                        try:
                            orchestration_result["result"] = self._parse_structured_output(orchestration_result["result"])
                        except Exception as parse_error:
                            # Keep original result if parsing fails
                            # 解析に失敗した場合は元のresultを保持
                            # Failed to parse orchestration result with output_model, keeping original
                            pass
                    final_content = orchestration_result
                    metadata["orchestration_mode"] = True
                    metadata["parsed_json"] = True
                except Exception as e:
                    # If orchestration parsing fails, check if content is structured output
                    # オーケストレーション解析が失敗した場合、コンテンツが構造化出力かチェック
                    if self.output_model:
                        try:
                            # Try to parse as structured output and wrap in orchestration format
                            # 構造化出力として解析し、オーケストレーション形式でラップを試行
                            structured_result = self._parse_structured_output(parsed_content)
                            orchestration_result = {
                                "status": "completed",
                                "result": structured_result,
                                "reasoning": f"Generated structured output using {self.output_model.__name__}",
                                "next_hint": {
                                        "task": "review_output",
                                        "confidence": 0.8,
                                        "rationale": "Structured output generated successfully"
                                    }
                                }
                            final_content = orchestration_result
                            metadata["orchestration_mode"] = True
                            metadata["structured_fallback"] = True
                            # Wrapped structured output in orchestration format
                        except Exception as structured_error:
                            # Both orchestration and structured parsing failed
                            # オーケストレーション解析と構造化解析の両方が失敗
                            # Both orchestration and structured parsing failed - raise exception
                            from ...core.exceptions import RefinireValidationError
                            raise RefinireValidationError(f"Both orchestration and structured parsing failed: {str(e)}, {str(structured_error)}", details={"orchestration_error": str(e), "structured_error": str(structured_error)})
                        else:
                            # Restore original instructions before returning error
                            # エラー返却前に元の指示を復元
                            self._sdk_agent.instructions = original_instructions
                            return LLMResult(
                                content=None,
                                success=False,
                                metadata={"error": f"Orchestration JSON parsing failed: {str(e)}", "attempts": 1, "orchestration_mode": True}
                            )
            else:
                final_content = parsed_content
            
            llm_result = LLMResult(
                content=final_content,
                success=True,
                metadata=metadata,
                evaluation_score=None,
                attempts=1
            )
            self._store_in_history(user_input, llm_result)
            # Restore original instructions before returning
            # 戻る前に元の指示を復元
            self._sdk_agent.instructions = original_instructions
            return llm_result
            
        except Exception as e:
            # Restore original instructions before handling error
            # エラー処理前に元の指示を復元
            self._sdk_agent.instructions = original_instructions
            
            # Check if this is a network-related error and raise custom exception immediately
            # ネットワーク関連エラーかチェックし、即座にカスタム例外を発生
            import openai
            import httpx
            
            if isinstance(e, (openai.APIConnectionError, openai.APITimeoutError, 
                             openai.AuthenticationError, openai.RateLimitError,
                             openai.APIStatusError, openai.APIError)):
                # Determine provider from model name
                # モデル名からプロバイダーを判定
                provider = "openai"
                if "anthropic" in self.model_name.lower() or "claude" in self.model_name.lower():
                    provider = "anthropic"
                elif "gemini" in self.model_name.lower() or "google" in self.model_name.lower():
                    provider = "google"
                elif "ollama" in self.model_name.lower() or "llama" in self.model_name.lower():
                    provider = "ollama"
                elif "openrouter" in self.model_name.lower():
                    provider = "openrouter"
                elif "groq" in self.model_name.lower():
                    provider = "groq"
                elif "lmstudio" in self.model_name.lower():
                    provider = "lmstudio"
                
                # Map OpenAI exception to Refinire custom exception and raise immediately
                # OpenAI例外をRefinireカスタム例外にマップして即座に発生
                raise map_openai_exception(e, provider)
            
            elif isinstance(e, (httpx.ConnectError, httpx.TimeoutException,
                               httpx.HTTPStatusError, httpx.RequestError)):
                # Determine provider from model name
                # モデル名からプロバイダーを判定
                provider = "unknown"
                if "anthropic" in self.model_name.lower() or "claude" in self.model_name.lower():
                    provider = "anthropic"
                elif "gemini" in self.model_name.lower() or "google" in self.model_name.lower():
                    provider = "google"
                elif "ollama" in self.model_name.lower() or "llama" in self.model_name.lower():
                    provider = "ollama"
                elif "openrouter" in self.model_name.lower():
                    provider = "openrouter"
                elif "groq" in self.model_name.lower():
                    provider = "groq"
                elif "lmstudio" in self.model_name.lower():
                    provider = "lmstudio"
                
                # Map httpx exception to Refinire custom exception and raise immediately
                # httpx例外をRefinireカスタム例外にマップして即座に発生
                raise map_httpx_exception(e, provider)
            
            else:
                # For non-network errors, return LLMResult with error
                # ネットワークエラー以外の場合は、エラー付きでLLMResultを返す
                return LLMResult(
                    content=None,
                    success=False,
                    metadata={"error": str(e), "attempts": 1, "sdk": True}
                )
    
    
    
    
    def _validate_input(self, user_input: str) -> bool:
        """Validate input using guardrails / ガードレールを使用して入力を検証"""
        for guardrail in self.input_guardrails:
            if not guardrail(user_input):
                return False
        return True
    
    def _validate_output(self, output: str) -> bool:
        """Validate output using guardrails / ガードレールを使用して出力を検証"""
        for guardrail in self.output_guardrails:
            if not guardrail(output):
                return False
        return True
    
    def _substitute_variables(self, text: str, ctx: Optional[Context] = None) -> str:
        """
        Substitute variables in text using {{variable}} syntax
        {{変数}}構文を使用してテキストの変数を置換
        
        Args:
            text: Text with potential variables / 変数を含む可能性のあるテキスト
            ctx: Context for variable substitution / 変数置換用のコンテキスト
            
        Returns:
            str: Text with variables substituted / 変数が置換されたテキスト
        """
        if not text or not ctx:
            return text
        
        # Find all {{variable}} patterns
        # {{変数}}パターンをすべて検索
        import re
        variable_pattern = r'\{\{([^}]+)\}\}'
        variables = re.findall(variable_pattern, text)
        
        if not variables:
            return text
        
        result_text = text
        
        for variable in variables:
            variable_key = variable.strip()
            placeholder = f"{{{{{variable}}}}}"
            
            # Handle special reserved variables
            # 特別な予約変数を処理
            if variable_key == "RESULT":
                # Use the most recent result
                # 最新の結果を使用
                replacement = str(ctx.result) if ctx.result is not None else ""
            elif variable_key == "EVAL_RESULT":
                # Use evaluation result if available
                # 評価結果が利用可能な場合は使用
                if hasattr(ctx, 'evaluation_result') and ctx.evaluation_result:
                    eval_info = []
                    if 'score' in ctx.evaluation_result:
                        eval_info.append(f"Score: {ctx.evaluation_result['score']}")
                    if 'passed' in ctx.evaluation_result:
                        eval_info.append(f"Passed: {ctx.evaluation_result['passed']}")
                    if 'feedback' in ctx.evaluation_result:
                        eval_info.append(f"Feedback: {ctx.evaluation_result['feedback']}")
                    replacement = ", ".join(eval_info) if eval_info else ""
                else:
                    replacement = ""
            else:
                # Use shared_state for other variables
                # その他の変数にはshared_stateを使用
                replacement = str(ctx.shared_state.get(variable_key, "")) if ctx.shared_state else ""
            
            # Replace the placeholder with the value
            # プレースホルダーを値で置換
            result_text = result_text.replace(placeholder, replacement)
        
        return result_text

    def _create_routing_output_model(self) -> Type[BaseModel]:
        """
        Create a dynamic RoutingResult model based on the output_model.
        output_model に基づいて動的 RoutingResult モデルを作成
        
        Returns:
            A dynamically created RoutingResult model with the appropriate content type
        """
        # For now, always use the standard RoutingResult to avoid JSON schema issues
        # JSON スキーマの問題を避けるため、現在は常に標準 RoutingResult を使用
        return RoutingResult
        
        # TODO: Fix JSON schema generation for Union types in dynamic models
        # TODO: 動的モデルでの Union 型の JSON スキーマ生成を修正
        # if self.output_model:
        #     # Create a dynamic RoutingResult with the specified content type
        #     # 指定されたコンテンツ型で動的 RoutingResult を作成
        #     return create_routing_result_model(self.output_model)
        # else:
        #     # Use the standard RoutingResult with string content
        #     # 文字列コンテンツで標準 RoutingResult を使用
        #     return RoutingResult

    def _initialize_dedicated_agents(self) -> None:
        """
        Initialize dedicated routing and evaluation agents
        専用のルーティング・評価エージェントを初期化
        """
        # Initialize RoutingAgent if routing_instruction is provided
        # routing_instructionが提供されている場合はRoutingAgentを初期化
        if self.routing_instruction:
            from ..routing_agent import RoutingAgent
            self._routing_agent = RoutingAgent(
                name=f"{self.name}_router",
                routing_instruction=self.routing_instruction,
                routing_destinations=self.routing_destinations,
                model=self.model_name,
                temperature=0.1,  # Low temperature for consistent routing
                namespace=self.namespace
            )
        
        # Initialize EvaluationAgent if evaluation_instructions is provided
        # evaluation_instructionsが提供されている場合はEvaluationAgentを初期化
        if self.evaluation_instructions:
            from ..evaluation_agent import EvaluationAgent
            self._evaluation_agent = EvaluationAgent(
                name=f"{self.name}_evaluator",
                evaluation_instruction=self.evaluation_instructions,
                pass_threshold=self.threshold / 100.0,  # Convert percentage to 0-1 scale
                model=self.evaluation_model_name,
                temperature=0.2,  # Low temperature for consistent evaluation
                namespace=self.namespace
            )

    def _build_routing_prompt(self, content: Any, routing_instruction: str) -> str:
        """
        Build a routing prompt for evaluating generated content.
        生成されたコンテンツを評価するためのルーティングプロンプトを構築
        
        Args:
            content: Generated content to evaluate
            routing_instruction: Routing instruction for decision making
            
        Returns:
            Formatted routing prompt string
        """
        return f"""
これまでの会話履歴と生成されたコンテンツを分析し、次のルーティング判断を行ってください。

重要: 会話履歴に含まれる全ての情報を考慮して判断してください。最新の応答だけでなく、過去のユーザー入力も確認してください。

=== 生成コンテンツ ===
{content}

=== ルーティング指示 ===
{routing_instruction}

上記の指示に従って、適切なルーティング判断を行い、指定された形式で出力してください。
"""

    def _build_routing_prompt_with_context(self, content: Any, routing_instruction: str, ctx: Optional[Context] = None) -> str:
        """
        Build a routing prompt using shared_state for last prompt and generation.
        shared_stateを使用して直前のプロンプトと生成結果でルーティングプロンプトを構築
        
        Args:
            content: Generated content to evaluate
            routing_instruction: Routing instruction for decision making
            ctx: Context containing shared_state with _last_prompt/_last_generation
            
        Returns:
            Formatted routing prompt string with last prompt and generation
        """
        # Extract last prompt and generation from shared_state
        # shared_stateから直前のプロンプトと生成結果を抽出
        last_prompt = ctx.shared_state.get('_last_prompt', '') if ctx else ''
        last_generation = ctx.shared_state.get('_last_generation', content) if ctx else content
        
        # Build prompt with last prompt and generation
        # 直前のプロンプトと生成結果でプロンプトを構築
        if last_prompt:
            return f"""
直前の生成プロセスを分析し、ルーティング判断を行ってください。

=== 直前の生成プロンプト ===
{last_prompt}

=== 直前の生成結果 ===
{last_generation}

=== ルーティング指示 ===
{routing_instruction}

上記の情報に基づいて、適切なルーティング判断を行い、指定された形式で出力してください。
"""
        else:
            # Fallback to original format if no last_prompt
            # last_promptがない場合は元の形式にフォールバック
            return self._build_routing_prompt(content, routing_instruction)

    def _build_evaluation_prompt(self, content: Any, evaluation_instruction: str, ctx: Optional[Context] = None) -> str:
        """
        Build an evaluation prompt using shared_state for last prompt and generation.
        shared_stateを使用して直前のプロンプトと生成結果で評価プロンプトを構築
        
        Args:
            content: Generated content to evaluate
            evaluation_instruction: Evaluation instruction for quality assessment
            ctx: Context containing shared_state with _last_prompt/_last_generation
            
        Returns:
            Formatted evaluation prompt string with last prompt and generation
        """
        # Extract last prompt and generation from shared_state
        # shared_stateから直前のプロンプトと生成結果を抽出
        last_prompt = ctx.shared_state.get('_last_prompt', '') if ctx else ''
        last_generation = ctx.shared_state.get('_last_generation', content) if ctx else content
        
        # Build evaluation prompt with last prompt and generation
        # 直前のプロンプトと生成結果で評価プロンプトを構築
        if last_prompt:
            return f"""
生成プロセスの品質を評価してください。

=== 元のプロンプト ===
{last_prompt}

=== 生成結果 ===
{last_generation}

=== 評価指示 ===
{evaluation_instruction}

上記の情報に基づいて品質を評価し、指定された形式で出力してください。
"""
        else:
            # Fallback to basic evaluation if no last_prompt
            # last_promptがない場合は基本評価にフォールバック
            return f"""
生成結果の品質を評価してください。

=== 生成結果 ===
{content}

=== 評価指示 ===
{evaluation_instruction}

上記の情報に基づいて品質を評価し、指定された形式で出力してください。
"""

    async def _execute_routing(self, content: Any, ctx: Optional[Context] = None) -> Optional[RoutingResult]:
        """
        Execute routing decision based on the generated content.
        生成されたコンテンツに基づいてルーティング判断を実行
        
        Args:
            content: Generated content to evaluate
            ctx: Context for routing execution
            
        Returns:
            RoutingResult if routing is enabled, None otherwise
        """
        if not self.routing_instruction:
            return None
            
        # Preserve _last_prompt and _last_generation during routing execution
        # routing実行中の_last_prompt/_last_generation保護
        preserved_last_prompt = None
        preserved_last_generation = None
        if ctx:
            preserved_last_prompt = ctx.shared_state.get('_last_prompt')
            preserved_last_generation = ctx.shared_state.get('_last_generation')
        
        try:
            # Create the appropriate output model
            # 適切な出力モデルを作成
            routing_output_model = self._create_routing_output_model()
            
            # Execute accurate routing with dedicated agent
            # 専用エージェントによる正確なルーティング実行
            return await self._execute_accurate_routing(content, routing_output_model, ctx)
        
        except Exception as e:
            # Log error but don't fail the entire process
            # エラーをログに記録するが、プロセス全体を失敗させない
            print(f"Warning: Routing execution failed: {e}")
            return None
        finally:
            # Restore _last_prompt and _last_generation to prevent overwrite
            # 上書きを防ぐために_last_prompt/_last_generationを復元
            if ctx:
                if preserved_last_prompt is not None:
                    ctx.shared_state['_last_prompt'] = preserved_last_prompt
                if preserved_last_generation is not None:
                    ctx.shared_state['_last_generation'] = preserved_last_generation

    async def _execute_accurate_routing(self, content: Any, routing_output_model: Type[BaseModel], ctx: Optional[Context] = None) -> Optional[RoutingResult]:
        """
        Execute accurate routing with dedicated routing agent.
        専用ルーティングエージェントによる正確なルーティング実行
        
        Args:
            content: Generated content to evaluate
            routing_output_model: The routing output model to use
            ctx: Context for routing execution
            
        Returns:
            RoutingResult if successful, None otherwise
        """
        try:
            # Use dedicated RoutingAgent if available
            # 利用可能な場合は専用RoutingAgentを使用
            if self._routing_agent and ctx:
                result_context = await self._routing_agent.run_async("", ctx)
                return result_context.routing_result
            
            # Fallback to legacy routing implementation
            # レガシールーティング実装にフォールバック
            return await self._execute_legacy_routing(content, routing_output_model, ctx)
            
        except Exception as e:
            print(f"Warning: Accurate routing failed: {e}")
            return None

    async def _execute_legacy_routing(self, content: Any, routing_output_model: Type[BaseModel], ctx: Optional[Context] = None) -> Optional[RoutingResult]:
        """
        Legacy routing implementation using RefinireAgent
        RefinireAgentを使用したレガシールーティング実装
        """
        try:
            # Build routing prompt with last prompt and generation from shared_state
            # shared_stateの直前プロンプトと生成結果でルーティングプロンプトを構築
            routing_prompt = self._build_routing_prompt_with_context(content, self.routing_instruction, ctx)
            
            # Create dedicated routing agent
            # 専用ルーティングエージェントを作成
            # Note: We need to avoid circular imports, so we'll use a different approach
            # 循環インポートを避けるため、異なるアプローチを使用
            
            # Check for existing traces and generate unique router name
            # 既存のトレースを確認し、ユニークなルーター名を生成
            from ...core.trace_registry import get_global_registry
            
            registry = get_global_registry()
            router_base_name = f"{self.name}_router"
            router_name = router_base_name
            
            # Check if a trace with this name already exists and generate unique name if needed
            # この名前のトレースが既に存在するかチェックし、必要に応じてユニーク名を生成
            counter = 1
            while any(trace.agent_names and router_name in trace.agent_names for trace in registry.get_all_traces()):
                router_name = f"{router_base_name}_{counter}"
                counter += 1
            
            routing_agent = self.__class__(
                name=router_name,
                generation_instructions=routing_prompt,
                output_model=routing_output_model,
                model=self.model_name,
                temperature=0.1,  # Lower temperature for more consistent routing
                namespace=self.namespace,
                context_providers_config=[]  # No context providers needed, history is in prompt
            )
            
            # Execute routing with proper input
            # 適切な入力でルーティングを実行
            routing_result = await routing_agent.run_async("Please analyze the content and determine the next route.", ctx)
            
            # Parse and return the routing result
            # ルーティング結果をパースして返す
            if routing_result and routing_result.success and routing_result.content:
                # Check if content is already a RoutingResult object (due to output_model)
                # コンテンツが既にRoutingResultオブジェクトかチェック（output_modelのため）
                from ...core.routing import RoutingResult
                if isinstance(routing_result.content, RoutingResult):
                    return routing_result.content
                
                # If content is a string, try to parse it as JSON
                # コンテンツが文字列の場合、JSONとしてパースを試行
                if isinstance(routing_result.content, str):
                    try:
                        import json
                        parsed_data = json.loads(routing_result.content)
                        return RoutingResult(
                            content=parsed_data.get('content', ''),
                            next_route=parsed_data.get('next_route', 'continue'),
                            confidence=parsed_data.get('confidence', 0.5),
                            reasoning=parsed_data.get('reasoning', 'No reasoning provided')
                        )
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"Warning: Failed to parse routing result JSON: {e}")
                        return None
                
                # If content is neither RoutingResult nor string, log and return None
                # コンテンツがRoutingResultでも文字列でもない場合、ログを出力してNoneを返す
                print(f"Warning: Unexpected routing result content type: {type(routing_result.content)}")
                return None
            return None
        
        except Exception as e:
            print(f"Warning: Accurate routing execution failed: {e}")
            return None


    def _build_prompt(self, user_input: str, include_instructions: bool = True, ctx: Optional[Context] = None) -> str:
        """
        Build complete prompt with instructions, context providers, and history
        指示、コンテキストプロバイダー、履歴を含む完全なプロンプトを構築
        
        Args:
            user_input: User input / ユーザー入力
            include_instructions: Whether to include instructions (for OpenAI Agents SDK, set to False)
            include_instructions: 指示文を含めるかどうか（OpenAI Agents SDKの場合はFalse）
            ctx: Context for variable substitution / 変数置換用のコンテキスト
        """
        prompt_parts = []
        
        # Add instructions only if requested (not for OpenAI Agents SDK)
        # 要求された場合のみ指示文を追加（OpenAI Agents SDKの場合は除く）
        if include_instructions:
            # Apply variable substitution to generation instructions
            # generation_instructionsにも変数置換を適用
            processed_instructions = self._substitute_variables(self.generation_instructions, ctx)
            prompt_parts.append(processed_instructions)
        
        # Add context from context providers (with chaining)
        # コンテキストプロバイダーからのコンテキストを追加（連鎖機能付き）
        has_conversation_provider = False
        if hasattr(self, 'context_providers') and self.context_providers:
            context_parts = []
            previous_context = ""
            
            # Check if any context provider is for conversation history
            # 会話履歴用のコンテキストプロバイダーがあるかチェック
            for provider in self.context_providers:
                if hasattr(provider, 'provider_name') and provider.provider_name == 'conversation_history':
                    has_conversation_provider = True
                elif provider.__class__.__name__ == 'ConversationHistoryProvider':
                    has_conversation_provider = True
            
            for provider in self.context_providers:
                try:
                    provider_context = provider.get_context(user_input, previous_context)
                    # Ensure provider_context is a string (convert None to empty string)
                    # provider_contextが文字列であることを保証（Noneは空文字列に変換）
                    if provider_context is None:
                        provider_context = ""
                    if provider_context:
                        context_parts.append(provider_context)
                        previous_context = provider_context
                except Exception as e:
                    # Log error but continue with other providers
                    # エラーをログに記録するが、他のプロバイダーは続行
                    # Context provider failed, continue with others
                    continue
            
            if context_parts:
                context_text = "\n\n".join(context_parts)
                prompt_parts.append(f"Context:\n{context_text}")
        
        # Add history if available and no conversation provider is used
        # 利用可能で会話プロバイダーが使用されていない場合は履歴を追加
        if self.session_history and not has_conversation_provider:
            history_text = "\n".join(self.session_history[-self.history_size:])
            prompt_parts.append(f"Previous context:\n{history_text}")
        
        # Substitute variables in user input before adding
        # ユーザー入力を追加する前に変数を置換
        processed_user_input = self._substitute_variables(user_input, ctx)
        prompt_parts.append(f"User input: {processed_user_input}")
        
        return "\n\n".join(prompt_parts)
    
    def _parse_structured_output(self, content: str) -> Any:
        """Parse structured output if model specified / モデルが指定されている場合は構造化出力を解析"""
        if not self.output_model:
            return content
            
        try:
            # Extract JSON from markdown codeblock if present
            # Markdownコードブロックが存在する場合はJSONを抽出
            json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                json_content = json_match.group(1).strip()
            else:
                json_content = content.strip()
            
            # Parse JSON and validate with Pydantic model
            # JSONを解析してPydanticモデルで検証
            data = json.loads(json_content)
            return self.output_model.model_validate(data)
        except Exception:
            # Fallback to raw content if parsing fails
            # パースに失敗した場合は生のコンテンツにフォールバック
            return content
    
    def _evaluate_content(self, user_input: str, generated_content: Any, ctx: Optional[Context] = None) -> EvaluationResult:
        """Evaluate generated content / 生成されたコンテンツを評価"""
        # Use the new prompt building method that leverages shared_state
        # shared_stateを活用する新しいプロンプト構築メソッドを使用
        evaluation_prompt = self._build_evaluation_prompt(generated_content, self.evaluation_instructions, ctx)
        
        messages = [{"role": "user", "content": evaluation_prompt}]
        
        try:
            # Simplified evaluation with basic scoring
            # 基本スコアリングによる簡略化された評価
            content_length = len(str(generated_content))
            is_empty = not generated_content or str(generated_content).strip() == ""
            
            # Basic heuristic evaluation
            # 基本的なヒューリスティック評価
            if is_empty:
                score = 0.0
                feedback = "Empty or invalid response"
            elif content_length < 10:
                score = 40.0
                feedback = "Response too short"
            elif content_length > 1000:
                score = 60.0
                feedback = "Response quite long"
            else:
                score = 80.0
                feedback = "Response appears appropriate in length and content"
            
            return EvaluationResult(
                score=score,
                passed=score >= self.threshold,
                feedback=feedback,
                metadata={"model": self.evaluation_model_name, "evaluation_type": "heuristic"}
            )
            
        except Exception as e:
            # Fallback evaluation - assume basic success
            # フォールバック評価 - 基本的な成功を仮定
            return EvaluationResult(
                score=75.0,  # Default moderate score
                passed=True,
                feedback=f"Evaluation completed with fallback scoring. Original error: {str(e)}",
                metadata={"error": str(e), "fallback": True}
            )
    
    async def _execute_evaluation(self, user_input: str, generated_content: Any, ctx: Optional[Context] = None) -> EvaluationResult:
        """
        Execute evaluation with dedicated evaluation agent.
        専用評価エージェントによる評価実行
        
        Args:
            user_input: User input text
            generated_content: Generated content to evaluate
            ctx: Context for evaluation execution
            
        Returns:
            EvaluationResult with evaluation details
        """
        try:
            # Use dedicated EvaluationAgent if available
            # 利用可能な場合は専用EvaluationAgentを使用
            if self._evaluation_agent and ctx:
                result_context = await self._evaluation_agent.run_async("", ctx)
                if result_context.evaluation_result:
                    # Convert 0-1 scale to 0-100 scale for backward compatibility
                    # 後方互換性のため0-1スケールを0-100スケールに変換
                    evaluation_result = EvaluationResult(
                        score=result_context.evaluation_result.score * 100.0,  # Convert to 0-100 scale
                        passed=result_context.evaluation_result.passed,
                        feedback=result_context.evaluation_result.feedback,
                        metadata=result_context.evaluation_result.metadata
                    )
                    return evaluation_result
            
            # Fallback to legacy evaluation implementation
            # レガシー評価実装にフォールバック
            return self._evaluate_content(user_input, generated_content, ctx)
            
        except Exception as e:
            print(f"Warning: Evaluation execution failed: {e}")
            # Fallback to legacy evaluation
            # レガシー評価にフォールバック
            return self._evaluate_content(user_input, generated_content, ctx)
    
    def _store_in_history(self, user_input: str, result: LLMResult) -> None:
        """Store interaction in history and update context providers / 対話を履歴に保存し、コンテキストプロバイダーを更新"""
        interaction = {
            "user_input": user_input,
            "result": result.content,
            "success": result.success,
            "metadata": result.metadata,
            "timestamp": json.dumps({"pipeline": self.name}, ensure_ascii=False)
        }
        
        self._pipeline_history.append(interaction)
        
        # Add to session history for context
        session_entry = f"User: {user_input}\nAssistant: {result.content}"
        self.session_history.append(session_entry)
        
        # Trim history if needed
        if len(self.session_history) > self.history_size:
            self.session_history = self.session_history[-self.history_size:]
        
        # Update context providers
        # コンテキストプロバイダーを更新
        if hasattr(self, 'context_providers') and self.context_providers:
            for provider in self.context_providers:
                try:
                    provider.update(interaction)
                except Exception as e:
                    # Log error but continue with other providers
                    # エラーをログに記録するが、他のプロバイダーは続行
                    # Failed to update context provider, continue with others
                    continue
    
    def clear_history(self) -> None:
        """Clear all history and context providers / 全履歴とコンテキストプロバイダーをクリア"""
        self._pipeline_history.clear()
        self.session_history.clear()
        
        # Clear context providers
        # コンテキストプロバイダーをクリア
        if hasattr(self, 'context_providers') and self.context_providers:
            for provider in self.context_providers:
                try:
                    provider.clear()
                except Exception as e:
                    # Log error but continue with other providers
                    # エラーをログに記録するが、他のプロバイダーは続行
                    # Failed to clear context provider, continue with others
                    continue
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get pipeline history / パイプライン履歴を取得"""
        return self._pipeline_history.copy()
    
    def update_instructions(
        self, 
        generation_instructions: Optional[str] = None,
        evaluation_instructions: Optional[str] = None
    ) -> None:
        """Update instructions / 指示を更新"""
        if generation_instructions:
            self.generation_instructions = generation_instructions
        if evaluation_instructions:
            self.evaluation_instructions = evaluation_instructions
    
    def set_threshold(self, threshold: float) -> None:
        """Set evaluation threshold / 評価閾値を設定"""
        if 0 <= threshold <= 100:
            self.threshold = threshold
        else:
            raise ValueError("Threshold must be between 0 and 100")
    
    @classmethod
    def get_context_provider_schemas(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get available context provider schemas
        利用可能なコンテキストプロバイダーのスキーマを取得
        
        Returns:
            Dict[str, Dict[str, Any]]: Provider schemas / プロバイダースキーマ
        """
        return ContextProviderFactory.get_all_provider_schemas()
    
    def clear_context(self) -> None:
        """
        Clear context providers only (keep history)
        コンテキストプロバイダーのみをクリア（履歴は保持）
        """
        if hasattr(self, 'context_providers') and self.context_providers:
            for provider in self.context_providers:
                try:
                    provider.clear()
                except Exception as e:
                    # Failed to clear context provider, continue with others
                    continue
    
    def _has_orchestration_instruction(self, instructions: str) -> bool:
        """
        Check if instructions already contain orchestration template
        指示にオーケストレーション・テンプレートが既に含まれているかチェック
        
        Args:
            instructions: Instructions to check / チェックする指示
            
        Returns:
            bool: True if orchestration template is found / オーケストレーション・テンプレートが見つかった場合True
        """
        if not instructions:
            return False
        
        # Check for locale-specific orchestration indicators
        # ロケール固有のオーケストレーション指標をチェック
        if self.locale == "ja":
            japanese_indicators = [
                "JSON構造で必ず回答",
                "以下のJSON構造で",
                "この形式から逸脱しない"
            ]
            return any(indicator in instructions for indicator in japanese_indicators)
        else:
            english_indicators = [
                "JSON structure",
                "You must respond in the following JSON",
                "Do not deviate from this format"
            ]
            return any(indicator in instructions for indicator in english_indicators)
    
    def _parse_orchestration_result(self, content: Any) -> Dict[str, Any]:
        """
        Parse orchestration result from LLM output
        LLM出力からオーケストレーション結果を解析
        
        Args:
            content: LLM output content / LLM出力コンテンツ
            
        Returns:
            Dict[str, Any]: Parsed orchestration result / 解析されたオーケストレーション結果
            
        Raises:
            Exception: If parsing fails / 解析に失敗した場合
        """
        try:
            # If content is already a dict, validate it
            # contentが既に辞書の場合は検証
            if isinstance(content, dict):
                parsed_data = content
            elif isinstance(content, str):
                # Extract JSON from markdown codeblock if present
                # Markdownコードブロックが存在する場合はJSONを抽出
                json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', str(content), re.DOTALL)
                if json_match:
                    json_content = json_match.group(1).strip()
                else:
                    json_content = str(content).strip()
                
                # Parse JSON
                parsed_data = json.loads(json_content)
            else:
                # Try to convert to string and parse
                # 文字列に変換して解析を試行
                parsed_data = json.loads(str(content))
            
            # Validate required fields
            # 必須フィールドを検証
            required_fields = ["status", "result", "reasoning"]
            for field in required_fields:
                if field not in parsed_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate status field
            # statusフィールドを検証
            if parsed_data["status"] not in ["completed", "failed"]:
                raise ValueError(f"Invalid status value: {parsed_data['status']}. Must be 'completed' or 'failed'")
            
            # Ensure next_hint has proper structure if present
            # next_hintが存在する場合は適切な構造を確保
            if "next_hint" in parsed_data and parsed_data["next_hint"] is not None:
                next_hint = parsed_data["next_hint"]
                if not isinstance(next_hint, dict):
                    raise ValueError("next_hint must be a dictionary")
                # Set default values for optional fields
                # オプションフィールドのデフォルト値を設定
                if "confidence" not in next_hint:
                    next_hint["confidence"] = 0.5
                if "rationale" not in next_hint:
                    next_hint["rationale"] = ""
                # Validate confidence value
                # confidence値を検証
                try:
                    confidence = float(next_hint["confidence"])
                    if not 0 <= confidence <= 1:
                        next_hint["confidence"] = 0.5
                    else:
                        next_hint["confidence"] = confidence
                except (ValueError, TypeError):
                    next_hint["confidence"] = 0.5
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise Exception(f"Orchestration parsing error: {str(e)}")
    
    def __str__(self) -> str:
        return f"RefinireAgent(name={self.name}, model={self.model_name})"
    
    def __repr__(self) -> str:
        return self.__str__()
    


# Utility functions for common configurations
# 共通設定用のユーティリティ関数

def create_simple_agent(
    name: str,
    instructions: str,
    model: str = "gpt-4o-mini",
    **kwargs
) -> RefinireAgent:
    """
    Create a simple Refinire agent
    シンプルなRefinireエージェントを作成
    """
    return RefinireAgent(
        name=name,
        generation_instructions=instructions,
        model=model,
        **kwargs
    )


def create_evaluated_agent(
    name: str,
    generation_instructions: str,
    evaluation_instructions: str,
    model: str = "gpt-4o-mini",
    evaluation_model: Optional[str] = None,
    threshold: float = 85.0,
    **kwargs
) -> RefinireAgent:
    """
    Create a Refinire agent with evaluation
    評価機能付きRefinireエージェントを作成
    """
    return RefinireAgent(
        name=name,
        generation_instructions=generation_instructions,
        evaluation_instructions=evaluation_instructions,
        model=model,
        evaluation_model=evaluation_model,
        threshold=threshold,
        **kwargs
    )


def create_tool_enabled_agent(
    name: str,
    instructions: str,
    tools: Optional[List[callable]] = None,
    model: str = "gpt-4o-mini",
    **kwargs
) -> RefinireAgent:
    """
    Create a Refinire agent with automatic tool registration
    自動tool登録機能付きRefinireエージェントを作成
    
    Args:
        name: Agent name / エージェント名
        instructions: System instructions / システム指示
        tools: List of Python functions to register as tools / tool登録するPython関数のリスト
        model: LLM model name / LLMモデル名
        **kwargs: Additional arguments for RefinireAgent / RefinireAgent用追加引数
    
    Returns:
        RefinireAgent: Configured agent with tools / tool設定済みエージェント
    
    Example:
        >>> def get_weather(city: str) -> str:
        ...     '''Get weather for a city'''
        ...     return f"Weather in {city}: Sunny"
        ...
        >>> def calculate(expression: str) -> float:
        ...     '''Calculate mathematical expression'''
        ...     return eval(expression)
        ...
        >>> agent = create_tool_enabled_agent(
        ...     name="assistant",
        ...     instructions="You are a helpful assistant with access to tools.",
        ...     tools=[get_weather, calculate]
        ... )
        >>> result = agent.run("What's the weather in Tokyo and what's 2+2?")
    """
    return RefinireAgent(
        name=name,
        generation_instructions=instructions,
        model=model,
        tools=tools or [],  # Pass tools directly to constructor
        **kwargs
    )


def create_web_search_agent(
    name: str,
    instructions: str = "You are a helpful assistant with access to web search. Use web search when you need current information.",
    model: str = "gpt-4o-mini",
    **kwargs
) -> RefinireAgent:
    """
    Create a Refinire agent with web search capability
    Web検索機能付きRefinireエージェントを作成
    
    Note: This is a template - actual web search implementation would require
          integration with search APIs like Google Search API, Bing API, etc.
    注意：これはテンプレートです。実際のWeb検索実装には
          Google Search API、Bing APIなどとの統合が必要です。
    """
    def web_search(query: str) -> str:
        """Search the web for information (placeholder implementation)"""
        # This is a placeholder implementation
        # Real implementation would use actual search APIs
        return f"Web search results for '{query}': [This is a placeholder. Integrate with actual search API.]"
    
    return create_tool_enabled_agent(
        name=name,
        instructions=instructions,
        tools=[web_search],
        model=model,
        **kwargs
    )


def create_calculator_agent(
    name: str,
    instructions: str = "You are a helpful assistant with calculation capabilities. Use the calculator for mathematical computations.",
    model: str = "gpt-4o-mini",
    **kwargs
) -> RefinireAgent:
    """
    Create a Refinire agent with calculation capability
    計算機能付きRefinireエージェントを作成
    """
    def calculate(expression: str) -> float:
        """Calculate mathematical expression safely"""
        try:
            # For production, use a safer expression evaluator
            # 本番環境では、より安全な式評価器を使用
            import ast
            import operator
            
            # Allowed operations
            operators = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.Mod: operator.mod,
                ast.USub: operator.neg,
            }
            
            def eval_expr(expr):
                if isinstance(expr, ast.Num):
                    return expr.n
                elif isinstance(expr, ast.Constant):
                    return expr.value
                elif isinstance(expr, ast.BinOp):
                    return operators[type(expr.op)](eval_expr(expr.left), eval_expr(expr.right))
                elif isinstance(expr, ast.UnaryOp):
                    return operators[type(expr.op)](eval_expr(expr.operand))
                else:
                    raise TypeError(f"Unsupported operation: {type(expr)}")
            
            tree = ast.parse(expression, mode='eval')
            return eval_expr(tree.body)
            
        except Exception as e:
            return f"Error calculating '{expression}': {str(e)}"
    
    return create_tool_enabled_agent(
        name=name,
        instructions=instructions,
        tools=[calculate],
        model=model,
        **kwargs
    )


@dataclass
class InteractionQuestion:
    """
    Represents a question from the interactive pipeline
    対話的パイプラインからの質問を表現するクラス
    
    Attributes:
        question: The question text / 質問テキスト
        turn: Current turn number / 現在のターン番号
        remaining_turns: Remaining turns / 残りターン数
        metadata: Additional metadata / 追加メタデータ
    """
    question: str  # The question text / 質問テキスト
    turn: int  # Current turn number / 現在のターン番号
    remaining_turns: int  # Remaining turns / 残りターン数
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata / 追加メタデータ
    
    def __str__(self) -> str:
        """
        String representation of the interaction question
        対話質問の文字列表現
        
        Returns:
            str: Formatted question with turn info / ターン情報付きフォーマット済み質問
        """
        return f"[Turn {self.turn}/{self.turn + self.remaining_turns}] {self.question}"


@dataclass
class InteractionResult:
    """
    Result from interactive pipeline execution
    対話的パイプライン実行の結果
    
    Attributes:
        is_complete: True if interaction is complete / 対話が完了した場合True
        content: Result content or next question / 結果コンテンツまたは次の質問
        turn: Current turn number / 現在のターン番号
        remaining_turns: Remaining turns / 残りターン数
        success: Whether execution was successful / 実行が成功したか
        metadata: Additional metadata / 追加メタデータ
    """
    is_complete: bool  # True if interaction is complete / 対話が完了した場合True
    content: Any  # Result content or next question / 結果コンテンツまたは次の質問
    turn: int  # Current turn number / 現在のターン番号
    remaining_turns: int  # Remaining turns / 残りターン数
    success: bool = True  # Whether execution was successful / 実行が成功したか
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata / 追加メタデータ


class InteractiveAgent(RefinireAgent):
    """
    Interactive Agent for multi-turn conversations using RefinireAgent
    RefinireAgentを使用した複数ターン会話のための対話的エージェント
    
    This class extends RefinireAgent to handle:
    このクラスはRefinireAgentを拡張して以下を処理します：
    - Multi-turn interactive conversations / 複数ターンの対話的会話
    - Completion condition checking / 完了条件のチェック
    - Turn management / ターン管理
    - Conversation history tracking / 会話履歴の追跡
    
    The agent uses a completion check function to determine when the interaction is finished.
    エージェントは完了チェック関数を使用して対話の終了時期を判定します。
    """
    
    def __init__(
        self,
        name: str,
        generation_instructions: str,
        completion_check: Callable[[Any], bool],
        max_turns: int = 20,
        evaluation_instructions: Optional[str] = None,
        question_format: Optional[Callable[[str, int, int], str]] = None,
        **kwargs
    ) -> None:
        """
        Initialize the InteractiveAgent
        InteractiveAgentを初期化する
        
        Args:
            name: Agent name / エージェント名
            generation_instructions: System prompt for generation / 生成用システムプロンプト
            completion_check: Function to check if interaction is complete / 対話完了チェック関数
            max_turns: Maximum number of interaction turns / 最大対話ターン数
            evaluation_instructions: System prompt for evaluation / 評価用システムプロンプト
            question_format: Optional function to format questions / 質問フォーマット関数（任意）
            **kwargs: Additional arguments for RefinireAgent / RefinireAgent用追加引数
        """
        # Initialize base RefinireAgent
        # ベースのRefinireAgentを初期化
        super().__init__(
            name=name,
            generation_instructions=generation_instructions,
            evaluation_instructions=evaluation_instructions,
            **kwargs
        )
        
        # Interactive-specific configuration
        # 対話固有の設定
        self.completion_check = completion_check
        self.max_turns = max_turns
        self.question_format = question_format or self._default_question_format
        
        # Interaction state
        # 対話状態
        self._turn_count = 0
        self._conversation_history: List[Dict[str, Any]] = []
        self._is_complete = False
        self._final_result: Any = None
    
    def run_interactive(self, initial_input: str) -> InteractionResult:
        """
        Start an interactive conversation
        対話的会話を開始する
        
        Args:
            initial_input: Initial user input / 初期ユーザー入力
            
        Returns:
            InteractionResult: Initial interaction result / 初期対話結果
        """
        self.reset_interaction()
        return self.continue_interaction(initial_input)
    
    def continue_interaction(self, user_input: str) -> InteractionResult:
        """
        Continue the interactive conversation with user input
        ユーザー入力で対話的会話を継続する
        
        Args:
            user_input: User input for this turn / このターンのユーザー入力
            
        Returns:
            InteractionResult: Interaction result / 対話結果
        """
        # Check if max turns reached
        # 最大ターン数に達したかを確認
        if self._turn_count >= self.max_turns:
            return InteractionResult(
                is_complete=True,
                content=self._final_result,
                turn=self._turn_count,
                remaining_turns=0,
                success=False,
                metadata={"error": "Maximum turns reached"}
            )
        
        return self._process_turn(user_input)
    
    def _process_turn(self, user_input: str) -> InteractionResult:
        """
        Process a single turn of interaction
        単一ターンの対話を処理する
        
        Args:
            user_input: User input text / ユーザー入力テキスト
            
        Returns:
            InteractionResult: Turn result / ターン結果
        """
        try:
            # Increment turn count
            # ターン数を増加
            self._turn_count += 1
            
            # Build context with conversation history
            # 会話履歴でコンテキストを構築
            context_prompt = self._build_interaction_context()
            full_input = f"{context_prompt}\n\nCurrent user input: {user_input}"
            
            # Run the RefinireAgent
            # RefinireAgentを実行
            llm_result = super().run(full_input)
            
            # Store interaction in history
            # 対話を履歴に保存
            self._store_turn(user_input, llm_result)
            
            if not llm_result.success:
                # Handle LLM execution failure
                # LLM実行失敗を処理
                return InteractionResult(
                    is_complete=False,
                    content=InteractionQuestion(
                        question="Sorry, I encountered an error. Please try again.",
                        turn=self._turn_count,
                        remaining_turns=max(0, self.max_turns - self._turn_count),
                        metadata=llm_result.metadata
                    ),
                    turn=self._turn_count,
                    remaining_turns=max(0, self.max_turns - self._turn_count),
                    success=False,
                    metadata=llm_result.metadata
                )
            
            # Check if interaction is complete using completion check function
            # 完了チェック関数を使用して対話完了を確認
            if self.completion_check(llm_result.content):
                # Interaction complete
                # 対話完了
                self._is_complete = True
                self._final_result = llm_result.content
                
                return InteractionResult(
                    is_complete=True,
                    content=llm_result.content,
                    turn=self._turn_count,
                    remaining_turns=0,
                    success=True,
                    metadata=llm_result.metadata
                )
            else:
                # Check if max turns reached after this turn
                # このターン後に最大ターン数に達したかを確認
                if self._turn_count >= self.max_turns:
                    # Force completion due to max turns
                    # 最大ターン数により強制完了
                    self._is_complete = True
                    self._final_result = llm_result.content
                    
                    return InteractionResult(
                        is_complete=True,
                        content=llm_result.content,
                        turn=self._turn_count,
                        remaining_turns=0,
                        success=True,
                        metadata=llm_result.metadata
                    )
                
                # Continue interaction - format as question
                # 対話継続 - 質問としてフォーマット
                question_text = self.question_format(
                    str(llm_result.content),
                    self._turn_count,
                    max(0, self.max_turns - self._turn_count)
                )
                
                question = InteractionQuestion(
                    question=question_text,
                    turn=self._turn_count,
                    remaining_turns=max(0, self.max_turns - self._turn_count),
                    metadata=llm_result.metadata
                )
                
                return InteractionResult(
                    is_complete=False,
                    content=question,
                    turn=self._turn_count,
                    remaining_turns=max(0, self.max_turns - self._turn_count),
                    success=True,
                    metadata=llm_result.metadata
                )
                
        except Exception as e:
            # Handle errors gracefully
            # エラーを適切に処理
            return InteractionResult(
                is_complete=False,
                content=InteractionQuestion(
                    question=f"An error occurred: {str(e)}. Please try again.",
                    turn=self._turn_count,
                    remaining_turns=max(0, self.max_turns - self._turn_count),
                    metadata={"error": str(e)}
                ),
                turn=self._turn_count,
                remaining_turns=max(0, self.max_turns - self._turn_count),
                success=False,
                metadata={"error": str(e)}
            )
    
    def _build_interaction_context(self) -> str:
        """
        Build interaction context from conversation history
        会話履歴から対話コンテキストを構築する
        
        Returns:
            str: Conversation context / 会話コンテキスト
        """
        if not self._conversation_history:
            return "This is the beginning of the conversation."
        
        context_parts = ["Previous conversation:"]
        for i, interaction in enumerate(self._conversation_history, 1):
            user_input = interaction.get('user_input', '')
            ai_response = str(interaction.get('ai_result', {}).get('content', ''))
            context_parts.append(f"{i}. User: {user_input}")
            context_parts.append(f"   Assistant: {ai_response}")
        
        return "\n".join(context_parts)
    
    def _store_turn(self, user_input: str, llm_result: LLMResult) -> None:
        """
        Store interaction turn in conversation history
        対話ターンを会話履歴に保存する
        
        Args:
            user_input: User input / ユーザー入力
            llm_result: LLM result / LLM結果
        """
        # Get timestamp safely
        try:
            timestamp = asyncio.get_event_loop().time()
        except RuntimeError:
            # Fallback to regular time if no event loop is running
            import time
            timestamp = time.time()
            
        interaction = {
            'user_input': user_input,
            'ai_result': {
                'content': llm_result.content,
                'success': llm_result.success,
                'metadata': llm_result.metadata
            },
            'turn': self._turn_count,
            'timestamp': timestamp
        }
        self._conversation_history.append(interaction)
    
    def _default_question_format(self, response: str, turn: int, remaining: int) -> str:
        """
        Default question formatting function
        デフォルト質問フォーマット関数
        
        Args:
            response: AI response / AI応答
            turn: Current turn / 現在のターン
            remaining: Remaining turns / 残りターン
            
        Returns:
            str: Formatted question / フォーマット済み質問
        """
        return f"[Turn {turn}] {response}"
    
    def reset_interaction(self) -> None:
        """
        Reset the interaction session
        対話セッションをリセットする
        """
        self._turn_count = 0
        self._conversation_history = []
        self._is_complete = False
        self._final_result = None
    
    @property
    def is_complete(self) -> bool:
        """
        Check if interaction is complete
        対話が完了しているかを確認する
        
        Returns:
            bool: True if complete / 完了している場合True
        """
        return self._is_complete
    
    @property
    def current_turn(self) -> int:
        """
        Get current turn number
        現在のターン番号を取得する
        
        Returns:
            int: Current turn / 現在のターン
        """
        return self._turn_count
    
    @property
    def remaining_turns(self) -> int:
        """
        Get remaining turns
        残りターン数を取得する
        
        Returns:
            int: Remaining turns / 残りターン数
        """
        return max(0, self.max_turns - self._turn_count)
    
    @property
    def interaction_history(self) -> List[Dict[str, Any]]:
        """
        Get interaction history
        対話履歴を取得する
        
        Returns:
            List[Dict[str, Any]]: Interaction history / 対話履歴
        """
        return self._conversation_history.copy()
    
    @property
    def final_result(self) -> Any:
        """
        Get final result if interaction is complete
        対話完了の場合は最終結果を取得する
        
        Returns:
            Any: Final result or None / 最終結果またはNone
        """
        return self._final_result if self._is_complete else None


def create_simple_interactive_agent(
    name: str,
    instructions: str,
    completion_check: Callable[[Any], bool],
    max_turns: int = 20,
    model: str = "gpt-4o-mini",
    **kwargs
) -> InteractiveAgent:
    """
    Create a simple InteractiveAgent with basic configuration
    基本設定でシンプルなInteractiveAgentを作成する
    
    Args:
        name: Agent name / エージェント名
        instructions: Generation instructions / 生成指示
        completion_check: Function to check completion / 完了チェック関数
        max_turns: Maximum interaction turns / 最大対話ターン数
        model: LLM model name / LLMモデル名
        **kwargs: Additional arguments / 追加引数
        
    Returns:
        InteractiveAgent: Configured agent / 設定済みエージェント
    """
    return InteractiveAgent(
        name=name,
        generation_instructions=instructions,
        completion_check=completion_check,
        max_turns=max_turns,
        model=model,
        **kwargs
    )


def create_evaluated_interactive_agent(
    name: str,
    generation_instructions: str,
    evaluation_instructions: str,
    completion_check: Callable[[Any], bool],
    max_turns: int = 20,
    model: str = "gpt-4o-mini",
    evaluation_model: Optional[str] = None,
    threshold: float = 85.0,
    **kwargs
) -> InteractiveAgent:
    """
    Create an InteractiveAgent with evaluation capabilities
    評価機能付きInteractiveAgentを作成する
    
    Args:
        name: Agent name / エージェント名
        generation_instructions: Generation instructions / 生成指示
        evaluation_instructions: Evaluation instructions / 評価指示
        completion_check: Function to check completion / 完了チェック関数
        max_turns: Maximum interaction turns / 最大対話ターン数
        model: LLM model name / LLMモデル名
        evaluation_model: Evaluation model name / 評価モデル名
        threshold: Evaluation threshold / 評価閾値
        **kwargs: Additional arguments / 追加引数
        
    Returns:
        InteractiveAgent: Configured agent / 設定済みエージェント
    """
    return InteractiveAgent(
        name=name,
        generation_instructions=generation_instructions,
        evaluation_instructions=evaluation_instructions,
        completion_check=completion_check,
        max_turns=max_turns,
        model=model,
        evaluation_model=evaluation_model,
        threshold=threshold,
        **kwargs
    )


# Flow integration utility functions
# Flow統合用ユーティリティ関数

def create_flow_agent(
    name: str,
    instructions: str,
    next_step: Optional[str] = None,
    model: str = "gpt-4o-mini",
    store_result_key: Optional[str] = None,
    **kwargs
) -> RefinireAgent:
    """
    Create a RefinireAgent configured for Flow integration
    Flow統合用に設定されたRefinireAgentを作成
    
    Args:
        name: Agent name / エージェント名
        instructions: Generation instructions / 生成指示
        next_step: Next step for Flow routing / Flow ルーティング用次ステップ
        model: LLM model name / LLMモデル名
        store_result_key: Key to store result in Flow context / Flow context内での結果保存キー
        **kwargs: Additional RefinireAgent parameters / 追加のRefinireAgentパラメータ
    
    Returns:
        RefinireAgent: Flow-enabled agent / Flow対応エージェント
    """
    return RefinireAgent(
        name=name,
        generation_instructions=instructions,
        model=model,
        next_step=next_step,
        store_result_key=store_result_key,
        **kwargs
    )


def create_evaluated_flow_agent(
    name: str,
    generation_instructions: str,
    evaluation_instructions: str,
    next_step: Optional[str] = None,
    model: str = "gpt-4o-mini",
    evaluation_model: Optional[str] = None,
    threshold: float = 85.0,
    store_result_key: Optional[str] = None,
    **kwargs
) -> RefinireAgent:
    """
    Create a RefinireAgent with evaluation for Flow integration
    Flow統合用評価機能付きRefinireAgentを作成
    
    Args:
        name: Agent name / エージェント名
        generation_instructions: Generation instructions / 生成指示
        evaluation_instructions: Evaluation instructions / 評価指示
        next_step: Next step for Flow routing / Flow ルーティング用次ステップ
        model: LLM model name / LLMモデル名
        evaluation_model: Evaluation model name / 評価モデル名
        threshold: Evaluation threshold / 評価閾値
        store_result_key: Key to store result in Flow context / Flow context内での結果保存キー
        **kwargs: Additional RefinireAgent parameters / 追加のRefinireAgentパラメータ
    
    Returns:
        RefinireAgent: Flow-enabled agent with evaluation / 評価機能付きFlow対応エージェント
    """
    return RefinireAgent(
        name=name,
        generation_instructions=generation_instructions,
        evaluation_instructions=evaluation_instructions,
        model=model,
        evaluation_model=evaluation_model,
        threshold=threshold,
        next_step=next_step,
        store_result_key=store_result_key,
        **kwargs
    ) 


# Note: RefinireAgent now inherits from Step directly
# 注意: RefinireAgentは現在、Stepを直接継承しています
# No wrapper class needed - use RefinireAgent directly in Flow workflows
# ラッパークラスは不要 - FlowワークフローでRefinireAgentを直接使用してください
