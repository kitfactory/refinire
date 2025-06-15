"""LLM Pipeline - A replacement for deprecated AgentPipeline using OpenAI Python SDK directly.

LLMパイプライン - 非推奨のAgentPipelineに代わって、OpenAI Python SDKを直接使用する新しい実装。
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


class LLMPipeline:
    """
    Modern LLM Pipeline using OpenAI Python SDK directly
    OpenAI Python SDKを直接使用するモダンなLLMパイプライン
    
    This class replaces the deprecated AgentPipeline with a cleaner, more maintainable implementation.
    このクラスは非推奨のAgentPipelineを、よりクリーンで保守しやすい実装で置き換えます。
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
        Initialize LLM Pipeline
        LLMパイプラインを初期化する
        
        Args:
            name: Pipeline name / パイプライン名
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
        self.generation_instructions = generation_instructions
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
        
        # Initialize OpenAI clients
        self.sync_client = OpenAI()
        self.async_client = AsyncOpenAI()
    
    def run(self, user_input: str) -> LLMResult:
        """
        Run the pipeline synchronously
        パイプラインを同期的に実行する
        
        Args:
            user_input: User input / ユーザー入力
            
        Returns:
            LLMResult: Generation result / 生成結果
        """
        # Input validation
        if not self._validate_input(user_input):
            return LLMResult(
                content=None,
                success=False,
                metadata={"error": "Input validation failed", "input": user_input}
            )
        
        # Build prompt with history
        full_prompt = self._build_prompt(user_input)
        
        # Generation with retries
        for attempt in range(1, self.max_retries + 1):
            try:
                # Generate content
                generation_result = self._generate_content(full_prompt)
                
                # Output validation
                if not self._validate_output(generation_result):
                    if attempt < self.max_retries:
                        continue
                    return LLMResult(
                        content=None,
                        success=False,
                        metadata={"error": "Output validation failed", "attempts": attempt}
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
                result = LLMResult(
                    content=parsed_content,
                    success=True,
                    metadata={
                        "model": self.model,
                        "temperature": self.temperature,
                        "attempts": attempt
                    },
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
                        metadata={"error": str(e), "attempts": attempt}
                    )
                continue
        
        # Should not reach here
        return LLMResult(
            content=None,
            success=False,
            metadata={"error": "Maximum retries exceeded"}
        )
    
    async def run_async(self, user_input: str) -> LLMResult:
        """
        Run the pipeline asynchronously
        パイプラインを非同期的に実行する
        
        Args:
            user_input: User input / ユーザー入力
            
        Returns:
            LLMResult: Generation result / 生成結果
        """
        # For simplicity, run sync version in executor
        # In production, this would be fully async
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.run, user_input)
    
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
    
    def _build_prompt(self, user_input: str) -> str:
        """Build complete prompt with instructions and history / 指示と履歴を含む完全なプロンプトを構築"""
        prompt_parts = [self.generation_instructions]
        
        # Add history if available
        if self.session_history:
            history_text = "\n".join(self.session_history[-self.history_size:])
            prompt_parts.append(f"Previous context:\n{history_text}")
        
        prompt_parts.append(f"User input: {user_input}")
        
        return "\n\n".join(prompt_parts)
    
    def _generate_content(self, prompt: str) -> str:
        """Generate content using OpenAI API with full tool support / OpenAI APIを使用した完全なtoolサポート付きコンテンツ生成"""
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
                params["tools"] = self.tools
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
        """Add a tool to the pipeline / パイプラインにtoolを追加"""
        if handler:
            tool_definition["callable"] = handler
        self.tools.append(tool_definition)
    
    def add_function_tool(
        self, 
        func: callable, 
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        """Add a Python function as a tool / Python関数をtoolとして追加"""
        import inspect
        
        function_name = name or func.__name__
        function_description = description or func.__doc__ or f"Function: {function_name}"
        
        # Get function signature for parameters
        # パラメータ用の関数シグネチャを取得
        sig = inspect.signature(func)
        parameters = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            param_info = {"type": "string"}  # Default type
            
            # Try to infer type from annotation
            # アノテーションから型を推論
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_info["type"] = "integer"
                elif param.annotation == float:
                    param_info["type"] = "number"
                elif param.annotation == bool:
                    param_info["type"] = "boolean"
                elif param.annotation == list:
                    param_info["type"] = "array"
                elif param.annotation == dict:
                    param_info["type"] = "object"
            
            parameters[param_name] = param_info
            
            # Add to required if no default value
            # デフォルト値がない場合は必須に追加
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        tool_definition = {
            "type": "function",
            "function": {
                "name": function_name,
                "description": function_description,
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": required
                }
            },
            "callable": func
        }
        
        self.tools.append(tool_definition)
    
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
        return [
            tool.get("function", {}).get("name", "unnamed")
            for tool in self.tools
        ]
    
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
        return f"LLMPipeline(name={self.name}, model={self.model})"
    
    def __repr__(self) -> str:
        return self.__str__()


