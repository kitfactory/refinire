from __future__ import annotations

"""ClarifyAgent — Interactive Requirements Clarification Agent for Flow workflows.

ClarifyAgentはユーザーとの対話を通じて必要なデータモデルクラスの情報を収集するStepクラスです。
RefinireAgentを参考に作成されており、Flowワークフロー内で使用できます。
"""

import asyncio
import logging
from typing import Any, Callable, List, Dict, Optional, Type, TypeVar, Generic
from dataclasses import dataclass
import json

from .flow.step import Step
from .flow.context import Context
from .pipeline.llm_pipeline import (
    RefinireAgent, LLMResult, InteractiveAgent, InteractionResult, InteractionQuestion
)

try:
    from pydantic import BaseModel  # type: ignore
except ImportError:
    BaseModel = object  # type: ignore

# English: Generic type variable for user requirement type
# 日本語: ユーザー要求型用のジェネリック型変数
T = TypeVar('T')

logger = logging.getLogger(__name__)


class ClarifyBase(BaseModel):
    """
    Base class for requirement clarification output
    要件明確化出力のベースクラス
    
    Attributes:
        clearity: True if requirements are confirmed / 要件が確定した場合True
    """
    clearity: bool  # True if requirements are confirmed / 要件が確定した場合True


class ClarifyGeneric(ClarifyBase, Generic[T]):
    """
    Generic clarification output with typed user requirement
    型付きユーザー要求を持つジェネリック明確化出力
    
    Attributes:
        clearity: True if requirements are confirmed / 要件が確定した場合True  
        user_requirement: Confirmed user requirement / 確定したユーザー要求
    """
    user_requirement: Optional[T] = None  # Confirmed user requirement / 確定したユーザー要求


class Clarify(ClarifyBase):
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


class ClarifyPipeline:
    """
    ClarifyPipeline class for requirements clarification using InteractiveAgent
    InteractiveAgentを使用した要件明確化パイプラインクラス
    
    This class wraps InteractiveAgent to handle:
    このクラスはInteractiveAgentをラップして以下を処理します：
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
        model: Optional[str] = None,
        evaluation_model: Optional[str] = None,
        threshold: int = 85,
        retries: int = 3,
        tools: Optional[List[Dict]] = None,
        mcp_servers: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """
        Initialize the ClarifyPipeline with configuration parameters
        設定パラメータでClarifyPipelineを初期化する
        
        Args:
            name: Pipeline name / パイプライン名
            generation_instructions: System prompt for generation / 生成用システムプロンプト
            output_data: Output data model type / 出力データモデル型
            clerify_max_turns: Maximum number of clarification turns / 最大明確化ターン数
            evaluation_instructions: System prompt for evaluation / 評価用システムプロンプト
            model: LLM model name / LLMモデル名
            evaluation_model: Evaluation model name / 評価モデル名
            threshold: Evaluation threshold / 評価閾値
            retries: Number of retries / リトライ回数
            **kwargs: Additional arguments for RefinireAgent / RefinireAgent用追加引数
        """
        
        # English: Store original output data type before wrapping
        # 日本語: ラッピング前の元の出力データ型を保存
        self.original_output_data = output_data
        self.clerify_max_turns = clerify_max_turns
        
        # English: Create wrapped output model based on provided type
        # 日本語: 提供された型に基づいてラップされた出力モデルを作成
        if output_data is not None:
            # English: For typed output, create generic wrapper
            # 日本語: 型付き出力の場合、ジェネリックラッパーを作成
            wrapped_output_model = self._create_wrapped_model(output_data)
        else:
            # English: For untyped output, use default string wrapper
            # 日本語: 型なし出力の場合、デフォルトの文字列ラッパーを使用
            wrapped_output_model = Clarify
        
        # English: Enhanced generation instructions for clarification
        # 日本語: 明確化用の拡張生成指示
        enhanced_instructions = self._build_clarification_instructions(
            generation_instructions, 
            output_data
        )
        
        # English: Filter kwargs for InteractiveAgent compatibility
        # 日本語: InteractiveAgent互換性のためkwargsをフィルタリング
        pipeline_kwargs = {
            k: v for k, v in kwargs.items() 
            if k in [
                'temperature', 'max_tokens', 'timeout', 'input_guardrails', 
                'output_guardrails', 'session_history', 'history_size', 
                'improvement_callback', 'locale'
            ]
        }
        
        # English: Add tools and MCP servers if provided
        # 日本語: 提供された場合はtoolsとMCPサーバーを追加
        if tools is not None:
            pipeline_kwargs['tools'] = tools
        if mcp_servers is not None:
            pipeline_kwargs['mcp_servers'] = mcp_servers
        
        # English: Create internal InteractiveAgent instance
        # 日本語: 内部InteractiveAgentインスタンスを作成
        self.interactive_pipeline = InteractiveAgent(
            name=f"{name}_pipeline",
            generation_instructions=enhanced_instructions,
            evaluation_instructions=evaluation_instructions,
            output_model=wrapped_output_model,
            completion_check=self._is_clarification_complete,
            max_turns=clerify_max_turns,
            question_format=self._format_clarification_question,
            model=model,
            evaluation_model=evaluation_model,
            threshold=threshold,
            max_retries=retries,
            **pipeline_kwargs
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
        
        class WrappedClarify(BaseModel):
            clearity: bool  # True if requirements are confirmed / 要件が確定した場合True
            user_requirement: Optional[output_data_type] = None  # Confirmed user requirement / 確定したユーザー要求
        
        return WrappedClarify
    
    def _is_clarification_complete(self, result: Any) -> bool:
        """
        Check if clarification is complete based on result
        結果に基づいて明確化が完了しているかをチェック
        
        Args:
            result: LLM result content / LLM結果コンテンツ
            
        Returns:
            bool: True if clarification is complete / 明確化が完了している場合True
        """
        return (hasattr(result, 'clearity') and result.clearity) or \
               (hasattr(result, 'user_requirement') and result.user_requirement is not None)
    
    def _format_clarification_question(self, response: str, turn: int, remaining: int) -> str:
        """
        Format clarification response as a question
        明確化応答を質問としてフォーマット
        
        Args:
            response: AI response / AI応答
            turn: Current turn / 現在のターン
            remaining: Remaining turns / 残りターン
            
        Returns:
            str: Formatted question / フォーマット済み質問
        """
        return f"[ターン {turn}/{turn + remaining}] {response}"
    
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
        
        enhanced_instructions = f"""
{base_instructions}

