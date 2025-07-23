# Context仕様修正プロジェクト

## 概要

RefinireAgentの返却値であるContextクラスの`result`属性と`content`属性の仕様を正しく修正する。
- `result`属性: 完全なLLMResult オブジェクト（推奨: 高度な使用）
- `content`属性: 生成されたコンテンツのみ（推奨: 一般使用）

## 影響を受けるファイル一覧

### コアソースコード（最高優先度）
1. `src/refinire/agents/flow/context.py` - Contextクラスの実装
2. `src/refinire/agents/pipeline/llm_pipeline.py` - RefinireAgentの実装

### サポートソースコード（高優先度）
3. `src/refinire/agents/flow/flow.py` - Flow実装での使用
4. `src/refinire/agents/flow/step.py` - Step実装での使用
5. `src/refinire/agents/clarify_agent.py` - エージェント実装
6. `src/refinire/agents/extractor.py` - エージェント実装
7. `src/refinire/core/llm.py` - LLMコア実装
8. `src/refinire/core/prompt_store.py` - プロンプトストア実装

### テストファイル（高優先度）
9. `tests/test_context.py` - Contextクラステスト
10. `tests/test_refinire_agent.py` - RefinireAgentテスト
11. `tests/test_refinire_agent_tools.py` - RefinireAgentツールテスト
12. `tests/test_evaluation_result_access.py` - 評価結果アクセステスト
13. `tests/test_flow_*` - Flow関連テスト（複数ファイル）
14. `tests/test_llm_pipeline_tools.py` - LLMパイプラインテスト
15. `tests/test_orchestration_*.py` - オーケストレーション関連テスト
16. `tests/test_streaming.py` - ストリーミングテスト
17. その他のテストファイル（約10ファイル）

### サンプルコード（中優先度）
18. `examples/` - 約15個のサンプルファイル
19. `study/` - 学習用ファイル（2ファイル）
20. `docs/example_unified_processor.py` - ドキュメント内サンプル

## 修正手順

### Phase 1: コア実装の修正

#### 1.1 Context.contentプロパティの修正
**ファイル**: `src/refinire/agents/flow/context.py`
**修正内容**:
```python
@property
def content(self) -> Any:
    """
    Access to generated content only (recommended for most users)
    生成されたコンテンツのみにアクセス（一般ユーザー推奨）
    """
    return self.result.content if self.result else None

@content.setter
def content(self, value: Any) -> None:
    """
    Setter for content property - updates LLMResult.content
    contentプロパティのセッター - LLMResult.contentを更新
    """
    if self.result:
        self.result.content = value
    else:
        # Create minimal LLMResult if none exists
        from refinire.agents.pipeline.llm_pipeline import LLMResult
        self.result = LLMResult(content=value, success=True)
```

#### 1.2 RefinireAgent結果格納の修正
**ファイル**: `src/refinire/agents/pipeline/llm_pipeline.py`
**修正内容**:
```python
# 現在: ctx.result = llm_result.content
# 修正後: ctx.result = llm_result  # 完全なLLMResultオブジェクトを格納
```

### Phase 2: 依存ソースコードの修正

#### 2.1 Flow関連の修正
**ファイル**: `src/refinire/agents/flow/flow.py`, `src/refinire/agents/flow/step.py`
**修正内容**: Context使用箇所で`.content`または`.result`の適切な使い分け

#### 2.2 エージェント実装の修正
**ファイル**: `src/refinire/agents/clarify_agent.py`, `src/refinire/agents/extractor.py`
**修正内容**: Context使用箇所の適切な修正

### Phase 3: テストファイルの修正

#### 3.1 Contextテストの修正
**ファイル**: `tests/test_context.py`
**修正内容**: 新しいContent仕様に合わせたテストケース更新

#### 3.2 RefinireAgentテストの修正
**ファイル**: `tests/test_refinire_agent.py`, `tests/test_refinire_agent_tools.py`
**修正内容**: 
- `result.content`と`result.result`の使い分けテスト
- 新しい仕様に合わせた期待値の修正

