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

## 🏗️ Pipelineクラスの使い方

`Pipeline` クラスは、生成テンプレート・評価テンプレート・ツール・ガードレールなどを柔軟に組み合わせて、LLMエージェントのワークフローを簡単に構築できます。

### 基本構成
```python
from agents_sdk_models.pipeline import Pipeline

pipeline = Pipeline(
    name="my_pipeline",
    generation_template="...",  # 生成指示
    evaluation_template=None,    # 評価不要ならNone
    model="gpt-3.5-turbo"
)
result = pipeline.run("ユーザー入力")
```

### 生成物の自動評価
```python
pipeline = Pipeline(
    name="evaluated_generator",
    generation_template="...",
    evaluation_template="...",  # 評価指示
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

pipeline = Pipeline(
    name="tooled_generator",
    generation_template="...",
    evaluation_template=None,
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

pipeline = Pipeline(...)
pipeline.gen_agent.input_guardrails = [math_guardrail]

try:
    result = pipeline.run("Can you help me solve for x: 2x + 3 = 11?")
except InputGuardrailTripwireTriggered:
    print("[Guardrail Triggered] Math homework detected. Request blocked.")
```

---

## 💡 サンプル事例

- シンプルな生成: `examples/pipeline_simple_generation.py`
- 生成物の評価: `examples/pipeline_with_evaluation.py`
- ツール連携: `examples/pipeline_with_tools.py`
- ガードレール: `examples/pipeline_with_guardrails.py`

詳細は [docs/pipeline_examples.md](pipeline_examples.md) を参照してください。

---

## 🖥️ サポート環境
- Python 3.10以上
- Windows, macOS, Linux
- OpenAI Agents SDK（[公式ドキュメント](https://openai.github.io/openai-agents-python/)参照）

---

## 🎯 なぜ使うのか？
- 🚀 **素早いプロトタイピング**: 数分でエージェントワークフローを構築・検証
- 🧑‍💻 **開発者フレンドリー**: 最小限の記述で最大限の柔軟性
- 🔒 **安全**: ガードレールや評価で堅牢な運用が可能
- 🎉 **楽しい**: サンプルが豊富で拡張も簡単

---

## 📝 ライセンス
MIT 