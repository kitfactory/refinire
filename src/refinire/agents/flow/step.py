from __future__ import annotations

"""Step — Step interface and basic implementations for Flow workflows.

Stepはフローワークフロー用のステップインターフェースと基本実装を提供します。
UserInputStep、ConditionStep、ForkStep、JoinStepなどの基本的なステップを含みます。
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union, Awaitable
from concurrent.futures import ThreadPoolExecutor
import threading

from .context import Context

logger = logging.getLogger(__name__)


class Step(ABC):
    """
    Abstract base class for workflow steps
    ワークフローステップの抽象基底クラス
    
    All step implementations must provide:
    全てのステップ実装は以下を提供する必要があります：
    - name: Step identifier for DSL reference / DSL参照用ステップ識別子
    - run: Async execution method / 非同期実行メソッド
    """
    
    def __init__(self, name: str):
        """
        Initialize step with name
        名前でステップを初期化
        
        Args:
            name: Step name / ステップ名
        """
        self.name = name
    
    def _create_step_span(self, step_type: str = None):
        """
        Create a custom span for this step execution
        このステップ実行用のカスタムスパンを作成
        
        Args:
            step_type: Optional step type for span metadata
            
        Returns:
            Span object or None if tracing not available
        """
        try:
            from agents.tracing import custom_span
            
            span_name = f"{step_type or self.__class__.__name__}({self.name})"
            span = custom_span(
                name=span_name,
                data={
                    "step.name": self.name,
                    "step.type": self.__class__.__name__,
                    "step.category": step_type or "workflow"
                }
            )
            return span
        except ImportError:
            return None
    
    def _update_span_with_result(self, span, user_input: Optional[str], ctx: Context, success: bool = True, error: Optional[str] = None):
        """
        Update span with execution results
        実行結果でスパンを更新
        
        Args:
            span: Span object to update
            user_input: User input provided to step
            ctx: Context after execution
            success: Whether execution was successful
            error: Error message if any
        """
        if span is None:
            return
            
        try:
            # Update span data with execution details
            if user_input is not None:
                span.span_data.data['input'] = user_input
            
            span.span_data.data['success'] = success
            span.span_data.data['current_step'] = ctx.current_step
            span.span_data.data['next_label'] = ctx.next_label
            span.span_data.data['step_count'] = ctx.step_count
            
            if error:
                span.span_data.data['error'] = error
            
            # Add context information
            if hasattr(ctx, 'result') and ctx.result is not None:
                span.span_data.data['output'] = str(ctx.result)
            
            # Add system messages
            if ctx.messages:
                recent_messages = ctx.messages[-3:]  # Last 3 messages
                span.span_data.data['recent_messages'] = [
                    {"role": msg.get("role", "unknown"), "content": msg.get("content", "")[:200]}
                    for msg in recent_messages
                ]
                
        except Exception as e:
            logger.debug(f"Failed to update span data: {e}")
    
    @abstractmethod
    async def run_async(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute step asynchronously and return updated context
        ステップを非同期実行し、更新されたコンテキストを返す
        
        Args:
            user_input: User input if any / ユーザー入力（あれば）
            ctx: Current context / 現在のコンテキスト
            
        Returns:
            Context: Updated context with next_label set / next_labelが設定された更新済みコンテキスト
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
    
    def __repr__(self) -> str:
        return self.__str__()


class UserInputStep(Step):
    """
    Step that waits for user input
    ユーザー入力を待機するステップ
    
    This step displays a prompt and waits for user response.
    このステップはプロンプトを表示し、ユーザー応答を待機します。
    It sets the context to waiting state and returns without advancing.
    コンテキストを待機状態に設定し、進行せずに返します。
    """
    
    def __init__(self, name: str, prompt: str, next_step: Optional[str] = None):
        """
        Initialize user input step
        ユーザー入力ステップを初期化
        
        Args:
            name: Step name / ステップ名
            prompt: Prompt to display to user / ユーザーに表示するプロンプト
            next_step: Next step after input (optional) / 入力後の次ステップ（オプション）
        """
        super().__init__(name)
        self.prompt = prompt
        self.next_step = next_step
    
    async def run_async(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute user input step
        ユーザー入力ステップを実行
        
        Args:
            user_input: User input if available / 利用可能なユーザー入力
            ctx: Current context / 現在のコンテキスト
            
        Returns:
            Context: Updated context / 更新済みコンテキスト
        """
        ctx.update_step_info(self.name)
        
        # If user input is provided, process it
        # ユーザー入力が提供されている場合、処理する
        if user_input is not None:
            ctx.provide_user_input(user_input)
            if self.next_step:
                ctx.goto(self.next_step)
            else:
                ctx.finish()
            # Note: If next_step is None, flow will end
            # 注：next_stepがNoneの場合、フローは終了
        else:
            # Set waiting state for user input
            # ユーザー入力の待機状態を設定
            ctx.set_waiting_for_user_input(self.prompt)
        
        return ctx


