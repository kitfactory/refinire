import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from refinire.agents.flow import Flow, FlowExecutionError, create_simple_flow, create_conditional_flow
from refinire.agents.flow import Step, UserInputStep, ConditionStep, FunctionStep
from refinire.agents.flow import Context


class DummyStep(Step):
    """
    Dummy step for testing
    テスト用ダミーステップ
    """
    def __init__(self, name: str, next_step: str = None, should_error: bool = False):
        super().__init__(name)
        self.next_step = next_step
        self.should_error = should_error
        self.executed = False
    
    async def run_async(self, user_input: str, ctx: Context) -> Context:
        """
        Execute dummy step
        ダミーステップを実行
        """
        self.executed = True
        ctx.update_step_info(self.name)
        
        if self.should_error:
            raise Exception(f"Error in step {self.name}")
        
        if user_input:
            ctx.add_user_message(user_input)
        
        if self.next_step:
            ctx.goto(self.next_step)
        else:
            # No next step means this is the end
            ctx.finish()
        
        return ctx


class TestFlow:
    """
    Test Flow class basic functionality
    Flowクラスの基本機能をテスト
    """
    
    def test_flow_initialization(self):
        """
        Test Flow initialization
        Flow初期化をテスト
        """
        # Create steps
        # ステップを作成
        step1 = DummyStep("step1", "step2")
        step2 = DummyStep("step2")
        steps = {"step1": step1, "step2": step2}
        
        # Initialize flow
        # フローを初期化
        flow = Flow(start="step1", steps=steps)
        
        # Check initialization
        # 初期化をチェック
        assert flow.start == "step1"
        assert flow.steps == steps
        assert flow.context is not None
        assert flow.max_steps == 1000
        assert flow.trace_id is not None
        assert flow.context.next_label == "step1"
        assert not flow.finished
        assert flow.current_step_name is None
        assert flow.next_step_name == "step1"
    
    def test_flow_initialization_with_context(self):
        """
        Test Flow initialization with custom context
        カスタムコンテキストでのFlow初期化をテスト
        """
        custom_context = Context()
        custom_context.add_user_message("initial message")
        
        step1 = DummyStep("step1")
        steps = {"step1": step1}
        
        flow = Flow(start="step1", steps=steps, context=custom_context)
        
        # Check that custom context is used
        # カスタムコンテキストが使用されていることをチェック
        assert flow.context == custom_context
        assert flow.context.trace_id is not None
        assert flow.context.next_label == "step1"
    
    @pytest.mark.asyncio
    async def test_flow_run_simple(self):
        """
        Test simple flow execution
        単純なフロー実行をテスト
        """
        step1 = DummyStep("step1", "step2")
        step2 = DummyStep("step2")
        steps = {"step1": step1, "step2": step2}
        
        flow = Flow(start="step1", steps=steps)
        result_context = await flow.run("initial input")
        
        # Check execution
        # 実行をチェック
        assert step1.executed
        assert step2.executed
        assert flow.finished
        assert "initial input" in str(result_context.messages)
    
    @pytest.mark.asyncio
    async def test_flow_run_single_step(self):
        """
        Test flow with single step
        単一ステップのフローをテスト
        """
        step1 = DummyStep("step1")
        steps = {"step1": step1}
        
        flow = Flow(start="step1", steps=steps)
        result_context = await flow.run("test input")
        
        # Check execution
        # 実行をチェック
        assert step1.executed
        assert flow.finished
        assert "test input" in str(result_context.messages)
    
    @pytest.mark.asyncio
    async def test_flow_run_max_steps_exceeded(self):
        """
        Test flow with max steps exceeded
        最大ステップ数超過のフローをテスト
        """
        # Create infinite loop
        # 無限ループを作成
        step1 = DummyStep("step1", "step1")  # Points to itself
        steps = {"step1": step1}
        
        flow = Flow(start="step1", steps=steps, max_steps=5)
        
        with pytest.raises(FlowExecutionError, match="exceeded maximum steps"):
            await flow.run()
    
    @pytest.mark.asyncio
    async def test_flow_run_error_handling(self):
        """
        Test flow error handling
        フローエラーハンドリングをテスト
        """
        step1 = DummyStep("step1", should_error=True)
        steps = {"step1": step1}
        
        flow = Flow(start="step1", steps=steps)
        result_context = await flow.run()
        
        # Flow should stop on error but not raise
        # フローはエラー時に停止するが例外は発生させない
        assert step1.executed
        assert flow.finished  # Flow is finished due to error
        assert "error" in result_context.artifacts  # Error artifact should be set
    
    @pytest.mark.asyncio
    async def test_flow_run_unknown_step(self):
        """
        Test flow with unknown step reference
        未知のステップ参照があるフローをテスト
        """
        step1 = DummyStep("step1", "unknown_step")
        steps = {"step1": step1}
        
        flow = Flow(start="step1", steps=steps)
        result_context = await flow.run()
        
        # Flow should stop when unknown step is encountered
        # 未知のステップに遭遇したときフローは停止する
        assert step1.executed
        assert flow.finished  # Flow finishes when reaching unknown step
    
    @pytest.mark.asyncio
    async def test_flow_run_loop_basic(self):
        """
        Test flow run_loop method
        フローのrun_loopメソッドをテスト
        """
        step1 = DummyStep("step1", "step2")
        step2 = DummyStep("step2")
        steps = {"step1": step1, "step2": step2}
        
        flow = Flow(start="step1", steps=steps)
        
        # Start run_loop as background task
        # run_loopをバックグラウンドタスクとして開始
        task = asyncio.create_task(flow.run_loop())
        
        # Wait a bit for execution
        # 実行を少し待つ
        await asyncio.sleep(0.1)
        
        # Check that steps were executed
        # ステップが実行されたことをチェック
        assert step1.executed
        assert step2.executed
        
        # Cancel the task
        # タスクをキャンセル
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    def test_flow_hooks(self):
        """
        Test flow hooks functionality
        フローフック機能をテスト
        """
        step1 = DummyStep("step1")
        steps = {"step1": step1}
        flow = Flow(start="step1", steps=steps)
        
        # Create mock hooks
        # モックフックを作成
        before_hook = MagicMock()
        after_hook = MagicMock()
        error_hook = MagicMock()
        
        # Add hooks
        # フックを追加
        flow.add_hook("before_step", before_hook)
        flow.add_hook("after_step", after_hook)
        flow.add_hook("error", error_hook)
        
        # Check hooks were added
        # フックが追加されたことをチェック
        assert before_hook in flow.before_step_hooks
        assert after_hook in flow.after_step_hooks
        assert error_hook in flow.error_hooks
    
    def test_flow_properties(self):
        """
        Test flow property methods
        フロープロパティメソッドをテスト
        """
        step1 = DummyStep("step1")
        steps = {"step1": step1}
        flow = Flow(start="step1", steps=steps)
        
        # Test initial state
        # 初期状態をテスト
        assert not flow.finished
        assert flow.current_step_name is None
        assert flow.next_step_name == "step1"
        
        # Update context to simulate step execution
        # ステップ実行をシミュレートするためコンテキストを更新
        flow.context.update_step_info("step1")
        assert flow.current_step_name == "step1"
    
    def test_flow_step_history(self):
        """
        Test flow step history functionality
        フローステップ履歴機能をテスト
        """
        step1 = DummyStep("step1")
        steps = {"step1": step1}
        flow = Flow(start="step1", steps=steps)
        
        # Get initial history
        # 初期履歴を取得
        history = flow.get_step_history()
        assert isinstance(history, list)
        assert len(history) == 0
        
        # Add some history
        # 履歴を追加
        flow.context.update_step_info("step1")
        history = flow.get_step_history()
        assert len(history) > 0
    
    def test_flow_summary(self):
        """
        Test flow summary functionality
        フロー要約機能をテスト
        """
        step1 = DummyStep("step1")
        steps = {"step1": step1}
        flow = Flow(start="step1", steps=steps)
        
        summary = flow.get_flow_summary()
        
        # Check summary structure
        # 要約構造をチェック
        assert isinstance(summary, dict)
        assert "trace_id" in summary
        assert "current_step" in summary
        assert "next_step" in summary
        assert "finished" in summary
        assert "step_count" in summary
    
    def test_flow_reset(self):
        """
        Test flow reset functionality
        フローリセット機能をテスト
        """
        step1 = DummyStep("step1")
        steps = {"step1": step1}
        flow = Flow(start="step1", steps=steps)
        
        # Modify context
        # コンテキストを変更
        flow.context.add_user_message("test message")
        flow.context.update_step_info("step1")
        
        # Reset flow
        # フローをリセット
        flow.reset()
        
        # Check reset state
        # リセット状態をチェック
        assert flow.context.next_label == "step1"
        assert flow.context.step_count == 0
        assert len(flow.context.messages) == 0
    
    def test_flow_stop(self):
        """
        Test flow stop functionality
        フロー停止機能をテスト
        """
        step1 = DummyStep("step1")
        steps = {"step1": step1}
        flow = Flow(start="step1", steps=steps)
        
        # Stop flow
        # フローを停止
        flow.stop()
        
        # Check stop state
        # 停止状態をチェック
        assert not flow._running
    
    @pytest.mark.asyncio
    async def test_flow_background_task(self):
        """
        Test flow background task functionality
        フローバックグラウンドタスク機能をテスト
        """
        step1 = DummyStep("step1")
        steps = {"step1": step1}
        flow = Flow(start="step1", steps=steps)
        
        # Start background task
        # バックグラウンドタスクを開始
        task = await flow.start_background_task()
        
        # Check task is created
        # タスクが作成されたことをチェック
        assert task is not None
        assert isinstance(task, asyncio.Task)
        
        # Cancel task
        # タスクをキャンセル
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    def test_flow_string_representation(self):
        """
        Test flow string representation
        フロー文字列表現をテスト
        """
        step1 = DummyStep("step1")
        steps = {"step1": step1}
        flow = Flow(start="step1", steps=steps)
        
        # Test __str__ and __repr__
        # __str__と__repr__をテスト
        str_repr = str(flow)
        repr_repr = repr(flow)
        
        assert "Flow" in str_repr
        assert "step1" in str_repr
        assert str_repr == repr_repr


