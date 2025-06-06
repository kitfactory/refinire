from __future__ import annotations

"""Step — Step interface and basic implementations for Flow workflows.

Stepはフローワークフロー用のステップインターフェースと基本実装を提供します。
UserInputStep、ConditionStep、ForkStep、JoinStepなどの基本的なステップを含みます。
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union, Awaitable
from concurrent.futures import ThreadPoolExecutor
import threading

from .context import Context


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
    
    @abstractmethod
    async def run(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute step and return updated context
        ステップを実行し、更新されたコンテキストを返す
        
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
    
    async def run(self, user_input: Optional[str], ctx: Context) -> Context:
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
    
    async def run(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute condition step
        条件ステップを実行
        
        Args:
            user_input: User input (not used) / ユーザー入力（使用されない）
            ctx: Current context / 現在のコンテキスト
            
        Returns:
            Context: Updated context with routing / ルーティング付き更新済みコンテキスト
        """
        ctx.update_step_info(self.name)
        
        # Evaluate condition (may be async)
        # 条件を評価（非同期の可能性あり）
        try:
            result = self.condition(ctx)
            if asyncio.iscoroutine(result):
                result = await result
        except Exception as e:
            # On error, go to false branch
            # エラー時はfalseブランチに進む
            ctx.add_system_message(f"Condition evaluation error: {e}")
            result = False
        
        # Route based on condition result
        # 条件結果に基づいてルーティング
        next_step = self.if_true if result else self.if_false
        ctx.goto(next_step)
        
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
    
    async def run(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute function step
        関数ステップを実行
        
        Args:
            user_input: User input / ユーザー入力
            ctx: Current context / 現在のコンテキスト
            
        Returns:
            Context: Updated context / 更新済みコンテキスト
        """
        ctx.update_step_info(self.name)
        
        try:
            # Execute the function (may be async)
            # 関数を実行（非同期の可能性あり）
            result = self.function(user_input, ctx)
            if asyncio.iscoroutine(result):
                ctx = await result
            else:
                ctx = result
        except Exception as e:
            ctx.add_system_message(f"Function execution error in {self.name}: {e}")
        
        # Set next step if specified, otherwise finish the flow
        # 指定されている場合は次ステップを設定、そうでなければフローを終了
        if self.next_step:
            ctx.goto(self.next_step)
        else:
            ctx.finish()
        
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
    
    async def run(self, user_input: Optional[str], ctx: Context) -> Context:
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
    
    async def run(self, user_input: Optional[str], ctx: Context) -> Context:
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


class AgentPipelineStep(Step):
    """
    Step that wraps AgentPipeline for use in Flow
    FlowでAgentPipelineを使用するためのラッパーステップ
    
    This step allows using existing AgentPipeline instances as flow steps.
    このステップは既存のAgentPipelineインスタンスをフローステップとして使用できます。
    """
    
    def __init__(self, name: str, pipeline: Any, next_step: Optional[str] = None):
        """
        Initialize agent pipeline step
        エージェントパイプラインステップを初期化
        
        Args:
            name: Step name / ステップ名
            pipeline: AgentPipeline instance / AgentPipelineインスタンス
            next_step: Next step after pipeline execution / パイプライン実行後の次ステップ
        """
        super().__init__(name)
        self.pipeline = pipeline
        self.next_step = next_step
    
    async def run(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute agent pipeline step
        エージェントパイプラインステップを実行
        
        Args:
            user_input: User input / ユーザー入力
            ctx: Current context / 現在のコンテキスト
            
        Returns:
            Context: Updated context / 更新済みコンテキスト
        """
        ctx.update_step_info(self.name)
        
        try:
            # Use the last user input if available
            # 利用可能な場合は最後のユーザー入力を使用
            input_text = user_input or ctx.last_user_input or ""
            
            # Execute pipeline in thread pool to handle sync methods
            # 同期メソッドを処理するためにスレッドプールでパイプラインを実行
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                future = loop.run_in_executor(executor, self.pipeline.run, input_text)
                result = await future
            
            # Store result in context
            # 結果をコンテキストに保存
            if result is not None:
                ctx.prev_outputs[self.name] = result
                ctx.add_assistant_message(str(result))
            
        except Exception as e:
            ctx.add_system_message(f"Pipeline execution error in {self.name}: {e}")
            ctx.prev_outputs[self.name] = None
        
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
    デバッグとログ用ステップ
    
    This step prints or logs context information for debugging purposes.
    このステップはデバッグ目的でコンテキスト情報を印刷またはログ出力します。
    """
    
    def __init__(self, name: str, message: str = "", print_context: bool = False, next_step: Optional[str] = None):
        """
        Initialize debug step
        デバッグステップを初期化
        
        Args:
            name: Step name / ステップ名
            message: Debug message / デバッグメッセージ
            print_context: Whether to print full context / 完全なコンテキストを印刷するか
            next_step: Next step / 次ステップ
        """
        super().__init__(name)
        self.message = message
        self.print_context = print_context
        self.next_step = next_step
    
    async def run(self, user_input: Optional[str], ctx: Context) -> Context:
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
        
        # Print debug information
        # デバッグ情報を印刷
        print(f"🐛 DEBUG [{self.name}]: {self.message}")
        if user_input:
            print(f"   User Input: {user_input}")
        print(f"   Step Count: {ctx.step_count}")
        print(f"   Next Label: {ctx.next_label}")
        
        if self.print_context:
            print(f"   Context: {ctx.dict()}")
        
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