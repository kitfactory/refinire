# 実装TODO

- [x] AnthropicModel の async テストを作成する
- [x] GeminiModel の async テストを作成する
- [x] OllamaModel のテストを作成する
- [x] AgentPipeline の `_build_generation_prompt` メソッドのテストを作成する
- [x] AgentPipeline の `_build_evaluation_prompt` メソッドのテストを作成する
- [x] 評価が閾値未満の場合の `improvements_callback` の動作テストを作成する
- [x] ガードレール機能（Guardrails）統合テストを作成する
- [x] ツール統合のテストを作成する
- [x] ダイナミックプロンプト機能のテストを作成する
- [x] ルーティング機能のテストを作成する
- [x] コードカバレッジを90%以上に向上させる
- [x] examples フォルダ内のスクリプトを動作検証する
- [x] docs フォルダ内のドキュメントの整合性を確認・更新する

## docs/ APIリファレンス & チュートリアル構築（MkDocs Material）
- [x] MkDocs Material をプロジェクトに開発環境に導入する
- [x] mkdocs.yml 設定ファイルを作成し、サイト構成を設計する
- [x] docs/index.md にプロジェクト概要・導入方法を記載する
- [x] docs/api_reference.md に主要クラス・関数のAPIリファレンスを記載する
- [x] docs/tutorials/ ディレクトリを作成し、チュートリアル記事（例：クイックスタート、応用例）を追加する
- [x] コードブロックや図（PlantUML等）を活用し、分かりやすいドキュメントにする
- [x] mkdocs serve でローカルプレビューし、表示・リンク切れ等を確認する
- [x] 完成したらGitにコミット・プッシュする

## 粒度の確認

- 上記のステップは対象ファイルと対象機能が明確であり、現状の粒度で十分です。

# TODO

- [x] OpenAI Agents SDK標準Tracerの無効化方法を調査する
- [x] set_tracing_disabledの挙動を確認し、ソースコード上で依存箇所を特定する
- [x] 独自TracingProcessorに必要な要件を整理する
- [x] 独自TracingProcessorのインターフェース設計を行う
  - [x] トレース入力フォーマットを定義する
  - [x] トレース出力フォーマットを定義する
- [x] 独自TracingProcessorの機能クラスを実装する
- [x] 独自TracingProcessorのテストを作成し、機能を検証する
- [x] set_tracing_disabledと独自TracingProcessorを組み合わせて動作確認を行う
- [x] トレース表示の簡易UI/CLIコンポーネントを設計・実装する
- [x] pytestを実行し、すべてのテストがパスすることを確認する
- [x] 全体の動作テストを実行し、問題がないことを確認する

## 粒度確認
各ステップは単一責務に基づき、末端機能のテスト作成→実装→結合テストの順で実行可能な粒度に細分化しています。

## 調査結果
- `set_tracing_disabled`はGLOBAL_TRACE_PROVIDER.set_disabledを呼び出し、トレースの有効/無効を切り替える。
- デフォルトTraceProcessor(`default_processor`)はimport時にGLOBAL_TRACE_PROVIDERに登録されている。
- 標準Tracerを無効化し、独自Processorを使用するには`set_trace_processors`でProcessorリストを置き換える必要がある。
- 依存箇所: `src/agents_sdk_models/llm.py`、examplesディレクトリ内の各スクリプト。

## 要件整理
- `on_trace_start`, `on_trace_end`, `on_span_start`, `on_span_end`, `shutdown`, `force_flush`のすべてのメソッドを実装すること
- デフォルトProcessor(`default_processor`)への依存を排除し、OpenAIへの通信を行わないこと
- コンソールやファイルなど、出力先を設定可能にすること
- トレースおよびスパン情報を開始時刻、終了時刻、ID、親子関係を含む読みやすいフォーマットで出力すること
- 例外を投げず、安全に動作すること
- アプリケーション終了時に`force_flush`を必ず呼び出すこと
- 並列実行や高頻度呼び出しに耐えうる性能を確保すること
- テスト可能性を考慮し、出力を検証できること
- 他の機能に影響を与えない設計とすること

