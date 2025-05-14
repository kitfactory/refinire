# 応用例

このチュートリアルでは、Agents SDK Models の応用的な使い方を紹介します。

## 1. ツール連携
```python
from agents import function_tool
from agents_sdk_models.pipeline import AgentPipeline

@function_tool
def get_weather(location: str) -> str:
    return f"Weather in {location}: Sunny, 25°C"

pipeline = AgentPipeline(
    name="tool_example",
    generation_instructions="""
    あなたは天気情報を提供するアシスタントです。必要に応じてget_weatherツールを使ってください。
    """,
    model="gpt-4o-mini",
    generation_tools=[get_weather]
)
result = pipeline.run("東京の天気は？")
print(result)
```

## 2. ガードレール（入力制御）
```python
from agents import input_guardrail, GuardrailFunctionOutput, Runner, RunContextWrapper, Agent
from agents_sdk_models.pipeline import AgentPipeline
from pydantic import BaseModel

class MathCheck(BaseModel):
    is_math: bool
    reason: str

guardrail_agent = Agent(
    name="math_check",
    instructions="数学の宿題か判定してください。",
    output_type=MathCheck
)

@input_guardrail
async def math_guardrail(ctx: RunContextWrapper, agent: Agent, input: str):
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math,
    )

pipeline = AgentPipeline(
    name="guardrail_example",
    generation_instructions="質問に答えてください。",
    model="gpt-4o-mini",
    input_guardrails=[math_guardrail]
)
try:
    result = pipeline.run("2x+3=11を解いて")
    print(result)
except Exception:
    print("ガードレール発動: 数学の宿題依頼を検出")
```

## 3. ダイナミックプロンプト
```python
def dynamic_prompt(user_input: str) -> str:
    return f"[DYNAMIC] {user_input.upper()}"

pipeline = AgentPipeline(
    name="dynamic_example",
    generation_instructions="リクエストに答えてください。",
    model="gpt-4o-mini",
    dynamic_prompt=dynamic_prompt
)
result = pipeline.run("面白い話をして")
print(result)
```

## 4. リトライ＆自己改善
```python
pipeline = AgentPipeline(
    name="retry_example",
    generation_instructions="文章を生成してください。",
    evaluation_instructions="分かりやすさで評価し、コメントも返してください。",
    model="gpt-4o-mini",
    threshold=80,
    retries=2,
    retry_comment_importance=["serious", "normal"]
)
result = pipeline.run("AIの歴史を教えて")
print(result)
```

---

## ポイント
- ツールやガードレール、動的プロンプト、自己改善を柔軟に組み合わせ可能
- 実運用に近い高度なワークフローもシンプルに記述できます 