class ConditionStep(Step):
    """
    Step that performs conditional routing
    条件付きルーティングを実行するステップ
    
    This step evaluates a condition and routes to different steps based on the result.
    このステップは条件を評価し、結果に基づいて異なるステップにルーティングします。
    """
    
    def __init__(
        self, 
        name: str, 
        condition: Callable[[Context], Union[bool, Awaitable[bool]]], 
        if_true: str, 
        if_false: str
    ):
        """
        Initialize condition step
        条件ステップを初期化
        
        Args:
            name: Step name / ステップ名
            condition: Condition function / 条件関数
            if_true: Step to go if condition is True / 条件がTrueの場合のステップ
            if_false: Step to go if condition is False / 条件がFalseの場合のステップ
        """
        super().__init__(name)
        self.condition = condition
        self.if_true = if_true
        self.if_false = if_false
    
    async def run_async(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute condition step
        条件ステップを実行
        
        Args:
            user_input: User input (not used) / ユーザー入力（使用されない）
            ctx: Current context / 現在のコンテキスト
            
        Returns:
            Context: Updated context with routing / ルーティング付き更新済みコンテキスト
        """
        # Create span for tracing
        # トレーシング用のスパンを作成
        span = self._create_step_span("condition")
        
        if span is not None:
            with span:
                return await self._execute_condition_with_span(user_input, ctx, span)
        else:
            return await self._execute_condition_with_span(user_input, ctx, None)
    
    async def _execute_condition_with_span(self, user_input: Optional[str], ctx: Context, span) -> Context:
        """Execute condition step with span tracking"""
        ctx.update_step_info(self.name)
        
        # Add condition metadata to span
        if span is not None:
            span.span_data.data['if_true'] = self.if_true
            span.span_data.data['if_false'] = self.if_false
            span.span_data.data['condition_function'] = getattr(self.condition, '__name__', 'anonymous')
        
        # Evaluate condition (may be async)
        # 条件を評価（非同期の可能性あり）
        result = False
        error_msg = None
        try:
            result = self.condition(ctx)
            if asyncio.iscoroutine(result):
                result = await result
        except Exception as e:
            # On error, go to false branch
            # エラー時はfalseブランチに進む
            error_msg = f"Condition evaluation error: {e}"
            ctx.add_system_message(error_msg)
            result = False
        
        # Route based on condition result
        # 条件結果に基づいてルーティング
        next_step = self.if_true if result else self.if_false
        ctx.goto(next_step)
        
        # Update span with results
        if span is not None:
            span.span_data.data['condition_result'] = result
            span.span_data.data['next_step'] = next_step
            self._update_span_with_result(span, user_input, ctx, success=error_msg is None, error=error_msg)
        
        return ctx


class FunctionStep(Step):
    """
    Step that executes a custom function
    カスタム関数を実行するステップ
    
    This step allows executing arbitrary code within the workflow.
    このステップはワークフロー内で任意のコードを実行できます。
    """
    
    def __init__(
        self, 
        name: str, 
        function: Callable[[Optional[str], Context], Union[Context, Awaitable[Context]]], 
        next_step: Optional[str] = None
    ):
        """
        Initialize function step
        関数ステップを初期化
        
        Args:
            name: Step name / ステップ名
            function: Function to execute / 実行する関数
            next_step: Next step after execution / 実行後の次ステップ
        """
        super().__init__(name)
        self.function = function
        self.next_step = next_step
    
    async def run_async(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute function step
        関数ステップを実行
        
        Args:
            user_input: User input / ユーザー入力
            ctx: Current context / 現在のコンテキスト
            
        Returns:
            Context: Updated context / 更新済みコンテキスト
        """
        # Create span for tracing
        # トレーシング用のスパンを作成
        span = self._create_step_span("function")
        
        if span is not None:
            with span:
                return await self._execute_function_with_span(user_input, ctx, span)
        else:
            return await self._execute_function_with_span(user_input, ctx, None)
    
    async def _execute_function_with_span(self, user_input: Optional[str], ctx: Context, span) -> Context:
        """Execute function step with span tracking"""
        ctx.update_step_info(self.name)
        
        # Add function metadata to span
        if span is not None:
            span.span_data.data['function_name'] = getattr(self.function, '__name__', 'anonymous')
            span.span_data.data['next_step'] = self.next_step
        
        error_msg = None
        try:
            # Execute the function (may be async)
            # 関数を実行（非同期の可能性あり）
            result = self.function(user_input, ctx)
            if asyncio.iscoroutine(result):
                result_ctx = await result
                if result_ctx is not None:
                    ctx = result_ctx
            else:
                if result is not None:
                    ctx = result
        except Exception as e:
            error_msg = f"Function execution error in {self.name}: {e}"
            ctx.add_system_message(error_msg)
        
        # Set next step if specified, otherwise finish the flow
        # 指定されている場合は次ステップを設定、そうでなければフローを終了
        if self.next_step:
            ctx.goto(self.next_step)
        else:
            ctx.finish()
        
        # Update span with results
        if span is not None:
            self._update_span_with_result(span, user_input, ctx, success=error_msg is None, error=error_msg)
        
        return ctx


class ForkStep(Step):
    """
    Step that executes multiple branches in parallel
    複数のブランチを並列実行するステップ
    
    This step starts multiple sub-flows concurrently and collects their results.
    このステップは複数のサブフローを同時に開始し、結果を収集します。
    """
    
    def __init__(self, name: str, branches: List[str], join_step: str):
        """
        Initialize fork step
        フォークステップを初期化
        
        Args:
            name: Step name / ステップ名
            branches: List of branch step names to execute in parallel / 並列実行するブランチステップ名のリスト
            join_step: Step to join results / 結果を結合するステップ
        """
        super().__init__(name)
        self.branches = branches
        self.join_step = join_step
    
    async def run_async(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute fork step
        フォークステップを実行
        
        Args:
            user_input: User input / ユーザー入力
            ctx: Current context / 現在のコンテキスト
            
        Returns:
            Context: Updated context / 更新済みコンテキスト
        """
        ctx.update_step_info(self.name)
        
        # Store branch information for join step
        # ジョインステップ用にブランチ情報を保存
        ctx.shared_state[f"{self.name}_branches"] = self.branches
        ctx.shared_state[f"{self.name}_started"] = True
        
        # For now, just route to the join step
        # 現在のところ、ジョインステップにルーティングするだけ
        # In a full implementation, this would start parallel execution
        # 完全な実装では、これは並列実行を開始する
        ctx.goto(self.join_step)
        
        return ctx


class JoinStep(Step):
    """
    Step that joins results from parallel branches
    並列ブランチからの結果を結合するステップ
    
    This step waits for parallel branches to complete and merges their results.
    このステップは並列ブランチの完了を待機し、結果をマージします。
    """
    
    def __init__(self, name: str, fork_step: str, join_type: str = "all", next_step: Optional[str] = None):
        """
        Initialize join step
        ジョインステップを初期化
        
        Args:
            name: Step name / ステップ名
            fork_step: Associated fork step name / 関連するフォークステップ名
            join_type: Join type ("all" or "any") / ジョインタイプ（"all"または"any"）
            next_step: Next step after join / ジョイン後の次ステップ
        """
        super().__init__(name)
        self.fork_step = fork_step
        self.join_type = join_type
        self.next_step = next_step
    
    async def run_async(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute join step
        ジョインステップを実行
        
        Args:
            user_input: User input / ユーザー入力
            ctx: Current context / 現在のコンテキスト
            
        Returns:
            Context: Updated context / 更新済みコンテキスト
        """
        ctx.update_step_info(self.name)
        
        # Get branch information from shared state
        # 共有状態からブランチ情報を取得
        branches = ctx.shared_state.get(f"{self.fork_step}_branches", [])
        
        # For now, just mark as completed
        # 現在のところ、完了としてマークするだけ
        # In a full implementation, this would wait for and merge branch results
        # 完全な実装では、これはブランチ結果を待機してマージする
        ctx.add_system_message(f"Joined {len(branches)} branches using {self.join_type} strategy")
        
        # Set next step if specified, otherwise finish the flow
        # 指定されている場合は次ステップを設定、そうでなければフローを終了
        if self.next_step:
            ctx.goto(self.next_step)
        else:
            ctx.finish()
        
        return ctx



class DebugStep(Step):
    """
    Step for debugging and logging
    デバッグとログ記録用のステップ
    
    This step prints or logs context information for debugging purposes.
    このステップはデバッグ目的でコンテキスト情報を印刷またはログ記録します。
    """
    
    def __init__(self, name: str, message: str = "", print_context: bool = False, next_step: Optional[str] = None):
        """
        Initialize debug step
        デバッグステップを初期化
        
        Args:
            name: Step name / ステップ名
            message: Debug message / デバッグメッセージ
            print_context: Whether to print full context / 完全なコンテキストを印刷するかどうか
            next_step: Next step name / 次ステップ名
        """
        super().__init__(name)
        self.message = message
        self.print_context = print_context
        self.next_step = next_step
    
    async def run_async(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute debug step
        デバッグステップを実行
        
        Args:
            user_input: User input / ユーザー入力
            ctx: Current context / 現在のコンテキスト
            
        Returns:
            Context: Updated context / 更新済みコンテキスト
        """
        ctx.update_step_info(self.name)
        
        # Log debug information
        # デバッグ情報をログ記録
        debug_info = f"DEBUG [{self.name}]: {self.message}"
        if user_input:
            debug_info += f" | User Input: {user_input}"
        debug_info += f" | Step Count: {ctx.step_count} | Next Label: {ctx.next_label}"
        
        logger.debug(debug_info)
        
        if self.print_context:
            logger.debug(f"Context: {ctx.model_dump()}")
        
        # Add debug message to system messages
        # デバッグメッセージをシステムメッセージに追加
        ctx.add_system_message(f"DEBUG {self.name}: {self.message}")
        
        # Set next step if specified, otherwise finish the flow
        # 指定されている場合は次ステップを設定、そうでなければフローを終了
        if self.next_step:
            ctx.goto(self.next_step)
        else:
            ctx.finish()
        
        return ctx


# Utility functions for creating common step patterns
# 一般的なステップパターンを作成するユーティリティ関数

def create_simple_condition(field_path: str, expected_value: Any) -> Callable[[Context], bool]:
    """
    Create a simple condition function that checks a field value
    フィールド値をチェックする簡単な条件関数を作成
    
    Args:
        field_path: Dot-separated path to field (e.g., "shared_state.status") / フィールドへのドット区切りパス
        expected_value: Expected value / 期待値
        
    Returns:
        Callable[[Context], bool]: Condition function / 条件関数
    """
    def condition(ctx: Context) -> bool:
        try:
            # Navigate to the field using dot notation
            # ドット記法を使用してフィールドに移動
            obj = ctx
            for part in field_path.split('.'):
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                elif isinstance(obj, dict) and part in obj:
                    obj = obj[part]
                else:
                    return False
            return obj == expected_value
        except Exception:
            return False
    
    return condition


def create_lambda_step(name: str, func: Callable[[Context], Any], next_step: Optional[str] = None) -> FunctionStep:
    """
    Create a simple function step from a lambda
    ラムダから簡単な関数ステップを作成
    
    Args:
        name: Step name / ステップ名
        func: Function to execute / 実行する関数
        next_step: Next step / 次ステップ
        
    Returns:
        FunctionStep: Function step / 関数ステップ
    """
    def wrapper(user_input: Optional[str], ctx: Context) -> Context:
        func(ctx)
        return ctx
    
    return FunctionStep(name, wrapper, next_step)


class ParallelStep(Step):
    """
    Step that executes multiple steps in parallel
    複数のステップを並列実行するステップ
    
    This step automatically manages parallel execution of child steps.
    このステップは子ステップの並列実行を自動管理します。
    It waits for all parallel steps to complete before proceeding.
    全ての並列ステップが完了するまで待機してから進行します。
    """
    
    def __init__(
        self, 
        name: str, 
        parallel_steps: List[Step], 
        next_step: Optional[str] = None,
        max_workers: Optional[int] = None
    ):
        """
        Initialize parallel step
        並列ステップを初期化
        
        Args:
            name: Step name / ステップ名
            parallel_steps: List of steps to execute in parallel / 並列実行するステップのリスト
            next_step: Next step after all parallel steps complete / 全並列ステップ完了後の次ステップ
            max_workers: Maximum number of concurrent workers / 最大同時ワーカー数
        """
        super().__init__(name)
        self.parallel_steps = parallel_steps
        self.next_step = next_step
        self.max_workers = max_workers or min(32, len(parallel_steps) + 4)
        
        # Validate that all steps have names
        # 全ステップに名前があることを検証
        for step in parallel_steps:
            if not hasattr(step, 'name') or not step.name:
                raise ValueError(f"All parallel steps must have valid names: {step}")
    
    async def run_async(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute parallel steps
        並列ステップを実行
        
        Args:
            user_input: User input (passed to all parallel steps) / ユーザー入力（全並列ステップに渡される）
            ctx: Current context / 現在のコンテキスト
            
        Returns:
            Context: Updated context with merged results / マージされた結果を持つ更新済みコンテキスト
        """
        # Create span for tracing
        # トレーシング用のスパンを作成
        span = self._create_step_span("parallel")
        
        if span is not None:
            with span:
                return await self._execute_parallel_with_span(user_input, ctx, span)
        else:
            return await self._execute_parallel_with_span(user_input, ctx, None)
    
    async def _execute_parallel_with_span(self, user_input: Optional[str], ctx: Context, span) -> Context:
        """Execute parallel steps with span tracking"""
        ctx.update_step_info(self.name)
        
        # Add parallel execution metadata to span
        if span is not None:
            span.span_data.data['parallel_steps'] = [step.name for step in self.parallel_steps]
            span.span_data.data['max_workers'] = self.max_workers
            span.span_data.data['step_count'] = len(self.parallel_steps)
        
        # Create separate contexts for each parallel step
        # 各並列ステップ用に別々のコンテキストを作成
        parallel_contexts = []
        for step in self.parallel_steps:
            # Clone context for each parallel execution
            # 各並列実行用にコンテキストをクローン
            step_ctx = self._clone_context_for_parallel(ctx, step.name)
            parallel_contexts.append((step, step_ctx))
        
        # Execute all steps in parallel
        # 全ステップを並列実行
        async def run_parallel_step(step_and_ctx):
            step, step_ctx = step_and_ctx
            try:
                result_ctx = await step.run_async(user_input, step_ctx)
                return step.name, result_ctx, None
            except Exception as e:
                return step.name, step_ctx, e
        
        # Use asyncio.gather for parallel execution
        # 並列実行にasyncio.gatherを使用
        import time
        start_time = time.time()
        
        results = await asyncio.gather(
            *[run_parallel_step(sc) for sc in parallel_contexts],
            return_exceptions=True
        )
        
        execution_time = time.time() - start_time
        
        # Merge results back into main context
        # 結果をメインコンテキストにマージ
        errors = []
        successful_steps = []
        for result in results:
            if isinstance(result, Exception):
                errors.append(result)
                continue
                
            step_name, result_ctx, error = result
            if error:
                errors.append(f"Step {step_name}: {error}")
                continue
            
            successful_steps.append(step_name)
            # Merge parallel step results
            # 並列ステップ結果をマージ
            self._merge_parallel_result(ctx, step_name, result_ctx)
        
        # Update span with execution results
        if span is not None:
            span.span_data.data['execution_time_seconds'] = execution_time
            span.span_data.data['successful_steps'] = successful_steps
            span.span_data.data['failed_steps'] = len(errors)
            span.span_data.data['total_steps'] = len(self.parallel_steps)
        
        # Handle errors if any
        # エラーがあれば処理
        error_msg = None
        if errors:
            error_msg = f"Parallel execution errors: {'; '.join(map(str, errors))}"
            ctx.add_system_message(error_msg)
        
        # Set next step or finish
        # 次ステップを設定または終了
        if self.next_step:
            ctx.goto(self.next_step)
        else:
            ctx.finish()
        
        # Update span with final results
        if span is not None:
            self._update_span_with_result(span, user_input, ctx, success=error_msg is None, error=error_msg)
        
        # Raise error after span update
        if error_msg:
            raise RuntimeError(error_msg)
        
        return ctx
    
    def _clone_context_for_parallel(self, ctx: Context, step_name: str) -> Context:
        """
        Clone context for parallel execution
        並列実行用にコンテキストをクローン
        
        Args:
            ctx: Original context / 元のコンテキスト
            step_name: Name of the step / ステップ名
            
        Returns:
            Context: Cloned context / クローンされたコンテキスト
        """
        # Create new context with shared state
        # 共有状態を持つ新しいコンテキストを作成
        cloned_ctx = Context()
        
        # Copy essential state
        # 必須状態をコピー
        cloned_ctx.shared_state = ctx.shared_state.copy()
        cloned_ctx.messages = ctx.messages.copy()
        cloned_ctx.last_user_input = ctx.last_user_input
        cloned_ctx.trace_id = ctx.trace_id
        cloned_ctx.span_history = ctx.span_history.copy()
        
        # Set step-specific information
        # ステップ固有情報を設定
        cloned_ctx.current_step = step_name
        
        return cloned_ctx
    
    def _merge_parallel_result(self, main_ctx: Context, step_name: str, result_ctx: Context) -> None:
        """
        Merge parallel step result into main context
        並列ステップ結果をメインコンテキストにマージ
        
        Args:
            main_ctx: Main context / メインコンテキスト
            step_name: Name of the completed step / 完了したステップ名
            result_ctx: Result context from parallel step / 並列ステップからの結果コンテキスト
        """
        # Merge shared state with step-specific keys
        # ステップ固有キーで共有状態をマージ
        for key, value in result_ctx.shared_state.items():
            if key not in main_ctx.shared_state:
                main_ctx.shared_state[key] = value
            else:
                # Handle conflicts by prefixing with step name
                # ステップ名をプレフィックスとして衝突を処理
                prefixed_key = f"{step_name}_{key}"
                main_ctx.shared_state[prefixed_key] = value
        
        # Merge conversation history
        # 会話履歴をマージ
        main_ctx.messages.extend(result_ctx.messages)
        
        # Update execution path
        # 実行パスを更新
        main_ctx.span_history.extend(result_ctx.span_history)
        
        # Store step-specific results metadata (avoid overwriting user data)
        # ステップ固有結果メタデータを保存（ユーザーデータの上書きを避ける）
        main_ctx.shared_state[f"__{step_name}_metadata__"] = {
            "status": "completed",
            "output": result_ctx.shared_state,
            "messages": result_ctx.messages
        } 