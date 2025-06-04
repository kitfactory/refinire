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
    
    # External data / 外部データ
    knowledge: Dict[str, Any] = Field(default_factory=dict)  # External knowledge (RAG, etc.) / 外部知識（RAGなど）
    prev_outputs: Dict[str, Any] = Field(default_factory=dict)  # Previous step outputs / 前ステップの出力
    
    # Flow control / フロー制御
    next_label: Optional[str] = None  # Next step routing instruction / 次ステップのルーティング指示
    current_step: Optional[str] = None  # Current step name / 現在のステップ名
    
    # Results / 結果
    artifacts: Dict[str, Any] = Field(default_factory=dict)  # Flow-wide artifacts / フロー全体の成果物
    shared_state: Dict[str, Any] = Field(default_factory=dict)  # Arbitrary shared values / 任意の共有値
    
    # User interaction / ユーザー対話
    awaiting_prompt: Optional[str] = None  # Prompt waiting for user input / ユーザー入力待ちのプロンプト
    awaiting_user_input: bool = False  # Flag indicating waiting for user input / ユーザー入力待ちフラグ
    
    # Execution metadata / 実行メタデータ
    trace_id: Optional[str] = None  # Trace ID for observability / オブザーバビリティ用トレースID
    start_time: datetime = Field(default_factory=datetime.now)  # Flow start time / フロー開始時刻
    step_count: int = 0  # Number of steps executed / 実行されたステップ数
    
    # Internal async coordination (private attributes) / 内部非同期調整（プライベート属性）
    _user_input_event: Optional[asyncio.Event] = PrivateAttr(default=None)
    _awaiting_prompt_event: Optional[asyncio.Event] = PrivateAttr(default=None)
    
    def __init__(self, **data):
        """
        Initialize Context with async events
        非同期イベントでContextを初期化
        """
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
        message = Message(
            role="user",
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.last_user_input = content
    
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
    
    def set_waiting_for_user_input(self, prompt: str) -> None:
        """
        Set context to wait for user input with a prompt
        プロンプトでユーザー入力待ち状態に設定
        
        Args:
            prompt: Prompt to display to user / ユーザーに表示するプロンプト
        """
        self.awaiting_prompt = prompt
        self.awaiting_user_input = True
        if self._awaiting_prompt_event:
            self._awaiting_prompt_event.set()
    
    def provide_user_input(self, user_input: str) -> None:
        """
        Provide user input and clear waiting state
        ユーザー入力を提供し、待ち状態をクリア
        
        Args:
            user_input: User input text / ユーザー入力テキスト
        """
        self.add_user_message(user_input)
        self.awaiting_prompt = None
        self.awaiting_user_input = False
        if self._user_input_event:
            self._user_input_event.set()
    
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
    
    async def wait_for_user_input(self) -> str:
        """
        Async wait for user input
        ユーザー入力を非同期で待機
        
        Returns:
            str: User input / ユーザー入力
        """
        if self._user_input_event:
            await self._user_input_event.wait()
            self._user_input_event.clear()
        return self.last_user_input or ""
    
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
        Set next step routing
        次ステップのルーティングを設定
        
        Args:
            label: Next step label / 次ステップのラベル
        """
        self.next_label = label
    
    def finish(self) -> None:
        """
        Mark flow as finished
        フローを完了としてマーク
        """
        self.next_label = None
    
    def is_finished(self) -> bool:
        """
        Check if flow is finished
        フローが完了しているかチェック
        
        Returns:
            bool: True if finished / 完了している場合True
        """
        return self.next_label is None
    
    def as_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for LangChain LCEL compatibility
        LangChain LCEL互換性のために辞書に変換
        
        Returns:
            Dict[str, Any]: Dictionary representation / 辞書表現
        """
        data = self.dict()
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
        self.current_step = step_name
        self.step_count += 1
    
    def set_artifact(self, key: str, value: Any) -> None:
        """
        Set artifact value
        成果物の値を設定
        
        Args:
            key: Artifact key / 成果物キー
            value: Artifact value / 成果物値
        """
        self.artifacts[key] = value
    
    def get_artifact(self, key: str, default: Any = None) -> Any:
        """
        Get artifact value
        成果物の値を取得
        
        Args:
            key: Artifact key / 成果物キー
            default: Default value if not found / 見つからない場合のデフォルト値
            
        Returns:
            Any: Artifact value / 成果物値
        """
        return self.artifacts.get(key, default)
    
    class Config:
        # Allow arbitrary types for flexibility
        # 柔軟性のために任意の型を許可
        arbitrary_types_allowed = True 