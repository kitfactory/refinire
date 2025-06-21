# LLMPipeline移行ガイド

## 概要

AgentPipelineの非推奨化に伴い、新しい`LLMPipeline`と`GenAgent`を導入しました。これらは非推奨のAgentPipelineに依存せず、OpenAI Agents SDKを直接使用するモダンな実装です。

## 🚨 非推奨化の背景

### AgentPipelineの問題点

| 問題 | 詳細 |
|------|------|
| **非推奨化** | v0.1.0で完全削除予定 |
| **非同期競合** | Flow内でasyncio.run()による競合 |
| **保守性** | 複雑な内部実装 |
| **依存関係** | 非推奨コンポーネントへの依存 |

### 新しいアプローチの利点

| 利点 | 詳細 |
|------|------|
| **将来性** | 非推奨コンポーネントに依存しない |
| **安定性** | 非同期競合問題を解決 |
| **シンプル性** | OpenAI Agents SDKを直接使用 |
| **拡張性** | モジュラー設計 |

## 🔧 新しいアーキテクチャ

### LLMPipeline

```python
from refinire import LLMPipeline, LLMResult

# 基本的な使用
pipeline = LLMPipeline(
    name="my_pipeline",
    generation_instructions="あなたは親切なアシスタントです。",
    model="gpt-4o-mini"
)

result = pipeline.run("こんにちは")
if result.success:
    print(result.content)
```

### GenAgent

```python
from refinire import GenAgent, Flow, Context

# Flow内での使用
agent = GenAgent(
    name="assistant",
    generation_instructions="ユーザーを支援してください。",
    model="gpt-4o-mini"
)

flow = Flow(steps=agent)
result = await flow.run(input_data="入力データ")
```

## 📊 機能比較

| 機能 | AgentPipeline | LLMPipeline | GenAgent |
|------|---------------|-------------|----------|
| **生成** | ✅ | ✅ | ✅ |
| **評価** | ✅ | ✅ | ✅ |
| **リトライ** | ✅ | ✅ | ✅ |
| **ガードレール** | ✅ | ✅ | ✅ |
| **構造化出力** | ✅ | ✅ | ✅ |
| **Flow統合** | ❌ | ❌ | ✅ |
| **非同期安全** | ❌ | ✅ | ✅ |
| **将来性** | ❌ | ✅ | ✅ |

## 🔄 移行手順

### 1. AgentPipelineからLLMPipelineへ

**Before (非推奨):**
```python
from refinire import AgentPipeline

pipeline = AgentPipeline(
    name="old_pipeline",
    generation_instructions="指示",
    evaluation_instructions="評価指示",
    threshold=85,
    retries=3
)

result = pipeline.run("入力")
```

**After (推奨):**
```python
from refinire import LLMPipeline

pipeline = LLMPipeline(
    name="new_pipeline",
    generation_instructions="指示",
    evaluation_instructions="評価指示",
    threshold=85.0,
    max_retries=3
)

result = pipeline.run("入力")
```

### 2. FlowでのGenAgent使用

**Before (非推奨):**
```python
from refinire import AgentPipeline

pipeline = AgentPipeline(
    name="old_agent",
    generation_instructions="指示",
    evaluation_instructions="評価指示"
)

# 非同期問題が発生する可能性
result = pipeline.run("入力")
```

**After (推奨):**
```python
from refinire import create_simple_gen_agent, Flow

agent = create_simple_gen_agent(
    name="new_agent",
    instructions="指示",
    model="gpt-4o-mini"
)

flow = Flow(steps=agent)
result = await flow.run(input_data="入力")
```

### 3. ClarifyAgentの更新

ClarifyAgentは内部的にLLMPipelineを使用するよう更新済みです：

```python
from refinire.agents import ClarifyAgent

# APIは変更なし、内部実装のみ更新
agent = ClarifyAgent(
    name="clarify",
    instructions="要件を明確化してください。",
    model="gpt-4o-mini"
)
```

## 🛠️ 高度な機能

### ガードレール機能

```python
def input_filter(text: str) -> bool:
    """入力フィルター - 1000文字以下に制限"""
    return len(text) < 1000

def output_filter(text: str) -> bool:
    """出力フィルター - 不適切な内容を除外"""
    return "不適切" not in text

pipeline = LLMPipeline(
    name="guarded_pipeline",
    generation_instructions="安全な応答を生成してください",
    input_guardrails=[input_filter],
    output_guardrails=[output_filter]
)
```

### 構造化出力

```python
from pydantic import BaseModel

class TaskResult(BaseModel):
    task: str
    status: str
    confidence: float

pipeline = LLMPipeline(
    name="structured_pipeline",
    generation_instructions="タスクを分析してJSONで返してください。",
    output_model=TaskResult
)

result = pipeline.run("プロジェクト計画を作成")
if result.success:
    task_data = result.content  # TaskResultインスタンス
```

### 評価とリトライ機能

```python
pipeline = LLMPipeline(
    name="quality_pipeline",
    generation_instructions="高品質なコンテンツを生成してください",
    evaluation_instructions="品質を0-100で評価してください",
    threshold=85.0,
    max_retries=3
)

result = pipeline.run("技術記事を作成")
if result.success:
    print(f"生成結果: {result.content}")
    print(f"品質スコア: {result.evaluation_score}")
```

