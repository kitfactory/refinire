#!/usr/bin/env python3
"""
Flow Show Example
フローショー例

This example demonstrates how to use the Flow.show() method to visualize
flow structures, especially with RouterAgent that has multiple routes.
この例では、Flow.show()メソッドを使用してフロー構造を可視化する方法、
特に複数のルートを持つRouterAgentの場合を示します。
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire.flow.flow import Flow
from refinire.flow.step import UserInputStep, ConditionStep, FunctionStep
from refinire.flow.context import Context
from refinire.agents.router import RouterAgent, RouterConfig


def main():
    """
    Main example function.
    メイン例関数。
    """
    print("=" * 80)
    print("Flow Show Method Examples")
    print("フローショーメソッドの例")
    print("=" * 80)
    
    # Example 1: Simple Linear Flow
    # 例1: 簡単な線形フロー
    print("\n1. Simple Linear Flow / 簡単な線形フロー")
    print("-" * 50)
    
    simple_flow = create_simple_linear_flow()
    print("Text format:")
    print(simple_flow.show(format="text", include_history=False))
    print("\nMermaid format:")
    print(simple_flow.show(format="mermaid", include_history=False))
    
    # Example 2: Conditional Flow
    # 例2: 条件付きフロー
    print("\n\n2. Conditional Flow / 条件付きフロー")
    print("-" * 50)
    
    conditional_flow = create_conditional_flow()
    print("Text format:")
    print(conditional_flow.show(format="text", include_history=False))
    print("\nMermaid format:")
    print(conditional_flow.show(format="mermaid", include_history=False))
    
    # Example 3: Router Agent Flow
    # 例3: ルーターエージェントフロー
    print("\n\n3. Router Agent Flow / ルーターエージェントフロー")
    print("-" * 50)
    
    router_flow = create_router_flow()
    print("Text format:")
    print(router_flow.show(format="text", include_history=False))
    print("\nMermaid format:")
    print(router_flow.show(format="mermaid", include_history=False))
    
    # Example 4: Get Possible Routes
    # 例4: 可能なルートの取得
    print("\n\n4. Get Possible Routes / 可能なルートの取得")
    print("-" * 50)
    
    for step_name in router_flow.steps.keys():
        routes = router_flow.get_possible_routes(step_name)
        print(f"Step '{step_name}' can route to: {routes}")
    
    print("\n" + "="*80)


def create_simple_linear_flow() -> Flow:
    """
    Create a simple linear flow.
    簡単な線形フローを作成します。
    """
    steps = {
        "start": UserInputStep("start", "Enter your request:", "process"),
        "process": FunctionStep("process", lambda ui, ctx: ctx.goto("output")),
        "output": UserInputStep("output", "Here's the result:", None)
    }
    
    return Flow(start="start", steps=steps)


def create_conditional_flow() -> Flow:
    """
    Create a conditional flow.
    条件付きフローを作成します。
    """
    def check_condition(ctx: Context) -> bool:
        """Check if input contains 'yes'"""
        user_input = ctx.get_user_input()
        return user_input and "yes" in user_input.lower()
    
    steps = {
        "start": UserInputStep("start", "Do you want to continue? (yes/no):", "condition"),
        "condition": ConditionStep("condition", check_condition, "yes_path", "no_path"),
        "yes_path": UserInputStep("yes_path", "Great! Let's continue.", None),
        "no_path": UserInputStep("no_path", "Okay, stopping here.", None)
    }
    
    return Flow(start="start", steps=steps)


def create_router_flow() -> Flow:
    """
    Create a flow with RouterAgent.
    RouterAgentを持つフローを作成します。
    """
    # Create router configuration
    # ルーター設定を作成
    router_config = RouterConfig(
        name="intent_router",
        routes={
            "question": "answer_step",
            "complaint": "complaint_step",
            "request": "request_step",
            "greeting": "greeting_step"
        },
        classifier_type="rule",
        classification_rules={
            "question": lambda data, ctx: data and "?" in str(data),
            "complaint": lambda data, ctx: data and any(word in str(data).lower() 
                                                       for word in ["problem", "issue", "wrong"]),
            "request": lambda data, ctx: data and any(word in str(data).lower() 
                                                     for word in ["please", "can you", "help"]),
            "greeting": lambda data, ctx: data and any(word in str(data).lower() 
                                                      for word in ["hello", "hi", "good morning"])
        },
        default_route="question"
    )
    
    # Create router agent
    # ルーターエージェントを作成
    router_agent = RouterAgent(router_config)
    
    steps = {
        "start": UserInputStep("start", "What can I help you with?", "router"),
        "router": router_agent,
        "answer_step": UserInputStep("answer_step", "I'll answer your question.", None),
        "complaint_step": UserInputStep("complaint_step", "I'm sorry to hear about the issue.", None),
        "request_step": UserInputStep("request_step", "I'll help you with that.", None),
        "greeting_step": UserInputStep("greeting_step", "Hello! Nice to meet you.", "start")
    }
    
    return Flow(start="start", steps=steps)


if __name__ == "__main__":
    main() 
