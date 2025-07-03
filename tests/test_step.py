import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass

from refinire.agents.flow.step import (
    Step, UserInputStep, ConditionStep, FunctionStep, 
    DebugStep,
    create_simple_condition, create_lambda_step
)
from refinire.agents.flow.context import Context


class DummyStep(Step):
    """
    Dummy step for testing
    テスト用ダミーステップ
    """
    def __init__(self, name: str, next_step: str = None):
        super().__init__(name)
        self.next_step = next_step
        self.executed = False
    
    async def run_async(self, user_input: str, ctx: Context) -> Context:
        """
        Execute dummy step
        ダミーステップを実行
        """
        self.executed = True
        ctx.update_step_info(self.name)
        
        if user_input:
            ctx.add_user_message(user_input)
        
        if self.next_step:
            ctx.goto(self.next_step)
        
        return ctx


class TestStepBase:
    """
    Test Step base class
    Step基底クラスをテスト
    """
    
    def test_step_initialization(self):
        """
        Test Step initialization
        Step初期化をテスト
        """
        step = DummyStep("test_step")
        
        assert step.name == "test_step"
        assert not step.executed
    
    def test_step_string_representation(self):
        """
        Test Step string representation
        Step文字列表現をテスト
        """
        step = DummyStep("test_step")
        
        str_repr = str(step)
        repr_repr = repr(step)
        
        assert "DummyStep" in str_repr
        assert "test_step" in str_repr
        assert str_repr == repr_repr
    
    @pytest.mark.asyncio
    async def test_step_execution(self):
        """
        Test Step execution
        Step実行をテスト
        """
        step = DummyStep("test_step", "next_step")
        ctx = Context()
        
        result_ctx = await step.run_async("test input", ctx)
        
        assert step.executed
        assert result_ctx.current_step == "test_step"
        assert result_ctx.next_label == "next_step"
        assert "test input" in str(result_ctx.messages)


class TestUserInputStep:
    """
    Test UserInputStep class
    UserInputStepクラスをテスト
    """
    
    def test_user_input_step_initialization(self):
        """
        Test UserInputStep initialization
        UserInputStep初期化をテスト
        """
        step = UserInputStep("input_step", "Enter something:", "next_step")
        
        assert step.name == "input_step"
        assert step.prompt == "Enter something:"
        assert step.next_step == "next_step"
    
    @pytest.mark.asyncio
    async def test_user_input_step_without_input(self):
        """
        Test UserInputStep without user input
        ユーザー入力なしのUserInputStepをテスト
        """
        step = UserInputStep("input_step", "Enter something:", "next_step")
        ctx = Context()
        
        result_ctx = await step.run_async(None, ctx)
        
        assert result_ctx.current_step == "input_step"
        assert result_ctx.awaiting_user_input
        assert result_ctx.awaiting_prompt == "Enter something:"
        assert result_ctx.next_label != "next_step"  # Should not advance yet
    
    @pytest.mark.asyncio
    async def test_user_input_step_with_input(self):
        """
        Test UserInputStep with user input
        ユーザー入力ありのUserInputStepをテスト
        """
        step = UserInputStep("input_step", "Enter something:", "next_step")
        ctx = Context()
        
        result_ctx = await step.run_async("user response", ctx)
        
        assert result_ctx.current_step == "input_step"
        assert not result_ctx.awaiting_user_input
        assert result_ctx.next_label == "next_step"
        assert "user response" in str(result_ctx.messages)
    
    @pytest.mark.asyncio
    async def test_user_input_step_no_next_step(self):
        """
        Test UserInputStep without next step
        次ステップなしのUserInputStepをテスト
        """
        step = UserInputStep("input_step", "Enter something:")
        ctx = Context()
        
        result_ctx = await step.run_async("user response", ctx)
        
        assert result_ctx.current_step == "input_step"
        assert result_ctx.next_label is None  # Flow should end


