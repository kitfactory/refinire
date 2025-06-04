# agents-sdk-models ドキュメント

## 🌟 はじめに

このプロジェクトは、OpenAI Agents SDKを活用したエージェント・パイプラインの構築を支援するPythonライブラリです。  
**生成・評価・ツール連携・ガードレール**など、実践的なAIワークフローを最小限の記述で実現できます。

---

## 🚀 特徴・メリット

- 🧩 生成・評価・ツール・ガードレールを柔軟に組み合わせたワークフローを簡単に構築
- 🛠️ Python関数をそのままツールとして利用可能
- 🛡️ ガードレールで安全・堅牢な入力/出力制御
- 📦 豊富なサンプル（`examples/`）ですぐに試せる
- 🚀 最小限の記述で素早くプロトタイピング

---

## ⚡ インストール

```bash
pip install agents-sdk-models
```
- OpenAI Agents SDK, pydantic 2.x などが必要です。詳細は[公式ドキュメント](https://openai.github.io/openai-agents-python/)も参照してください。

---

## 🏗️ AgentPipelineクラスの使い方

`AgentPipeline` クラスは、生成指示・評価指示・ツール・ガードレールなどを柔軟に組み合わせて、LLMエージェントのワークフローを簡単に構築できます。

### 基本構成
```python
from agents_sdk_models import AgentPipeline

pipeline = AgentPipeline(
    name="my_pipeline",
    generation_instructions="...",  # 生成指示
    evaluation_instructions=None,    # 評価不要ならNone
    model="gpt-3.5-turbo"
)
result = pipeline.run("ユーザー入力")
```

### 生成物の自動評価
```python
pipeline = AgentPipeline(
    name="evaluated_generator",
    generation_instructions="...",
    evaluation_instructions="...",  # 評価指示
    model="gpt-3.5-turbo",
    threshold=70
)
result = pipeline.run("評価対象の入力")
```

### ツール連携
```python
from agents import function_tool

@function_tool
def search_web(query: str) -> str:
    ...

pipeline = AgentPipeline(
    name="tooled_generator",
    generation_instructions="...",
    evaluation_instructions=None,
    model="gpt-3.5-turbo",
    generation_tools=[search_web]
)
```

### ガードレール（入力制御）
```python
from agents import input_guardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered

@input_guardrail
async def math_guardrail(ctx, agent, input):
    ...

pipeline = AgentPipeline(
    name="guardrail_pipeline",
    generation_instructions="...",
    evaluation_instructions=None,
    model="gpt-4o",
    input_guardrails=[math_guardrail]
)

try:
    result = pipeline.run("Can you help me solve for x: 2x + 3 = 11?")
except InputGuardrailTripwireTriggered:
    print("[Guardrail Triggered] Math homework detected. Request blocked.")
```

### リトライ時のコメントフィードバック
```python
from agents_sdk_models import AgentPipeline

pipeline = AgentPipeline(
    name="comment_retry",
    generation_instructions="生成プロンプト",
    evaluation_instructions="評価プロンプト",
    model="gpt-4o-mini",
    threshold=80,
    retries=2,
    retry_comment_importance=["serious", "normal"]
)
result = pipeline.run("入力テキスト")
print(result)
```
リトライ時に前回の評価コメント（指定した重大度のみ）が生成プロンプトに自動で付与され、改善を促します。

---

## 🚀 新機能：超シンプルFlow（v0.0.8+）

新しいFlowコンストラクタで**3つの方法**でワークフローを作成できます：

### 単一ステップFlow（最もシンプル！）
```python
from agents_sdk_models import create_simple_gen_agent, Flow

gen_agent = create_simple_gen_agent("assistant", "親切に回答します", "gpt-4o-mini")
flow = Flow(steps=gen_agent)  # たった1行！
result = await flow.run(input_data="こんにちは")
```

### シーケンシャルFlow（自動接続！）
```python
from agents_sdk_models import create_simple_gen_agent, Flow

idea_gen = create_simple_gen_agent("idea", "アイデア生成", "gpt-4o-mini")
writer = create_simple_gen_agent("writer", "記事執筆", "gpt-4o")
reviewer = create_simple_gen_agent("reviewer", "レビュー", "claude-3-5-sonnet-latest")

flow = Flow(steps=[idea_gen, writer, reviewer])  # 自動シーケンシャル実行！
result = await flow.run(input_data="AI技術について")
```

### 従来方式（複雑なフロー用）
```python
flow = Flow(
    start="step1",
    steps={"step1": step1, "step2": step2}
)
```

**📚 詳細ガイド：** [新しいFlow機能完全ガイド](new_flow_features.md)

---

## 📚 関連ドキュメント

- **[新しいFlow機能完全ガイド](new_flow_features.md)** - v0.0.8で追加された超シンプルなFlow作成方法
- **[クイックスタート](tutorials/quickstart.md)** - 3行でAIワークフローを構築
- **[応用例](tutorials/advanced.md)** - マルチエージェント協調とツール連携
- **[Flow/Step API リファレンス](flow_step.md)** - 詳細なAPI仕様