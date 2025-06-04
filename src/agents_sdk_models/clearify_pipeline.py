from __future__ import annotations

"""ClearifyPipeline — Requirements clarification pipeline for OpenAI Agents SDK.

ClearifyPipelineは要件を明確化するのに必要なAgentPipelineのサブクラスです。
次のステップへ要件が満たされているかを確認されるまで、繰り返し質問を行い、
ユーザーに確認を行います。
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
import json
from dataclasses import dataclass

from agents_sdk_models.pipeline import AgentPipeline

try:
    from pydantic import BaseModel  # type: ignore
except ImportError:
    BaseModel = object  # type: ignore

# English: Generic type variable for user requirement type
# 日本語: ユーザー要求型用のジェネリック型変数
T = TypeVar('T')

class ClearifyBase(BaseModel):
    """
    Base class for requirement clarification output
    要件明確化出力のベースクラス
    
    Attributes:
        clearity: True if requirements are confirmed / 要件が確定した場合True
    """
    clearity: bool  # True if requirements are confirmed / 要件が確定した場合True

class ClearifyGeneric(ClearifyBase, Generic[T]):
    """
    Generic clarification output with typed user requirement
    型付きユーザー要求を持つジェネリック明確化出力
    
    Attributes:
        clearity: True if requirements are confirmed / 要件が確定した場合True  
        user_requirement: Confirmed user requirement / 確定したユーザー要求
    """
    user_requirement: Optional[T] = None  # Confirmed user requirement / 確定したユーザー要求

class Clearify(ClearifyBase):
    """
    Default clarification output with string user requirement
    文字列ユーザー要求を持つデフォルト明確化出力
    
    Attributes:
        clearity: True if requirements are confirmed / 要件が確定した場合True
        user_requirement: Confirmed user requirement as string / 文字列として確定したユーザー要求
    """
    user_requirement: Optional[str] = None  # Confirmed user requirement as string / 文字列として確定したユーザー要求


@dataclass
class ClarificationQuestion:
    """
    Represents a clarification question from the pipeline
    パイプラインからの明確化質問を表現するクラス
    
    Attributes:
        question: The clarification question text / 明確化質問テキスト
        turn: Current turn number / 現在のターン番号
        remaining_turns: Remaining turns / 残りターン数
    """
    question: str  # The clarification question text / 明確化質問テキスト
    turn: int  # Current turn number / 現在のターン番号
    remaining_turns: int  # Remaining turns / 残りターン数
    
    def __str__(self) -> str:
        """
        String representation of the clarification question
        明確化質問の文字列表現
        
        Returns:
            str: Formatted question with turn info / ターン情報付きフォーマット済み質問
        """
        return f"[ターン {self.turn}/{self.turn + self.remaining_turns}] {self.question}"


class ClearifyPipeline(AgentPipeline):
    """
    ClearifyPipeline class for requirements clarification using OpenAI Agents SDK
    OpenAI Agents SDKを使用した要件明確化パイプラインクラス
    
    This class extends AgentPipeline to handle:
    このクラスはAgentPipelineを拡張して以下を処理します：
    - Iterative requirement clarification / 反復的な要件明確化
    - Type-safe output wrapping / 型安全な出力ラッピング
    - Maximum turn control / 最大ターン数制御
    - Structured requirement extraction / 構造化された要求抽出
    """
    
    def __init__(
        self,
        name: str,
        generation_instructions: str,
        output_data: Optional[Type[Any]] = None,
        clerify_max_turns: int = 20,
        evaluation_instructions: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialize the ClearifyPipeline with configuration parameters
        設定パラメータでClearifyPipelineを初期化する
        
        Args:
            name: Pipeline name / パイプライン名
            generation_instructions: System prompt for generation / 生成用システムプロンプト
            output_data: Output data model type / 出力データモデル型
            clerify_max_turns: Maximum number of clarification turns / 最大明確化ターン数
            evaluation_instructions: System prompt for evaluation / 評価用システムプロンプト
            **kwargs: Additional arguments for AgentPipeline / AgentPipeline用追加引数
        """
        
        # English: Store original output data type before wrapping
        # 日本語: ラッピング前の元の出力データ型を保存
        self.original_output_data = output_data
        self.clerify_max_turns = clerify_max_turns
        self._turn_count = 0
        
        # English: Create wrapped output model based on provided type
        # 日本語: 提供された型に基づいてラップされた出力モデルを作成
        if output_data is not None:
            # English: For typed output, create generic wrapper
            # 日本語: 型付き出力の場合、ジェネリックラッパーを作成
            wrapped_output_model = self._create_wrapped_model(output_data)
        else:
            # English: For untyped output, use default string wrapper
            # 日本語: 型なし出力の場合、デフォルトの文字列ラッパーを使用
            wrapped_output_model = Clearify
        
        # English: Enhanced generation instructions for clarification
        # 日本語: 明確化用の拡張生成指示
        enhanced_instructions = self._build_clarification_instructions(
            generation_instructions, 
            output_data
        )
        
        # English: Initialize parent with wrapped output model
        # 日本語: ラップされた出力モデルで親クラスを初期化
        super().__init__(
            name=name,
            generation_instructions=enhanced_instructions,
            evaluation_instructions=evaluation_instructions,
            output_model=wrapped_output_model,
            **kwargs
        )
    
    def _create_wrapped_model(self, output_data_type: Type[Any]) -> Type[BaseModel]:
        """
        Create a wrapped output model for the given type
        指定された型用のラップされた出力モデルを作成する
        
        Args:
            output_data_type: Original output data type / 元の出力データ型
            
        Returns:
            Type[BaseModel]: Wrapped model type / ラップされたモデル型
        """
        # English: Create dynamic Pydantic model that wraps the original type
        # 日本語: 元の型をラップする動的Pydanticモデルを作成
        
        class WrappedClearify(BaseModel):
            clearity: bool  # True if requirements are confirmed / 要件が確定した場合True
            user_requirement: Optional[output_data_type] = None  # Confirmed user requirement / 確定したユーザー要求
        
        return WrappedClearify
    
    def _build_clarification_instructions(
        self, 
        base_instructions: str, 
        output_data_type: Optional[Type[Any]]
    ) -> str:
        """
        Build enhanced instructions for clarification process
        明確化プロセス用の拡張指示を構築する
        
        Args:
            base_instructions: Base generation instructions / ベース生成指示
            output_data_type: Output data type for schema reference / スキーマ参照用出力データ型
            
        Returns:
            str: Enhanced instructions / 拡張指示
        """
        schema_info = ""
        if output_data_type is not None:
            try:
                # English: Try to get schema information if available
                # 日本語: 利用可能な場合はスキーマ情報を取得を試行
                if hasattr(output_data_type, 'model_json_schema'):
                    schema = output_data_type.model_json_schema()
                    schema_info = f"\n\n必要な出力形式のスキーマ:\n{json.dumps(schema, indent=2, ensure_ascii=False)}"
                elif hasattr(output_data_type, '__annotations__'):
                    annotations = output_data_type.__annotations__
                    schema_info = f"\n\n必要なフィールド: {list(annotations.keys())}"
            except Exception:
                pass
        
        enhanced_instructions = f"""{base_instructions}

あなたは要件明確化の専門家です。以下の手順に従ってください：

1. ユーザーの要求を理解し、不明確な点や不足している情報を特定する
2. より良い結果のために必要な追加情報を質問する
3. 要件が十分に明確になった場合は、clearityをtrueに設定する
4. 要件が不十分な場合は、clearityをfalseに設定し、追加の質問を行う

出力形式：
- clearity: 要件が明確で完全な場合はtrue、追加情報が必要な場合はfalse
- user_requirement: clearityがtrueの場合のみ、確定した要件を設定

{schema_info}

最大{self.clerify_max_turns}回のやり取りで要件を明確化してください。
"""
        
        return enhanced_instructions
    
    def run(self, user_input: str) -> Any:
        """
        Run the clarification pipeline with user input
        ユーザー入力で明確化パイプラインを実行する
        
        Args:
            user_input: User input text / ユーザー入力テキスト
            
        Returns:
            Any: Final clarified requirement, clarification question, or None if failed / 最終的な明確化された要求、明確化質問、または失敗時はNone
        """
        # English: Reset turn count for new session
        # 日本語: 新しいセッション用にターンカウントをリセット
        self._turn_count = 0
        return self._process_input(user_input)
    
    def continue_clarification(self, user_response: str) -> Any:
        """
        Continue clarification with user response to previous question
        前の質問に対するユーザー回答で明確化を継続する
        
        Args:
            user_response: User response to clarification question / 明確化質問に対するユーザー回答
            
        Returns:
            Any: Final clarified requirement, next clarification question, or None if failed / 最終的な明確化された要求、次の明確化質問、または失敗時はNone
        """
        if self._turn_count >= self.clerify_max_turns:
            # English: Maximum turns reached, cannot continue
            # 日本語: 最大ターン数に達した、継続できない
            return None
            
        return self._process_input(user_response)
    
    def _process_input(self, user_input: str) -> Any:
        """
        Process user input and return result or next question
        ユーザー入力を処理し、結果または次の質問を返す
        
        Args:
            user_input: User input text / ユーザー入力テキスト
            
        Returns:
            Any: Final clarified requirement, clarification question, or None if failed / 最終的な明確化された要求、明確化質問、または失敗時はNone
        """
        # English: Build context with conversation history
        # 日本語: 会話履歴を含むコンテキストを構築
        if self._turn_count > 0:
            # English: For subsequent turns, include conversation history
            # 日本語: 2回目以降のターンでは会話履歴を含める
            conversation_context = self._build_conversation_context()
            full_input = f"{conversation_context}\n\nユーザー: {user_input}"
        else:
            full_input = user_input
        
        # English: Run parent pipeline
        # 日本語: 親パイプラインを実行
        result = super().run(full_input)
        
        if result is None:
            # English: Pipeline failed
            # 日本語: パイプライン失敗
            return None
        
        self._turn_count += 1
        
        # English: Store this interaction in history
        # 日本語: この対話を履歴に保存
        self._store_interaction(user_input, result)
        
        # English: Check if clarification is complete
        # 日本語: 明確化が完了しているかチェック
        if hasattr(result, 'clearity') and result.clearity:
            # English: Requirements are clear, extract and return final result
            # 日本語: 要件が明確、最終結果を抽出して返す
            if hasattr(result, 'user_requirement') and result.user_requirement:
                return result.user_requirement
            else:
                return result
        
        # English: Requirements not clear yet, return the clarification question
        # 日本語: 要件がまだ明確でない、明確化質問を返す
        if hasattr(result, 'user_requirement') and result.user_requirement:
            # English: Return the clarification question/request for more info
            # 日本語: 明確化質問/追加情報の要求を返す
            return ClarificationQuestion(
                question=str(result.user_requirement),
                turn=self._turn_count,
                remaining_turns=self.remaining_turns
            )
        
        # English: No clear question, return the raw result
        # 日本語: 明確な質問がない、生の結果を返す
        return result
    
    def _build_conversation_context(self) -> str:
        """
        Build conversation context from history
        履歴から会話コンテキストを構築する
        
        Returns:
            str: Formatted conversation context / フォーマット済み会話コンテキスト
        """
        if not hasattr(self, '_conversation_history'):
            return ""
        
        context_lines = []
        for interaction in self._conversation_history:
            context_lines.append(f"ユーザー: {interaction['user_input']}")
            context_lines.append(f"AI: {interaction['ai_response']}")
        
        return "\n".join(context_lines)
    
    def _store_interaction(self, user_input: str, ai_result: Any) -> None:
        """
        Store interaction in conversation history
        会話履歴に対話を保存する
        
        Args:
            user_input: User input / ユーザー入力
            ai_result: AI result / AI結果
        """
        if not hasattr(self, '_conversation_history'):
            self._conversation_history = []
        
        # English: Extract AI response text
        # 日本語: AI応答テキストを抽出
        if hasattr(ai_result, 'user_requirement') and ai_result.user_requirement:
            ai_response = str(ai_result.user_requirement)
        else:
            ai_response = str(ai_result)
        
        self._conversation_history.append({
            'user_input': user_input,
            'ai_response': ai_response,
            'turn': self._turn_count
        })
        
        # English: Keep only recent history to avoid context overflow
        # 日本語: コンテキストオーバーフローを避けるため最近の履歴のみ保持
        max_history = 10
        if len(self._conversation_history) > max_history:
            self._conversation_history = self._conversation_history[-max_history:]
    
    def reset_turns(self) -> None:
        """
        Reset the turn counter for a new clarification session
        新しい明確化セッション用にターンカウンターをリセットする
        """
        self._turn_count = 0
        if hasattr(self, '_conversation_history'):
            self._conversation_history = []
    
    def reset_session(self) -> None:
        """
        Reset the entire session including conversation history
        会話履歴を含むセッション全体をリセットする
        """
        self.reset_turns()
        if hasattr(self, '_conversation_history'):
            self._conversation_history = []
    
    @property
    def is_complete(self) -> bool:
        """
        Check if clarification process is complete (max turns reached)
        明確化プロセスが完了しているかチェック（最大ターン数に達した）
        
        Returns:
            bool: True if max turns reached / 最大ターン数に達した場合True
        """
        return self._turn_count >= self.clerify_max_turns
    
    @property
    def conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversation history
        会話履歴を取得する
        
        Returns:
            List[Dict[str, Any]]: Conversation history / 会話履歴
        """
        if not hasattr(self, '_conversation_history'):
            return []
        return self._conversation_history.copy()
    
    @property
    def current_turn(self) -> int:
        """
        Get the current turn number
        現在のターン番号を取得する
        
        Returns:
            int: Current turn number / 現在のターン番号
        """
        return self._turn_count
    
    @property
    def remaining_turns(self) -> int:
        """
        Get the remaining number of turns
        残りのターン数を取得する
        
        Returns:
            int: Remaining turns / 残りターン数
        """
        return max(0, self.clerify_max_turns - self._turn_count) 