class TestConditionStep:
    """
    Test ConditionStep class
    ConditionStepクラスをテスト
    """
    
    def test_condition_step_initialization(self):
        """
        Test ConditionStep initialization
        ConditionStep初期化をテスト
        """
        def condition_func(ctx):
            return True
        
        step = ConditionStep("condition", condition_func, "true_step", "false_step")
        
        assert step.name == "condition"
        assert step.condition == condition_func
        assert step.if_true == "true_step"
        assert step.if_false == "false_step"
    
    @pytest.mark.asyncio
    async def test_condition_step_true_sync(self):
        """
        Test ConditionStep with True condition (sync)
        True条件（同期）のConditionStepをテスト
        """
        def condition_func(ctx):
            return True
        
        step = ConditionStep("condition", condition_func, "true_step", "false_step")
        ctx = Context()
        
        result_ctx = await step.run_async(None, ctx)
        
        assert result_ctx.current_step == "condition"
        assert result_ctx.next_label == "true_step"
    
    @pytest.mark.asyncio
    async def test_condition_step_false_sync(self):
        """
        Test ConditionStep with False condition (sync)
        False条件（同期）のConditionStepをテスト
        """
        def condition_func(ctx):
            return False
        
        step = ConditionStep("condition", condition_func, "true_step", "false_step")
        ctx = Context()
        
        result_ctx = await step.run_async(None, ctx)
        
        assert result_ctx.current_step == "condition"
        assert result_ctx.next_label == "false_step"
    
    @pytest.mark.asyncio
    async def test_condition_step_true_async(self):
        """
        Test ConditionStep with True condition (async)
        True条件（非同期）のConditionStepをテスト
        """
        async def condition_func(ctx):
            return True
        
        step = ConditionStep("condition", condition_func, "true_step", "false_step")
        ctx = Context()
        
        result_ctx = await step.run_async(None, ctx)
        
        assert result_ctx.current_step == "condition"
        assert result_ctx.next_label == "true_step"
    
    @pytest.mark.asyncio
    async def test_condition_step_error_handling(self):
        """
        Test ConditionStep error handling
        ConditionStepエラーハンドリングをテスト
        """
        def condition_func(ctx):
            raise Exception("Condition error")
        
        step = ConditionStep("condition", condition_func, "true_step", "false_step")
        ctx = Context()
        
        result_ctx = await step.run_async(None, ctx)
        
        assert result_ctx.current_step == "condition"
        assert result_ctx.next_label == "false_step"  # Should go to false on error
        assert "Condition evaluation error" in str(result_ctx.messages)


class TestFunctionStep:
    """
    Test FunctionStep class
    FunctionStepクラスをテスト
    """
    
    def test_function_step_initialization(self):
        """
        Test FunctionStep initialization
        FunctionStep初期化をテスト
        """
        def test_func(user_input, ctx):
            return ctx
        
        step = FunctionStep("func_step", test_func, "next_step")
        
        assert step.name == "func_step"
        assert step.function == test_func
        assert step.next_step == "next_step"
    
    @pytest.mark.asyncio
    async def test_function_step_sync_function(self):
        """
        Test FunctionStep with sync function
        同期関数のFunctionStepをテスト
        """
        def test_func(user_input, ctx):
            ctx.add_system_message(f"Function executed with: {user_input}")
            return ctx
        
        step = FunctionStep("func_step", test_func, "next_step")
        ctx = Context()
        
        result_ctx = await step.run_async("test input", ctx)
        
        assert result_ctx.current_step == "func_step"
        assert result_ctx.next_label == "next_step"
        assert "Function executed with: test input" in str(result_ctx.messages)
    
    @pytest.mark.asyncio
    async def test_function_step_async_function(self):
        """
        Test FunctionStep with async function
        非同期関数のFunctionStepをテスト
        """
        async def test_func(user_input, ctx):
            ctx.add_system_message(f"Async function executed with: {user_input}")
            return ctx
        
        step = FunctionStep("func_step", test_func, "next_step")
        ctx = Context()
        
        result_ctx = await step.run_async("test input", ctx)
        
        assert result_ctx.current_step == "func_step"
        assert result_ctx.next_label == "next_step"
        assert "Async function executed with: test input" in str(result_ctx.messages)
    
    @pytest.mark.asyncio
    async def test_function_step_error_handling(self):
        """
        Test FunctionStep error handling
        FunctionStepエラーハンドリングをテスト
        """
        def error_func(user_input, ctx):
            raise Exception("Function error")
        
        step = FunctionStep("func_step", error_func, "next_step")
        ctx = Context()
        
        result_ctx = await step.run_async("test input", ctx)

        assert result_ctx.current_step == "func_step"
        assert result_ctx.next_label == "next_step"  # Step continues to next even on error
        assert "Function execution error" in str(result_ctx.messages)
    
    @pytest.mark.asyncio
    async def test_function_step_no_next_step(self):
        """
        Test FunctionStep without next step
        次ステップなしのFunctionStepをテスト
        """
        def test_func(user_input, ctx):
            ctx.add_system_message("Function executed")
            return ctx
        
        step = FunctionStep("func_step", test_func)
        ctx = Context()
        
        result_ctx = await step.run_async("test input", ctx)
        
        assert result_ctx.current_step == "func_step"
        assert result_ctx.next_label is None  # Flow should end


