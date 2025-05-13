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
from agents_sdk_models.pipeline import AgentPipeline

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
from agents_sdk_models.pipeline import AgentPipeline

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