あなたは要件明確化の専門家です。以下のルールに従ってください：

1. ユーザーの要求を理解し、不明確な点や不足している情報を特定する
2. 要件が不完全な場合は、clarityをfalseにして、必要な追加情報を質問する
3. すべての必要な情報が揃い、要件が明確になった場合のみ、clarityをtrueにして確定する
4. 質問は一度に一つずつ、分かりやすく行う
5. 最大{self.clerify_max_turns}ターンまで質問できる
{schema_info}

出力形式：
- clarity: 要件が確定した場合はtrue、追加質問が必要な場合はfalse
- user_requirement: 要件が確定した場合のみ、完全な要求データを含める
"""
        
        return enhanced_instructions
    
    def run(self, user_input: str) -> Any:
        """
        Execute the clarification pipeline
        明確化パイプラインを実行する
        
        Args:
            user_input: User input for clarification / 明確化用ユーザー入力
            
        Returns:
            Any: Clarification result or question / 明確化結果または質問
        """
        interaction_result = self.interactive_pipeline.run_interactive(user_input)
        return self._convert_interaction_result(interaction_result)
    
    def continue_clarification(self, user_response: str) -> Any:
        """
        Continue the clarification process with user response
        ユーザー応答で明確化プロセスを継続する
        
        Args:
            user_response: User response to previous question / 前の質問へのユーザー応答
            
        Returns:
            Any: Next clarification result or question / 次の明確化結果または質問
        """
        interaction_result = self.interactive_pipeline.continue_interaction(user_response)
        return self._convert_interaction_result(interaction_result)
    
    def _convert_interaction_result(self, interaction_result: InteractionResult) -> Any:
        """
        Convert InteractionResult to ClarifyPipeline format
        InteractionResultをClarifyPipeline形式に変換する
        
        Args:
            interaction_result: Result from InteractiveAgent / InteractiveAgentからの結果
            
        Returns:
            Any: Clarification response / 明確化応答
        """
        if interaction_result.is_complete:
            # English: Interaction complete - return final result
            # 日本語: 対話完了 - 最終結果を返す
            return interaction_result.content
        else:
            # English: Convert InteractionQuestion to ClarificationQuestion
            # 日本語: InteractionQuestionをClarificationQuestionに変換
            if isinstance(interaction_result.content, InteractionQuestion):
                return ClarificationQuestion(
                    question=interaction_result.content.question,
                    turn=interaction_result.turn,
                    remaining_turns=interaction_result.remaining_turns
                )
            else:
                # English: Create ClarificationQuestion from content
                # 日本語: コンテンツからClarificationQuestionを作成
                return ClarificationQuestion(
                    question=str(interaction_result.content),
                    turn=interaction_result.turn,
                    remaining_turns=interaction_result.remaining_turns
                )
    
    def reset_turns(self) -> None:
        """
        Reset turn counter
        ターンカウンターをリセットする
        """
        self.interactive_pipeline.reset_interaction()
    
    def reset_session(self) -> None:
        """
        Reset the entire clarification session
        明確化セッション全体をリセットする
        """
        self.interactive_pipeline.reset_interaction()
    
    @property
    def is_complete(self) -> bool:
        """
        Check if clarification is complete
        明確化が完了しているかを確認する
        
        Returns:
            bool: True if complete / 完了している場合True
        """
        return self.interactive_pipeline.is_complete
    
    @property
    def conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get conversation history
        会話履歴を取得する
        
        Returns:
            List[Dict[str, Any]]: Conversation history / 会話履歴
        """
        return self.interactive_pipeline.interaction_history
    
    @property
    def current_turn(self) -> int:
        """
        Get current turn number
        現在のターン番号を取得する
        
        Returns:
            int: Current turn / 現在のターン
        """
        return self.interactive_pipeline.current_turn
    
    @property
    def remaining_turns(self) -> int:
        """
        Get remaining turns
        残りターン数を取得する
        
        Returns:
            int: Remaining turns / 残りターン数
        """
        return self.interactive_pipeline.remaining_turns
    
    @property 
    def threshold(self) -> float:
        """
        Get evaluation threshold from internal InteractiveAgent
        内部InteractiveAgentから評価閾値を取得する
        
        Returns:
            float: Evaluation threshold / 評価閾値
        """
        return self.interactive_pipeline.threshold
    
    @property
    def retries(self) -> int:
        """
        Get retry count from internal InteractiveAgent
        内部InteractiveAgentからリトライ回数を取得する
        
        Returns:
            int: Retry count / リトライ回数
        """
        return self.interactive_pipeline.max_retries
    
    def get_session_history(self) -> Optional[List[str]]:
        """
        Get session history as string list
        セッション履歴を文字列リストとして取得する
        
        Returns:
            Optional[List[str]]: Session history / セッション履歴
        """
        return self.interactive_pipeline.get_session_history()


