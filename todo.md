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