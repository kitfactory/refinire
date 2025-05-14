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

## 3. AgentPipeline で生成＋評価
```python
from agents_sdk_models.pipeline import AgentPipeline
pipeline = AgentPipeline(
    name="eval_example",
    generation_instructions="""
    あなたは役立つアシスタントです。ユーザーの要望に応じて文章を生成してください。
    """,
    evaluation_instructions="""
    生成された文章を分かりやすさで100点満点評価し、コメントも付けてください。
    """,
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
- `AgentPipeline` で生成・評価・自己改善まで一気通貫
- どちらも最小限の記述で高度なワークフローが実現できます 