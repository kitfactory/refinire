#!/usr/bin/env python3
"""
Tests for Trace/Span functionality
トレース/スパン機能のテスト

Tests the mapping of Flow -> Trace and Step -> Span
FlowからTrace、StepからSpanへのマッピングをテスト
"""

import pytest
import asyncio
from datetime import datetime
from refinire import Flow, Context, FunctionStep


def simple_function(input_data: str, ctx: Context) -> Context:
    """Simple test function / 簡単なテスト関数"""
    ctx.set_artifact("result", f"processed: {input_data}")
    return ctx


def error_function(input_data: str, ctx: Context) -> Context:
    """Function that raises an error / エラーを発生させる関数"""
    raise ValueError("Test error")


class TestTraceSpanMapping:
    """Test trace/span mapping functionality / トレース/スパンマッピング機能のテスト"""
    
    def test_flow_creates_trace_id(self):
        """Test that Flow creates a trace ID / FlowがトレースIDを作成することをテスト"""
        flow = Flow(name="test_flow", steps={"step1": FunctionStep(name="step1", function=simple_function)}, start="step1")
        
        assert flow.trace_id is not None
        assert flow.flow_name == "test_flow"
        assert flow.flow_id is not None
        assert flow.flow_name in flow.flow_id
    
    def test_context_has_span_tracking(self):
        """Test that Context tracks spans / Contextがスパンを追跡することをテスト"""
        ctx = Context()
        
        # Initially no spans
        # 初期状態ではスパンなし
        assert len(ctx.span_history) == 0
        assert ctx.current_span_id is None
        
        # Update step info creates span
        # ステップ情報更新でスパンを作成
        ctx.update_step_info("test_step")
        
        assert len(ctx.span_history) == 1
        assert ctx.current_span_id is not None
        assert ctx.current_step == "test_step"
        
        # Check span structure
        # スパン構造をチェック
        span = ctx.span_history[0]
        assert span["span_id"] == ctx.current_span_id
        assert span["step_name"] == "test_step"
        assert span["status"] == "started"
        assert span["start_time"] is not None
        assert span["end_time"] is None
    
    def test_span_finalization(self):
        """Test span finalization / スパン終了処理のテスト"""
        ctx = Context()
        ctx.update_step_info("test_step")
        
        # Finalize span
        # スパンを終了
        ctx._finalize_current_span("completed")
        
        span = ctx.span_history[0]
        assert span["status"] == "completed"
        assert span["end_time"] is not None
    
    def test_span_error_handling(self):
        """Test span error handling / スパンエラーハンドリングのテスト"""
        ctx = Context()
        ctx.update_step_info("error_step")
        
        # Finalize with error
        # エラーで終了
        ctx._finalize_current_span("error", "Test error message")
        
        span = ctx.span_history[0]
        assert span["status"] == "error"
        assert span["error"] == "Test error message"
        assert span["end_time"] is not None
    
    def test_multiple_spans_in_sequence(self):
        """Test multiple spans in sequence / 連続する複数スパンのテスト"""
        ctx = Context()
        
        # First span
        # 最初のスパン
        ctx.update_step_info("step1")
        first_span_id = ctx.current_span_id
        ctx._finalize_current_span("completed")
        
        # Second span
        # 2番目のスパン
        ctx.update_step_info("step2")
        second_span_id = ctx.current_span_id
        ctx._finalize_current_span("completed")
        
        assert len(ctx.span_history) == 2
        assert first_span_id != second_span_id
        assert ctx.span_history[0]["step_name"] == "step1"
        assert ctx.span_history[1]["step_name"] == "step2"
    
    def test_trace_summary(self):
        """Test trace summary functionality / トレースサマリー機能のテスト"""
        ctx = Context(trace_id="test_trace_123")
        
        # Add some spans
        # スパンを追加
        ctx.update_step_info("step1")
        ctx._finalize_current_span("completed")
        
        ctx.update_step_info("step2")
        ctx._finalize_current_span("error", "Test error")
        
        summary = ctx.get_trace_summary()
        
        assert summary["trace_id"] == "test_trace_123"
        assert summary["total_spans"] == 2
        assert summary["completed_spans"] == 1
        assert summary["error_spans"] == 1
        assert summary["active_spans"] == 0
        assert summary["total_duration_seconds"] is not None
    
    @pytest.mark.asyncio
    async def test_flow_execution_creates_spans(self):
        """Test that flow execution creates spans / フロー実行がスパンを作成することをテスト"""
        steps = {
            "step1": FunctionStep(name="step1", function=simple_function, next_step="step2"),
            "step2": FunctionStep(name="step2", function=simple_function, next_step=None)
        }
        
        flow = Flow(name="test_flow", steps=steps, start="step1")
        
        # Execute flow
        # フローを実行
        context = await flow.run("test input")
        
        # Check trace information
        # トレース情報をチェック
        assert context.trace_id == flow.trace_id
        assert len(context.span_history) == 2
        
        # Check spans
        # スパンをチェック
        span1 = context.span_history[0]
        span2 = context.span_history[1]
        
        assert span1["step_name"] == "step1"
        assert span2["step_name"] == "step2"
        assert span1["trace_id"] == flow.trace_id
        assert span2["trace_id"] == flow.trace_id
        assert span1["status"] == "completed"
        assert span2["status"] == "completed" 
