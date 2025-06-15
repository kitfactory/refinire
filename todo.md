# Namespace Package 移行計画

## Phase 1: パッケージ構造設計 ✅ 完了

### 分割戦略の確定
- [x] **refinire.core**: LLMプロバイダー抽象化、トレーシング・モニタリング
- [x] **refinire.agents**: Flow/Step、各種エージェント実装、パイプライン機能
- [x] 現在の `src/refinire/__init__.py` の機能分割計画策定

### 移行後の構造設計
- [x] refinire-core パッケージ構造の設計
- [x] refinire-agents パッケージ構造の設計  
- [x] namespace package の仕組み確認（refinire.rag の独立提供可能性）

## Phase 2: refinire-core パッケージ作成 ✅ 完了

### ディレクトリ構造作成
- [x] `refinire-core/` ディレクトリ作成
- [x] `refinire-core/src/refinire/core/` 構造作成
- [x] `refinire-core/pyproject.toml` 作成

### コアモジュールの移行
- [x] `llm.py` → `refinire-core/src/refinire/core/llm.py`
- [x] `anthropic.py` → `refinire-core/src/refinire/core/anthropic.py`
- [x] `gemini.py` → `refinire-core/src/refinire/core/gemini.py`
- [x] `ollama.py` → `refinire-core/src/refinire/core/ollama.py`
- [x] `tracing.py` → `refinire-core/src/refinire/core/tracing.py`
- [x] `trace_registry.py` → `refinire-core/src/refinire/core/trace_registry.py`
- [x] `message.py` → `refinire-core/src/refinire/core/message.py`

### refinire.core の __init__.py 作成
- [x] コア機能のエクスポート設定
```python
from .llm import ProviderType, get_llm, get_available_models, get_available_models_async
from .anthropic import ClaudeModel
from .gemini import GeminiModel  
from .ollama import OllamaModel
from .tracing import enable_console_tracing, disable_tracing
from .trace_registry import TraceRegistry, TraceMetadata, get_global_registry, set_global_registry
```

### pyproject.toml 設定
- [x] パッケージメタデータ設定（name: "refinire-core"）
- [x] 依存関係の最小化（OpenAI、Anthropic、Google等のAPI依存のみ）
- [x] namespace package ビルド設定

## Phase 3: refinire-agents パッケージ作成 ✅ 完了

### ディレクトリ構造作成
- [x] `refinire-agents/` ディレクトリ作成
- [x] `refinire-agents/src/refinire/agents/` 構造作成
- [x] `refinire-agents/pyproject.toml` 作成

### エージェントモジュールの移行
- [x] `context.py` → `refinire-agents/src/refinire/agents/context.py`
- [x] `step.py` → `refinire-agents/src/refinire/agents/step.py`
- [x] `flow.py` → `refinire-agents/src/refinire/agents/flow.py`
- [x] `pipeline.py` → `refinire-agents/src/refinire/agents/pipeline.py`
- [x] `llm_pipeline.py` → `refinire-agents/src/refinire/agents/llm_pipeline.py`
- [x] `agents/` ディレクトリ全体の移行
  - [x] `clarify_agent.py`
  - [x] `extractor.py`
  - [x] `gen_agent.py`
  - [x] `notification.py`  
  - [x] `router.py`
  - [x] `validator.py`

### refinire.agents の __init__.py 作成
- [x] 全エージェント機能のエクスポート設定
- [x] Flow/Step関連機能のエクスポート設定
- [x] パイプライン機能のエクスポート設定

### pyproject.toml 設定
- [x] パッケージメタデータ設定（name: "refinire-agents"）
- [x] refinire-core への依存関係設定
- [x] namespace package ビルド設定

## Phase 4: 依存関係の解決 ✅ 完了

### import文の修正
- [x] refinire-agents 内での refinire.core import修正
```python
# 修正前
from .tracing import get_global_registry

# 修正後  
from refinire.core.trace_registry import get_global_registry
```

### 相互依存の解決
- [x] flow.py での trace_registry import修正
- [x] pipeline.py での llm, message import修正
- [x] エージェント内での相対import修正（..step → .step など）
- [x] refinire-core内のtracing.pyでのmessage import修正

### namespace package の確認
- [x] src/refinire/ に __init__.py が存在しないことを確認
- [x] 両パッケージが同じnamespace下で動作することを確認
- [x] 両パッケージをdevelopment modeでインストール完了

## Phase 5: テストの修正 ✅ 部分完了

### テストファイルのimport修正（重要なファイルは修正済み）
- [x] `tests/test_llm.py` の import修正 (`refinire.core`)
- [x] `tests/test_anthropic.py` の import修正 (`refinire.core.anthropic`)  
- [x] `tests/test_context.py` の import修正 (`refinire.agents.context`)
- [x] `tests/test_flow.py` の import修正 (`refinire.agents.flow`)
- [x] `tests/test_step.py` の import修正 (`refinire.agents.step`)

