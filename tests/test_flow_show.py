#!/usr/bin/env python3
"""
Test Flow.show() method for flow visualization.

Flow.show()メソッドの流れ可視化テスト。
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import Flow, UserInputStep, ConditionStep, FunctionStep, Context, RouterAgent
from refinire.agents.router import RouterConfig


class TestFlowShow:
    """
    Test cases for Flow.show() method.
    Flow.show()メソッドのテストケース。
    """
    
    def test_simple_flow_text_format(self):
        """Test show() method with simple flow in text format."""
        # Create simple flow
        # 簡単なフローを作成
        steps = {
            "start": UserInputStep("start", "Start prompt", "middle"),
            "middle": UserInputStep("middle", "Middle prompt", "end"),
            "end": UserInputStep("end", "End prompt", None)
        }
        flow = Flow(start="start", steps=steps)
        
        # Get text diagram
        # テキスト図を取得
        result = flow.show(format="text", include_history=False)
        
        # Verify text format content
        # テキスト形式の内容を検証
        assert "Flow Diagram:" in result
        assert "start (UserInputStep)" in result
        assert "middle (UserInputStep)" in result
        assert "end (UserInputStep)" in result
    
    def test_simple_flow_mermaid_format(self):
        """Test show() method with simple flow in Mermaid format."""
        # Create simple flow
        # 簡単なフローを作成
        steps = {
            "start": UserInputStep("start", "Start prompt", "end"),
            "end": UserInputStep("end", "End prompt", None)
        }
        flow = Flow(start="start", steps=steps)
        
        # Get Mermaid diagram
        # Mermaid図を取得
        result = flow.show(format="mermaid", include_history=False)
        
        # Verify Mermaid format content
        # Mermaid形式の内容を検証
        assert "graph TD" in result
        assert 'start["start<br/>(UserInputStep)"]:::start' in result
        assert 'end["end<br/>(UserInputStep)"]' in result
        assert "start --> end" in result
    
    def test_conditional_flow_show(self):
        """Test show() method with conditional flow."""
        def dummy_condition(ctx: Context) -> bool:
            return True
        
        # Create conditional flow
        # 条件付きフローを作成
        steps = {
            "start": UserInputStep("start", "Start", "condition"),
            "condition": ConditionStep("condition", dummy_condition, "true_path", "false_path"),
            "true_path": UserInputStep("true_path", "True path", None),
            "false_path": UserInputStep("false_path", "False path", None)
        }
        flow = Flow(start="start", steps=steps)
        
        # Get Mermaid diagram
        # Mermaid図を取得
        result = flow.show(format="mermaid", include_history=False)
        
        # Verify conditional flow structure
        # 条件付きフロー構造を検証
        assert 'condition["condition<br/>(ConditionStep)"]:::condition' in result
        assert 'condition -->|"True"| true_path' in result
        assert 'condition -->|"False"| false_path' in result
    
    def test_router_agent_flow_show(self):
        """Test show() method with RouterAgent flow."""
        # Create router configuration
        # ルーター設定を作成
        router_config = RouterConfig(
            name="test_router",
            routes={
                "route1": "step1",
                "route2": "step2"
            },
            classifier_type="rule",
            classification_rules={
                "route1": lambda data, ctx: "route1" in str(data),
                "route2": lambda data, ctx: "route2" in str(data)
            }
        )
        
        # Create flow with router
        # ルーター付きフローを作成
        router_agent = RouterAgent(router_config)
        steps = {
            "start": UserInputStep("start", "Start", "router"),
            "router": router_agent,
            "step1": UserInputStep("step1", "Step 1", None),
            "step2": UserInputStep("step2", "Step 2", None)
        }
        flow = Flow(start="start", steps=steps)
        
        # Get Mermaid diagram
        # Mermaid図を取得
        result = flow.show(format="mermaid", include_history=False)
        
        # Verify router flow structure
        # ルーターフロー構造を検証
        assert 'router["router<br/>(RouterAgent)"]:::router' in result
        assert 'router -->|"route1"| step1' in result
        assert 'router -->|"route2"| step2' in result
    
    def test_get_possible_routes_simple(self):
        """Test get_possible_routes() with simple steps."""
        # Create simple flow
        # 簡単なフローを作成
        steps = {
            "start": UserInputStep("start", "Start", "end"),
            "end": UserInputStep("end", "End", None)
        }
        flow = Flow(start="start", steps=steps)
        
        # Test route discovery
        # ルート発見をテスト
        start_routes = flow.get_possible_routes("start")
        end_routes = flow.get_possible_routes("end")
        
        assert start_routes == ["end"]
        assert end_routes == []
    
    def test_get_possible_routes_condition(self):
        """Test get_possible_routes() with condition step."""
        def dummy_condition(ctx: Context) -> bool:
            return True
        
        # Create conditional flow
        # 条件付きフローを作成
        condition_step = ConditionStep("condition", dummy_condition, "true_path", "false_path")
        steps = {
            "condition": condition_step,
            "true_path": UserInputStep("true_path", "True", None),
            "false_path": UserInputStep("false_path", "False", None)
        }
        flow = Flow(start="condition", steps=steps)
        
        # Test route discovery
        # ルート発見をテスト
        routes = flow.get_possible_routes("condition")
        
        assert set(routes) == {"true_path", "false_path"}
    
    def test_get_possible_routes_router(self):
        """Test get_possible_routes() with RouterAgent."""
        # Create router configuration
        # ルーター設定を作成
        router_config = RouterConfig(
            name="test_router",
            routes={
                "route1": "step1",
                "route2": "step2",
                "route3": "step3"
            },
            classifier_type="rule",
            classification_rules={
                "route1": lambda data, ctx: True
            }
        )
        
        # Create router agent
        # ルーターエージェントを作成
        router_agent = RouterAgent(router_config)
        steps = {
            "router": router_agent,
            "step1": UserInputStep("step1", "Step 1", None),
            "step2": UserInputStep("step2", "Step 2", None),
            "step3": UserInputStep("step3", "Step 3", None)
        }
        flow = Flow(start="router", steps=steps)
        
        # Test route discovery
        # ルート発見をテスト
        routes = flow.get_possible_routes("router")
        
        assert set(routes) == {"step1", "step2", "step3"}
    
    def test_get_possible_routes_nonexistent_step(self):
        """Test get_possible_routes() with non-existent step."""
        # Create simple flow
        # 簡単なフローを作成
        steps = {
            "start": UserInputStep("start", "Start", None)
        }
        flow = Flow(start="start", steps=steps)
        
        # Test with non-existent step
        # 存在しないステップでテスト
        routes = flow.get_possible_routes("nonexistent")
        
        assert routes == []
    
    def test_show_unsupported_format(self):
        """Test show() method with unsupported format."""
        # Create simple flow
        # 簡単なフローを作成
        steps = {
            "start": UserInputStep("start", "Start", None)
        }
        flow = Flow(start="start", steps=steps)
        
        # Test unsupported format
        # サポートされていない形式をテスト
        with pytest.raises(ValueError, match="Unsupported format"):
            flow.show(format="unsupported")
    
    def test_show_include_history_parameter(self):
        """Test show() method with include_history parameter."""
        # Create simple flow
        # 簡単なフローを作成
        steps = {
            "start": UserInputStep("start", "Start", None)
        }
        flow = Flow(start="start", steps=steps)
        
        # Test with history included and excluded
        # 履歴付きと履歴なしでテスト
        result_with_history = flow.show(format="text", include_history=True)
        result_without_history = flow.show(format="text", include_history=False)
        
        # Both should work without errors
        # 両方ともエラーなしで動作するはず
        assert "Flow Diagram:" in result_with_history
        assert "Flow Diagram:" in result_without_history
    
    def test_text_format_with_router_routes(self):
        """Test text format shows router routes properly."""
        # Create router configuration
        # ルーター設定を作成
        router_config = RouterConfig(
            name="test_router",
            routes={
                "email": "email_step",
                "phone": "phone_step"
            },
            classifier_type="rule",
            classification_rules={
                "email": lambda data, ctx: "@" in str(data),
                "phone": lambda data, ctx: "phone" in str(data)
            }
        )
        
        # Create flow with router
        # ルーター付きフローを作成
        router_agent = RouterAgent(router_config)
        steps = {
            "start": UserInputStep("start", "Start", "router"),
            "router": router_agent,
            "email_step": UserInputStep("email_step", "Email", None),
            "phone_step": UserInputStep("phone_step", "Phone", None)
        }
        flow = Flow(start="start", steps=steps)
        
        # Get text diagram
        # テキスト図を取得
        result = flow.show(format="text", include_history=False)
        
        # Verify router routes are shown
        # ルーターのルートが表示されることを検証
        assert "Routes:" in result
        assert "email → email_step" in result
        assert "phone → phone_step" in result 
