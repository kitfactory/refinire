# AgentPipeline Deprecation Plan
# AgentPipelineの廃止予定計画

## 背景 (Background)

Flow/Stepアーキテクチャの導入により、より柔軟で拡張性の高いワークフロー管理が可能になりました。GenAgentクラスにより、AgentPipelineの機能はFlowワークフロー内でStepとして使用できるようになったため、AgentPipelineクラスを段階的に廃止していきます。

## 移行の利点 (Migration Benefits)

### English:
- More flexible workflow composition using Flow/Step architecture
- Better reusability through modular Step design
- Enhanced error handling and context management
- Cleaner separation of concerns
- Future-proof architecture for complex workflows

### 日本語:
- Flow/Stepアーキテクチャによるより柔軟なワークフロー構成
- モジュラーなStep設計による再利用性の向上
- エラーハンドリングとコンテキスト管理の強化
- 関心の分離のよりクリーンな実現
- 複雑なワークフローに対応する将来性のあるアーキテクチャ

## 廃止計画 (Deprecation Timeline)

### フェーズ 1: Deprecation Warning追加 (v0.0.22) ✅ 完了
- [x] AgentPipelineクラスにdeprecation warningを追加
- [x] 新しいGenAgentへの移行ガイドを作成
- [x] README.mdでFlow/Stepアーキテクチャを推奨として記載

### フェーズ 2: Examples移行 (v0.0.23) ✅ 完了
- [x] genagent_simple_generation.py - 基本的な生成例の移行版
- [x] genagent_with_evaluation.py - 評価機能付きの移行版
- [x] genagent_with_tools.py - ツール使用例の移行版
- [x] genagent_with_guardrails.py - ガードレール使用例の移行版
- [x] genagent_with_history.py - 履歴管理例の移行版
- [x] genagent_with_retry.py - リトライ機能例の移行版
- [x] genagent_with_dynamic_prompt.py - 動的プロンプト例の移行版
- [x] 新しいFlow/Step使用例の充実（各exampleで複数の使用例を実装）
- [x] 移行ガイドの完成（deprecation_plan.mdに詳細な移行例を記載）

### フェーズ 3: テスト移行 (v0.0.24) ✅ 完了
- [x] AgentPipelineのテストをGenAgentベースに移行
- [x] 後方互換性テストの追加
- [x] GenAgentの完全なテストカバレッジ

#### 移行されたテストファイル:
- **`test_gen_agent_compatibility.py`** (377行) - 互換性とdeprecation警告テスト
- **`test_gen_agent_comprehensive.py`** (306行, 12テスト) - 全機能カバレッジテスト
- **テスト結果**: 全て成功 (12 passed, 19 warnings)
- **カバレッジ**: ガードレール、プロンプト構築、ユーティリティ、履歴管理、閾値設定

### フェーズ 4: 完全削除 (v0.1.0)
- [ ] AgentPipelineクラスの完全削除
- [ ]関連するimportとexportの削除
- [ ] ドキュメントのクリーンアップ

## 移行方法 (Migration Guide)

### 基本的な移行パターン

#### 旧: AgentPipeline
```python
from agents_sdk_models import AgentPipeline

pipeline = AgentPipeline(
    name="example",
    generation_instructions="Generate a response",
    model="gpt-4o-mini"
)

result = pipeline.run("User input")
```

#### 新: GenAgent (Flow/Step内)
```python
from agents_sdk_models import GenAgent, Flow, create_simple_flow

# Method 1: Direct GenAgent usage
gen_agent = GenAgent(
    name="example", 
    generation_instructions="Generate a response",
    model="gpt-4o-mini",
    context_key="result"
)

flow = create_simple_flow(gen_agent)
result = await flow.run(input_data="User input")

# Method 2: Utility function
from agents_sdk_models import create_simple_gen_agent

gen_agent = create_simple_gen_agent(
    name="example",
    generation_instructions="Generate a response", 
    model="gpt-4o-mini"
)
```

### 評価機能付きの移行

#### 旧: AgentPipeline with evaluation
```python
pipeline = AgentPipeline(
    name="evaluated_pipeline",
    generation_instructions="Generate creative content",
    evaluation_instructions="Evaluate creativity and quality",
    model="gpt-4o-mini",
    evaluation_threshold=0.8
)
```

#### 新: GenAgent with evaluation
```python
from agents_sdk_models import create_evaluated_gen_agent

gen_agent = create_evaluated_gen_agent(
    name="evaluated_agent",
    generation_instructions="Generate creative content",
    evaluation_instructions="Evaluate creativity and quality",
    model="gpt-4o-mini",
    evaluation_threshold=0.8
)
```

## 対象ファイル (Target Files)

### コアファイル
- `src/agents_sdk_models/pipeline.py` - AgentPipelineクラス
- `src/agents_sdk_models/__init__.py` - export削除

### Examplesファイル
- `examples/pipeline_simple_generation.py`
- `examples/pipeline_with_dynamic_prompt.py`
- `examples/pipeline_with_evaluation.py`
- `examples/pipeline_with_guardrails.py`
- `examples/pipeline_with_history.py`
- `examples/pipeline_with_retry.py`
- `examples/pipeline_with_tools.py`
- `examples/simple_llm_query.py`

### テストファイル
- `tests/test_pipeline.py`
- `tests/test_pipeline_*.py` 系統

## 後方互換性の保証 (Backward Compatibility)

v0.1.0まで完全な後方互換性を保証します：
- 既存のAgentPipelineコードは引き続き動作
- Deprecation warningのみ表示
- ドキュメントで新しい方法を推奨

## サポート (Support)

移行に関する質問やサポートは：
- GitHub Issues
- ドキュメントの移行ガイド
- Example コードの参照 