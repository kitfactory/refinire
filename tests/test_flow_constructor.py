"""Test cases for the enhanced Flow constructor.

新しい拡張されたFlowコンストラクタのテストケース。
"""

import pytest
import asyncio
from typing import Optional

from refinire import Flow, Step, UserInputStep, DebugStep, Context, create_simple_agent


class DummyStep(Step):
    """Simple step for testing."""
    
    def __init__(self, name: str, next_step: Optional[str] = None):
        super().__init__(name)
        self.next_step = next_step
    
    async def run_async(self, user_input: Optional[str], ctx: Context) -> Context:
        ctx.update_step_info(self.name)
        ctx.add_system_message(f"DummyStep {self.name} executed")
        if self.next_step:
            ctx.goto(self.next_step)
        else:
            # If no next_step, finish the flow
            # next_stepがない場合、フローを終了
            ctx.finish()
        return ctx


class TestFlowConstructor:
    """Test the enhanced Flow constructor functionality.
    
    拡張されたFlowコンストラクタ機能のテスト。
    """
    
    def test_traditional_dict_mode(self):
        """Test traditional dictionary mode with start step.
        
        開始ステップありの従来の辞書モードをテスト。
        """
        step1 = DummyStep("step1")
        step2 = DummyStep("step2")
        
        flow = Flow(
            start="step1",
            steps={"step1": step1, "step2": step2}
        )
        
        assert flow.start == "step1"
        assert flow.steps == {"step1": step1, "step2": step2}
    
    def test_dict_mode_requires_start(self):
        """Test that dictionary mode requires start parameter.
        
        辞書モードではstartパラメータが必要であることをテスト。
        """
        step1 = DummyStep("step1")
        
        with pytest.raises(ValueError, match="start parameter is required"):
            Flow(steps={"step1": step1})
    
    def test_single_step_mode(self):
        """Test single step mode.
        
        単一ステップモードをテスト。
        """
        step = DummyStep("my_step")
        
        flow = Flow(steps=step)
        
        assert flow.start == "my_step"
        assert flow.steps == {"my_step": step}
    
    def test_list_mode_sequential(self):
        """Test list mode creates sequential workflow.
        
        リストモードがシーケンシャルワークフローを作成することをテスト。
        """
        step1 = DummyStep("step1")
        step2 = DummyStep("step2")
        step3 = DummyStep("step3")
        
        flow = Flow(steps=[step1, step2, step3])
        
        assert flow.start == "step1"
        assert len(flow.steps) == 3
        assert "step1" in flow.steps
        assert "step2" in flow.steps
        assert "step3" in flow.steps
        
        # Check sequential linking
        # シーケンシャルリンクをチェック
        assert step1.next_step == "step2"
        assert step2.next_step == "step3"
        assert step3.next_step is None  # Last step has no next
    
    def test_list_mode_respects_existing_next_step(self):
        """Test that list mode respects existing next_step values.
        
        リストモードが既存のnext_step値を尊重することをテスト。
        """
        step1 = DummyStep("step1", next_step="custom_next")
        step2 = DummyStep("step2")
        
        flow = Flow(steps=[step1, step2])
        
        # Should not override existing next_step
        # 既存のnext_stepを上書きしないこと
        assert step1.next_step == "custom_next"
        assert step2.next_step is None
    
    def test_empty_list_raises_error(self):
        """Test that empty list raises error.
        
        空のリストがエラーを発生させることをテスト。
        """
        with pytest.raises(ValueError, match="Steps list cannot be empty"):
            Flow(steps=[])
    
    def test_invalid_step_type_raises_error(self):
        """Test that invalid step type raises error.
        
        無効なステップタイプがエラーを発生させることをテスト。
        """
        with pytest.raises(ValueError, match="steps must be Dict\\[str, Step\\], List\\[Step\\], or Step"):
            Flow(steps="invalid")
    
    def test_step_without_name_raises_error(self):
        """Test that step without name attribute raises error.
        
        name属性のないステップがエラーを発生させることをテスト。
        """
        class InvalidStep:
            pass
        
        invalid_step = InvalidStep()
        
        with pytest.raises(ValueError, match="steps must be Dict\\[str, Step\\], List\\[Step\\], or Step"):
            Flow(steps=invalid_step)
    
    @pytest.mark.asyncio
    async def test_single_step_execution(self):
        """Test execution of single step flow.
        
        単一ステップフローの実行をテスト。
        """
        step = DummyStep("test_step")
        flow = Flow(steps=step, max_steps=5)  # Limit steps for debugging
        
        result = await flow.run(input_data="test input")
        
        assert result.current_step == "test_step"
        # Check system messages more carefully
        # システムメッセージをより注意深くチェック
        system_messages = [msg.content for msg in result.messages if msg.role == "system"]
        assert any("DummyStep test_step executed" in msg for msg in system_messages)
    
    @pytest.mark.asyncio
    async def test_sequential_flow_execution(self):
        """Test execution of sequential flow.
        
        シーケンシャルフローの実行をテスト。
        """
        step1 = DummyStep("step1")
        step2 = DummyStep("step2")
        step3 = DummyStep("step3")
        
        flow = Flow(steps=[step1, step2, step3])
        
        result = await flow.run(input_data="test input")
        
        # Should have executed all steps
        # すべてのステップが実行されるべき
        system_messages = [msg.content for msg in result.messages if msg.role == "system"]
        assert any("DummyStep step1 executed" in msg for msg in system_messages)
        assert any("DummyStep step2 executed" in msg for msg in system_messages)
        assert any("DummyStep step3 executed" in msg for msg in system_messages)
    
    @pytest.mark.asyncio
    async def test_genagent_single_step(self):
        """Test with GenAgent as single step.
        
        GenAgentを単一ステップとして使用することをテスト。
        """
        gen_agent = create_simple_agent(
            name="story_generator",
            instructions="Generate creative stories",
            model="gpt-4o-mini"
        )
        
        flow = Flow(steps=gen_agent)
        
        assert flow.start == "story_generator"
        assert "story_generator" in flow.steps
        assert flow.steps["story_generator"] == gen_agent
    
    @pytest.mark.asyncio
    async def test_genagent_list_mode(self):
        """Test with GenAgent list.
        
        GenAgentリストを使用することをテスト。
        """
        gen_agent1 = create_simple_agent(
            name="brainstormer",
            instructions="Generate ideas"
        )
        gen_agent2 = create_simple_agent(
            name="writer",
            instructions="Write content"
        )
        
        flow = Flow(steps=[gen_agent1, gen_agent2])
        
        assert flow.start == "brainstormer"
        assert len(flow.steps) == 2
        assert "brainstormer" in flow.steps
        assert "writer" in flow.steps
        
        # Check that sequential linking was set up correctly
        # シーケンシャルリンクが正しく設定されたことをチェック
        assert gen_agent1.next_step == "writer"
    
    def test_mixed_step_types_in_list(self):
        """Test mixing different step types in list.
        
        リスト内で異なるステップタイプを混合することをテスト。
        """
        gen_agent = create_simple_agent(
            name="generator",
            instructions="Generate content"
        )
        debug_step = DebugStep("debugger", "Debug message")
        user_step = UserInputStep("input", "Please provide input", "generator")
        
        flow = Flow(steps=[user_step, gen_agent, debug_step])
        
        assert flow.start == "input"
        assert len(flow.steps) == 3
        assert all(step_name in flow.steps for step_name in ["input", "generator", "debugger"])
        
        # Check sequential linking (where applicable)
        # シーケンシャルリンク（該当する場合）をチェック
        assert gen_agent.next_step == "debugger"
    
    def test_context_initialization(self):
        """Test that context is properly initialized.
        
        コンテキストが適切に初期化されることをテスト。
        """
        step = DummyStep("test_step")
        flow = Flow(steps=step)
        
        assert flow.context is not None
        assert flow.context.next_label == "test_step"
        assert flow.context.trace_id is not None
    
    def test_custom_context(self):
        """Test with custom context.
        
        カスタムコンテキストを使用することをテスト。
        """
        custom_context = Context()
        custom_context.add_user_message("Custom message")
        
        step = DummyStep("test_step")
        flow = Flow(steps=step, context=custom_context)
        
        assert flow.context == custom_context
        assert flow.context.next_label == "test_step"
        assert len(flow.context.messages) == 1
    
    def test_trace_id_setting(self):
        """Test trace ID setting.
        
        トレースID設定をテスト。
        """
        step = DummyStep("test_step")
        flow = Flow(steps=step, trace_id="custom_trace_123")
        
        assert flow.trace_id == "custom_trace_123"
        assert flow.context.trace_id == "custom_trace_123"
    
    def test_max_steps_setting(self):
        """Test max steps setting.
        
        最大ステップ設定をテスト。
        """
        step = DummyStep("test_step")
        flow = Flow(steps=step, max_steps=500)
        
        assert flow.max_steps == 500


