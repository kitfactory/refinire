"""Refinire Agent - A powerful AI agent with built-in evaluation and tool support.

Refinireエージェント - 組み込み評価とツールサポートを備えた強力なAIエージェント。
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Callable, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import warnings

try:
    from openai import OpenAI, AsyncOpenAI
    from pydantic import BaseModel
except ImportError as e:
    raise ImportError(f"Required dependencies not found: {e}. Please install openai and pydantic.")

try:
    from agents import Agent, Runner, function_tool
except ImportError as e:
    raise ImportError(f"OpenAI Agents SDK not found: {e}. Please install openai-agents.")

try:
    from ...core.prompt_store import PromptReference
except ImportError:
    PromptReference = None

from agents.tool import FunctionTool


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


class RefinireAgent:
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
        tools: Optional[List[Dict]] = None,
        mcp_servers: Optional[List[str]] = None
    ) -> None:
        """
        Initialize Refinire Agent
        Refinireエージェントを初期化する
        
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
        """
        # Basic configuration
        self.name = name
        
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
        
        # Tools and MCP support
        self.tools = tools or []
        self.mcp_servers = mcp_servers or []
        self.tool_handlers = {}  # Initialize tool handlers dictionary
        
        # Initialize OpenAI Agents SDK Agent
        # OpenAI Agents SDK Agentを初期化
        self._sdk_tools = []
        
        # Process tools if provided
        # ツールが提供されている場合は処理
        if tools:
            for i, tool in enumerate(tools):
                if callable(tool) or isinstance(tool, FunctionTool):
                    self._sdk_tools.append(tool)
                elif isinstance(tool, dict):
                    self.add_tool(tool)
        
        # Create SDK agent with tools
        # ツール付きでSDKエージェントを作成
        self._sdk_agent = Agent(
            name=f"{name}_sdk_agent",
            instructions=self.generation_instructions,
            tools=self._sdk_tools
        )
        
        # Initialize OpenAI clients for fallback
        # フォールバック用のOpenAIクライアントを初期化
        self.sync_client = OpenAI()
        self.async_client = AsyncOpenAI()
    
    def run(self, user_input: str) -> LLMResult:
        """
        Run the agent synchronously by waiting for async completion
        非同期完了を待ってエージェントを同期的に実行する
        
        Args:
            user_input: User input / ユーザー入力
            
        Returns:
            LLMResult: Generation result / 生成結果
        """
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # If we're in a loop, use nest_asyncio or fallback
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                    future = asyncio.ensure_future(self.run_async(user_input))
                    return loop.run_until_complete(future)
                except ImportError:
                    # Fallback to direct API if nest_asyncio not available
                    return self._generate_content_fallback_with_retries(user_input)
            except RuntimeError:
                # No running loop, we can create one
                return asyncio.run(self.run_async(user_input))
        except Exception as e:
            # Fallback to direct API if async method fails
            warnings.warn(f"Async execution failed, falling back to direct API: {e}")
            return self._generate_content_fallback_with_retries(user_input)
    
    def _generate_content_fallback_with_retries(self, user_input: str) -> LLMResult:
        """
        Fallback generation with retries using direct API
        直接APIを使用したリトライ付きフォールバック生成
        """
        full_prompt = self._build_prompt(user_input)
        
        for attempt in range(1, self.max_retries + 1):
            try:
                generation_result = self._generate_content_fallback(full_prompt)
                
                # Output validation
                if not self._validate_output(generation_result):
                    if attempt < self.max_retries:
                        continue
                    return LLMResult(
                        content=None,
                        success=False,
                        metadata={"error": "Output validation failed", "attempts": attempt, "fallback": True}
                    )
                
                # Parse structured output if model specified
                parsed_content = self._parse_structured_output(generation_result)
                
                # Evaluate if evaluation instructions provided
                evaluation_result = None
                if self.evaluation_instructions:
                    evaluation_result = self._evaluate_content(user_input, parsed_content)
                    
                    # Check if evaluation passed
                    if not evaluation_result.passed and attempt < self.max_retries:
                        # Generate improvement if callback provided
                        if self.improvement_callback:
                            improvement = self.improvement_callback(
                                LLMResult(content=parsed_content, success=True),
                                evaluation_result
                            )
                            full_prompt = f"{full_prompt}\n\nImprovement needed: {improvement}"
                        continue
                
                # Success - store in history and return
                metadata = {
                    "model": self.model,
                    "temperature": self.temperature,
                    "attempts": attempt,
                    "fallback": True
                }
                
                result = LLMResult(
                    content=parsed_content,
                    success=True,
                    metadata=metadata,
                    evaluation_score=evaluation_result.score if evaluation_result else None,
                    attempts=attempt
                )
                self._store_in_history(user_input, result)
                return result
                
            except Exception as e:
                if attempt == self.max_retries:
                    return LLMResult(
                        content=None,
                        success=False,
                        metadata={"error": str(e), "attempts": attempt, "fallback": True}
                    )
                continue
        
        # Should not reach here
        return LLMResult(
            content=None,
            success=False,
            metadata={"error": "Maximum retries exceeded", "fallback": True}
        )
    
    async def run_async(self, user_input: str) -> LLMResult:
        print("run_async entered")
        # Debug: Check SDK tools at the start of run_async
        # デバッグ: run_async開始時のSDKツールを確認
        print(f"🔍 DEBUG: run_async - SDK tools count: {len(self._sdk_tools)}")
        for i, tool in enumerate(self._sdk_tools):
            print(f"🔍 DEBUG: run_async - SDK tool {i+1}: {getattr(tool, 'name', getattr(tool, '__name__', 'unknown'))} - {type(tool)}")
        
        # Input validation
        if not self._validate_input(user_input):
            return LLMResult(
                content=None,
                success=False,
                metadata={"error": "Input validation failed", "input": user_input}
            )
        
        # Build prompt with history
        if self._sdk_tools:
            # If tools are available, use only user input (instructions are in Agent)
            # ツールが利用可能な場合、ユーザー入力のみを使用（指示文はAgentに含まれる）
            full_prompt = user_input
            print(f"🔍 DEBUG: Using {len(self._sdk_tools)} SDK tools")
            for i, tool in enumerate(self._sdk_tools):
                print(f"🔍 DEBUG: Tool {i+1}: {getattr(tool, '__name__', 'unknown')}")
        else:
            # For non-tool agents, include history but not instructions (Agent already has them)
            # ツールなしエージェントの場合は履歴を含めるが指示文は除く（Agentは既に持っている）
            full_prompt = self._build_prompt(user_input, include_instructions=False)
            print(f"🔍 DEBUG: No SDK tools available")
        
        # Debug output
        print(f"🔍 DEBUG: Full prompt sent to SDK: {full_prompt}")
        print(f"🔍 DEBUG: Agent instructions: {getattr(self._sdk_agent, 'instructions', 'No instructions')}")
        print(f"🔍 DEBUG: Agent tools count: {len(getattr(self._sdk_agent, 'tools', []))}")
        
        # Generation with retries using OpenAI Agents SDK
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"🔍 DEBUG: Attempt {attempt}/{self.max_retries}")
                # Use OpenAI Agents SDK Runner
                result = await Runner.run(self._sdk_agent, full_prompt)
                
                # Debug the result structure
                print(f"🔍 DEBUG: Result type: {type(result)}")
                print(f"🔍 DEBUG: Result attributes: {dir(result)}")
                print(f"🔍 DEBUG: Result final_output: {result.final_output}")
                if hasattr(result, 'output'):
                    print(f"🔍 DEBUG: Result output: {result.output}")
                if hasattr(result, 'steps'):
                    print(f"🔍 DEBUG: Result steps count: {len(result.steps) if result.steps else 0}")
                    for i, step in enumerate(result.steps or []):
                        print(f"🔍 DEBUG: Step {i}: {type(step)} - {getattr(step, 'type', 'unknown')}")
                
                # Extract content from result
                content = result.final_output
                if not content and hasattr(result, 'output') and result.output:
                    content = result.output
                
                print(f"🔍 DEBUG: Attempt {attempt} result: {content}")
                
                # Parse structured output if model specified
                if self.output_model and content:
                    parsed_content = self._parse_structured_output(content)
                else:
                    parsed_content = content
                
                # Output validation
                if not self._validate_output(parsed_content):
                    print(f"🔍 DEBUG: Attempt {attempt} failed validation")
                    if attempt < self.max_retries:
                        continue
                    return LLMResult(
                        content=None,
                        success=False,
                        metadata={"error": "Output validation failed", "attempts": attempt}
                    )
                
                # Evaluate if evaluation instructions provided
                evaluation_result = None
                if self.evaluation_instructions:
                    evaluation_result = self._evaluate_content(user_input, parsed_content)
                    
                    # Check if evaluation passed
                    if not evaluation_result.passed and attempt < self.max_retries:
                        print(f"🔍 DEBUG: Attempt {attempt} failed evaluation")
                        # Generate improvement if callback provided
                        if self.improvement_callback:
                            improvement = self.improvement_callback(
                                LLMResult(content=parsed_content, success=True),
                                evaluation_result
                            )
                            full_prompt = f"{full_prompt}\n\nImprovement needed: {improvement}"
                        continue
                
                print(f"🔍 DEBUG: Attempt {attempt} succeeded")
                # Success - store in history and return
                metadata = {
                    "model": self.model,
                    "temperature": self.temperature,
                    "attempts": attempt,
                    "sdk": True
                }
                
                # Add prompt metadata if available
                if self._generation_prompt_metadata:
                    metadata.update(self._generation_prompt_metadata)
                
                if self._evaluation_prompt_metadata:
                    metadata["evaluation_prompt"] = self._evaluation_prompt_metadata
                
                llm_result = LLMResult(
                    content=parsed_content,
                    success=True,
                    metadata=metadata,
                    evaluation_score=evaluation_result.score if evaluation_result else None,
                    attempts=attempt
                )
                self._store_in_history(user_input, llm_result)
                
                return llm_result
                
            except Exception as e:
                if attempt == self.max_retries:
                    return LLMResult(
                        content=None,
                        success=False,
                        metadata={"error": str(e), "attempts": attempt, "sdk": True}
                    )
                continue
        
        # Should not reach here
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
    
    def _build_prompt(self, user_input: str, include_instructions: bool = True) -> str:
        """
        Build complete prompt with instructions and history
        指示と履歴を含む完全なプロンプトを構築
        
        Args:
            user_input: User input / ユーザー入力
            include_instructions: Whether to include instructions (for OpenAI Agents SDK, set to False)
            include_instructions: 指示文を含めるかどうか（OpenAI Agents SDKの場合はFalse）
        """
        prompt_parts = []
        
        # Add instructions only if requested (not for OpenAI Agents SDK)
        # 要求された場合のみ指示文を追加（OpenAI Agents SDKの場合は除く）
        if include_instructions:
            prompt_parts.append(self.generation_instructions)
        
        # Add history if available
        if self.session_history:
            history_text = "\n".join(self.session_history[-self.history_size:])
            prompt_parts.append(f"Previous context:\n{history_text}")
        
        prompt_parts.append(f"User input: {user_input}")
        
        return "\n\n".join(prompt_parts)
    
    def _generate_content_with_sdk(self, prompt: str) -> str:
        """
        Generate content using OpenAI Agents SDK Runner
        OpenAI Agents SDK Runnerを使用したコンテンツ生成
        
        Args:
            prompt: Input prompt / 入力プロンプト
            
        Returns:
            str: Generated content / 生成されたコンテンツ
        """
        try:
            # Create new event loop for SDK
            # SDK用に新しいイベントループを作成
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(Runner.run(self._sdk_agent, prompt))
                return result.final_output or ""
            finally:
                loop.close()
                
        except Exception as e:
            # Fallback to original implementation if SDK fails
            # SDKが失敗した場合は元の実装にフォールバック
            warnings.warn(f"OpenAI Agents SDK failed, falling back to direct API: {e}")
            return self._generate_content_fallback(prompt)
    
    def _generate_content(self, prompt: str) -> str:
        """Generate content using OpenAI Agents SDK / OpenAI Agents SDKを使用したコンテンツ生成"""
        try:
            # Use OpenAI Agents SDK Agent for generation
            # OpenAI Agents SDK Agentを使用して生成
            # Check if we're already in an event loop
            # 既にイベントループ内にいるかチェック
            try:
                loop = asyncio.get_running_loop()
                # If we're in a loop, use the fallback
                # ループ内にいる場合はフォールバックを使用
                return self._generate_content_fallback(prompt)
            except RuntimeError:
                # No running loop, we can create one
                # 実行中のループがない場合、作成可能
                pass
            
            # Create new event loop for SDK
            # SDK用に新しいイベントループを作成
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(Runner.run(self._sdk_agent, prompt))
                return result.final_output or ""
            finally:
                loop.close()
                
        except Exception as e:
            # Fallback to original implementation if SDK fails
            # SDKが失敗した場合は元の実装にフォールバック
            warnings.warn(f"OpenAI Agents SDK failed, falling back to direct API: {e}")
            return self._generate_content_fallback(prompt)
    
    def _generate_content_fallback(self, prompt: str) -> str:
        """Fallback content generation using direct OpenAI API / 直接OpenAI APIを使用したフォールバックコンテンツ生成"""
        messages = [{"role": "user", "content": prompt}]
        
        # Tools/function calling loop
        # Tools/function calling ループ
        max_tool_iterations = 10  # Prevent infinite loops / 無限ループを防ぐ
        iteration = 0
        
        while iteration < max_tool_iterations:
            # Prepare API call parameters
            # API呼び出しパラメータを準備
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "timeout": self.timeout
            }
            
            if self.max_tokens:
                params["max_tokens"] = self.max_tokens
            
            # Add tools if available
            # toolsが利用可能な場合は追加
            if self.tools:
                # Convert tools to OpenAI API format
                # toolsをOpenAI API形式に変換
                openai_tools = []
                for tool in self.tools:
                    if tool.get("type") == "function" and "function" in tool:
                        # Ensure all parameters have type information
                        # すべてのパラメータに型情報があることを確認
                        function_def = tool["function"].copy()
                        if "parameters" in function_def:
                            parameters = function_def["parameters"]
                            if "properties" in parameters:
                                for prop_name, prop_info in parameters["properties"].items():
                                    if "type" not in prop_info:
                                        # Default to string if type is missing
                                        # 型が不足している場合はデフォルトでstring
                                        prop_info["type"] = "string"
                        openai_tools.append({
                            "type": "function",
                            "function": function_def
                        })
            
            params["tools"] = openai_tools
            params["tool_choice"] = "auto"
            
            # Add structured output if model specified
            # 構造化出力が指定されている場合は追加
            if self.output_model:
                params["response_format"] = {"type": "json_object"}
                
            response = self.sync_client.chat.completions.create(**params)
            message = response.choices[0].message
            
            # Add assistant message to conversation
            # アシスタントメッセージを対話に追加
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in (message.tool_calls or [])
                ]
            })
            
            # If no tool calls, we're done
            # tool呼び出しがない場合は完了
            if not message.tool_calls:
                return message.content or ""
            
            # Execute tool calls
            # tool呼び出しを実行
            for tool_call in message.tool_calls:
                try:
                    # Execute the tool function
                    # tool関数を実行
                    tool_result = self._execute_tool(tool_call)
                    
                    # Add tool result to conversation
                    # tool結果を対話に追加
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result)
                    })
                    
                except Exception as e:
                    # Handle tool execution errors
                    # tool実行エラーを処理
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": f"Error executing tool: {str(e)}"
                    })
            
            iteration += 1
        
        # If we reach here, we hit the iteration limit
        # ここに到達した場合は反復制限に達した
        return "Maximum tool iteration limit reached. Please try a simpler request."
    
    def _execute_tool(self, tool_call) -> Any:
        """Execute a tool function call / tool関数呼び出しを実行"""
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        # Find the tool by name
        # 名前でtoolを検索
        for tool in self.tools:
            if tool.get("function", {}).get("name") == function_name:
                # Check if tool has a callable function
                # toolに呼び出し可能な関数があるかチェック
                if "callable" in tool:
                    return tool["callable"](**arguments)
                elif "handler" in tool:
                    return tool["handler"](**arguments)
                else:
                    # Try to find a Python function with the same name
                    # 同じ名前のPython関数を検索
                    import inspect
                    frame = inspect.currentframe()
                    while frame:
                        if function_name in frame.f_globals:
                            func = frame.f_globals[function_name]
                            if callable(func):
                                return func(**arguments)
                        frame = frame.f_back
                    
                    raise ValueError(f"No callable implementation found for tool: {function_name}")
        
        raise ValueError(f"Tool not found: {function_name}")
    
    def add_tool(self, tool_definition: Dict, handler: Optional[callable] = None) -> None:
        """Add a tool definition / tool定義を追加"""
        self.tools.append(tool_definition)
        if handler:
            self.tool_handlers[tool_definition.get("function", {}).get("name", "unknown")] = handler
    
    def add_mcp_server(self, server_config: Dict) -> None:
        """Add MCP server configuration / MCPサーバー設定を追加"""
        # MCP server integration would be implemented here
        # MCPサーバー統合をここで実装
        self.mcp_servers.append(server_config)
        
        # For now, log that MCP is configured but not fully implemented
        # 現在のところ、MCPが設定されているがまだ完全に実装されていないことをログ
        print(f"MCP server configured: {server_config.get('name', 'unnamed')}")
        print("Note: Full MCP integration is planned for future release")
    
    def remove_tool(self, tool_name: str) -> bool:
        """Remove a tool by name / 名前でtoolを削除"""
        for i, tool in enumerate(self.tools):
            if tool.get("function", {}).get("name") == tool_name:
                del self.tools[i]
                return True
        return False
    
    def list_tools(self) -> List[str]:
        """List all available tool names / 利用可能なtool名をリスト"""
        tool_names = []
        
        # Handle SDK tools (FunctionTool objects)
        for tool in self._sdk_tools:
            if hasattr(tool, 'name'):
                tool_names.append(tool.name)
            elif hasattr(tool, '__name__'):
                tool_names.append(tool.__name__)
            else:
                tool_names.append(str(tool))
        
        # Handle legacy dictionary tools
        for tool in self.tools:
            if isinstance(tool, dict):
                tool_names.append(tool.get("function", {}).get("name", "unnamed"))
            else:
                tool_names.append(str(tool))
        
        return tool_names
    
    def _parse_structured_output(self, content: str) -> Any:
        """Parse structured output if model specified / モデルが指定されている場合は構造化出力を解析"""
        if not self.output_model:
            return content
            
        try:
            # Parse JSON and validate with Pydantic model
            data = json.loads(content)
            return self.output_model.model_validate(data)
        except Exception:
            # Fallback to raw content if parsing fails
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
            response = self.sync_client.chat.completions.create(
                model=self.evaluation_model,
                messages=messages,
                temperature=0.3,  # Lower temperature for evaluation
                response_format={"type": "json_object"},
                timeout=self.timeout
            )
            
            eval_data = json.loads(response.choices[0].message.content)
            score = float(eval_data.get("score", 0))
            feedback = eval_data.get("feedback", "")
            
            return EvaluationResult(
                score=score,
                passed=score >= self.threshold,
                feedback=feedback,
                metadata={"model": self.evaluation_model}
            )
            
        except Exception as e:
            # Fallback evaluation
            return EvaluationResult(
                score=0.0,
                passed=False,
                feedback=f"Evaluation failed: {str(e)}",
                metadata={"error": str(e)}
            )
    
    def _store_in_history(self, user_input: str, result: LLMResult) -> None:
        """Store interaction in history / 対話を履歴に保存"""
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
    
    def clear_history(self) -> None:
        """Clear all history / 全履歴をクリア"""
        self._pipeline_history.clear()
        self.session_history.clear()
    
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


# Utility functions for RefinireAgent (existing)
# RefinireAgent用ユーティリティ関数（既存）

# Utility functions for RefinireAgent (existing)
# RefinireAgent用ユーティリティ関数（既存） 
