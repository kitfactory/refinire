#!/usr/bin/env python3
"""
Test to verify Context inheritance fix is working
コンテキスト継承修正の動作確認テスト
"""

import asyncio
import sys
import os

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Flow
from refinire.agents.flow import Context, FunctionStep


def create_info_collector():
    """情報収集エージェント - シンプル版"""
    return RefinireAgent(
        name="collector",
        generation_instructions="ユーザーからの情報を受け取り、簡単に確認してください。",
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 5}
        ],
        routing_instruction="""
情報が集まったら "generator" を返してください。
まだ情報が不足していたら "collector" を返してください。
        """.strip()
    )


def create_info_generator():
    """情報生成エージェント"""
    return RefinireAgent(
        name="generator", 
        generation_instructions="""
これまでの会話履歴を確認して、収集された情報をまとめてください。

会話履歴から以下の情報を抽出してまとめてください：
- ユーザーが提供した全ての情報
- 会話の流れ

形式：
=== 収集された情報 ===
[会話履歴から抽出した情報をまとめる]
        """.strip(),
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 10}
        ]
    )


async def test_context_inheritance():
    """Context継承テスト"""
    print("=== Context継承テスト開始 ===")
    
    # エージェント作成
    collector = create_info_collector()
    generator = create_info_generator()
    
    # フロー作成
    flow = Flow(
        name="context_test_flow",
        start="collector",
        steps={
            "collector": collector,
            "generator": generator
        }
    )
    
    print("\n1. 初回実行（情報収集）")
    result1 = await flow.run("私の名前は田中です。25歳です。")
    print(f"結果1: {result1.content}")
    print(f"Context messages count: {len(result1.messages)}")
    print(f"Context step count: {result1.step_count}")
    
    if not flow.finished:
        print("\n2. 追加情報提供")
        result2 = await flow.run("プログラマーをしています。読書が趣味です。")
        print(f"結果2: {result2.content}")
        print(f"Context messages count: {len(result2.messages)}")
        print(f"Context step count: {result2.step_count}")
        
        # 会話履歴を確認
        print(f"\n=== 最終的な会話履歴 ===")
        for i, msg in enumerate(result2.messages):
            print(f"{i+1}. {msg.role}: {str(msg.content)[:100]}...")
    
    print(f"\nフロー完了: {flow.finished}")


async def test_step_context_preservation():
    """ステップ間でのContext保持テスト"""
    print("\n=== ステップ間Context保持テスト ===")
    
    def step1_func(user_input, context):
        """Step1: 情報をshared_stateに保存"""
        print(f"Step1 - 受信Context ID: {id(context)}")
        print(f"Step1 - Messages count: {len(context.messages)}")
        
        context.shared_state['step1_data'] = f"Step1で処理: {user_input}"
        context.shared_state['step1_context_id'] = id(context)
        context.goto("step2")
        
        print(f"Step1 - 保存後shared_state: {context.shared_state}")
        return context
    
    def step2_func(user_input, context):
        """Step2: shared_stateから情報を読み込み"""
        print(f"Step2 - 受信Context ID: {id(context)}")
        print(f"Step2 - Messages count: {len(context.messages)}")
        print(f"Step2 - 受信shared_state: {context.shared_state}")
        
        step1_data = context.shared_state.get('step1_data', 'なし')
        step1_context_id = context.shared_state.get('step1_context_id', 'なし')
        
        result = f"Step2結果: {step1_data}, Context継承OK: {id(context) == step1_context_id}"
        context.content = result
        context.finish()
        return context
    
    # FunctionStepを使用したシンプルなフロー
    step1 = FunctionStep("step1", step1_func)
    step2 = FunctionStep("step2", step2_func)
    
    flow = Flow(
        name="context_preservation_test",
        start="step1", 
        steps={
            "step1": step1,
            "step2": step2
        }
    )
    
    result = await flow.run("テストデータ")
    print(f"\n最終結果: {result.content}")
    print(f"Context ID一致: {'Context継承OK: True' in result.content}")


if __name__ == "__main__":
    async def main():
        await test_context_inheritance()
        await test_step_context_preservation()
    
    asyncio.run(main())