### 残りのテストファイル（26ファイル中21ファイル）
- [ ] `tests/test_anthropic_extra.py` - `refinire.core.anthropic`
- [ ] `tests/test_clarify_agent.py` - `refinire.agents`
- [ ] `tests/test_dag_parallel.py` - `refinire.agents`
- [ ] `tests/test_extractor_agent.py` - `refinire.agents.extractor + context`
- [ ] `tests/test_flow_constructor.py` - `refinire.agents.flow + step + context`
- [ ] `tests/test_flow_identification.py` - `refinire.agents`
- [ ] `tests/test_flow_show.py` - `refinire.agents.flow + step + context`
- [ ] `tests/test_gemini.py` - `refinire.core.gemini`
- [ ] `tests/test_gen_agent.py` - `refinire.agents`
- [ ] `tests/test_gen_agent_modern.py` - `refinire.agents.gen_agent + context + llm_pipeline`
- [ ] `tests/test_get_available_models.py` - `refinire.core.llm`
- [ ] `tests/test_interactive_pipeline.py` - `refinire.agents`
- [ ] `tests/test_llm_pipeline.py` - `refinire.agents.llm_pipeline`
- [ ] `tests/test_llm_pipeline_tools.py` - `refinire.agents.llm_pipeline`
- [ ] `tests/test_notification_agent.py` - `refinire.agents.notification + context`
- [ ] `tests/test_ollama.py` - `refinire.core.ollama`
- [ ] `tests/test_router_agent.py` - `refinire.agents.router + context + llm_pipeline`
- [ ] `tests/test_trace_search.py` - `refinire.core` (TraceRegistry関連)
- [ ] `tests/test_trace_span.py` - `refinire.agents` (Flow, Context)
- [ ] `tests/test_tracing.py` - `refinire.core.tracing + agents.context + core.message`
- [ ] `tests/test_tracing_integration.py` - `refinire.core.tracing + core.llm`
- [ ] `tests/test_validator_agent.py` - `refinire.agents.validator + context`

### テスト環境の調整
- [x] 両パッケージをdevelopment modeでインストール
- [x] namespace packageの動作確認完了
- [ ] テスト実行環境の確認
- [ ] CI/CDパイプラインの調整（必要に応じて）

### テスト実行確認計画
- [ ] Core modules: `test_llm.py`, `test_anthropic.py`, `test_gemini.py`, `test_ollama.py`, `test_tracing.py`, `test_trace_search.py`
- [ ] Agent modules: `test_context.py`, `test_flow.py`, `test_step.py`, `test_gen_agent.py`, `test_clarify_agent.py`
- [ ] Integration tests: `test_tracing_integration.py`, `test_dag_parallel.py`

## Phase 6: examples の修正

### examplesファイルのimport修正
- [ ] 全てのexampleファイルでのimport文修正
```python
# 修正前
from refinire import get_llm, Flow, create_simple_gen_agent

# 修正後
from refinire.core import get_llm
from refinire.agents import Flow, create_simple_gen_agent
```

### 動作確認
- [ ] 各exampleファイルの動作確認
- [ ] エラーの修正とテスト

## Phase 7: ドキュメントの更新

### インストール手順の更新
- [ ] README.md の更新
```bash
# 基本機能のみ
pip install refinire-core

# エージェント機能も含む
pip install refinire-core refinire-agents

# 全機能（将来的に統合パッケージも提供）
pip install refinire-full
```

### 使用例の更新
- [ ] 全ドキュメントでのimport例の修正
- [ ] API reference の更新
- [ ] チュートリアルの更新

### CLAUDE.md の更新
- [ ] namespace package構造の説明追加
- [ ] 新しいimportパターンの説明

## Phase 8: 統合パッケージの作成（オプション）

### refinire-full パッケージ
- [ ] ユーザー利便性のための統合パッケージ作成
- [ ] refinire-core + refinire-agents の依存関係設定
- [ ] 後方互換性レイヤーの検討

### 後方互換性の提供
- [ ] 既存ユーザー向けの移行ガイド作成
- [ ] deprecation警告の実装（必要に応じて）

## Phase 9: リリース準備

### バージョン管理
- [ ] refinire-core v0.2.0 リリース準備
- [ ] refinire-agents v0.2.0 リリース準備
- [ ] 破壊的変更の文書化

### 品質保証
- [ ] 全テストの通過確認
- [ ] type checking (mypy) の通過確認
- [ ] パッケージビルドの確認
- [ ] インストールテストの実行

### リリース
- [ ] PyPI へのアップロード
- [ ] リリースノートの作成
- [ ] ユーザーへの移行案内

## 期待される利点

### 開発者向け
- [ ] 必要な機能のみのインストール可能
- [ ] 明確な責任分離による保守性向上
- [ ] 将来的な機能拡張の柔軟性確保

### エコシステム向け  
- [ ] refinire.rag 等の独立パッケージ開発の促進
- [ ] サードパーティ拡張の容易化
- [ ] モジュラーアーキテクチャの実現

## 注意事項

### 破壊的変更
- [ ] 既存ユーザーのimport文修正が必要
- [ ] 適切な移行期間とサポートの提供
- [ ] 明確なコミュニケーション

### 技術的制約
- [ ] namespace package の制約に関する理解
- [ ] 依存関係の循環回避
- [ ] パッケージングツールとの互換性