#### 3.3 その他テストの修正
**ファイル**: 各種test_*.pyファイル
**修正内容**: `.content`/.result`の適切な使い分け

### Phase 4: サンプルコードの修正

#### 4.1 examplesディレクトリの修正
**ファイル**: `examples/*.py` (約15ファイル)
**修正内容**: 
- 一般的な使用例では`result.content`を使用
- デバッグや高度な使用例では`result.result`を使用

#### 4.2 学習用ファイルの修正
**ファイル**: `study/*.py`
**修正内容**: 適切な使用例の提示

## 実装チェックリスト

### Phase 1: コア実装 🔥

#### 1.1 Context.contentプロパティの修正
- [x] `src/refinire/agents/flow/context.py` - contentプロパティ修正
- [x] `tests/test_context.py` - Context.contentプロパティのテスト修正

#### 1.2 RefinireAgent結果格納の修正  
- [x] `src/refinire/agents/pipeline/llm_pipeline.py` - 結果格納方法修正
- [x] `tests/test_refinire_agent.py` - RefinireAgent結果格納のテスト修正
- [x] `tests/test_refinire_agent_tools.py` - RefinireAgentツールのテスト修正

### Phase 2: 依存ソースコード修正 🔥

#### 2.1 Flow関連の修正
- [x] `src/refinire/agents/flow/flow.py` - Context使用箇所修正
- [x] `tests/test_flow_*.py` - Flow関連テスト修正（複数ファイル）
- [x] `src/refinire/agents/flow/step.py` - Context使用箇所修正

#### 2.2 エージェント実装の修正
- [x] `src/refinire/agents/clarify_agent.py` - Context使用箇所修正
- [x] `src/refinire/agents/extractor.py` - Context使用箇所修正

#### 2.3 コア実装の修正
- [x] `src/refinire/core/llm.py` - Context使用箇所修正
- [x] `src/refinire/core/prompt_store.py` - Context使用箇所修正

### Phase 3: 残りテスト修正 ⚡

#### 3.1 機能別テスト修正
- [x] `tests/test_evaluation_result_access.py` - 評価結果アクセステスト修正
- [x] `tests/test_llm_pipeline_tools.py` - LLMパイプラインテスト修正
- [x] `tests/test_orchestration_*.py` - オーケストレーションテスト修正
- [x] `tests/test_streaming.py` - ストリーミングテスト修正

#### 3.2 統合・その他テスト修正
- [x] `tests/test_async_flow.py` - 非同期Flowテスト修正
- [x] `tests/test_dag_parallel.py` - DAG並列テスト修正
- [x] `tests/test_extractor_agent.py` - 抽出エージェントテスト修正
- [x] `tests/test_interactive_pipeline.py` - 対話パイプラインテスト修正
- [x] `tests/test_simple.py` - 基本テスト修正
- [x] `tests/test_tools_integration.py` - ツール統合テスト修正
- [x] `tests/test_tracing_integration.py` - トレーシング統合テスト修正

### Phase 4: サンプルコード修正 💡

#### 4.1 Examples修正
- [x] `examples/debug_streaming.py` - デバッグストリーミングサンプル修正
- [x] `examples/evaluation_examples.py` - 評価サンプル修正
- [x] `examples/flow_streaming_example.py` - Flowストリーミングサンプル修正
- [x] `examples/grafana_tempo_tracing_example.py` - トレーシングサンプル修正
- [x] `examples/lmstudio_*.py` - LM Studioサンプル修正（2ファイル）
- [x] `examples/mcp_server_example.py` - MCPサーバーサンプル修正
- [x] `examples/migration_example.py` - 移行サンプル修正
- [x] `examples/oneenv_tracing_example.py` - oneenvサンプル修正
- [x] `examples/openrouter_basic_usage.py` - OpenRouterサンプル修正
- [x] `examples/opentelemetry_tracing_example.py` - OpenTelemetryサンプル修正
- [x] `examples/orchestration_mode_example.py` - オーケストレーションサンプル修正
- [x] `examples/prompt_store_example.py` - プロンプトストアサンプル修正
- [x] `examples/refinire_tools_example.py` - ツールサンプル修正
- [x] `examples/simple_chat.py` - シンプルチャットサンプル修正
- [x] `examples/simple_flow_*.py` - シンプルFlowサンプル修正（2ファイル）
- [x] `examples/streaming_structured_test.py` - 構造化ストリーミングサンプル修正
- [x] `examples/tools_example.py` - ツールサンプル修正

#### 4.2 Study・Docs修正
- [x] `study/refinire_agent_basic_study.py` - 基本学習ファイル修正
- [x] `study/refinire_agent_tools_study.py` - ツール学習ファイル修正
- [x] `docs/example_unified_processor.py` - ドキュメントサンプル修正

## 品質保証

### テスト実行
- [x] 全テスト実行: `python -m pytest`
- [x] 型チェック: `python -m mypy src/refinire`
- [x] カバレッジ確認: `python -m pytest --cov=src/refinire`

### 互換性確認
- [x] 既存APIの動作確認
- [x] サンプルコードの実行確認
- [x] パフォーマンステスト

## 完了基準

### Phase 1完了基準
- [x] Context.contentプロパティが正しく実装
- [x] RefinireAgentがLLMResultオブジェクトを正しく格納
- [x] 基本テストが通過

### Phase 2完了基準  
- [x] 全依存ソースコードが修正完了
- [x] 関連テストが通過

### Phase 3完了基準
- [x] 全テストファイルが修正完了
- [x] テストスイート全体が通過
- [x] 型チェックエラーなし

### Phase 4完了基準
- [x] 全サンプルコードが修正完了
- [x] サンプル実行確認完了
- [x] ドキュメント整合性確認完了

---

# RefinireAgent Prompt-Result管理システム実装

## 概要

RefinireAgentのgeneration → routing/evaluation の流れで、直前のプロンプトと生成結果のペアを効率的に参照できるシステムを実装する。
Context.shared_stateの規約を使用して、routing/evaluationエージェントでContextProviderを使わずプロンプト内で参照可能にする。

## 実装要件

- `_last_prompt`: 生成時に使用された完全なプロンプト（会話履歴、instructions、ユーザー入力を含む）
- `_last_generation`: 生成された結果コンテンツ
- routing/evaluationエージェント実行時の上書き防止機能
- ContextProvider不使用でプロンプト内参照

## 実装タスク

### Phase 1: コア機能実装 🔥

#### 1.1 shared_state自動保存機能
- [ ] `src/refinire/agents/pipeline/llm_pipeline.py` - `_execute_with_context`修正
  - [ ] 生成前に`_last_prompt`をshared_stateに保存
  - [ ] 生成後に`_last_generation`をshared_stateに保存
  - [ ] 保存タイミングの最適化

#### 1.2 Routing用プロンプト構築修正
- [ ] `src/refinire/agents/pipeline/llm_pipeline.py` - `_build_routing_prompt_with_history`修正
  - [ ] shared_stateから`_last_prompt`を取得
  - [ ] shared_stateから`_last_generation`を取得  
  - [ ] 冗長な会話履歴抽出を削除（last_promptに既に含まれているため）
  - [ ] 新しいプロンプト形式に更新

#### 1.3 Evaluation用プロンプト構築実装
- [ ] `src/refinire/agents/pipeline/llm_pipeline.py` - `_build_evaluation_prompt`新規作成
  - [ ] shared_stateから`_last_prompt`/_last_generation`を取得
  - [ ] evaluation用プロンプトテンプレート作成
  - [ ] evaluation実行部分での使用

#### 1.4 上書き防止機能実装
- [ ] `src/refinire/agents/pipeline/llm_pipeline.py` - `_execute_routing`修正
  - [ ] routing実行前の値保存
  - [ ] routing実行後の値復元
  - [ ] finally句による確実な復元
- [ ] `src/refinire/agents/pipeline/llm_pipeline.py` - evaluation用上書き防止
  - [ ] evaluation実行前後の値保護
  - [ ] 例外時の適切な復元

### Phase 2: 機能拡張・最適化 ⚡

#### 2.1 デバッグ・ログ機能
- [ ] shared_state保存時のデバッグログ追加
- [ ] routing/evaluation実行時の参照ログ追加
- [ ] 上書き防止の動作確認ログ

#### 2.2 エラーハンドリング強化
- [ ] shared_state未設定時のフォールバック処理
- [ ] プロンプト構築失敗時のエラー処理
- [ ] 上書き防止失敗時の警告

### Phase 3: テスト実装 ✅

#### 3.1 機能テスト作成
- [ ] `tests/test_prompt_result_management.py` - 新規作成
  - [ ] shared_state保存機能のテスト
  - [ ] routing用プロンプト構築テスト
  - [ ] evaluation用プロンプト構築テスト
  - [ ] 上書き防止機能のテスト

#### 3.2 統合テスト追加
- [ ] 既存routing/evaluationテストの更新
- [ ] マルチエージェント実行時のテスト
- [ ] 例外発生時の動作テスト

### Phase 4: ドキュメント・サンプル 📝

#### 4.1 サンプルコード作成
- [ ] `examples/prompt_result_management_example.py` - 新規作成
  - [ ] 基本的な使用例
  - [ ] routing/evaluation活用例
  - [ ] デバッグ用途での使用例

#### 4.2 ドキュメント更新
- [ ] 機能説明ドキュメントの作成
- [ ] shared_state使用規約の文書化
- [ ] トラブルシューティングガイド

## 実装チェックリスト

### Phase 1: コア機能実装 🔥

#### 1.1 shared_state自動保存機能
- [ ] `_execute_with_context`でのプロンプト保存実装
- [ ] `_execute_with_context`での生成結果保存実装
- [ ] 保存タイミングの検証

#### 1.2 Routing用プロンプト構築修正
- [ ] `_build_routing_prompt_with_context`実装
- [ ] shared_stateからの値取得処理
- [ ] プロンプトテンプレートの最適化

#### 1.3 Evaluation用プロンプト構築実装
- [ ] `_build_evaluation_prompt`メソッド新規作成
- [ ] evaluation実行フローへの組み込み
- [ ] プロンプトテンプレートの作成

#### 1.4 上書き防止機能実装
- [ ] routing実行での保存・復元処理
- [ ] evaluation実行での保存・復元処理
- [ ] 例外安全性の確保

## 完了基準

### Phase 1完了基準
- [ ] shared_stateに`_last_prompt`/`_last_generation`が正しく保存される
- [ ] routing/evaluationで値を正しく参照できる
- [ ] 上書き防止が正しく動作する

### Phase 2完了基準
- [ ] エラーハンドリングが適切に動作する
- [ ] デバッグログが有効に機能する
- [ ] パフォーマンスが許容範囲内

### Phase 3完了基準
- [ ] 全テストが通過する
- [ ] カバレッジが95%以上
- [ ] 既存機能に影響がない

### Phase 4完了基準
- [ ] サンプルコードが正常に動作する
- [ ] ドキュメントが完備されている
- [ ] 使用方法が明確に説明されている