@dataclass
class ClarificationResult:
    """
    Result of clarification process
    明確化プロセスの結果
    
    Attributes:
        is_complete: True if clarification is complete / 明確化が完了した場合True
        data: Clarified data or next question / 明確化されたデータまたは次の質問
        turn: Current turn number / 現在のターン番号
        remaining_turns: Remaining turns / 残りターン数
    """
    is_complete: bool  # True if clarification is complete / 明確化が完了した場合True
    data: Any  # Clarified data or next question / 明確化されたデータまたは次の質問
    turn: int  # Current turn number / 現在のターン番号
    remaining_turns: int  # Remaining turns / 残りターン数


class ClarifyAgent(RefinireAgent):
    """
    Step implementation for interactive requirements clarification
    対話的要件明確化のためのStep実装
    
    This class allows clarifying user requirements through interactive dialog
    within Flow workflows, providing structured data collection capabilities.
    このクラスはFlowワークフロー内で対話的なダイアログを通じてユーザー要求を明確化し、
    構造化されたデータ収集機能を提供します。
    """

    def __init__(
        self,
        name: str,
        generation_instructions: str,
        output_data: Optional[Type[Any]] = None,
        *,
        clerify_max_turns: int = 20,
        evaluation_instructions: Optional[str] = None,
        input_guardrails: Optional[list] = None,
        output_guardrails: Optional[list] = None,
        model: str | None = None,
        evaluation_model: str | None = None,
        generation_tools: Optional[list] = None,
        evaluation_tools: Optional[list] = None,
        routing_func: Optional[Callable[[Any], Any]] = None,
        session_history: Optional[list] = None,
        history_size: int = 10,
        threshold: int = 85,
        retries: int = 3,
        improvement_callback: Optional[Callable[[Any, Any], None]] = None,
        dynamic_prompt: Optional[Callable[[str], str]] = None,
        retry_comment_importance: Optional[list[str]] = None,
        locale: str = "en",
        next_step: Optional[str] = None,
        store_result_key: Optional[str] = None,
        conversation_key: Optional[str] = None,
    ) -> None:
        """
        Initialize ClarifyAgent with clarification configuration
        明確化設定でClarifyAgentを初期化する

        Args:
            name: Step name / ステップ名
            generation_instructions: System prompt for clarification / 明確化用システムプロンプト
            output_data: Target data model type / ターゲットデータモデル型
            clerify_max_turns: Maximum number of clarification turns / 最大明確化ターン数
            evaluation_instructions: System prompt for evaluation / 評価用システムプロンプト
            input_guardrails: Guardrails for generation / 生成用ガードレール
            output_guardrails: Guardrails for evaluation / 評価用ガードレール
            model: LLM model name / LLMモデル名
            evaluation_model: Optional LLM model name for evaluation / 評価用LLMモデル名（任意）
            generation_tools: Tools for generation / 生成用ツール
            evaluation_tools: Tools for evaluation / 評価用ツール
            routing_func: Function for output routing / 出力ルーティング用関数
            session_history: Session history / セッション履歴
            history_size: Size of history to keep / 保持する履歴サイズ
            threshold: Evaluation score threshold / 評価スコア閾値
            retries: Number of retry attempts / リトライ試行回数
            improvement_callback: Callback for improvement suggestions / 改善提案用コールバック
            dynamic_prompt: Optional function to dynamically build prompt / 動的プロンプト生成関数（任意）
            retry_comment_importance: Importance levels of comments to include on retry / リトライ時コメント重要度レベル
            locale: Language code for localized messages / ローカライズメッセージ用言語コード
            next_step: Next step after clarification completion / 明確化完了後の次ステップ
            store_result_key: Key to store result in context shared_state / コンテキスト共有状態に結果を格納するキー
            conversation_key: Key to store conversation state / 会話状態を格納するキー
        """
        # Initialize RefinireAgent base class
        # RefinireAgent基底クラスを初期化
        super().__init__(
            name=name,
            generation_instructions=generation_instructions,
            evaluation_instructions=evaluation_instructions,
            model=model or "gpt-4o-mini",
            evaluation_model=evaluation_model,
            threshold=threshold,
            max_retries=retries,
            input_guardrails=input_guardrails,
            output_guardrails=output_guardrails,
            session_history=session_history,
            history_size=history_size,
            improvement_callback=improvement_callback,
            locale=locale,
            next_step=next_step,
            store_result_key=store_result_key or f"{name}_result"
        )
        
        # Store clarification-specific configuration
        # 明確化固有の設定を保存
        self.conversation_key = conversation_key or f"{name}_conversation"
        self.clerify_max_turns = clerify_max_turns
        self.output_data = output_data
        
        # Create internal ClarifyPipeline instance
        # 内部ClarifyPipelineインスタンスを作成
        self.pipeline = ClarifyPipeline(
            name=f"{name}_pipeline",
            generation_instructions=generation_instructions,
            evaluation_instructions=evaluation_instructions,
            output_data=output_data,
            clerify_max_turns=clerify_max_turns,
            input_guardrails=input_guardrails,
            output_guardrails=output_guardrails,
            model=model,
            evaluation_model=evaluation_model,
            generation_tools=generation_tools,
            evaluation_tools=evaluation_tools,
            routing_func=routing_func,
            session_history=session_history,
            history_size=history_size,
            threshold=threshold,
            retries=retries,
            improvement_callback=improvement_callback,
            dynamic_prompt=dynamic_prompt,
            retry_comment_importance=retry_comment_importance,
            locale=locale,
        )

    async def run_async(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute ClarifyAgent step using ClarifyPipeline
        ClarifyPipelineを使用してClarifyAgentステップを実行する

        Args:
            user_input: User input for clarification / 明確化用ユーザー入力
            ctx: Current workflow context / 現在のワークフローコンテキスト

        Returns:
            Context: Updated context with clarification results / 明確化結果付き更新済みコンテキスト
        """
        # English: Update step information in context
        # 日本語: コンテキストのステップ情報を更新
        ctx.update_step_info(self.name)
        
        try:
            # English: Determine input text for clarification
            # 日本語: 明確化用入力テキストを決定
            input_text = user_input or ctx.last_user_input or ""
            
            if not input_text:
                # English: If no input available, add system message and continue
                # 日本語: 入力がない場合、システムメッセージを追加して続行
                ctx.add_system_message(f"ClarifyAgent {self.name}: No input available, skipping clarification")
                result = ClarificationResult(
                    is_complete=False,
                    data=None,
                    turn=0,
                    remaining_turns=self.pipeline.clerify_max_turns
                )
            else:
                # English: Check if this is a continuation of existing conversation
                # 日本語: 既存の会話の継続かを確認
                existing_conversation = ctx.shared_state.get(self.conversation_key)
                
                # English: Execute clarification using RefinireAgent-based pipeline
                # 日本語: RefinireAgentベースのパイプラインを使用して明確化を実行
                if existing_conversation and not self.pipeline.is_complete:
                    # English: Continue existing clarification
                    # 日本語: 既存の明確化を継続
                    pipeline_result = self.pipeline.continue_clarification(input_text)
                else:
                    # English: Start new clarification
                    # 日本語: 新しい明確化を開始
                    pipeline_result = self.pipeline.run(input_text)
                
                # English: Wrap pipeline result in ClarificationResult
                # 日本語: パイプライン結果をClarificationResultにラップ
                result = ClarificationResult(
                    is_complete=self.pipeline.is_complete,
                    data=pipeline_result,
                    turn=self.pipeline.current_turn,
                    remaining_turns=self.pipeline.remaining_turns
                )
            
            # English: Store conversation state
            # 日本語: 会話状態を保存
            ctx.shared_state[self.conversation_key] = {
                "is_complete": result.is_complete,
                "turn": result.turn,
                "remaining_turns": result.remaining_turns,
                "conversation_history": self.pipeline.conversation_history
            }
            
            # English: Handle result based on completion status
            # 日本語: 完了状態に基づいて結果を処理
            if result.is_complete:
                # English: Clarification completed - store final result
                # 日本語: 明確化完了 - 最終結果を保存
                ctx.shared_state[self.store_result_key] = result.data
                ctx.prev_outputs[self.name] = result.data
                
                # English: Add completion message
                # 日本語: 完了メッセージを追加
                ctx.add_assistant_message(f"要求明確化完了: {str(result.data)}")
                ctx.add_system_message(f"ClarifyAgent {self.name}: Clarification completed successfully")
                
                # English: Set next step if specified
                # 日本語: 指定されている場合は次ステップを設定
                if self.next_step:
                    ctx.goto(self.next_step)
                    
            else:
                # English: Clarification in progress - store question
                # 日本語: 明確化進行中 - 質問を保存
                if isinstance(result.data, ClarificationQuestion):
                    question_text = str(result.data)
                    ctx.add_assistant_message(question_text)
                    ctx.add_system_message(f"ClarifyAgent {self.name}: Clarification question asked (Turn {result.turn})")
                else:
                    ctx.add_assistant_message(str(result.data))
                    ctx.add_system_message(f"ClarifyAgent {self.name}: Clarification in progress")
                
                # English: Store intermediate result for potential continuation
                # 日本語: 継続可能性のため中間結果を保存
                ctx.shared_state[self.store_result_key] = result
                ctx.prev_outputs[self.name] = result
                
                # English: Check if max turns reached and force completion
                # 日本語: 最大ターン数に達した場合は強制完了
                if result.remaining_turns <= 0 and self.next_step:
                    ctx.add_system_message(f"ClarifyAgent {self.name}: Maximum turns reached, proceeding to next step")
                    ctx.goto(self.next_step)
                
                # English: Do not advance to next step - wait for user response
                # 日本語: 次ステップに進まない - ユーザー応答を待機
                
        except Exception as e:
            # English: Handle execution errors
            # 日本語: 実行エラーを処理
            error_msg = f"ClarifyAgent {self.name} execution error: {str(e)}"
            ctx.add_system_message(error_msg)
            
            # English: Store error result
            # 日本語: エラー結果を保存
            error_result = ClarificationResult(
                is_complete=False,
                data=None,
                turn=0,
                remaining_turns=0
            )
            ctx.shared_state[self.store_result_key] = error_result
            ctx.prev_outputs[self.name] = error_result
            
            # English: Log error for debugging
            # 日本語: デバッグ用エラーログ
            logger.error(error_msg)
        
        return ctx

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversation history from the internal pipeline
        内部パイプラインから会話履歴を取得する

        Returns:
            List[Dict[str, Any]]: Conversation history / 会話履歴
        """
        return self.pipeline.conversation_history

    def get_session_history(self) -> Optional[List[str]]:
        """
        Get the session history from the internal pipeline
        内部パイプラインからセッション履歴を取得する

        Returns:
            Optional[List[str]]: Session history / セッション履歴
        """
        return self.pipeline.get_session_history()

    def reset_clarification(self) -> None:
        """
        Reset the clarification session
        明確化セッションをリセットする
        """
        self.pipeline.reset_session()

    def is_clarification_complete(self) -> bool:
        """
        Check if the clarification process is complete
        明確化プロセスが完了しているかを確認する

        Returns:
            bool: True if complete / 完了している場合True
        """
        return self.pipeline.is_complete

    @property
    def current_turn(self) -> int:
        """
        Get current turn number
        現在のターン番号を取得する

        Returns:
            int: Current turn number / 現在のターン番号
        """
        return self.pipeline.current_turn

    @property
    def remaining_turns(self) -> int:
        """
        Get remaining turn count
        残りターン数を取得する

        Returns:
            int: Remaining turns / 残りターン数
        """
        return self.pipeline.remaining_turns

    def __str__(self) -> str:
        return f"ClarifyAgent(name={self.name}, turns={self.current_turn}/{self.pipeline.clerify_max_turns})"

    def __repr__(self) -> str:
        return self.__str__()
    
    async def run_as_agent(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute ClarifyAgent using parent RefinireAgent functionality
        親のRefinireAgent機能を使用してClarifyAgentを実行
        
        This method allows ClarifyAgent to be used as a regular RefinireAgent
        when clarification features are not needed.
        このメソッドは、明確化機能が不要な場合にClarifyAgentを
        通常のRefinireAgentとして使用可能にします。
        
        Args:
            user_input: User input for the agent / エージェント用ユーザー入力
            ctx: Current workflow context / 現剈のワークフローコンテキスト
        
        Returns:
            Context: Updated context with agent results / エージェント結果付き更新済みコンテキスト
        """
        # Use parent RefinireAgent's run_async method for standard agent functionality
        # 標準エージェント機能については親のRefinireAgentのrun_asyncメソッドを使用
        return await super().run_async(user_input, ctx)


def create_simple_clarify_agent(
    name: str,
    instructions: str,
    output_data: Optional[Type[Any]] = None,
    max_turns: int = 20,
    model: Optional[str] = None,
    next_step: Optional[str] = None,
    tools: Optional[List[Dict]] = None,
    mcp_servers: Optional[List[str]] = None
) -> ClarifyAgent:
    """
    Create a simple ClarifyAgent with basic configuration
    基本設定でシンプルなClarifyAgentを作成する

    Args:
        name: Agent name / エージェント名
        instructions: Clarification instructions / 明確化指示
        output_data: Target data model type / ターゲットデータモデル型
        max_turns: Maximum clarification turns / 最大明確化ターン数
        model: LLM model name / LLMモデル名
        next_step: Next step after completion / 完了後の次ステップ

    Returns:
        ClarifyAgent: Configured ClarifyAgent instance / 設定済みClarifyAgentインスタンス
    """
    return ClarifyAgent(
        name=name,
        generation_instructions=instructions,
        output_data=output_data,
        clerify_max_turns=max_turns,
        model=model,
        next_step=next_step
    )


def create_evaluated_clarify_agent(
    name: str,
    generation_instructions: str,
    evaluation_instructions: str,
    output_data: Optional[Type[Any]] = None,
    max_turns: int = 20,
    model: Optional[str] = None,
    evaluation_model: Optional[str] = None,
    next_step: Optional[str] = None,
    threshold: int = 85,
    retries: int = 3,
    tools: Optional[List[Dict]] = None,
    mcp_servers: Optional[List[str]] = None
) -> ClarifyAgent:
    """
    Create a ClarifyAgent with evaluation capabilities
    評価機能付きClarifyAgentを作成する

    Args:
        name: Agent name / エージェント名
        generation_instructions: Generation instructions / 生成指示
        evaluation_instructions: Evaluation instructions / 評価指示
        output_data: Target data model type / ターゲットデータモデル型
        max_turns: Maximum clarification turns / 最大明確化ターン数
        model: LLM model name / LLMモデル名
        evaluation_model: Evaluation model name / 評価モデル名
        next_step: Next step after completion / 完了後の次ステップ
        threshold: Evaluation threshold / 評価閾値
        retries: Number of retries / リトライ回数

    Returns:
        ClarifyAgent: Configured ClarifyAgent instance / 設定済みClarifyAgentインスタンス
    """
    return ClarifyAgent(
        name=name,
        generation_instructions=generation_instructions,
        evaluation_instructions=evaluation_instructions,
        output_data=output_data,
        clerify_max_turns=max_turns,
        model=model,
        evaluation_model=evaluation_model,
        next_step=next_step,
        threshold=threshold,
        retries=retries
    )
