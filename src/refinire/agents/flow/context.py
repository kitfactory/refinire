from __future__ import annotations

"""Context — Shared state management for Flow/Step workflows.

Contextはフロー/ステップワークフロー用の共有状態管理を提供します。
型安全で読みやすく、LangChain LCELとの互換性も持ちます。
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

try:
    from pydantic import BaseModel, Field, PrivateAttr  # type: ignore
except ImportError:
    BaseModel = object  # type: ignore
    Field = lambda **kwargs: None  # type: ignore
    PrivateAttr = lambda **kwargs: None  # type: ignore


class Message(BaseModel):
    """
    Message class for conversation history
    会話履歴用メッセージクラス
    
    Attributes:
        role: Message role (user, assistant, system) / メッセージの役割
        content: Message content / メッセージ内容
        timestamp: Message timestamp / メッセージのタイムスタンプ
        metadata: Additional metadata / 追加メタデータ
    """
    role: str  # Message role (user, assistant, system) / メッセージの役割
    content: str  # Message content / メッセージ内容
    timestamp: datetime = Field(default_factory=datetime.now)  # Message timestamp / メッセージのタイムスタンプ
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Additional metadata / 追加メタデータ


class Context(BaseModel):
    """
    Context class for Flow/Step workflow state management
    フロー/ステップワークフロー状態管理用コンテキストクラス
    
    This class provides:
    このクラスは以下を提供します：
    - Type-safe shared state / 型安全な共有状態
    - Conversation history management / 会話履歴管理
    - Step routing control / ステップルーティング制御
    - LangChain LCEL compatibility / LangChain LCEL互換性
    - User input/output coordination / ユーザー入出力調整
    """
    
    # Core state / コア状態
    last_user_input: Optional[str] = None  # Most recent user input / 直近のユーザー入力
    messages: List[Message] = Field(default_factory=list)  # Conversation history / 会話履歴
    result: Any = None  # Complete LLM API response object (recommended for advanced usage) / 完全なLLM API応答オブジェクト（高度な使用推奨）
    evaluation_result: Optional[Dict[str, Any]] = None  # Latest evaluation result / 最新の評価結果
    routing_result: Optional[Dict[str, Any]] = None  # Latest routing result / 最新のルーティング結果
    error: Optional[Dict[str, Any]] = None  # Error information / エラー情報
    
    
    # Flow control / フロー制御
    current_step: Optional[str] = None  # Current step name / 現在のステップ名
    
    @property
    def content(self) -> Any:
        """
        Access to generated content only (recommended for most users)
        生成されたコンテンツのみにアクセス（一般ユーザー推奨）
        
        Returns the actual generated content from LLMResult.content
        LLMResult.contentから実際の生成コンテンツを返す
        """
        if self.result and hasattr(self.result, 'content'):
            return self.result.content
        
        # Fallback: Check if there's an error message in the last assistant message
        # フォールバック: 最後のアシスタントメッセージにエラーメッセージがあるかチェック
        if self.messages:
            for message in reversed(self.messages):
                if message.role == 'system' and 'error' in message.content.lower():
                    return f"[Error] {message.content}"
        
        return None
    
    @content.setter
    def content(self, value: Any) -> None:
        """
        Setter for content property - updates LLMResult.content
        contentプロパティのセッター - LLMResult.contentを更新
        """
        if self.result and hasattr(self.result, 'content'):
            self.result.content = value
        else:
            # Create minimal LLMResult if none exists
            # LLMResultが存在しない場合は最小限のものを作成
            try:
                from refinire.agents.pipeline.llm_pipeline import LLMResult
                self.result = LLMResult(content=value, success=True)
            except ImportError:
                # Fallback: store directly if LLMResult not available
                # フォールバック: LLMResultが利用できない場合は直接格納
                self.result = value
    
    @property
    def success(self) -> bool:
        """
        Indicates if the operation was successful
        操作が成功したかを示す
        
        Success is True when:
        - Result is not None
        - If evaluation_result exists, evaluation passed
        - No error indicators are present
        
        成功条件:
        - 結果がNoneでない
        - 評価結果がある場合、評価に合格
        - エラー指標がない
        """
        # Basic check: must have a result
        # 基本チェック: 結果が必要
        if self.result is None:
            return False
        
        # Check evaluation result if available
        # 評価結果がある場合はチェック
        if self.evaluation_result:
            # If evaluation was performed, it must have passed
            # 評価が実行された場合、合格している必要がある
            if not self.evaluation_result.get('passed', True):
                return False
        
        # Check for error information
        # エラー情報をチェック
        if self.error is not None:
            return False
            
        # Check routing result for error conditions
        # ルーティング結果でエラー条件をチェック
        if self.routing_result:
            if self.routing_result.get('next_route') == 'error':
                return False
        
        return True
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Metadata information (returns evaluation_result or empty dict)
        メタデータ情報（evaluation_resultまたは空辞書を返す）
        """
        return self.evaluation_result or {}
    
    @property
    def artifacts(self) -> Dict[str, Any]:
        """
        Compatibility property for artifacts (stored in shared_state)
        artifactsの互換性プロパティ（shared_stateに保存）
        """
        return self.shared_state.get('artifacts', {})
    
    @property
    def next_label(self) -> Optional[str]:
        """
        Compatibility property for next_label (stored in routing_result)
        next_labelの互換性プロパティ（routing_resultに保存）
        """
        if self.routing_result:
            return self.routing_result.get('next_route')
        return None
    
    @next_label.setter
    def next_label(self, value: Optional[str]) -> None:
        """
        Setter for next_label (stores in routing_result)
        next_labelのセッター（routing_resultに保存）
        """
        if not self.routing_result:
            self.routing_result = {}
        self.routing_result['next_route'] = value
    
    # Results / 結果
    shared_state: Dict[str, Any] = Field(default_factory=dict)  # Arbitrary shared values (includes artifacts) / 任意の共有値（成果物を含む）
    
    # User interaction / ユーザー対話
    awaiting_prompt: Optional[str] = None  # Prompt waiting for user input / ユーザー入力待ちのプロンプト
    awaiting_user_input: bool = False  # Flag indicating waiting for user input / ユーザー入力待ちフラグ
    
    # Execution metadata / 実行メタデータ
    trace_id: Optional[str] = None  # Trace ID for observability / オブザーバビリティ用トレースID
    current_span_id: Optional[str] = None  # Current span ID for step tracking / ステップ追跡用現在のスパンID
    start_time: datetime = Field(default_factory=datetime.now)  # Flow start time / フロー開始時刻
    step_count: int = 0  # Number of steps executed / 実行されたステップ数
    span_history: List[Dict[str, Any]] = Field(default_factory=list)  # Span execution history / スパン実行履歴
    
    # Internal async coordination (private attributes) / 内部非同期調整（プライベート属性）
    _user_input_event: Optional[asyncio.Event] = PrivateAttr(default=None)
    _awaiting_prompt_event: Optional[asyncio.Event] = PrivateAttr(default=None)
    
    def __init__(self, **data):
        """
        Initialize Context with async events and proper defaults
        非同期イベントと適切なデフォルト値でContextを初期化
        """
        # Ensure trace_id has a default value if not provided
        # trace_idが提供されていない場合はデフォルト値を設定
        if 'trace_id' not in data or data['trace_id'] is None:
            import uuid
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            data['trace_id'] = f"context_{timestamp}_{str(uuid.uuid4())[:8]}"
        
        super().__init__(**data)
        self._user_input_event = asyncio.Event()
        self._awaiting_prompt_event = asyncio.Event()
    
    def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add user message to conversation history
        ユーザーメッセージを会話履歴に追加
        
        Args:
            content: Message content / メッセージ内容
            metadata: Additional metadata / 追加メタデータ
        """
        # Validate content type and convert if necessary
        # コンテンツ型を検証し、必要に応じて変換
        if content is None:
            content = ""
        elif not isinstance(content, str):
            # Handle cases where content might be a Context object or other type
            # contentがContextオブジェクトやその他の型の場合を処理
            try:
                content = str(content)
            except Exception as e:
                # If conversion fails, use a safe default
                # 変換に失敗した場合は安全なデフォルトを使用
                content = f"[Invalid content type: {type(content).__name__}]"
        
        try:
            message = Message(
                role="user",
                content=content,
                metadata=metadata or {}
            )
            self.messages.append(message)
            self.last_user_input = content
        except Exception as e:
            # Handle pydantic validation errors gracefully
            # pydanticバリデーションエラーを適切に処理
            # Failed to create user message with content type - continue
            # Create a fallback message
            # フォールバックメッセージを作成
            fallback_message = Message(
                role="user",
                content=f"[Message creation failed: {str(e)}]",
                metadata=metadata or {}
            )
            self.messages.append(fallback_message)
            self.last_user_input = fallback_message.content
    
    def add_assistant_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add assistant message to conversation history
        アシスタントメッセージを会話履歴に追加
        
        Args:
            content: Message content / メッセージ内容
            metadata: Additional metadata / 追加メタデータ
        """
        message = Message(
            role="assistant",
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
    
    def add_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add system message to conversation history
        システムメッセージを会話履歴に追加
        
        Args:
            content: Message content / メッセージ内容
            metadata: Additional metadata / 追加メタデータ
        """
        message = Message(
            role="system",
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
    
    
    
    def clear_prompt(self) -> Optional[str]:
        """
        Clear and return the current prompt
        現在のプロンプトをクリアして返す
        
        Returns:
            str | None: The prompt if one was waiting / 待機中だったプロンプト
        """
        prompt = self.awaiting_prompt
        self.awaiting_prompt = None
        if self._awaiting_prompt_event:
            self._awaiting_prompt_event.clear()
        return prompt
    
    
    async def wait_for_prompt_event(self) -> str:
        """
        Async wait for prompt event
        プロンプトイベントを非同期で待機
        
        Returns:
            str: Prompt waiting for user / ユーザー待ちのプロンプト
        """
        if self._awaiting_prompt_event:
            await self._awaiting_prompt_event.wait()
        return self.awaiting_prompt or ""
    
    def goto(self, label: str) -> None:
        """
        Set next step routing (stores in routing_result)
        次ステップのルーティングを設定（routing_resultに保存）
        
        Args:
            label: Next step label / 次ステップのラベル
        """
        if not self.routing_result:
            self.routing_result = {}
        self.routing_result['next_route'] = label
    
    def finish(self) -> None:
        """
        Mark flow as finished (clears routing_result)
        フローを完了としてマーク（routing_resultをクリア）
        """
        if not self.routing_result:
            self.routing_result = {}
        self.routing_result['next_route'] = None
    
    def is_finished(self) -> bool:
        """
        Check if flow is finished (checks routing_result)
        フローが完了しているかチェック（routing_resultを確認）
        
        Returns:
            bool: True if finished / 完了している場合True
        """
        if self.routing_result:
            next_route = self.routing_result.get('next_route')
            # Check for None or special termination constants
            # Noneまたは特別な終了定数をチェック
            return (next_route is None or 
                    next_route in ("_FLOW_TERMINATE_", "_FLOW_END_", "_FLOW_FINISH_"))
        return True  # No routing result means finished
    
    @property
    def finished(self) -> bool:
        """
        Property to check if flow is finished
        フローが完了しているかチェックするプロパティ
        
        Returns:
            bool: True if finished / 完了している場合True
        """
        return self.is_finished()
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for LangChain LCEL compatibility
        LangChain LCEL互換性のために辞書に変換
        
        Returns:
            Dict[str, Any]: Dictionary representation / 辞書表現
        """
        data = self.model_dump()
        # Convert messages to LangChain format
        # メッセージをLangChain形式に変換
        data["history"] = [
            {"role": msg.role, "content": msg.content, "metadata": msg.metadata}
            for msg in self.messages
        ]
        data.pop("messages", None)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Context":
        """
        Create Context from dictionary (LangChain LCEL compatibility)
        辞書からContextを作成（LangChain LCEL互換性）
        
        Args:
            data: Dictionary data / 辞書データ
            
        Returns:
            Context: New context instance / 新しいコンテキストインスタンス
        """
        data = data.copy()
        
        # Handle next_label -> routing_result conversion
        # next_label -> routing_result変換を処理
        if "next_label" in data:
            next_label = data.pop("next_label")
            if next_label is not None:
                if "routing_result" not in data:
                    data["routing_result"] = {}
                data["routing_result"]["next_route"] = next_label
        
        # Convert history to messages
        # 履歴をメッセージに変換
        history = data.pop("history", [])
        messages = []
        for msg_data in history:
            if isinstance(msg_data, dict):
                messages.append(Message(
                    role=msg_data.get("role", "user"),
                    content=msg_data.get("content", ""),
                    metadata=msg_data.get("metadata", {})
                ))
        data["messages"] = messages
        return cls(**data)
    
    def get_conversation_text(self, include_system: bool = False) -> str:
        """
        Get conversation as formatted text
        会話をフォーマット済みテキストとして取得
        
        Args:
            include_system: Include system messages / システムメッセージを含める
            
        Returns:
            str: Formatted conversation / フォーマット済み会話
        """
        lines = []
        for msg in self.messages:
            if not include_system and msg.role == "system":
                continue
            role_label = {"user": "👤", "assistant": "🤖", "system": "⚙️"}.get(msg.role, msg.role)
            lines.append(f"{role_label} {msg.content}")
        return "\n".join(lines)
    
    def get_last_messages(self, n: int = 10) -> List[Message]:
        """
        Get last N messages
        最後のNメッセージを取得
        
        Args:
            n: Number of messages / メッセージ数
            
        Returns:
            List[Message]: Last N messages / 最後のNメッセージ
        """
        return self.messages[-n:] if len(self.messages) > n else self.messages.copy()
    
    def update_step_info(self, step_name: str) -> None:
        """
        Update current step information
        現在のステップ情報を更新
        
        Args:
            step_name: Current step name / 現在のステップ名
        """
        # Finalize previous span if exists
        # 前のスパンが存在する場合は終了
        if self.current_span_id and self.current_step:
            self._finalize_current_span()
        
        # Start new span
        # 新しいスパンを開始
        self.current_step = step_name
        self.step_count += 1
        self.current_span_id = self._generate_span_id(step_name)
        
        # Record span start
        # スパン開始を記録
        self._start_span(step_name)
    
    def _generate_span_id(self, step_name: str) -> str:
        """
        Generate a unique span ID for the step
        ステップ用のユニークなスパンIDを生成
        
        Args:
            step_name: Step name / ステップ名
            
        Returns:
            str: Generated span ID / 生成されたスパンID
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        return f"{step_name}_{self.step_count:03d}_{timestamp}"
    
    def _start_span(self, step_name: str) -> None:
        """
        Start a new span for step tracking
        ステップ追跡用の新しいスパンを開始
        
        Args:
            step_name: Step name / ステップ名
        """
        span_info = {
            "span_id": self.current_span_id,
            "step_name": step_name,
            "trace_id": self.trace_id,
            "start_time": datetime.now(),
            "end_time": None,
            "status": "started",
            "step_index": self.step_count,
            "metadata": {}
        }
        self.span_history.append(span_info)
    
    def _finalize_current_span(self, status: str = "completed", error: Optional[str] = None) -> None:
        """
        Finalize the current span
        現在のスパンを終了
        
        Args:
            status: Span status (completed, error, etc.) / スパンステータス
            error: Error message if failed / 失敗時のエラーメッセージ
        """
        if not self.span_history:
            return
            
        current_span = self.span_history[-1]
        if current_span["span_id"] == self.current_span_id:
            current_span["end_time"] = datetime.now()
            current_span["status"] = status
            if error:
                current_span["error"] = error
    
    def finalize_flow_span(self) -> None:
        """
        Finalize the current span when flow ends
        フロー終了時に現在のスパンを終了
        """
        if self.current_span_id:
            self._finalize_current_span()
            self.current_span_id = None
    
    def set_error(self, step: str, error: Exception, **kwargs) -> None:
        """
        Set error information
        エラー情報を設定
        
        Args:
            step: Step name where error occurred / エラーが発生したステップ名
            error: Error exception / エラー例外
            **kwargs: Additional error metadata / 追加エラーメタデータ
        """
        self.error = {
            "step": step,
            "message": str(error),
            "type": type(error).__name__,
            "timestamp": datetime.now(),
            **kwargs
        }
    
    def clear_error(self) -> None:
        """
        Clear error information
        エラー情報をクリア
        """
        self.error = None
    
    def has_error(self) -> bool:
        """
        Check if context has error information
        コンテキストにエラー情報があるかチェック
        
        Returns:
            bool: True if error exists / エラーが存在する場合True
        """
        return self.error is not None
    
    def get_current_span_info(self) -> Optional[Dict[str, Any]]:
        """
        Get current span information
        現在のスパン情報を取得
        
        Returns:
            Dict[str, Any] | None: Current span info / 現在のスパン情報
        """
        if self.current_span_id and self.span_history:
            return self.span_history[-1]
        return None
    
    def get_span_history(self) -> List[Dict[str, Any]]:
        """
        Get complete span execution history
        完全なスパン実行履歴を取得
        
        Returns:
            List[Dict[str, Any]]: Span history / スパン履歴
        """
        return self.span_history.copy()
    
    def get_trace_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive trace summary
        包括的なトレースサマリーを取得
        
        Returns:
            Dict[str, Any]: Trace summary / トレースサマリー
        """
        total_duration = None
        if self.span_history:
            start_time = min(span["start_time"] for span in self.span_history)
            completed_spans = [span for span in self.span_history if span.get("end_time")]
            if completed_spans:
                end_time = max(span["end_time"] for span in completed_spans)
                total_duration = (end_time - start_time).total_seconds()
        
        return {
            "trace_id": self.trace_id,
            "current_span_id": self.current_span_id,
            "total_spans": len(self.span_history),
            "completed_spans": len([s for s in self.span_history if s.get("status") == "completed"]),
            "active_spans": len([s for s in self.span_history if s.get("status") == "started"]),
            "error_spans": len([s for s in self.span_history if s.get("status") == "error"]),
            "total_duration_seconds": total_duration,
            "flow_start_time": self.start_time,
            "is_finished": self.is_finished()
        }
    
    class Config:
        # Allow arbitrary types for flexibility
        # 柔軟性のために任意の型を許可
        arbitrary_types_allowed = True 
