# クイックスタート

このチュートリアルでは、Refinire を使った最小限のLLM活用例を紹介します。数分で動作するAIエージェントを作成できます。

## 前提条件

- Python 3.9以上がインストールされていること
- OpenAIのAPIキーが設定されていること（`OPENAI_API_KEY`環境変数）

```bash
# 環境変数の設定例（Windows）
set OPENAI_API_KEY=your_api_key_here

# 環境変数の設定例（Linux/Mac）
export OPENAI_API_KEY=your_api_key_here
```

## 1. モデルインスタンスの取得

複数のLLMプロバイダーを統一インターフェースで扱えます。

```python
from refinire import get_llm

# OpenAI
llm = get_llm("gpt-4o-mini")

# Anthropic Claude
llm = get_llm("claude-3-sonnet")

# Google Gemini
llm = get_llm("gemini-pro")

# Ollama（ローカルLLM）
llm = get_llm("llama3.1:8b")
```

## 2. シンプルなAgent作成

基本的な対話エージェントを作成します。

```python
from agents import Agent, Runner
from refinire import get_llm

llm = get_llm("gpt-4o-mini")
agent = Agent(
    name="Assistant",
    model=llm,
    instructions="あなたは親切なアシスタントです。丁寧で分かりやすい回答を心がけてください。"
)

result = Runner.run_sync(agent, "こんにちは！")
print(result.final_output)
```

## 3. RefinireAgent + Flow で高度なワークフロー（推奨）

自動評価と品質向上機能を含む高度なエージェントを作成します。

```python
from refinire import create_evaluated_agent, Flow, Context
import asyncio

# 自動評価機能付きRefinireAgentを作成
agent = create_evaluated_agent(
    name="ai_expert",
    generation_instructions="""
    あなたは専門知識豊富なAIアシスタントです。
    ユーザーの要望に応じて、正確で分かりやすい文章を生成してください。
    専門用語を使う場合は、必ず説明を付けてください。
    """,
    evaluation_instructions="""
    生成された文章を以下の観点で100点満点で評価してください：
    - 正確性（40点）
    - 分かりやすさ（30点）
    - 完全性（30点）
    
    評価とともに改善点があれば具体的に指摘してください。
    """,
    model="gpt-4o-mini",
    threshold=75  # 75点未満の場合は自動で再生成
)

# 超シンプルなFlowを作成
flow = Flow(steps=agent)

# 実行
async def main():
    result = await flow.run(input_data="機械学習と深層学習の違いを教えて")
    print("生成結果:")
    print(result.shared_state["ai_expert_result"])
    
    # 評価結果も確認可能
    if result.evaluation_result:
        print(f"\n品質スコア: {result.evaluation_result['score']}")
        print(f"合格: {result.evaluation_result['passed']}")
        print(f"フィードバック: {result.evaluation_result['feedback']}")

# 実行
asyncio.run(main())
```

## 4. ツール使用可能なエージェント

外部機能を使えるエージェントを作成します。

```python
from refinire import create_simple_gen_agent, Flow
import asyncio

def get_weather(city: str) -> str:
    """指定された都市の天気を取得します"""
    # 実際のAPIを呼ぶ代わりにダミーデータを返す
    return f"{city}の天気: 晴れ、気温22度"

def calculate(expression: str) -> float:
    """数式を計算します"""
    try:
        return eval(expression)
    except:
        return 0.0

# ツール使用可能なエージェント
tool_agent = create_simple_gen_agent(
    name="tool_assistant",
    instructions="ユーザーの質問に対して、必要に応じてツールを使って回答してください。",
    model="gpt-4o-mini",
    tools=[get_weather, calculate]
)

flow = Flow(steps=tool_agent)

async def main():
    result = await flow.run(input_data="東京の天気と、15 * 23の計算結果を教えて")
    print(result.shared_state["tool_assistant_result"])

asyncio.run(main())
```

## 5. 複数ステップのワークフロー

複数のステップを組み合わせた複雑なワークフローも簡単に作成できます。

```python
from refinire import Flow, FunctionStep, Context
import asyncio

def analyze_input(user_input: str, ctx: Context) -> Context:
    """ユーザー入力を分析"""
    ctx.shared_state["analysis"] = f"入力「{user_input}」を分析しました"
    return ctx

def generate_response(user_input: str, ctx: Context) -> Context:
    """回答を生成"""
    analysis = ctx.shared_state.get("analysis", "")
    ctx.shared_state["response"] = f"{analysis}に基づいて回答を生成しました"
    ctx.finish()  # ワークフロー終了
    return ctx

# 複数ステップのFlow
flow = Flow([
    ("analyze", FunctionStep("analyze", analyze_input)),
    ("respond", FunctionStep("respond", generate_response))
])

async def main():
    result = await flow.run(input_data="AIについて教えて")
    print(result.shared_state["response"])

asyncio.run(main())
```

## 6. 旧AgentPipeline（非推奨）

```python
# 注意：AgentPipelineはv0.1.0で削除予定です
from refinire import AgentPipeline

pipeline = AgentPipeline(
    name="eval_example",
    generation_instructions="あなたは役立つアシスタントです。",
    evaluation_instructions="生成された文章を分かりやすさで100点満点評価してください。",
    model="gpt-4o-mini",
    threshold=70
)

result = pipeline.run("AIの活用事例を教えて")
print(result)
```

---

## 重要なポイント

### ✅ 推奨されるアプローチ
- **`get_llm`** で主要なLLMを簡単取得
- **`RefinireAgent + Flow`** で生成・評価・自己改善まで一気通貫
- **`Flow(steps=agent)`** だけで複雑なワークフローも**超シンプル**に実現
- **自動品質管理**: threshold設定で品質を自動維持
- **コンテキストベース結果アクセス**: エージェント間のシームレスなデータフロー

### ⚠️ 注意事項
- 旧 `AgentPipeline` は v0.1.0 で削除予定（移行は簡単です）
- 非同期処理（`asyncio`）の使用を推奨
- 環境変数でAPIキーを適切に設定

### 🔗 次のステップ
- [API リファレンス](../api_reference_ja.md) - 詳細な機能説明
- [組み合わせ可能なフローアーキテクチャ](../composable-flow-architecture_ja.md) - 高度なワークフロー
- [サンプル集](../../examples/) - 実用的な使用例 