## 次フェーズ: TracingProcessor拡張タスク
- [x] `todo.md`に計画をチェックリスト形式で追加・更新し、タスクの進捗を管理する
- [x] SDKの`llm.get_llm`で`set_tracing_disabled`を呼び出し、依存箇所を特定する
- [x] `TracingProcessor`インターフェースを確認し、独自Processorの要件を整理する
- [x] `src/agents_sdk_models/tracing_processor.py`に`ConsoleTracingProcessor`スケルトンを作成する
- [x] クラスドキュメントにトレース／スパンの入出力フォーマットを定義する
- [x] `ConsoleTracingProcessor`に`on_trace_start`、`on_trace_end`、`on_span_start`、`on_span_end`、`shutdown`、`force_flush`を実装する
- [x] テスト（`tests/test_tracing_processor.py`、`tests/test_tracing_integration.py`）を作成し、正常動作および`set_tracing_disabled`時の無効化を検証する
- [x] `pyproject.toml`のTOML構文エラー（`Bug Tracker`キー）を修正する
- [x] `examples/simple_llm_query.py`と`examples/pipeline_trace_example.py`を追加する
- [x] CLIコンポーネント`examples/trace_cli.py`を実装する
- [x] `ConsoleTracingProcessor`に`simple_mode`を追加し、ANSIカラーで`SPAN START`、`Input`、`Output`、`SPAN END`を表示する
- [x] ユーザー入力やプロンプト、実際のLLMレスポンス本文のみをカラー出力するよう改良する
- [x] `PipelineTracingProcessor`を定義し、`Runner.run_sync`をモンキーパッチしてプロンプトを捕捉し、生成と評価のinstruction、prompt、outputを一貫して表示する
- [x] `PipelineTracingProcessor`の`on_trace_start`/`on_trace_end`で単一のSpanにまとめて色分け表示する方法を示唆する

- [ ] ConsoleTracingProcessorの最終レビュー
  - [ ] ANSIカラー表示の動作検証（Span開始・終了、Instruction/Prompt/Output）
  - [ ] コードコメント・ドキュメントの整備
- [ ] PipelineTracingProcessorの重複表示防止ロジックのテスト作成
  - [ ] 正常系テストケースの追加
  - [ ] エッジケース（カスタムスパン含む）の動作確認
- [ ] DialogProcessorのユニットテスト実装
  - [ ] モックAgentPipelineを用いた入力・出力検証
  - [ ] 異常系テスト（入力なし、空リストなど）の作成
- [ ] examplesディレクトリのスクリプト動作確認
  - [ ] simple_llm_query.pyの動作検証
  - [ ] 他例スクリプトの動作検証
- [ ] docsフォルダにドキュメント作成
  - [ ] 要件定義書(requirements.md)の作成
  - [ ] アーキテクチャ設計書(architecture.md)の作成
  - [ ] 機能仕様書(function_spec.md)の作成
- [ ] README.mdとREADME_ja.mdの作成
  - [ ] README.md（英語、絵文字・サポート環境・メリット訴求）
  - [ ] README_ja.md（日本語のみ）
- [ ] pyproject.tomlの依存確認と調整
- [ ] 仮想環境(.venv)下でpytest実行による全体動作確認

## AgentPipeline Deprecation Plan（v0.0.22〜v0.1.0）

### フェーズ 1: Deprecation Warning追加 (v0.0.22) ✅ 完了
- [x] AgentPipelineクラスにdeprecation warningを追加
- [x] Deprecation計画文書の作成 (docs/deprecation_plan.md)
- [x] README.mdでFlow/Stepアーキテクチャを推奨として記載
- [x] AgentPipelineクラスの文書にdeprecated注記を追加

