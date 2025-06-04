# 🚀 新しいFlow機能完全ガイド

本ドキュメントでは、agents-sdk-models v0.0.8以降で追加された新しいFlow作成機能について詳しく説明します。

## 概要

従来のFlowは辞書形式でのステップ定義が必要でしたが、新しいFlowコンストラクタは**3つの方法**でワークフローを作成できます：

1. **単一ステップ** - `Flow(steps=single_step)`
2. **シーケンシャルステップ** - `Flow(steps=[step1, step2, step3])`  
3. **従来方式** - `Flow(start="step1", steps={"step1": step1, ...})`

## 🎯 最もシンプル：単一ステップFlow

```python
from agents_sdk_models import create_simple_gen_agent, Flow

# GenAgentを作成
gen_agent = create_simple_gen_agent(
    name="assistant",
    instructions="あなたは親切なアシスタントです。",
    model="gpt-4o-mini"
)

# Flowを作成（たった1行！）
flow = Flow(steps=gen_agent)

# 実行
result = await flow.run(input_data="こんにちは")
print(result.shared_state["assistant_result"])
```

## 🔗 自動接続：シーケンシャルFlow

```python
from agents_sdk_models import create_simple_gen_agent, Flow, DebugStep

# 複数のステップを定義
idea_gen = create_simple_gen_agent("idea", "アイデアを生成", "gpt-4o-mini")
writer = create_simple_gen_agent("writer", "記事を執筆", "gpt-4o")
reviewer = create_simple_gen_agent("reviewer", "記事をレビュー", "claude-3-5-sonnet-latest")
debug = DebugStep("debug", "ワークフロー完了")

# シーケンシャルFlow（自動接続！）
flow = Flow(steps=[idea_gen, writer, reviewer, debug])

# 実行（idea_gen → writer → reviewer → debug の順で自動実行）
result = await flow.run(input_data="AI技術について")

# 各ステップの結果を確認
print("アイデア:", result.shared_state["idea_result"])
print("記事:", result.shared_state["writer_result"])  
print("レビュー:", result.shared_state["reviewer_result"])
```

## ⚙️ 高度な例：評価付きGenAgent

```python
from agents_sdk_models import create_evaluated_gen_agent, Flow

# 評価機能付きGenAgent
smart_agent = create_evaluated_gen_agent(
    name="smart_writer",
    generation_instructions="技術記事を執筆してください",
    evaluation_instructions="記事の質を100点満点で評価し、改善点を指摘してください",
    model="gpt-4o",
    threshold=80,  # 80点未満なら自動リトライ
    retries=2
)

# シンプルなFlow
flow = Flow(steps=smart_agent)
result = await flow.run(input_data="機械学習の基礎について")

# 評価結果も含めて表示
evaluation = result.shared_state.get("smart_writer_evaluation")
if evaluation:
    print(f"評価点数: {evaluation.get('score', 'N/A')}")
    print(f"コメント: {evaluation.get('comment', 'N/A')}")
```

## 🔧 ツール連携

```python
from agents import function_tool
from agents_sdk_models import create_simple_gen_agent, Flow

@function_tool
def get_weather(location: str) -> str:
    """指定地域の天気情報を取得"""
    return f"Weather in {location}: Sunny, 25°C"

@function_tool  
def get_news(topic: str) -> str:
    """指定トピックのニュースを取得"""
    return f"Latest news about {topic}: AI breakthrough announced"

# ツール付きGenAgent
weather_agent = create_simple_gen_agent(
    name="weather_bot",
    instructions="天気やニュースの質問に答えてください。必要に応じてツールを使用してください。",
    model="gpt-4o-mini",
    generation_tools=[get_weather, get_news]
)

flow = Flow(steps=weather_agent)
result = await flow.run(input_data="東京の天気とAIのニュースを教えて")
```

## 🌟 マルチエージェント協調