### ツール統合

```python
from agents import function_tool

@function_tool
def tool1():
    pass

@function_tool
def tool2():
    pass

# AgentPipeline: generation_toolsパラメータ
pipeline = AgentPipeline(generation_tools=[tool1, tool2])

# LLMPipeline: toolsパラメータ
pipeline = LLMPipeline(tools=[tool1, tool2])

# GenAgent: create_simple_gen_agentのtoolsパラメータ
agent = create_simple_gen_agent(tools=[tool1, tool2])
```

## 🏃‍♂️ 段階的移行戦略

### フェーズ1: 新規開発での採用

```python
# 新規プロジェクトでは推奨パターンを使用
from refinire import create_simple_gen_agent, Flow

agent = create_simple_gen_agent(
    name="new_feature",
    instructions="新機能のサポートを提供",
    model="gpt-4o-mini"
)

flow = Flow(steps=agent)
```

### フェーズ2: 既存コードの段階的移行

```python
# 1. まずAgentPipelineをLLMPipelineに置き換え
# Before
old_pipeline = AgentPipeline(...)

# After
new_pipeline = LLMPipeline(
    name=old_pipeline.name,
    generation_instructions=old_pipeline.generation_instructions,
    # その他のパラメータを移行
)

# 2. 次にFlow/GenAgentアーキテクチャに移行
agent = create_simple_gen_agent(...)
flow = Flow(steps=agent)
```

### フェーズ3: 完全移行

```python
# 最終的にはすべてのワークフローをFlowベースに統一
complex_flow = Flow([
    ("preprocess", FunctionStep("prep", preprocess_func)),
    ("generate", create_simple_gen_agent(...)),
    ("postprocess", FunctionStep("post", postprocess_func))
])
```

## 🔍 トラブルシューティング

### よくある問題と解決策

#### 1. 非同期競合エラー

```python
# 問題: AgentPipelineをFlow内で使用
# RuntimeError: asyncio.run() cannot be called from a running event loop

# 解決策: GenAgentを使用
agent = create_simple_gen_agent(...)
flow = Flow(steps=agent)
```

#### 2. 評価スコアの取得方法の変更

```python
# Before (AgentPipeline)
result = pipeline.run("入力")
score = result.evaluation_result.score

# After (LLMPipeline)
result = pipeline.run("入力")
score = result.evaluation_score

# After (GenAgent + Flow)
result = await flow.run(input_data="入力")
score = result.shared_state.get("agent_name_evaluation", {}).get("score")
```

#### 3. ツール呼び出しの違い

```python
from agents import function_tool

@function_tool
def tool1():
    pass

@function_tool
def tool2():
    pass

# AgentPipeline: generation_toolsパラメータ
pipeline = AgentPipeline(generation_tools=[tool1, tool2])

# LLMPipeline: toolsパラメータ
pipeline = LLMPipeline(tools=[tool1, tool2])

# GenAgent: create_simple_gen_agentのtoolsパラメータ
agent = create_simple_gen_agent(tools=[tool1, tool2])
```

## ✅ 移行チェックリスト

### コード移行

- [ ] AgentPipelineのimportを削除
- [ ] LLMPipelineまたはGenAgentに置き換え
- [ ] パラメータ名の調整（retries → max_retries等）
- [ ] 戻り値の処理方法を更新
- [ ] ツール定義の形式を確認

### テスト移行

- [ ] AgentPipelineのテストを更新
- [ ] 非同期処理のテストを追加
- [ ] Flow統合のテストを作成
- [ ] エラーハンドリングのテストを確認

### ドキュメント更新

- [ ] API使用例を更新
- [ ] 移行前後の比較を記載
- [ ] 新機能の説明を追加
- [ ] 非推奨警告を追加

## 🎯 移行後のメリット

### 1. 将来性の確保

```python
# v0.1.0以降も安心して使用可能
pipeline = LLMPipeline(...)  # ✅ 継続サポート
# AgentPipeline(...)         # ❌ v0.1.0で削除
```

### 2. 非同期処理の安全性

```python
# Flow内で安全に使用可能
flow = Flow([
    ("step1", gen_agent),
    ("step2", another_agent)
])
await flow.run(input_data="データ")  # ✅ 非同期安全
```

### 3. モジュラー設計

```python
# 再利用可能なコンポーネント
validation_agent = create_simple_gen_agent(...)
processing_agent = create_simple_gen_agent(...)

# 異なるフローで再利用
flow1 = Flow([("validate", validation_agent)])
flow2 = Flow([("validate", validation_agent), ("process", processing_agent)])
```

## 📚 参考資料

- [APIリファレンス](api_reference_ja.md) - 新しいAPIの詳細
- [クイックスタート](tutorials/quickstart_ja.md) - 推奨パターンの例
- [組み合わせ可能なフローアーキテクチャ](composable-flow-architecture_ja.md) - Flowの詳細

## 💡 移行のヒント

1. **段階的アプローチ**: 一度にすべてを変更せず、段階的に移行
2. **テスト駆動**: 移行前に既存機能のテストを充実させる
3. **並行開発**: 新機能は推奨パターンで、既存機能は徐々に移行
4. **ドキュメント重視**: チーム内での知識共有を重視

移行に関する質問やサポートが必要な場合は、プロジェクトのIssueでお気軽にお問い合わせください。 