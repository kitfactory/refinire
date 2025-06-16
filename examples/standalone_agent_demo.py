"""
GenAgent, ClarifyAgent, LLMPipelineの単体実行デモ
Standalone execution demo for GenAgent, ClarifyAgent, and LLMPipeline

このデモでは、Flowを使わずに各Agentを直接単体で実行する方法を示します。
This demo shows how to run each Agent directly without using Flow.
"""

import asyncio
from typing import List
from pydantic import BaseModel

from refinire import (
    GenAgent, ClarifyAgent, RefinireAgent, Context,
    create_simple_gen_agent, create_simple_clarify_agent,
    create_simple_agent, create_evaluated_agent,
    ClarificationResult
)


# データモデル定義 / Data model definition
class TaskRequest(BaseModel):
    """
    Task request data model
    タスク要求データモデル
    """
    task_name: str      # Task name / タスク名
    priority: str       # Priority level / 優先度
    deadline: str       # Deadline / 締切
    description: str    # Task description / タスク説明


async def demo_genagent_standalone():
    """
    GenAgent単体実行デモ
    GenAgent standalone execution demo
    """
    print("🤖 === GenAgent単体実行デモ / GenAgent Standalone Demo ===")
    
    # 1. GenAgentを直接作成
    # Create GenAgent directly
    agent = create_simple_gen_agent(
        name="story_generator",
        instructions="""
        あなたは創造的な物語作家です。
        ユーザーのリクエストに基づいて短い物語を生成してください。
        You are a creative story writer.
        Generate short stories based on user requests.
        """,
        model="gpt-4o-mini"
    )
    
    # 2. Context作成（Flowなしでも単体実行可能）
    # Create Context (can run standalone without Flow)
    context = Context()
    
    # 3. 直接実行
    # Execute directly
    user_input = "宇宙飛行士が未知の惑星で発見したものについての物語"
    print(f"📝 入力: {user_input}")
    
    try:
        # GenAgentを直接run
        # Run GenAgent directly
        result_context = await agent.run(user_input, context)
        
        # 結果を取得
        # Get result
        generated_story = result_context.shared_state.get("story_generator_result")
        print(f"✅ 生成された物語:\n{generated_story}")
        
        # メッセージ履歴も確認可能
        # Message history is also available
        print(f"\n📚 メッセージ数: {len(result_context.messages)}")
        
    except Exception as e:
        print(f"⚠️ 実際の実行にはOpenAI APIキーが必要です。エラー: {e}")


async def demo_clarifyagent_standalone():
    """
    ClarifyAgent単体実行デモ（インタラクティブループ）
    ClarifyAgent standalone execution demo (Interactive Loop)
    """
    print("\n🔍 === ClarifyAgent単体実行デモ / ClarifyAgent Standalone Demo ===")
    
    # 1. ClarifyAgentを直接作成
    # Create ClarifyAgent directly
    agent = create_simple_clarify_agent(
        name="task_clarifier",
        instructions="""
        あなたはタスク要件明確化の専門家です。
        ユーザーの曖昧なタスク要求を明確にするために質問をしてください。
        必要な情報が全て揃ったら、確定した要件を出力してください。
        
        You are a task requirement clarification specialist.
        Ask questions to clarify user's ambiguous task requests.
        Output confirmed requirements when all necessary information is gathered.
        """,
        output_data=TaskRequest,
        max_turns=5,
        model="gpt-4o-mini"
    )
    
    # 2. シミュレーション用ユーザー応答リスト
    # Simulated user responses for demo
    user_inputs = [
        "プロジェクトのタスクを作成したい",
        "ウェブアプリの開発です",
        "高優先度で来週末までに完了させたい",
        "新機能の実装、特にユーザー認証機能を追加する"
    ]
    
    try:
        # 3. インタラクティブループ実行
        # Interactive loop execution
        context = Context()
        
        for turn, user_input in enumerate(user_inputs, 1):
            print(f"\n👤 ターン{turn}: {user_input}")
            
            # Agent実行
            # Run agent
            result_context = await agent.run(user_input, context)
            clarify_result = result_context.shared_state.get("task_clarifier_result")
            
            if isinstance(clarify_result, ClarificationResult):
                if clarify_result.is_complete:
                    print(f"✅ 明確化完了: {clarify_result.data}")
                    break
                else:
                    print(f"🤖 質問: {clarify_result.data}")
                    print(f"   📊 ターン進捗: {clarify_result.turn}/{clarify_result.turn + clarify_result.remaining_turns}")
            
            # 次のターンのためにcontextを更新
            # Update context for next turn
            context = result_context
        
        else:
            print("❗ 最大ターン数に達しました / Maximum turns reached")
        
    except Exception as e:
        print(f"⚠️ 実際の実行にはOpenAI APIキーが必要です。エラー: {e}")


async def demo_clarifyagent_interactive_real():
    """
    ClarifyAgent実際のインタラクティブデモ（オプション）
    ClarifyAgent real interactive demo (Optional)
    """
    print("\n🎮 === ClarifyAgent実際のインタラクティブデモ / ClarifyAgent Real Interactive Demo ===")
    print("📝 実際にキーボード入力で対話したい場合は、このファンクションをアンコメントして使用してください")
    print("To interact with real keyboard input, uncomment and use this function")
    
    """
    # リアルインタラクション版（コメントアウト）
    # Real interaction version (commented out)
    
    agent = create_simple_clarify_agent(
        name="task_clarifier",
        instructions="ユーザーの曖昧なタスク要求を明確にするために質問をしてください。",
        output_data=TaskRequest,
        max_turns=10,
        model="gpt-4o-mini"
    )
    
    context = Context()
    print("📝 タスクについて教えてください（'quit'で終了）:")
    
    while True:
        user_input = input("👤 あなた: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
            
        result_context = await agent.run(user_input, context)
        clarify_result = result_context.shared_state.get("task_clarifier_result")
        
        if isinstance(clarify_result, ClarificationResult):
            if clarify_result.is_complete:
                print(f"✅ 明確化完了: {clarify_result.data}")
                break
            else:
                print(f"🤖 Agent: {clarify_result.data}")
        
        context = result_context
    """