```python
from agents_sdk_models import create_simple_gen_agent, Flow

# 専門分野の異なるエージェント
researcher = create_simple_gen_agent(
    name="researcher", 
    instructions="技術調査を行い、正確な情報を提供します",
    model="gpt-4o"
)

translator = create_simple_gen_agent(
    name="translator",
    instructions="技術文書を分かりやすい日本語に翻訳します", 
    model="gpt-4o"
)

summarizer = create_simple_gen_agent(
    name="summarizer",
    instructions="長い文章を要点を押さえて要約します",
    model="claude-3-5-sonnet-latest"
)

# マルチエージェント協調Flow
flow = Flow(steps=[researcher, translator, summarizer])
result = await flow.run(input_data="量子コンピューティングの最新動向")

print("調査結果:", result.shared_state["researcher_result"])
print("翻訳結果:", result.shared_state["translator_result"]) 
print("要約結果:", result.shared_state["summarizer_result"])
```

## 🔀 条件分岐（従来方式）

複雑な条件分岐が必要な場合は従来の辞書方式を使用：

```python
from agents_sdk_models import Flow, ConditionStep, create_simple_gen_agent

def check_urgency(ctx):
    user_input = ctx.last_user_input or ""
    return "緊急" in user_input or "急ぎ" in user_input

urgent_agent = create_simple_gen_agent("urgent", "緊急対応します", "gpt-4o")
normal_agent = create_simple_gen_agent("normal", "通常対応します", "gpt-4o-mini")

# 条件分岐Flow
flow = Flow(
    start="check",
    steps={
        "check": ConditionStep("check", check_urgency, "urgent", "normal"),
        "urgent": urgent_agent,
        "normal": normal_agent
    }
)

result = await flow.run(input_data="緊急にレポートを作成してください")
```

## 💡 ベストプラクティス

### 1. ステップ命名規則
```python
# Good: 分かりやすい名前
gen_agent = create_simple_gen_agent("content_writer", "記事執筆", "gpt-4o")

# Bad: 意味不明な名前  
gen_agent = create_simple_gen_agent("step1", "記事執筆", "gpt-4o")
```

### 2. モデルの使い分け
```python
# 複雑なタスク: 高性能モデル
complex_agent = create_simple_gen_agent("analyzer", "複雑な分析", "gpt-4o")

# シンプルなタスク: 軽量モデル
simple_agent = create_simple_gen_agent("formatter", "テキスト整形", "gpt-4o-mini")
```

### 3. エラーハンドリング
```python
try:
    result = await flow.run(input_data="入力データ")
    if "error" in result.shared_state:
        print("エラーが発生しました:", result.shared_state["error"])
except Exception as e:
    print("実行エラー:", str(e))
```

## 📊 パフォーマンス比較

| 方式 | コード行数 | 設定の複雑さ | 学習コスト |
|------|------------|-------------|------------|
| 旧AgentPipeline | 10-15行 | 中 | 中 |
| 新Flow(単一) | 3行 | 低 | 低 |
| 新Flow(シーケンシャル) | 5-8行 | 低 | 低 |
| 新Flow(従来) | 15-20行 | 高 | 高 |

## 🚀 移行ガイド

### AgentPipelineからの移行

```python
# 旧: AgentPipeline
pipeline = AgentPipeline(
    name="example",
    generation_instructions="文章を生成",
    evaluation_instructions="評価します", 
    model="gpt-4o-mini",
    threshold=70
)
result = pipeline.run("入力")

# 新: GenAgent + Flow
gen_agent = create_evaluated_gen_agent(
    name="example",
    generation_instructions="文章を生成",
    evaluation_instructions="評価します",
    model="gpt-4o-mini", 
    threshold=70
)
flow = Flow(steps=gen_agent)
result = await flow.run(input_data="入力")
```

## 🔗 関連ドキュメント

- [クイックスタート](tutorials/quickstart.md)
- [応用例](tutorials/advanced.md)  
- [Flow/Step API リファレンス](flow_step.md)
- [API リファレンス](api_reference.md) 