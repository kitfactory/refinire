from __future__ import annotations

"""SimpleFlow — Simplified workflow orchestration for basic use cases.

SimpleFlowは基本的なユースケース向けの簡略化されたワークフローオーケストレーションです。
"""

import asyncio
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime

from .context import Context
from .step import Step


class SimpleFlow:
    """
    Simplified Flow orchestration for basic workflows
    基本的なワークフロー用の簡略化されたFlowオーケストレーション
    
    A streamlined version of Flow that focuses on ease of use:
    使いやすさに焦点を当てたFlowの簡略版：
    - Simple step definition / シンプルなステップ定義
    - Linear execution / 線形実行
    - Minimal configuration / 最小限の設定
    """
    
    def __init__(self, steps: List[Step], name: Optional[str] = None):
        """
        Initialize SimpleFlow with a list of steps
        ステップのリストでSimpleFlowを初期化
        
        Args:
            steps: List of steps to execute in order / 順番に実行するステップのリスト
            name: Optional flow name / オプションのフロー名
        """
        if not steps:
            raise ValueError("Steps list cannot be empty")
        
        self.steps = steps
        self.name = name or f"simple_flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.context = Context()
    
    async def run(self, user_input: Optional[str] = None) -> Context:
        """
        Execute all steps in sequence
        すべてのステップを順番に実行
        
        Args:
            user_input: Initial user input / 初期ユーザー入力
            
        Returns:
            Context: Final execution context / 最終実行コンテキスト
        """
        # Create trace context intelligently - only if no active trace exists
        # インテリジェントにトレースコンテキストを作成 - アクティブなトレースが存在しない場合のみ
        try:
            from ...core.trace_context import TraceContextManager
            
            trace_name = f"SimpleFlow({self.name})"
            with TraceContextManager(trace_name):
                return await self._execute_steps(user_input)
        except ImportError:
            # trace_context not available - run without trace context
            # trace_contextが利用できません - トレースコンテキストなしで実行
            return await self._execute_steps(user_input)
    
    async def _execute_steps(self, user_input: Optional[str] = None) -> Context:
        """
        Internal method to execute all steps
        すべてのステップを実行する内部メソッド
        """
        print(f"🌊 Starting SimpleFlow: {self.name}")
        print(f"🌊 SimpleFlow開始: {self.name}")
        
        # Initialize context
        # コンテキストを初期化
        if user_input:
            self.context.add_user_message(user_input)
            self.context.last_user_input = user_input
        
        # Execute each step
        # 各ステップを実行
        for i, step in enumerate(self.steps, 1):
            try:
                print(f"  📍 Step {i}/{len(self.steps)}: {step.name}")
                print(f"  📍 ステップ {i}/{len(self.steps)}: {step.name}")
                
                # Execute step
                # ステップを実行
                self.context = await step.run_async(user_input, self.context)
                
                # Check for errors
                # エラーをチェック
                if self.context.has_error():
                    print(f"  ❌ Step {i} failed: {self.context.error['message']}")
                    print(f"  ❌ ステップ {i} 失敗: {self.context.error['message']}")
                    break
                
                print(f"  ✅ Step {i} completed")
                print(f"  ✅ ステップ {i} 完了")
                
            except Exception as e:
                print(f"  💥 Step {i} error: {e}")
                print(f"  💥 ステップ {i} エラー: {e}")
                self.context.set_error(step.name, e)
                break
        
        if not self.context.has_error():
            print(f"🎉 SimpleFlow completed successfully!")
            print(f"🎉 SimpleFlow正常完了!")
        
        return self.context
    
    def add_step(self, step: Step) -> 'SimpleFlow':
        """
        Add a step to the flow (builder pattern)
        フローにステップを追加（ビルダーパターン）
        
        Args:
            step: Step to add / 追加するステップ
            
        Returns:
            SimpleFlow: Self for chaining / チェーン用の自身
        """
        self.steps.append(step)
        return self
    
    def get_result(self, step_name: Optional[str] = None) -> Any:
        """
        Get result from a specific step or the final result
        特定のステップまたは最終結果を取得
        
        Args:
            step_name: Name of step to get result from / 結果を取得するステップ名
            
        Returns:
            Any: Step result or final context content / ステップ結果または最終コンテキスト内容
        """
        if step_name:
            return self.context.shared_state.get(f"{step_name}_result")
        return self.context.content


# Convenience function for creating simple flows
# シンプルフロー作成用の便利関数
def create_simple_flow(steps: List[Step], name: Optional[str] = None) -> SimpleFlow:
    """
    Create a SimpleFlow with the given steps
    指定されたステップでSimpleFlowを作成
    
    Args:
        steps: List of steps / ステップのリスト
        name: Optional flow name / オプションのフロー名
        
    Returns:
        SimpleFlow: Configured simple flow / 設定済みシンプルフロー
    """
    return SimpleFlow(steps, name)


# Helper function to create function steps easily
# 関数ステップを簡単に作成するヘルパー関数
def simple_step(name: str, func: Callable[[str, Context], Context]) -> Step:
    """
    Create a simple function step
    シンプルな関数ステップを作成
    
    Args:
        name: Step name / ステップ名
        func: Function to execute / 実行する関数
        
    Returns:
        Step: Function step / 関数ステップ
    """
    from .step import FunctionStep
    return FunctionStep(name, func)