### フェーズ 2: Examples移行 (v0.0.23)
- [x] genagent_simple_generation.py - 基本的な生成例の移行版
- [x] genagent_with_evaluation.py - 評価機能付きの移行版
- [x] genagent_with_tools.py - ツール使用例の移行版
- [x] genagent_with_guardrails.py - ガードレール使用例の移行版
- [x] genagent_with_history.py - 履歴管理例の移行版
- [x] genagent_with_retry.py - リトライ機能例の移行版
- [x] genagent_with_dynamic_prompt.py - 動的プロンプト例の移行版
- [ ] 新しいFlow/Step使用例の充実
- [ ] 移行ガイドの完成

### フェーズ 3: テスト移行 (v0.0.24) ✅ 完了
- [x] AgentPipelineのテストをGenAgentベースに移行
  - [x] test_pipeline.py → test_gen_agent_compatibility.py
  - [x] test_pipeline_*.py系統の移行
- [x] 後方互換性テストの追加
- [x] GenAgentの完全なテストカバレッジ

#### 完了したテストファイル:
- ✅ test_gen_agent_compatibility.py (377行) - 8つの互換性テスト
- ✅ test_gen_agent_comprehensive.py (306行) - 12の包括的テスト
- ✅ 全テスト成功: 20+ tests passed, 適切なdeprecation warning動作確認

### フェーズ 4: 完全削除 (v0.1.0)
- [ ] AgentPipelineクラスの完全削除
- [ ] 関連するimportとexportの削除
- [ ] ドキュメントのクリーンアップ
- [ ] pipeline_*系のexamplesファイルの削除

## 実装済み機能

### Core クラス ✅ 完了
- [x] GenAgent: AgentPipelineのStepインターフェース実装
- [x] GenAgentの包括的テストスイート（99%カバレッジ）
- [x] create_simple_gen_agent, create_evaluated_gen_agent ユーティリティ関数

### Flow/Step システム ✅ 完了
- [x] Flow: ワークフロー管理クラス
- [x] Step: 基底ステップクラス
- [x] Context: ステップ間の状態共有
- [x] 包括的なFlow/Stepテストスイート

### 移行サポート ✅ 完了
- [x] Migration文書 (docs/deprecation_plan.md)
- [x] README.mdでの新アーキテクチャ推奨
- [x] Deprecation warningの実装

## 技術的詳細

### GenAgent の主な機能
- AgentPipelineをStepとして使用可能
- Flow内での非同期実行サポート
- コンテキスト共有による状態管理
- 完全なエラーハンドリング
- 評価機能の統合サポート

### 後方互換性
- AgentPipelineは引き続き動作（v0.1.0まで）
- Deprecation warningの表示
- 既存コードの段階的移行サポート

## 次のステップ

1. 残りのexample移行（フェーズ2完了）
2. テスト移行計画の策定
3. v0.0.23リリース準備
4. v0.1.0での完全削除準備

## 基本機能の実装

### 基本アーキテクチャ
- [x] Stepクラスの設計と実装
- [x] Flowクラスの設計と実装
- [x] Contextクラスの設計と実装
- [x] Pipelineクラスの設計と実装
- [x] LLMクラスの設計と実装

### LLMバックエンド
- [x] OpenAI APIクライアントの実装
- [x] Anthropic APIクライアントの実装
- [x] Gemini APIクライアントの実装
- [x] Ollama APIクライアントの実装

### 基本エージェント
- [x] GenAgentの実装
- [x] ClarifyAgentの実装
- [x] GenAgentLegacyの削除（不要な機能）

### パイプライン拡張
- [x] LLMPipelineの実装
- [x] InteractivePipelineの実装
- [x] パイプライン統合テスト

## 新規エージェント実装

### agentsフォルダの作成
- [x] `src/agents_sdk_models/agents/` フォルダ作成
- [x] `agents/__init__.py` 作成
- [x] 各エージェントの基底クラス設計

### 高優先度エージェント実装