class TestFlowHelperFunctions:
    """
    Test Flow helper functions
    フローヘルパー関数をテスト
    """
    
    def test_create_simple_flow(self):
        """
        Test create_simple_flow function
        create_simple_flow関数をテスト
        """
        step1 = DummyStep("step1")
        step2 = DummyStep("step2")
        
        steps = [("step1", step1), ("step2", step2)]
        flow = create_simple_flow(steps)
        
        # Check flow creation
        # フロー作成をチェック
        assert isinstance(flow, Flow)
        assert flow.start == "step1"
        assert "step1" in flow.steps
        assert "step2" in flow.steps
        assert flow.steps["step1"] == step1
        assert flow.steps["step2"] == step2
    
    def test_create_simple_flow_with_context(self):
        """
        Test create_simple_flow with custom context
        カスタムコンテキストでのcreate_simple_flow関数をテスト
        """
        step1 = DummyStep("step1")
        custom_context = Context()
        custom_context.add_user_message("custom message")
        
        steps = [("step1", step1)]
        flow = create_simple_flow(steps, context=custom_context)
        
        # Check context is used
        # コンテキストが使用されていることをチェック
        assert flow.context == custom_context
        assert "custom message" in str(flow.context.messages)
    
    def test_create_conditional_flow(self):
        """
        Test create_conditional_flow function
        create_conditional_flow関数をテスト
        """
        initial_step = DummyStep("initial")
        condition_step = DummyStep("condition")
        true_step = DummyStep("true_branch")
        false_step = DummyStep("false_branch")
        
        true_branch = [true_step]
        false_branch = [false_step]
        
        flow = create_conditional_flow(
            initial_step=initial_step,
            condition_step=condition_step,
            true_branch=true_branch,
            false_branch=false_branch
        )
        
        # Check flow creation
        # フロー作成をチェック
        assert isinstance(flow, Flow)
        assert flow.start == "start"  # create_conditional_flow uses "start" as initial step name
        assert "start" in flow.steps  # Initial step is named "start"
        assert "condition" in flow.steps
        assert "true_0" in flow.steps  # True branch steps are named "true_N"
        assert "false_0" in flow.steps  # False branch steps are named "false_N"


