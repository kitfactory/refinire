# 応用例

このチュートリアルでは、Agents SDK Models の応用的な使い方を紹介します。

## 0. 新しいFlow作成方法（超重要！）

新しい **Flow** は3つの方法で作成できます：

```python
from agents_sdk_models import create_simple_gen_agent, Flow, DebugStep

# 1. 単一ステップ（最もシンプル！）
gen_agent = create_simple_gen_agent("writer", "文章を書いてください", "gpt-4o-mini")
flow = Flow(steps=gen_agent)

# 2. シーケンシャルステップ（自動接続！）
debug_step = DebugStep("debug", "処理完了")
flow = Flow(steps=[gen_agent, debug_step])  # gen_agent → debug_step

# 3. 従来方式（複雑なフロー用）
flow = Flow(
    start="writer",
    steps={
        "writer": gen_agent,
        "debug": debug_step
    }
)

# 実行は全て同じ
result = await flow.run(input_data="AIについて書いて")
print(result.shared_state["writer_result"])
```

## 1. ツール連携（新推奨方法）
```python
from agents import function_tool
from agents_sdk_models import create_simple_gen_agent, Flow

@function_tool
def get_weather(location: str) -> str:
    return f"Weather in {location}: Sunny, 25°C"

# RefinireAgent + Flow方式（推奨）
weather_agent = create_simple_agent(
    name="weather_bot",
    instructions="""
    あなたは天気情報を提供するアシスタントです。必要に応じてget_weatherツールを使ってください。
    """,
    model="gpt-4o-mini",
    tools=[get_weather]
)

flow = Flow(steps=weather_agent)  # 超シンプル！
result = await flow.run(input_data="東京の天気は？")
print(result.shared_state["weather_bot_result"])
```

### 旧方式（非推奨）
```python
# AgentPipeline（v0.1.0で削除予定）
from agents_sdk_models import AgentPipeline
pipeline = AgentPipeline(
    name="tool_example",
    generation_instructions="天気情報を提供してください。",
    model="gpt-4o-mini",
    generation_tools=[get_weather]
)
result = pipeline.run("東京の天気は？")
print(result)
```

## 2. ガードレール（入力制御）
```python
from agents import input_guardrail, GuardrailFunctionOutput, Runner, RunContextWrapper, Agent
from agents_sdk_models import AgentPipeline
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

## 4. リトライ＆自己改善（新推奨方法）
```python
from refinire import create_evaluated_agent, Flow

# 評価付きRefinireAgent + Flow方式（推奨）
smart_agent = create_evaluated_agent(
    name="smart_writer",
    generation_instructions="文章を生成してください。",
    evaluation_instructions="分かりやすさで評価し、コメントも返してください。",
    model="gpt-4o-mini",
    threshold=80,
    retries=2
)

flow = Flow(steps=smart_agent)  # 自動でリトライ＆自己改善！
result = await flow.run(input_data="AIの歴史を教えて")
print(result.shared_state["smart_writer_result"])
```

### 旧方式（非推奨）
```python
# AgentPipeline（v0.1.0で削除予定）
pipeline = AgentPipeline(
    name="retry_example",
    generation_instructions="文章を生成してください。",
    evaluation_instructions="分かりやすさで評価し、コメントも返してください。",
    model="gpt-4o-mini",
    threshold=80,
    retries=2
)
result = pipeline.run("AIの歴史を教えて")
print(result)
```

---

## 5. 複雑なワークフロー（マルチステップ）
```python
from agents_sdk_models import (
    create_simple_agent, create_evaluated_agent, 
    Flow, DebugStep, UserInputStep, ConditionStep
)

# 複数のRefinireAgentを組み合わせ
idea_generator = create_simple_agent(
    name="idea_gen", 
    instructions="創造的なアイデアを生成してください", 
    model="gpt-4o-mini"
)

content_writer = create_evaluated_agent(
    name="writer",
    generation_instructions="提供されたアイデアを基に詳細な記事を書いてください",
    evaluation_instructions="記事の質を評価してください",
    model="gpt-4o",
    threshold=75
)

reviewer = create_simple_agent(
    name="reviewer",
    instructions="記事をレビューして改善提案をしてください",
    model="claude-3-5-sonnet-latest"
)

# シーケンシャルワークフロー（自動接続！）
flow = Flow(steps=[
    idea_generator,      # アイデア生成
    content_writer,      # 記事執筆（評価付き）
    reviewer,           # レビュー
    DebugStep("done", "ワークフロー完了")
])

result = await flow.run(input_data="AI技術について")
print("アイデア:", result.shared_state["idea_gen_result"])
print("記事:", result.shared_state["writer_result"])
print("レビュー:", result.shared_state["reviewer_result"])
```

## 6. 条件分岐付きワークフロー
```python
# 条件に応じて異なる処理パスを実行
def check_content_type(ctx):
    user_input = ctx.last_user_input or ""
    return "技術" in user_input

tech_writer = create_simple_gen_agent("tech", "技術記事を書く", "gpt-4o")
general_writer = create_simple_gen_agent("general", "一般記事を書く", "gpt-4o-mini")

# 従来方式（複雑なフロー用）
complex_flow = Flow(
    start="check_type",
    steps={
        "check_type": ConditionStep(
            "check_type", 
            check_content_type, 
            "tech_writer", 
            "general_writer"
        ),
        "tech_writer": tech_writer,
        "general_writer": general_writer,
        "review": create_simple_gen_agent("reviewer", "記事をレビュー", "claude-3-5-sonnet-latest")
    }
)

result = await complex_flow.run(input_data="技術的な内容について書いて")
```

## ポイント
- **新機能：** `Flow(steps=[step1, step2])` で自動シーケンシャル接続
- **新機能：** `Flow(steps=single_step)` で単一ステップも超シンプル
- ツールやガードレール、動的プロンプト、自己改善を柔軟に組み合わせ可能
- 旧 `AgentPipeline` から `RefinireAgent + Flow` への移行は簡単
- 複雑なワークフローも数行で構築可能