# Utility functions for common configurations
# 共通設定用のユーティリティ関数

def create_simple_llm_pipeline(
    name: str,
    instructions: str,
    model: str = "gpt-4o-mini",
    **kwargs
) -> LLMPipeline:
    """
    Create a simple LLM pipeline
    シンプルなLLMパイプラインを作成
    """
    return LLMPipeline(
        name=name,
        generation_instructions=instructions,
        model=model,
        **kwargs
    )


def create_evaluated_llm_pipeline(
    name: str,
    generation_instructions: str,
    evaluation_instructions: str,
    model: str = "gpt-4o-mini",
    evaluation_model: Optional[str] = None,
    threshold: float = 85.0,
    **kwargs
) -> LLMPipeline:
    """
    Create an LLM pipeline with evaluation
    評価機能付きLLMパイプラインを作成
    """
    return LLMPipeline(
        name=name,
        generation_instructions=generation_instructions,
        evaluation_instructions=evaluation_instructions,
        model=model,
        evaluation_model=evaluation_model,
        threshold=threshold,
        **kwargs
    )


def create_tool_enabled_llm_pipeline(
    name: str,
    instructions: str,
    tools: Optional[List[callable]] = None,
    model: str = "gpt-4o-mini",
    **kwargs
) -> LLMPipeline:
    """
    Create an LLM pipeline with automatic tool registration
    自動tool登録機能付きLLMパイプラインを作成
    
    Args:
        name: Pipeline name / パイプライン名
        instructions: System instructions / システム指示
        tools: List of Python functions to register as tools / tool登録するPython関数のリスト
        model: LLM model name / LLMモデル名
        **kwargs: Additional arguments for LLMPipeline / LLMPipeline用追加引数
    
    Returns:
        LLMPipeline: Configured pipeline with tools / tool設定済みパイプライン
    
    Example:
        >>> def get_weather(city: str) -> str:
        ...     '''Get weather for a city'''
        ...     return f"Weather in {city}: Sunny"
        ...
        >>> def calculate(expression: str) -> float:
        ...     '''Calculate mathematical expression'''
        ...     return eval(expression)
        ...
        >>> pipeline = create_tool_enabled_llm_pipeline(
        ...     name="assistant",
        ...     instructions="You are a helpful assistant with access to tools.",
        ...     tools=[get_weather, calculate]
        ... )
        >>> result = pipeline.run("What's the weather in Tokyo and what's 2+2?")
    """
    pipeline = LLMPipeline(
        name=name,
        generation_instructions=instructions,
        model=model,
        tools=[],  # Start with empty tools list
        **kwargs
    )
    
    # Register all provided tools
    # 提供されたすべてのtoolを登録
    if tools:
        for tool_func in tools:
            pipeline.add_function_tool(tool_func)
    
    return pipeline