def demo_llmpipeline_standalone():
    """
    LLMPipeline単体実行デモ
    LLMPipeline standalone execution demo
    """
    print("\n⚙️ === LLMPipeline単体実行デモ / LLMPipeline Standalone Demo ===")
    
    # 1. シンプルなLLMPipelineを直接作成
    # Create simple LLMPipeline directly
    pipeline = create_simple_agent(
        name="code_reviewer",
        instructions="""
        あなたはコードレビューの専門家です。
        提供されたコードを分析し、改善点やベストプラクティスを提案してください。
        
        You are a code review specialist.
        Analyze provided code and suggest improvements and best practices.
        """,
        model="gpt-4o-mini"
    )
    
    # 2. 直接実行（同期）
    # Execute directly (synchronous)
    code_input = """
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']
    return total
    """
    
    print(f"📝 入力コード:\n{code_input}")
    
    try:
        # LLMPipelineを直接run
        # Run LLMPipeline directly
        result = pipeline.run(code_input)
        
        if result.success:
            print(f"✅ レビュー結果:\n{result.content}")
            print(f"🔄 試行回数: {result.attempts}")
            print(f"📊 メタデータ: {result.metadata}")
        else:
            print(f"❌ 実行失敗: {result.metadata}")
            
    except Exception as e:
        print(f"⚠️ 実際の実行にはOpenAI APIキーが必要です。エラー: {e}")


def demo_evaluated_llmpipeline_standalone():
    """
    評価機能付きLLMPipeline単体実行デモ
    Evaluated LLMPipeline standalone execution demo
    """
    print("\n🔍 === 評価機能付きLLMPipeline単体実行デモ / Evaluated LLMPipeline Standalone Demo ===")
    
    # 1. 評価機能付きLLMPipelineを作成
    # Create LLMPipeline with evaluation
    pipeline = create_evaluated_agent(
        name="technical_writer",
        generation_instructions="""
        あなたは技術文書作成の専門家です。
        ユーザーの要求に基づいて、明確で理解しやすい技術文書を作成してください。
        
        You are a technical documentation specialist.
        Create clear and understandable technical documents based on user requests.
        """,
        evaluation_instructions="""
        生成された技術文書を以下の基準で評価してください：
        1. 明確性と理解しやすさ (0-25点)
        2. 技術的正確性 (0-25点)
        3. 構造と組織化 (0-25点)
        4. 実用性と価値 (0-25点)
        
        100点満点でスコアを付け、簡潔なフィードバックを提供してください。
        
        Evaluate the generated technical document based on:
        1. Clarity and understandability (0-25 points)
        2. Technical accuracy (0-25 points)
        3. Structure and organization (0-25 points)
        4. Practicality and value (0-25 points)
        
        Provide a score out of 100 and brief feedback.
        """,
        model="gpt-4o-mini",
        threshold=75.0,
        max_retries=2
    )
    
    # 2. 実行
    # Execute
    request = "APIの使用方法について、初心者向けのガイドを作成してください"
    print(f"📝 要求: {request}")
    print(f"🎯 品質閾値: {pipeline.threshold}%")
    
    try:
        result = pipeline.run(request)
        
        if result.success:
            print(f"✅ 高品質文書生成成功:")
            print(f"📄 内容: {result.content[:300]}...")
            print(f"⭐ 評価スコア: {result.evaluation_score}%")
            print(f"🔄 試行回数: {result.attempts}")
        else:
            print(f"❌ 品質閾値未達成: {result.metadata}")
            
    except Exception as e:
        print(f"⚠️ 実際の実行にはOpenAI APIキーが必要です。エラー: {e}")


async def main():
    """
    メイン実行関数
    Main execution function
    """
    print("🚀 === Agent単体実行総合デモ / Comprehensive Agent Standalone Demo ===")
    print("このデモでは、Flowを使わずに各Agentを直接実行する方法を示します。")
    print("This demo shows how to run each Agent directly without using Flow.\n")
    
    # 各Agentの単体実行をデモ
    # Demo standalone execution of each Agent
    await demo_genagent_standalone()
    await demo_clarifyagent_standalone()
    demo_llmpipeline_standalone()
    demo_evaluated_llmpipeline_standalone()
    
    print("\n" + "="*60)
    print("📋 === 単体実行まとめ / Standalone Execution Summary ===")
    print("✅ GenAgent: 単体実行可能（非同期）/ Standalone execution possible (async)")
    print("✅ ClarifyAgent: 単体実行可能・インタラクティブ対応 / Standalone interactive execution")
    print("✅ LLMPipeline: 単体実行可能（同期・非同期両対応）/ Standalone sync/async execution")
    print("✅ 全てのAgentがFlowなしで使用可能 / All Agents can be used without Flow")
    print("✅ インタラクティブ機能も単体で動作 / Interactive features work standalone")


if __name__ == "__main__":
    asyncio.run(main()) 
