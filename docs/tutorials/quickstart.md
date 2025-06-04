# クイックスタート

このチュートリアルでは、Agents SDK Models を使った最小限のLLM活用例を紹介します。

## 1. モデルインスタンスの取得
```python
from agents_sdk_models import get_llm
llm = get_llm("gpt-4o-mini")
```

## 2. Agent でシンプルな対話
```python
from agents import Agent, Runner
agent = Agent(
    name="Assistant",
    model=llm,
    instructions="あなたは親切なアシスタントです。"
)
result = Runner.run_sync(agent, "こんにちは！")
print(result.final_output)
```

## 3. GenAgent + Flow で生成＋評価（推奨）
```python
from agents_sdk_models import create_simple_gen_agent, Flow

# GenAgentを作成
gen_agent = create_simple_gen_agent(
    name="ai_expert",
    instructions="""
    あなたは役立つアシスタントです。ユーザーの要望に応じて文章を生成してください。
    """,
    evaluation_instructions="""
    生成された文章を分かりやすさで100点満点評価し、コメントも付けてください。
    """,
    model="gpt-4o-mini",
    threshold=70
)

# Flowを作成（超シンプル！）
flow = Flow(steps=gen_agent)
result = await flow.run(input_data="AIの活用事例を教えて")
print(result.shared_state["ai_expert_result"])
```

## 4. 旧AgentPipeline（非推奨）
```python
from agents_sdk_models import AgentPipeline
# 注意：AgentPipelineはv0.1.0で削除予定です
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

## ポイント
- `get_llm` で主要なLLMを簡単取得
- `Agent` でシンプルな対話
- **新推奨：** `GenAgent + Flow` で生成・評価・自己改善まで一気通貫
- `Flow(steps=gen_agent)` だけで複雑なワークフローも**超シンプル**に実現
- 旧 `AgentPipeline` は v0.1.0 で削除予定（移行は簡単です）