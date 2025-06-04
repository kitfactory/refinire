from __future__ import annotations

"""Flow — Workflow orchestration engine for Step-based workflows.

Flowはステップベースワークフロー用のワークフローオーケストレーションエンジンです。
同期・非同期両方のインターフェースを提供し、CLI、GUI、チャットボット対応します。
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
import traceback

from .context import Context
from .step import Step


logger = logging.getLogger(__name__)


class FlowExecutionError(Exception):
    """
    Exception raised during flow execution
    フロー実行中に発生する例外
    """
    pass


class Flow:
    """
    Flow orchestration engine for Step-based workflows
    ステップベースワークフロー用フローオーケストレーションエンジン
    
    This class provides:
    このクラスは以下を提供します：
    - Declarative step-based workflow definition / 宣言的ステップベースワークフロー定義
    - Synchronous and asynchronous execution modes / 同期・非同期実行モード
    - User input coordination for interactive workflows / 対話的ワークフロー用ユーザー入力調整
    - Error handling and observability / エラーハンドリングとオブザーバビリティ
    """
    
    def __init__(
        self, 
        start: Optional[str] = None, 
        steps: Optional[Union[Dict[str, Step], List[Step], Step]] = None, 
        context: Optional[Context] = None,
        max_steps: int = 1000,
        trace_id: Optional[str] = None
    ):
        """
        Initialize Flow with flexible step definitions
        柔軟なステップ定義でFlowを初期化
        
        This constructor now supports three ways to define steps:
        このコンストラクタは3つの方法でステップを定義できます：
        1. Traditional: start step name + Dict[str, Step]
        2. Sequential: List[Step] (creates sequential workflow)
        3. Single: Single Step (creates single-step workflow)
        
        Args:
            start: Start step label (optional for List/Single mode) / 開始ステップラベル（List/Singleモードでは省略可）
            steps: Step definitions - Dict[str, Step], List[Step], or Step / ステップ定義 - Dict[str, Step]、List[Step]、またはStep
            context: Initial context (optional) / 初期コンテキスト（オプション）
            max_steps: Maximum number of steps to prevent infinite loops / 無限ループ防止のための最大ステップ数
            trace_id: Trace ID for observability / オブザーバビリティ用トレースID
        """
        # Handle flexible step definitions
        # 柔軟なステップ定義を処理
        if isinstance(steps, dict):
            # Traditional mode: Dict[str, Step]
            # 従来モード: Dict[str, Step]
            if start is None:
                raise ValueError("start parameter is required when steps is a dictionary")
            self.start = start
            self.steps = steps
        elif isinstance(steps, list):
            # Sequential mode: List[Step] 
            # シーケンシャルモード: List[Step]
            if not steps:
                raise ValueError("Steps list cannot be empty")
            self.steps = {}
            prev_step_name = None
            
            for i, step in enumerate(steps):
                if not hasattr(step, 'name'):
                    raise ValueError(f"Step at index {i} must have a 'name' attribute")
                
                step_name = step.name
                self.steps[step_name] = step
                
                # Set sequential flow: each step goes to next step
                # シーケンシャルフロー設定: 各ステップが次のステップに進む
                if prev_step_name is not None and hasattr(self.steps[prev_step_name], 'next_step'):
                    if self.steps[prev_step_name].next_step is None:
                        self.steps[prev_step_name].next_step = step_name
                
                prev_step_name = step_name
            
            # Start with first step
            # 最初のステップから開始
            self.start = steps[0].name
            
        elif steps is not None:
            # Check if it's a Step instance
            # Stepインスタンスかどうかをチェック
            if isinstance(steps, Step):
                # Single step mode: Step
                # 単一ステップモード: Step
                if not hasattr(steps, 'name'):
                    raise ValueError("Step must have a 'name' attribute")
                
                step_name = steps.name
                self.start = step_name
                self.steps = {step_name: steps}
            else:
                # Not a valid type
                # 有効なタイプではない
                raise ValueError("steps must be Dict[str, Step], List[Step], or Step")
        else:
            raise ValueError("steps parameter cannot be None")
        
        self.context = context or Context()
        self.max_steps = max_steps
        self.trace_id = trace_id or f"flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize context
        # コンテキストを初期化
        self.context.trace_id = self.trace_id
        self.context.next_label = self.start
        
        # Execution state
        # 実行状態
        self._running = False
        self._run_loop_task: Optional[asyncio.Task] = None
        self._execution_lock = asyncio.Lock()
        
        # Hooks for observability
        # オブザーバビリティ用フック
        self.before_step_hooks: List[Callable[[str, Context], None]] = []
        self.after_step_hooks: List[Callable[[str, Context, Any], None]] = []
        self.error_hooks: List[Callable[[str, Context, Exception], None]] = []
    
    @property
    def finished(self) -> bool:
        """
        Check if flow is finished
        フローが完了しているかチェック
        
        Returns:
            bool: True if finished / 完了している場合True
        """
        return self.context.is_finished()
    
    @property
    def current_step_name(self) -> Optional[str]:
        """
        Get current step name
        現在のステップ名を取得
        
        Returns:
            str | None: Current step name / 現在のステップ名
        """
        return self.context.current_step
    
    @property
    def next_step_name(self) -> Optional[str]:
        """
        Get next step name
        次のステップ名を取得
        
        Returns:
            str | None: Next step name / 次のステップ名
        """
        return self.context.next_label
    
    async def run(self, input_data: Optional[str] = None, initial_input: Optional[str] = None) -> Context:
        """
        Run flow to completion without user input coordination
        ユーザー入力調整なしでフローを完了まで実行
        
        This is for non-interactive workflows that don't require user input.
        これはユーザー入力が不要な非対話的ワークフロー用です。
        
        Args:
            input_data: Input data to the flow (preferred parameter name) / フローへの入力データ（推奨パラメータ名）
            initial_input: Initial input to the flow (deprecated, use input_data) / フローへの初期入力（非推奨、input_dataを使用）
            
        Returns:
            Context: Final context / 最終コンテキスト
            
        Raises:
            FlowExecutionError: If execution fails / 実行失敗時
        """
        async with self._execution_lock:
            try:
                self._running = True
                
                # Reset context for new execution
                # 新しい実行用にコンテキストをリセット
                if self.context.step_count > 0:
                    self.context = Context(trace_id=self.trace_id)
                    self.context.next_label = self.start
                
                # Determine input to use (input_data takes precedence)
                # 使用する入力を決定（input_dataが優先）
                effective_input = input_data or initial_input
                
                # Add input if provided
                # 入力が提供されている場合は追加
                if effective_input:
                    self.context.add_user_message(effective_input)
                
                current_input = effective_input
                step_count = 0
                
                while not self.finished and step_count < self.max_steps:
                    step_name = self.context.next_label
                    if not step_name or step_name not in self.steps:
                        break
                    
                    step = self.steps[step_name]
                    
                    # Execute step
                    # ステップを実行
                    try:
                        await self._execute_step(step, current_input)
                        current_input = None  # Only use initial input for first step
                        step_count += 1
                        
                        # If step is waiting for user input, break
                        # ステップがユーザー入力を待機している場合、中断
                        if self.context.awaiting_user_input:
                            break
                            
                    except Exception as e:
                        logger.error(f"Error executing step {step_name}: {e}")
                        self._handle_step_error(step_name, e)
                        break
                
                # Check for infinite loop
                # 無限ループのチェック
                if step_count >= self.max_steps:
                    raise FlowExecutionError(f"Flow exceeded maximum steps ({self.max_steps})")
                
                return self.context
                
            finally:
                self._running = False
    
    async def run_loop(self) -> None:
        """
        Run flow as background task with user input coordination
        ユーザー入力調整を含むバックグラウンドタスクとしてフローを実行
        
        This method runs the flow continuously, pausing when user input is needed.
        このメソッドはフローを継続的に実行し、ユーザー入力が必要な時に一時停止します。
        Use feed() to provide user input when the flow is waiting.
        フローが待機している時はfeed()を使用してユーザー入力を提供してください。
        """
        async with self._execution_lock:
            try:
                self._running = True
                
                # Reset context for new execution
                # 新しい実行用にコンテキストをリセット
                if self.context.step_count > 0:
                    self.context = Context(trace_id=self.trace_id)
                    self.context.next_label = self.start
                
                step_count = 0
                current_input = None
                
                while not self.finished and step_count < self.max_steps:
                    step_name = self.context.next_label
                    if not step_name or step_name not in self.steps:
                        break
                    
                    step = self.steps[step_name]
                    
                    # Execute step
                    # ステップを実行
                    try:
                        await self._execute_step(step, current_input)
                        current_input = None
                        step_count += 1
                        
                        # If step is waiting for user input, wait for feed()
                        # ステップがユーザー入力を待機している場合、feed()を待つ
                        if self.context.awaiting_user_input:
                            await self.context.wait_for_user_input()
                            # After receiving input, continue with the same step
                            # 入力受信後、同じステップで継続
                            current_input = self.context.last_user_input
                            continue
                            
                    except Exception as e:
                        logger.error(f"Error executing step {step_name}: {e}")
                        self._handle_step_error(step_name, e)
                        break
                
                # Check for infinite loop
                # 無限ループのチェック
                if step_count >= self.max_steps:
                    raise FlowExecutionError(f"Flow exceeded maximum steps ({self.max_steps})")
                
            finally:
                self._running = False
    
    def next_prompt(self) -> Optional[str]:
        """
        Get next prompt for synchronous CLI usage
        同期CLI使用用の次のプロンプトを取得
        
        Returns:
            str | None: Prompt if waiting for user input / ユーザー入力待ちの場合のプロンプト
        """
        return self.context.clear_prompt()
    
    def feed(self, user_input: str) -> None:
        """
        Provide user input to the flow
        フローにユーザー入力を提供
        
        Args:
            user_input: User input text / ユーザー入力テキスト
        """
        self.context.provide_user_input(user_input)
    
    def step(self) -> None:
        """
        Execute one step synchronously
        1ステップを同期的に実行
        
        This method executes one step and returns immediately.
        このメソッドは1ステップを実行してすぐに返ります。
        Use for synchronous CLI applications.
        同期CLIアプリケーション用に使用してください。
        """
        if self.finished:
            return
        
        step_name = self.context.next_label
        if not step_name or step_name not in self.steps:
            self.context.finish()
            return
        
        step = self.steps[step_name]
        
        # Run step in event loop
        # イベントループでステップを実行
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a task
                # ループが実行中の場合、タスクを作成
                task = asyncio.create_task(self._execute_step(step, None))
                # This is a synchronous method, so we can't await
                # これは同期メソッドなので、awaitできない
                # The task will run in the background
                # タスクはバックグラウンドで実行される
            else:
                # If no loop is running, run until complete
                # ループが実行されていない場合、完了まで実行
                loop.run_until_complete(self._execute_step(step, None))
        except Exception as e:
            logger.error(f"Error executing step {step_name}: {e}")
            self._handle_step_error(step_name, e)
    
    async def _execute_step(self, step: Step, user_input: Optional[str]) -> None:
        """
        Execute a single step with hooks and error handling
        フックとエラーハンドリングで単一ステップを実行
        
        Args:
            step: Step to execute / 実行するステップ
            user_input: User input if any / ユーザー入力（あれば）
        """
        step_name = step.name
        
        # Before step hooks
        # ステップ前フック
        for hook in self.before_step_hooks:
            try:
                hook(step_name, self.context)
            except Exception as e:
                logger.warning(f"Before step hook error: {e}")
        
        start_time = datetime.now()
        result = None
        error = None
        
        try:
            # Execute step
            # ステップを実行
            result = await step.run(user_input, self.context)
            if result != self.context:
                # Step returned a new context, use it
                # ステップが新しいコンテキストを返した場合、それを使用
                self.context = result
            
            logger.debug(f"Step {step_name} completed in {datetime.now() - start_time}")
            
        except Exception as e:
            error = e
            logger.error(f"Step {step_name} failed: {e}")
            logger.debug(traceback.format_exc())
            
            # Add error to context
            # エラーをコンテキストに追加
            self.context.add_system_message(f"Step {step_name} failed: {str(e)}")
            
            # Call error hooks
            # エラーフックを呼び出し
            for hook in self.error_hooks:
                try:
                    hook(step_name, self.context, e)
                except Exception as hook_error:
                    logger.warning(f"Error hook failed: {hook_error}")
            
            raise e
        
        finally:
            # After step hooks
            # ステップ後フック
            for hook in self.after_step_hooks:
                try:
                    hook(step_name, self.context, result)
                except Exception as e:
                    logger.warning(f"After step hook error: {e}")
    
    def _handle_step_error(self, step_name: str, error: Exception) -> None:
        """
        Handle step execution error
        ステップ実行エラーを処理
        
        Args:
            step_name: Name of the failed step / 失敗したステップの名前
            error: The error that occurred / 発生したエラー
        """
        # Mark flow as finished on error
        # エラー時はフローを完了としてマーク
        self.context.finish()
        self.context.set_artifact("error", {
            "step": step_name,
            "error": str(error),
            "type": type(error).__name__
        })
    
    def add_hook(
        self, 
        hook_type: str, 
        callback: Callable
    ) -> None:
        """
        Add observability hook
        オブザーバビリティフックを追加
        
        Args:
            hook_type: Type of hook ("before_step", "after_step", "error") / フックタイプ
            callback: Callback function / コールバック関数
        """
        if hook_type == "before_step":
            self.before_step_hooks.append(callback)
        elif hook_type == "after_step":
            self.after_step_hooks.append(callback)
        elif hook_type == "error":
            self.error_hooks.append(callback)
        else:
            raise ValueError(f"Unknown hook type: {hook_type}")
    
    def get_step_history(self) -> List[Dict[str, Any]]:
        """
        Get execution history
        実行履歴を取得
        
        Returns:
            List[Dict[str, Any]]: Step execution history / ステップ実行履歴
        """
        history = []
        for msg in self.context.messages:
            if msg.role == "system" and "Step" in msg.content:
                history.append({
                    "timestamp": msg.timestamp,
                    "message": msg.content,
                    "metadata": msg.metadata
                })
        return history
    
    def get_flow_summary(self) -> Dict[str, Any]:
        """
        Get flow execution summary
        フロー実行サマリーを取得
        
        Returns:
            Dict[str, Any]: Flow summary / フローサマリー
        """
        return {
            "trace_id": self.trace_id,
            "start_step": self.start,
            "current_step": self.current_step_name,
            "next_step": self.next_step_name,
            "step_count": self.context.step_count,
            "finished": self.finished,
            "start_time": self.context.start_time,
            "artifacts": self.context.artifacts,
            "message_count": len(self.context.messages)
        }
    
    def reset(self) -> None:
        """
        Reset flow to initial state
        フローを初期状態にリセット
        """
        self.context = Context(trace_id=self.trace_id)
        self.context.next_label = self.start
        self._running = False
        if self._run_loop_task:
            self._run_loop_task.cancel()
            self._run_loop_task = None
    
    def stop(self) -> None:
        """
        Stop flow execution
        フロー実行を停止
        """
        self._running = False
        self.context.finish()
        if self._run_loop_task:
            self._run_loop_task.cancel()
            self._run_loop_task = None
    
    async def start_background_task(self) -> asyncio.Task:
        """
        Start flow as background task
        フローをバックグラウンドタスクとして開始
        
        Returns:
            asyncio.Task: Background task / バックグラウンドタスク
        """
        if self._run_loop_task and not self._run_loop_task.done():
            raise RuntimeError("Flow is already running as background task")
        
        self._run_loop_task = asyncio.create_task(self.run_loop())
        return self._run_loop_task
    
    def __str__(self) -> str:
        """String representation of flow"""
        return f"Flow(start={self.start}, steps={len(self.steps)}, finished={self.finished})"
    
    def __repr__(self) -> str:
        return self.__str__()


# Utility functions for flow creation
# フロー作成用ユーティリティ関数

def create_simple_flow(
    steps: List[tuple[str, Step]], 
    context: Optional[Context] = None
) -> Flow:
    """
    Create a simple linear flow from a list of steps
    ステップのリストから簡単な線形フローを作成
    
    Args:
        steps: List of (name, step) tuples / (名前, ステップ)タプルのリスト
        context: Initial context / 初期コンテキスト
        
    Returns:
        Flow: Created flow / 作成されたフロー
    """
    if not steps:
        raise ValueError("At least one step is required")
    
    step_dict = {}
    for i, (name, step) in enumerate(steps):
        # Set next step for each step
        # 各ステップの次ステップを設定
        if hasattr(step, 'next_step') and step.next_step is None:
            if i < len(steps) - 1:
                step.next_step = steps[i + 1][0]
        step_dict[name] = step
    
    return Flow(
        start=steps[0][0],
        steps=step_dict,
        context=context
    )


def create_conditional_flow(
    initial_step: Step,
    condition_step: Step,
    true_branch: List[Step],
    false_branch: List[Step],
    context: Optional[Context] = None
) -> Flow:
    """
    Create a conditional flow with true/false branches
    true/falseブランチを持つ条件付きフローを作成
    
    Args:
        initial_step: Initial step / 初期ステップ
        condition_step: Condition step / 条件ステップ
        true_branch: Steps for true branch / trueブランチのステップ
        false_branch: Steps for false branch / falseブランチのステップ
        context: Initial context / 初期コンテキスト
        
    Returns:
        Flow: Created flow / 作成されたフロー
    """
    steps = {
        "start": initial_step,
        "condition": condition_step
    }
    
    # Add true branch steps
    # trueブランチステップを追加
    for i, step in enumerate(true_branch):
        step_name = f"true_{i}"
        steps[step_name] = step
        if i == 0 and hasattr(condition_step, 'if_true'):
            condition_step.if_true = step_name
    
    # Add false branch steps
    # falseブランチステップを追加
    for i, step in enumerate(false_branch):
        step_name = f"false_{i}"
        steps[step_name] = step
        if i == 0 and hasattr(condition_step, 'if_false'):
            condition_step.if_false = step_name
    
    # Connect initial step to condition
    # 初期ステップを条件に接続
    if hasattr(initial_step, 'next_step'):
        initial_step.next_step = "condition"
    
    return Flow(
        start="start",
        steps=steps,
        context=context
    ) 