class TestFlowUserInput:
    """
    Test Flow user input coordination
    フローユーザー入力調整をテスト
    """
    
    @pytest.mark.asyncio
    async def test_flow_with_user_input_step(self):
        """
        Test flow with UserInputStep
        UserInputStepを含むフローをテスト
        """
        user_input_step = UserInputStep("input", "Please enter something:", "step2")
        step2 = DummyStep("step2")
        steps = {"input": user_input_step, "step2": step2}
        
        flow = Flow(start="input", steps=steps)
        
        # Create background task for interactive flow
        # 対話的フロー用のバックグラウンドタスクを作成
        flow_task = asyncio.create_task(flow.run_loop())
        
        # Wait a moment for the task to start and reach user input
        # タスクが開始してユーザー入力に到達するまで少し待つ
        await asyncio.sleep(0.1)
        
        # Check that flow is waiting for user input
        # フローがユーザー入力を待機していることをチェック
        assert flow.context.awaiting_user_input
        assert flow.context.awaiting_prompt == "Please enter something:"
        assert not step2.executed
        
        # Provide user input
        # ユーザー入力を提供
        flow.feed("user response")
        
        # Wait for flow to complete
        # フローの完了を待つ
        await flow_task
        
        # Now step2 should be executed
        # 今度はstep2が実行されるはず
        assert step2.executed
        assert flow.finished
    
    def test_flow_next_prompt(self):
        """
        Test flow next_prompt method
        フローnext_promptメソッドをテスト
        """
        user_input_step = UserInputStep("input", "Test prompt")
        steps = {"input": user_input_step}
        flow = Flow(start="input", steps=steps)
        
        # Initially no prompt
        # 初期はプロンプトなし
        assert flow.next_prompt() is None
        
        # Set waiting state
        # 待機状態を設定
        flow.context.set_waiting_for_user_input("Test prompt")
        assert flow.next_prompt() == "Test prompt"
    
    def test_flow_feed(self):
        """
        Test flow feed method
        フローfeedメソッドをテスト
        """
        step1 = DummyStep("step1")
        steps = {"step1": step1}
        flow = Flow(start="step1", steps=steps)
        
        # Feed user input
        # ユーザー入力を供給
        flow.feed("test input")
        
        # Check input was added to context
        # 入力がコンテキストに追加されたことをチェック
        assert "test input" in str(flow.context.messages)
    
    def test_flow_step_method(self):
        """
        Test flow step method for manual stepping
        手動ステッピング用フローstepメソッドをテスト
        """
        step1 = DummyStep("step1", "step2")
        step2 = DummyStep("step2")
        steps = {"step1": step1, "step2": step2}
        flow = Flow(start="step1", steps=steps)
        
        # Execute one step
        # 1ステップ実行
        flow.step()
        assert step1.executed
        assert not step2.executed
        
        # Execute next step
        # 次のステップ実行
        flow.step()
        assert step2.executed
        assert flow.finished