class TestFlowBackwardCompatibility:
    """Test backward compatibility with existing code.
    
    既存コードとの後方互換性をテスト。
    """
    
    def test_existing_code_still_works(self):
        """Test that existing Flow usage still works.
        
        既存のFlow使用法がまだ動作することをテスト。
        """
        step1 = DummyStep("step1")
        step2 = DummyStep("step2")
        
        # This should still work exactly as before
        # これは以前と全く同じように動作するべき
        flow = Flow(
            start="step1",
            steps={"step1": step1, "step2": step2}
        )
        
        assert flow.start == "step1"
        assert flow.steps == {"step1": step1, "step2": step2}
    
    @pytest.mark.asyncio
    async def test_initial_input_parameter_still_works(self):
        """Test that initial_input parameter still works for backward compatibility.
        
        後方互換性のためにinitial_inputパラメータがまだ動作することをテスト。
        """
        step = DummyStep("test_step")
        flow = Flow(steps=step)
        
        result = await flow.run(initial_input="legacy input")
        
        user_messages = [msg.content for msg in result.messages if msg.role == "user"]
        assert any("legacy input" in msg for msg in user_messages)
    
    @pytest.mark.asyncio
    async def test_input_data_takes_precedence(self):
        """Test that input_data takes precedence over initial_input.
        
        input_dataがinitial_inputより優先されることをテスト。
        """
        step = DummyStep("test_step")
        flow = Flow(steps=step)
        
        result = await flow.run(
            input_data="new input",
            initial_input="old input"
        )
        
        # Should use input_data, not initial_input
        # initial_inputではなくinput_dataを使用するべき
        user_messages = [msg.content for msg in result.messages if msg.role == "user"]
        assert any("new input" in msg for msg in user_messages)
        assert not any("old input" in msg for msg in user_messages) 