#### RouterAgent
- [x] RouterAgentクラスの設計
- [x] ルーティングロジックの実装
- [x] 分類器インターフェースの定義
- [x] RouterAgentのテスト作成
- [x] RouterAgentの使用例作成

#### ValidatorAgent
- [x] ValidatorAgentクラスの設計
- [x] 検証ルールシステムの実装
- [x] 標準検証ルールの実装
- [x] ValidatorAgentのテスト作成
- [x] ValidatorAgentの使用例作成

#### ExtractorAgent
- [x] ExtractorAgentクラスの設計
- [x] パターンベース抽出の実装
- [x] LLMベース抽出の実装
- [x] 抽出ルールシステムの実装
- [x] ExtractorAgentのテスト作成
- [x] ExtractorAgentの使用例作成

#### NotificationAgent
- [x] NotificationAgentクラスの設計
- [x] 通知チャネルシステムの実装
- [x] 標準通知チャネルの実装（メール、Slack、Webhook）
- [x] NotificationAgentのテスト作成
- [x] NotificationAgentの使用例作成

### 中優先度エージェント実装

#### ClassifierAgent
- [ ] ClassifierAgentクラスの設計
- [ ] 分類アルゴリズムの実装
- [ ] ClassifierAgentのテスト作成
- [ ] ClassifierAgentの使用例作成

#### TransformerAgent
- [ ] TransformerAgentクラスの設計
- [ ] データ変換システムの実装
- [ ] TransformerAgentのテスト作成
- [ ] TransformerAgentの使用例作成

#### AggregatorAgent
- [ ] AggregatorAgentクラスの設計
- [ ] データ集約システムの実装
- [ ] AggregatorAgentのテスト作成
- [ ] AggregatorAgentの使用例作成

#### SearchAgent
- [ ] SearchAgentクラスの設計
- [ ] 検索システムの実装
- [ ] SearchAgentのテスト作成
- [ ] SearchAgentの使用例作成

## 統合とテスト

### パッケージ統合
- [ ] `__init__.py` でのエクスポート設定
- [ ] 依存関係の整理
- [ ] 型ヒントの完成

### テストカバレッジ
- [ ] 全エージェントの単体テスト
- [ ] エージェント間連携テスト
- [ ] エンドツーエンドテスト

### ドキュメント
- [ ] 各エージェントのAPIドキュメント
- [ ] 使用例とチュートリアル
- [ ] agents.mdの更新

## 品質保証

### コード品質
- [ ] Linting (flake8, black)
- [ ] 型チェック (mypy)
- [ ] セキュリティチェック

### パフォーマンス
- [ ] ベンチマークテスト
- [ ] メモリ使用量の最適化
- [ ] 並行処理の最適化

## リリース準備

### パッケージング
- [ ] pyproject.tomlの更新
- [ ] バージョン管理
- [ ] パッケージ配布準備

### ドキュメント
- [ ] README.mdの更新
- [ ] CHANGELOG.mdの作成
- [ ] API仕様書の完成

## 完了項目

### ✅ 基本機能実装完了
- Stepクラス実装
- Flowクラス実装
- Contextクラス実装
- Pipelineクラス実装
- LLMクラス実装

### ✅ LLMバックエンド完了
- OpenAI APIクライアント
- Anthropic APIクライアント
- Gemini APIクライアント
- Ollama APIクライアント

### ✅ 基本エージェント完了
- GenAgent実装
- ClarifyAgent実装
- GenAgentLegacy削除

### ✅ パイプライン拡張完了
- LLMPipeline実装
- InteractivePipeline実装
- パイプライン統合テスト

### ✅ ドキュメント整備
- agents.mdの体系的整理
- ExtractorAgentの責務明確化

### ✅ Flow可視化機能完了
- Flow.show()メソッドの実装（Mermaid/テキスト形式）
- RouterAgentの複数ルート表示対応
- get_possible_routes()メソッド
- 実行履歴表示機能
- Flow.show()のテストスイート（11テストケース）
- Flow.show()の使用例とデモ 