class TestDebugStep:
    """
    Test DebugStep class
    DebugStepクラスをテスト
    """
    
    def test_debug_step_initialization(self):
        """
        Test DebugStep initialization
        DebugStep初期化をテスト
        """
        step = DebugStep("debug", "Debug message", True, "next_step")
        
        assert step.name == "debug"
        assert step.message == "Debug message"
        assert step.print_context == True
        assert step.next_step == "next_step"
        
    @pytest.mark.asyncio
    async def test_debug_step_execution(self):
        """
        Test DebugStep execution
        DebugStep実行をテスト
        """
        step = DebugStep("debug", "Debug message", False, "next_step")
        ctx = Context()
        ctx.add_user_message("test message")
        
        with patch('builtins.print') as mock_print:
            result_ctx = await step.run_async("test input", ctx)
        
        assert result_ctx.current_step == "debug"
        assert result_ctx.next_label == "next_step"
        
        # Check that debug message was printed
        # デバッグメッセージが出力されたことをチェック
        mock_print.assert_called()
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Debug message" in call for call in print_calls)
    
    @pytest.mark.asyncio
    async def test_debug_step_with_context_print(self):
        """
        Test DebugStep with context printing
        コンテキスト出力ありのDebugStepをテスト
        """
        step = DebugStep("debug", "Debug with context", True, "next_step")
        ctx = Context()
        ctx.add_user_message("context message")
        
        with patch('builtins.print') as mock_print:
            result_ctx = await step.run_async("test input", ctx)
        
        assert result_ctx.current_step == "debug"
        assert result_ctx.next_label == "next_step"
        
        # Check that both debug message and context were printed
        # デバッグメッセージとコンテキスト両方が出力されたことをチェック
        mock_print.assert_called()
        print_calls = [str(call.args[0]) for call in mock_print.call_args_list]
        assert any("Debug with context" in call for call in print_calls)
        assert any("Context:" in call for call in print_calls)





class TestStepHelperFunctions:
    """
    Test Step helper functions
    Stepヘルパー関数をテスト
    """
    
    def test_create_simple_condition(self):
        """
        Test create_simple_condition function
        create_simple_condition関数をテスト
        """
        condition = create_simple_condition("shared_state.user_name", "Alice")
        
        # Test with matching value
        # 一致する値でテスト
        ctx = Context()
        ctx.shared_state["user_name"] = "Alice"
        assert condition(ctx) == True
        
        # Test with non-matching value
        # 一致しない値でテスト
        ctx.shared_state["user_name"] = "Bob"
        assert condition(ctx) == False
        
        # Test with missing field
        # フィールドがない場合をテスト
        ctx = Context()
        assert condition(ctx) == False
    
    def test_create_lambda_step(self):
        """
        Test create_lambda_step function
        create_lambda_step関数をテスト
        """
        def test_func(ctx):
            ctx.add_system_message("Lambda executed")
            return "lambda result"
        
        step = create_lambda_step("lambda_step", test_func, "next_step")
        
        assert isinstance(step, FunctionStep)
        assert step.name == "lambda_step"
        assert step.next_step == "next_step"
    
    @pytest.mark.asyncio
    async def test_create_lambda_step_execution(self):
        """
        Test create_lambda_step execution
        create_lambda_step実行をテスト
        """
        def test_func(ctx):
            ctx.add_system_message("Lambda executed")
            return "lambda result"
        
        step = create_lambda_step("lambda_step", test_func, "next_step")
        ctx = Context()
        
        result_ctx = await step.run_async("test input", ctx)
        
        assert result_ctx.current_step == "lambda_step"
        assert result_ctx.next_label == "next_step"
        assert "Lambda executed" in str(result_ctx.messages)


