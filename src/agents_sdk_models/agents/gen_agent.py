from __future__ import annotations

"""GenAgent — Modern LLMPipeline-based Step for Flow workflows.

GenAgentはLLMPipelineをStepとして使用するためのモダンなクラスです。
生成、評価、リトライ機能をFlow/Stepアーキテクチャ内で提供します。
"""

import warnings
from typing import Any, Callable, List, Dict, Optional, Type

from ..step import Step
from ..context import Context
from .llm_pipeline import LLMPipeline, LLMResult


# GenAgent implementation using LLMPipeline
# LLMPipelineを使用するGenAgent実装

class GenAgent(Step):
    """
    Modern Step implementation using LLMPipeline instead of deprecated AgentPipeline
    非推奨のAgentPipelineに代わってLLMPipelineを使用するモダンなStep実装
    
    This class provides generation, evaluation, and retry capabilities within Flow workflows
    without depending on the deprecated AgentPipeline.
    このクラスは非推奨のAgentPipelineに依存することなく、Flowワークフロー内で
    生成、評価、リトライ機能を提供します。
    """

    def __init__(
        self,
        name: str,
        generation_instructions: str,
        evaluation_instructions: Optional[str] = None,
        *,
        output_model: Optional[Type[Any]] = None,
        model: str = "gpt-4o-mini",
        evaluation_model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: float = 30.0,
        threshold: float = 85.0,
        max_retries: int = 3,
        input_guardrails: Optional[List[Callable[[str], bool]]] = None,
        output_guardrails: Optional[List[Callable[[Any], bool]]] = None,
        session_history: Optional[List[str]] = None,
        history_size: int = 10,
        improvement_callback: Optional[Callable[[LLMResult, Any], str]] = None,
        locale: str = "en",
        next_step: Optional[str] = None,
        store_result_key: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        mcp_servers: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize GenAgent with LLMPipeline configuration
        LLMPipeline設定でGenAgentを初期化する

        Args:
            name: Step name / ステップ名
            generation_instructions: System prompt for generation / 生成用システムプロンプト
            evaluation_instructions: System prompt for evaluation / 評価用システムプロンプト
            output_model: Pydantic model for structured output / 構造化出力用Pydanticモデル
            model: LLM model name / LLMモデル名
            evaluation_model: Optional LLM model name for evaluation / 評価用LLMモデル名（任意）
            temperature: Sampling temperature / サンプリング温度
            max_tokens: Maximum tokens / 最大トークン数
            timeout: Request timeout / リクエストタイムアウト
            threshold: Evaluation score threshold / 評価スコア閾値
            max_retries: Number of retry attempts / リトライ試行回数
            input_guardrails: Input validation functions / 入力検証関数
            output_guardrails: Output validation functions / 出力検証関数
            session_history: Session history / セッション履歴
            history_size: Size of history to keep / 保持する履歴サイズ
            improvement_callback: Callback for improvement suggestions / 改善提案用コールバック
            locale: Language code for localized messages / ローカライズメッセージ用言語コード
            next_step: Next step after pipeline execution / パイプライン実行後の次ステップ
            store_result_key: Key to store result in context shared_state / コンテキスト共有状態に結果を格納するキー
        """
        # Initialize Step base class
        # Step基底クラスを初期化
        super().__init__(name)
        
        # Store flow-specific configuration
        # フロー固有の設定を保存
        self.next_step = next_step
        self.store_result_key = store_result_key or f"{name}_result"
        
        # Create internal LLMPipeline instance
        # 内部LLMPipelineインスタンスを作成
        self.llm_pipeline = LLMPipeline(
            name=f"{name}_pipeline",
            generation_instructions=generation_instructions,
            evaluation_instructions=evaluation_instructions,
            output_model=output_model,
            model=model,
            evaluation_model=evaluation_model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            threshold=threshold,
            max_retries=max_retries,
            input_guardrails=input_guardrails,
            output_guardrails=output_guardrails,
            session_history=session_history,
            history_size=history_size,
            improvement_callback=improvement_callback,
            locale=locale,
            tools=tools,
            mcp_servers=mcp_servers,
        )

    async def run(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute GenAgent step using LLMPipeline
        LLMPipelineを使用してGenAgentステップを実行する

        Args:
            user_input: User input for the pipeline / パイプライン用ユーザー入力
            ctx: Current workflow context / 現在のワークフローコンテキスト

        Returns:
            Context: Updated context with pipeline results / パイプライン結果付き更新済みコンテキスト
        """
        # English: Update step information in context
        # 日本語: コンテキストのステップ情報を更新
        ctx.update_step_info(self.name)
        
        try:
            # English: Determine input text for pipeline
            # 日本語: パイプライン用入力テキストを決定
            input_text = user_input or ctx.last_user_input or ""
            
            if not input_text:
                # English: If no input available, add system message and continue
                # 日本語: 入力がない場合、システムメッセージを追加して続行
                ctx.add_system_message(f"GenAgent {self.name}: No input available, skipping pipeline execution")
                result = None
            else:
                # English: Execute LLMPipeline synchronously (no async issues)
                # 日本語: LLMPipelineを同期的に実行（非同期問題なし）
                llm_result = self.llm_pipeline.run(input_text)
                result = llm_result.content if llm_result.success else None
            
            # English: Store result in context
            # 日本語: 結果をコンテキストに保存
            if result is not None:
                # English: Store in shared state for other steps to access
                # 日本語: 他のステップがアクセスできるよう共有状態に保存
                ctx.shared_state[self.store_result_key] = result
                ctx.prev_outputs[self.name] = result
                
                # English: Add result as assistant message
                # 日本語: 結果をアシスタントメッセージとして追加
                ctx.add_assistant_message(str(result))
                
                # English: Add success system message
                # 日本語: 成功システムメッセージを追加
                ctx.add_system_message(f"GenAgent {self.name}: Pipeline executed successfully")
            else:
                # English: Handle case where pipeline returned None (evaluation failed)
                # 日本語: パイプラインがNoneを返した場合（評価失敗）を処理
                ctx.shared_state[self.store_result_key] = None
                ctx.prev_outputs[self.name] = None
                
                # English: Add failure system message
                # 日本語: 失敗システムメッセージを追加
                ctx.add_system_message(f"GenAgent {self.name}: Pipeline execution failed (evaluation threshold not met)")
                
        except Exception as e:
            # English: Handle execution errors
            # 日本語: 実行エラーを処理
            error_msg = f"GenAgent {self.name} execution error: {str(e)}"
            ctx.add_system_message(error_msg)
            ctx.shared_state[self.store_result_key] = None
            ctx.prev_outputs[self.name] = None
            
            # English: Log error for debugging
            # 日本語: デバッグ用エラーログ
            print(f"🚨 {error_msg}")
        
        # English: Set next step if specified
        # 日本語: 指定されている場合は次ステップを設定
        if self.next_step:
            ctx.goto(self.next_step)
        
        return ctx

    def get_pipeline_history(self) -> List[Dict[str, Any]]:
        """
        Get the internal pipeline history
        内部パイプライン履歴を取得する

        Returns:
            List[Dict[str, Any]]: Pipeline history / パイプライン履歴
        """
        return self.llm_pipeline.get_history()

    def get_session_history(self) -> Optional[List[str]]:
        """
        Get the session history
        セッション履歴を取得する

        Returns:
            Optional[List[str]]: Session history / セッション履歴
        """
        return self.llm_pipeline.session_history

    def update_instructions(
        self, 
        generation_instructions: Optional[str] = None,
        evaluation_instructions: Optional[str] = None
    ) -> None:
        """
        Update pipeline instructions
        パイプライン指示を更新する

        Args:
            generation_instructions: New generation instructions / 新しい生成指示
            evaluation_instructions: New evaluation instructions / 新しい評価指示
        """
        self.llm_pipeline.update_instructions(generation_instructions, evaluation_instructions)

    def clear_history(self) -> None:
        """
        Clear pipeline history
        パイプライン履歴をクリア
        """
        self.llm_pipeline.clear_history()

    def set_threshold(self, threshold: float) -> None:
        """
        Update evaluation threshold
        評価閾値を更新する

        Args:
            threshold: New threshold value (0-100) / 新しい閾値（0-100）
        """
        self.llm_pipeline.set_threshold(threshold)

    def __str__(self) -> str:
        return f"GenAgent({self.name}, model={self.llm_pipeline.model})"

    def __repr__(self) -> str:
        return self.__str__()


# Modern utility functions for creating GenAgent with common configurations
# モダンなGenAgent作成用ユーティリティ関数

def create_simple_gen_agent(
    name: str,
    instructions: str,
    model: str = "gpt-4o-mini",
    next_step: Optional[str] = None,
    threshold: float = 85.0,
    retries: int = 3,
    tools: Optional[List[Dict]] = None,
    mcp_servers: Optional[List[str]] = None
) -> GenAgent:
    """
    Create a simple GenAgent with basic configuration
    基本設定でシンプルなGenAgentを作成

    Args:
        name: Agent name / エージェント名
        instructions: Generation instructions / 生成指示
        model: LLM model name / LLMモデル名
        next_step: Next step name / 次ステップ名
        threshold: Evaluation threshold / 評価閾値
        retries: Retry attempts / リトライ回数
        tools: OpenAI function tools / OpenAI関数ツール
        mcp_servers: MCP server identifiers / MCPサーバー識別子

    Returns:
        GenAgent: Configured agent / 設定済みエージェント
    """
    return GenAgent(
        name=name,
        generation_instructions=instructions,
        model=model,
        next_step=next_step,
        threshold=threshold,
        max_retries=retries,
        tools=tools,
        mcp_servers=mcp_servers
    )


def create_evaluated_gen_agent(
    name: str,
    generation_instructions: str,
    evaluation_instructions: str,
    model: str = "gpt-4o-mini",
    evaluation_model: Optional[str] = None,
    next_step: Optional[str] = None,
    threshold: float = 85.0,
    retries: int = 3,
    tools: Optional[List[Dict]] = None,
    mcp_servers: Optional[List[str]] = None
) -> GenAgent:
    """
    Create a GenAgent with evaluation capabilities
    評価機能付きGenAgentを作成

    Args:
        name: Agent name / エージェント名
        generation_instructions: Generation instructions / 生成指示
        evaluation_instructions: Evaluation instructions / 評価指示
        model: LLM model name / LLMモデル名
        evaluation_model: Evaluation model name / 評価モデル名
        next_step: Next step name / 次ステップ名
        threshold: Evaluation threshold / 評価閾値
        retries: Retry attempts / リトライ回数

    Returns:
        GenAgent: Configured agent with evaluation / 評価機能付き設定済みエージェント
    """
    return GenAgent(
        name=name,
        generation_instructions=generation_instructions,
        evaluation_instructions=evaluation_instructions,
        model=model,
        evaluation_model=evaluation_model,
        next_step=next_step,
        threshold=threshold,
        max_retries=retries,
        tools=tools,
        mcp_servers=mcp_servers
    )


