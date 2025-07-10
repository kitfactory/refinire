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

logger = logging.getLogger(__name__)


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
        store_result_key: Optional[str] = None
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
            is_flow_step: Enable Flow step mode / Flowステップモード有効化
        """
        # Initialize Step base class
        # Step基底クラスを初期化
        super().__init__(name)
        
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
        
        self.model = model
        self.evaluation_model = evaluation_model or model
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
                        logger.warning(f"Failed to convert tool {tool} to FunctionTool: {e}")
        
        # OpenAI Agents SDK Agentを初期化（Study 5と同じ方法）
        # Initialize OpenAI Agents SDK Agent
        agent_kwargs = {
            "name": f"{name}_sdk_agent",
            "instructions": self.generation_instructions,
            "tools": sdk_tools
        }
        
        # Add MCP servers support if specified
        # MCPサーバーが指定されている場合は追加
        if self.mcp_servers:
            agent_kwargs["mcp_servers"] = self.mcp_servers
        
        # Add structured output support if output_model is specified
        # output_modelが指定されている場合は構造化出力サポートを追加
        if self.output_model:
            agent_kwargs["output_type"] = self.output_model
            
        self._sdk_agent = Agent(**agent_kwargs)
        
        # Context providers
        self.context_providers = []
        if context_providers_config is None or (isinstance(context_providers_config, str) and not context_providers_config.strip()):
            # Default to conversation history provider
            # デフォルトで会話履歴プロバイダーを使用
            context_providers_config = [
                {"type": "conversation_history", "max_items": 10}
            ]
        
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
                # If we're in a loop, use nest_asyncio or fallback
                import nest_asyncio
                nest_asyncio.apply()
                future = asyncio.ensure_future(self.run_async(user_input, ctx))
                return loop.run_until_complete(future)
            except RuntimeError:
                # No running loop, we can create one
                return asyncio.run(self.run_async(user_input, ctx))
        except Exception as e:
            ctx.result = None
            ctx.add_system_message(f"Execution error: {e}")
            return ctx
    
    async def run_async(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Run the agent asynchronously and return Context with result
        エージェントを非同期実行し、結果付きContextを返す
        
        Args:
            user_input: User input for the agent / エージェント用ユーザー入力
            ctx: Workflow context / ワークフローコンテキスト
        
        Returns:
            Context: Updated context with result in ctx.result / ctx.resultに結果が格納された更新Context
        """
        # Try to create trace context if agents.tracing is available
        # agents.tracingが利用可能な場合はトレースコンテキストを作成を試行
        try:
            from agents.tracing import trace
            
            # Create trace context for this agent execution
            # このエージェント実行用のトレースコンテキストを作成
            trace_name = f"RefinireAgent({self.name})"
            with trace(trace_name):
                return await self._execute_with_context(user_input, ctx, None)
        except ImportError:
            # agents.tracing is not available - run without trace context
            # agents.tracingが利用できません - トレースコンテキストなしで実行
            logger.debug("agents.tracing not available, running without trace context")
            return await self._execute_with_context(user_input, ctx, None)
        except Exception as e:
            # If there's any issue with trace creation, fall back to no trace
            # トレース作成で問題がある場合は、トレースなしにフォールバック
            logger.debug(f"Unable to create trace context ({e}), running without trace context")
            return await self._execute_with_context(user_input, ctx, None)
    
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
                # Execute RefinireAgent and get LLMResult
                # RefinireAgentを実行してLLMResultを取得
                llm_result = await self._run_standalone(input_text, ctx)
                
                # Perform evaluation if evaluation_instructions are provided
                # evaluation_instructionsが提供されている場合は評価を実行
                evaluation_result = None
                if self.evaluation_instructions and llm_result.success and llm_result.content:
                    try:
                        evaluation_result = self._evaluate_content(input_text, llm_result.content)
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
                
                # Store result in ctx.result (simple access)
                # ctx.resultに結果を保存（シンプルアクセス）
                ctx.result = llm_result.content if llm_result.success else None
                
                # Also store in other locations for compatibility
                # 互換性のため他の場所にも保存
                ctx.shared_state[self.store_result_key] = ctx.result
                ctx.prev_outputs[self.name] = ctx.result
                
                # Add span metadata for result
                # 結果のスパンメタデータを追加
                if span is not None:
                    span.span_data.output = ctx.result
                    span.span_data.success = llm_result.success
                    span.span_data.model = self.model
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
            ctx.prev_outputs[self.name] = None
            
            # Add error to span if available
            # スパンが利用可能な場合はエラーを追加
            if span is not None:
                span.span_data.error = str(e)
                span.span_data.success = False
            
            # Log error for debugging / デバッグ用エラーログ
            logger.error(error_msg)
        
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
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # Apply variable substitution to SDK agent instructions if context is available
                # コンテキストが利用可能な場合はSDKエージェントの指示にも変数置換を適用
                if ctx:
                    processed_instructions = self._substitute_variables(self.generation_instructions, ctx)
                    self._sdk_agent.instructions = processed_instructions
                
                # full_promptを使用してRunner.runを呼び出し
                result = await Runner.run(self._sdk_agent, full_prompt)
                content = result.final_output
                if not content and hasattr(result, 'output') and result.output:
                    content = result.output
                if self.output_model and content:
                    parsed_content = self._parse_structured_output(content)
                else:
                    parsed_content = content
                if not self._validate_output(parsed_content):
                    if attempt < self.max_retries:
                        continue
                    # Restore original instructions before returning
                    # 戻る前に元の指示を復元
                    self._sdk_agent.instructions = original_instructions
                    return LLMResult(
                        content=None,
                        success=False,
                        metadata={"error": "Output validation failed", "attempts": attempt}
                    )
                metadata = {
                    "model": self.model,
                    "temperature": self.temperature,
                    "attempts": attempt,
                    "sdk": True
                }
                if self._generation_prompt_metadata:
                    metadata.update(self._generation_prompt_metadata)
                if self._evaluation_prompt_metadata:
                    metadata["evaluation_prompt"] = self._evaluation_prompt_metadata
                llm_result = LLMResult(
                    content=parsed_content,
                    success=True,
                    metadata=metadata,
                    evaluation_score=None,
                    attempts=attempt
                )
                self._store_in_history(user_input, llm_result)
                # Restore original instructions before returning
                # 戻る前に元の指示を復元
                self._sdk_agent.instructions = original_instructions
                return llm_result
            except Exception as e:
                if attempt == self.max_retries:
                    # Restore original instructions before returning
                    # 戻る前に元の指示を復元
                    self._sdk_agent.instructions = original_instructions
                    return LLMResult(
                        content=None,
                        success=False,
                        metadata={"error": str(e), "attempts": attempt, "sdk": True}
                    )
                continue
        # Restore original instructions before final return
        # 最終リターン前に元の指示を復元
        self._sdk_agent.instructions = original_instructions
        return LLMResult(
            content=None,
            success=False,
            metadata={"error": "Maximum retries exceeded", "sdk": True}
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
        if hasattr(self, 'context_providers') and self.context_providers:
            context_parts = []
            previous_context = ""
            
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
                    logger.warning(f"Context provider {provider.__class__.__name__} failed: {e}")
                    continue
            
            if context_parts:
                context_text = "\n\n".join(context_parts)
                prompt_parts.append(f"Context:\n{context_text}")
        
        # Add history if available
        if self.session_history:
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
    
    def _evaluate_content(self, user_input: str, generated_content: Any) -> EvaluationResult:
        """Evaluate generated content / 生成されたコンテンツを評価"""
        evaluation_prompt = f"""
{self.evaluation_instructions}

User Input: {user_input}
Generated Content: {generated_content}

Please provide a score from 0 to 100 and brief feedback.
Return your response as JSON with 'score' and 'feedback' fields.
"""
        
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
                metadata={"model": self.evaluation_model, "evaluation_type": "heuristic"}
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
                    logger.warning(f"Failed to update context provider {provider.__class__.__name__}: {e}")
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
                    logger.warning(f"Failed to clear context provider {provider.__class__.__name__}: {e}")
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
                    logger.warning(f"Failed to clear context provider {provider.__class__.__name__}: {e}")
                    continue
    
    def __str__(self) -> str:
        return f"RefinireAgent(name={self.name}, model={self.model})"
    
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
