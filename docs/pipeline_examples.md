# AgentPipeline活用事例集

このドキュメントでは、`AgentPipeline`クラスを活用した各種事例を紹介します。

---

## 1. シンプルな生成（評価なし）

- ファイル: `examples/pipeline_simple_generation.py`
- 概要: ユーザー入力に基づき、評価なしで直接生成結果を返す最小構成の例。

### コード例
```python
pipeline = AgentPipeline(
    name="simple_generator",
    generation_instructions="""
    You are a helpful assistant that generates creative stories.
    あなたは創造的な物語を生成する役立つアシスタントです。
    Please generate a short story based on the user's input.
    ユーザーの入力に基づいて短い物語を生成してください。
    """,
    evaluation_instructions=None,
    model="gpt-3.5-turbo"
)
result = pipeline.run("A story about a robot learning to paint")
```

---

## 2. 生成物の評価付き生成

- ファイル: `examples/pipeline_with_evaluation.py`
- 概要: 生成物に対して自動評価を行い、閾値を満たした場合のみ結果を返す例。

### コード例
```python
pipeline = AgentPipeline(
    name="evaluated_generator",
    generation_instructions="...",
    evaluation_instructions="...",
    model="gpt-3.5-turbo",
    threshold=70
)
result = pipeline.run("A story about a robot learning to paint")
```

---

## 3. ツール連携による生成

- ファイル: `examples/pipeline_with_tools.py`
- 概要: `@function_tool`で定義したPython関数をツールとして組み込み、外部情報取得や計算などを組み合わせた生成を行う例。

### コード例
```python
from agents import function_tool

@function_tool
def search_web(query: str) -> str:
    ...

@function_tool
def get_weather(location: str) -> str:
    ...

pipeline = AgentPipeline(
    name="tooled_generator",
    generation_instructions="...",
    evaluation_instructions=None,
    model="gpt-3.5-turbo",
    generation_tools=[search_web, get_weather]
)
result = pipeline.run("What's the weather like in Tokyo?")
```

---

## 4. ガードレール（入力ガードレール）による入力制御

- ファイル: `examples/pipeline_with_guardrails.py`
- 概要: 入力内容に対してガードレール（例: 数学の宿題依頼の検出）を設け、不適切なリクエストをブロックする例。

### コード例
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

---

## 5. リトライ時のコメントフィードバック

- 機能: 前回の評価コメントを指定した重大度レベルで生成プロンプトに付与し、改善を促す
- パラメータ:
  - `retry_comment_importance`: `serious`, `normal`, `minor` のいずれかを指定可能

### コード例
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
result = pipeline.run("評価対象のテキスト")
print(result)
```

---

## 参考
- 各サンプルは `examples/` フォルダに格納されています。
- 詳細な使い方や応用例はREADMEも参照してください。 