def create_web_search_pipeline(
    name: str,
    instructions: str = "You are a helpful assistant with access to web search. Use web search when you need current information.",
    model: str = "gpt-4o-mini",
    **kwargs
) -> LLMPipeline:
    """
    Create an LLM pipeline with web search capability
    Web検索機能付きLLMパイプラインを作成
    
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
    
    return create_tool_enabled_llm_pipeline(
        name=name,
        instructions=instructions,
        tools=[web_search],
        model=model,
        **kwargs
    )


def create_calculator_pipeline(
    name: str,
    instructions: str = "You are a helpful assistant with calculation capabilities. Use the calculator for mathematical computations.",
    model: str = "gpt-4o-mini",
    **kwargs
) -> LLMPipeline:
    """
    Create an LLM pipeline with calculation capability
    計算機能付きLLMパイプラインを作成
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
    
    return create_tool_enabled_llm_pipeline(
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


class InteractivePipeline(LLMPipeline):
    """
    Interactive Pipeline for multi-turn conversations using LLMPipeline
    LLMPipelineを使用した複数ターン会話のための対話的パイプライン
    
    This class extends LLMPipeline to handle:
    このクラスはLLMPipelineを拡張して以下を処理します：
    - Multi-turn interactive conversations / 複数ターンの対話的会話
    - Completion condition checking / 完了条件のチェック
    - Turn management / ターン管理
    - Conversation history tracking / 会話履歴の追跡
    
    The pipeline uses a completion check function to determine when the interaction is finished.
    パイプラインは完了チェック関数を使用して対話の終了時期を判定します。
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
        Initialize the InteractivePipeline
        InteractivePipelineを初期化する
        
        Args:
            name: Pipeline name / パイプライン名
            generation_instructions: System prompt for generation / 生成用システムプロンプト
            completion_check: Function to check if interaction is complete / 対話完了チェック関数
            max_turns: Maximum number of interaction turns / 最大対話ターン数
            evaluation_instructions: System prompt for evaluation / 評価用システムプロンプト
            question_format: Optional function to format questions / 質問フォーマット関数（任意）
            **kwargs: Additional arguments for LLMPipeline / LLMPipeline用追加引数
        """
        # Initialize base LLMPipeline
        # ベースのLLMPipelineを初期化
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
            
            # Run the LLMPipeline
            # LLMPipelineを実行
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
        interaction = {
            'user_input': user_input,
            'ai_result': {
                'content': llm_result.content,
                'success': llm_result.success,
                'metadata': llm_result.metadata
            },
            'turn': self._turn_count,
            'timestamp': asyncio.get_event_loop().time()
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


def create_simple_interactive_pipeline(
    name: str,
    instructions: str,
    completion_check: Callable[[Any], bool],
    max_turns: int = 20,
    model: str = "gpt-4o-mini",
    **kwargs
) -> InteractivePipeline:
    """
    Create a simple InteractivePipeline with basic configuration
    基本設定でシンプルなInteractivePipelineを作成する
    
    Args:
        name: Pipeline name / パイプライン名
        instructions: Generation instructions / 生成指示
        completion_check: Function to check completion / 完了チェック関数
        max_turns: Maximum interaction turns / 最大対話ターン数
        model: LLM model name / LLMモデル名
        **kwargs: Additional arguments / 追加引数
        
    Returns:
        InteractivePipeline: Configured pipeline / 設定済みパイプライン
    """
    return InteractivePipeline(
        name=name,
        generation_instructions=instructions,
        completion_check=completion_check,
        max_turns=max_turns,
        model=model,
        **kwargs
    )


def create_evaluated_interactive_pipeline(
    name: str,
    generation_instructions: str,
    evaluation_instructions: str,
    completion_check: Callable[[Any], bool],
    max_turns: int = 20,
    model: str = "gpt-4o-mini",
    evaluation_model: Optional[str] = None,
    threshold: float = 85.0,
    **kwargs
) -> InteractivePipeline:
    """
    Create an InteractivePipeline with evaluation capabilities
    評価機能付きInteractivePipelineを作成する
    
    Args:
        name: Pipeline name / パイプライン名
        generation_instructions: Generation instructions / 生成指示
        evaluation_instructions: Evaluation instructions / 評価指示
        completion_check: Function to check completion / 完了チェック関数
        max_turns: Maximum interaction turns / 最大対話ターン数
        model: LLM model name / LLMモデル名
        evaluation_model: Evaluation model name / 評価モデル名
        threshold: Evaluation threshold / 評価閾値
        **kwargs: Additional arguments / 追加引数
        
    Returns:
        InteractivePipeline: Configured pipeline / 設定済みパイプライン
    """
    return InteractivePipeline(
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


# Utility functions for LLMPipeline (existing)
# LLMPipeline用ユーティリティ関数（既存） 
