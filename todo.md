# RefinireAgent コンテキスト管理機能実装計画

## 概要

RefinireAgentに高度なコンテキスト管理機能を段階的に実装し、AIエージェントが効率的かつ効果的に会話履歴、文脈情報、長期記憶を管理できるシステムを構築します。

## 実装目標

- **Phase 1**: 基本コンテキストプロバイダーの実装（カバレッジ60%以上）✅ **完了**
- **Phase 2**: 高度なコンテキストプロバイダーの実装
- **Phase 3**: 最適化と拡張

## Phase 1: 基本コンテキストプロバイダー 🚀 ✅ **完了**

### 1.0 SourceCodeProviderの実装 ✅
#### 1.0.1 基本機能の実装
- [x] `src/refinire/agents/providers/source_code.py` ファイル作成
- [x] `SourceCodeProvider` クラスの実装
  - [x] コードベース検索機能
  - [x] 関連ファイル特定機能
  - [x] ファイル内容抽出・整形機能
- [x] テストの実装（カバレッジ目標: 85%）

### 1.1 ContextProvider インターフェースの実装 ✅

#### 1.1.1 抽象基底クラスの作成
- [x] `src/refinire/agents/context_provider.py` ファイル作成
- [x] `ContextProvider` 抽象基底クラスの実装
  - [x] `provider_name` クラス変数の定義
  - [x] `get_config_schema()` クラスメソッドの実装
  - [x] `from_config()` クラスメソッドの実装
  - [x] `get_context()` 抽象メソッドの定義
  - [x] `update()` 抽象メソッドの定義
  - [x] `clear()` 抽象メソッドの定義
- [x] 型ヒントとドキュメント文字列の追加（英語・日本語）
- [x] `tests/test_context_provider.py` テストファイル作成
  - [x] インターフェースの基本動作テスト
  - [x] 設定スキーマ取得テスト
  - [x] 設定からのインスタンス作成テスト

#### 1.1.2 テストカバレッジ目標: 95% ✅

### 1.2 ConversationHistoryProviderの実装 ✅

#### 1.2.1 基本機能の実装
- [x] `src/refinire/agents/providers/conversation_history.py` ファイル作成
- [x] `ConversationHistoryProvider` クラスの実装
  - [x] `__init__()` メソッド（履歴リスト、最大アイテム数）
  - [x] `get_context()` メソッド（履歴の文字列化）
  - [x] `update()` メソッド（新しい対話の追加）
  - [x] `clear()` メソッド（履歴のクリア）
  - [x] `get_config_schema()` クラスメソッド
  - [x] `from_config()` クラスメソッド
- [x] 既存の`session_history`との統合ロジック
- [x] 最大履歴数の制限機能

#### 1.2.2 テストの実装 ✅
- [x] `tests/test_conversation_history_provider.py` テストファイル作成
  - [x] 基本動作テスト（履歴の追加・取得・クリア）
  - [x] 最大履歴数制限テスト
  - [x] 設定からのインスタンス作成テスト
  - [x] 空の履歴での動作テスト
  - [x] エラーハンドリングテスト

#### 1.2.3 テストカバレッジ目標: 90% ✅

### 1.3 FixedFileProviderの実装 ✅

#### 1.3.1 基本機能の実装
- [x] `src/refinire/agents/providers/fixed_file.py` ファイル作成
- [x] `FixedFileProvider` クラスの実装
  - [x] `__init__()` メソッド（ファイルパス、エンコーディング）
  - [x] `get_context()` メソッド（ファイル内容の読み込み）
  - [x] `update()` メソッド（ファイル変更の検出）
  - [x] `clear()` メソッド（キャッシュのクリア）
  - [x] `get_config_schema()` クラスメソッド
  - [x] `from_config()` クラスメソッド
- [x] ファイル存在チェック機能
- [x] エンコーディング対応（UTF-8、Shift_JIS等）
- [x] ファイル変更検出機能（オプション）

#### 1.3.2 テストの実装 ✅
- [x] `tests/test_fixed_file_provider.py` テストファイル作成
  - [x] 正常なファイル読み込みテスト
  - [x] 存在しないファイルのエラーハンドリングテスト
  - [x] 異なるエンコーディングのテスト
  - [x] 設定からのインスタンス作成テスト
  - [x] ファイル変更検出テスト（オプション）

#### 1.3.3 テストカバレッジ目標: 85% ✅

### 1.4 ContextProviderFactoryの実装 ✅

#### 1.4.1 ファクトリー機能の実装
- [x] `src/refinire/agents/context_provider_factory.py` ファイル作成
- [x] `ContextProviderFactory` クラスの実装
  - [x] `create_provider()` メソッド（設定からプロバイダー作成）
  - [x] `parse_config_string()` メソッド（YAMLライク文字列の解析）
  - [x] `validate_config()` メソッド（設定の検証）
  - [x] `get_available_providers()` クラスメソッド
- [x] YAMLライクな文字列解析機能
- [x] 設定検証機能
- [x] エラーハンドリング

#### 1.4.2 テストの実装 ✅
- [x] `tests/test_context_provider_factory.py` テストファイル作成
  - [x] 正常な設定文字列の解析テスト
  - [x] 不正な設定文字列のエラーハンドリングテスト
  - [x] 存在しないプロバイダーのエラーハンドリングテスト
  - [x] 設定検証テスト
  - [x] 利用可能プロバイダー取得テスト

#### 1.4.3 テストカバレッジ目標: 90% ✅

### 1.5 RefinireAgentの拡張 ✅

#### 1.5.1 コンストラクタの拡張
- [x] `src/refinire/agents/pipeline/llm_pipeline.py` の修正
  - [x] `context_providers_config` パラメータの追加
  - [x] `context_providers` インスタンス変数の追加
  - [x] `ContextProviderFactory` を使用したプロバイダー初期化
  - [x] 既存機能との互換性維持

#### 1.5.2 プロンプト構築の拡張
- [x] `_build_prompt()` メソッドの修正
  - [x] コンテキストプロバイダーからのコンテキスト取得
  - [x] コンテキスト連鎖機能の実装
  - [x] エラーハンドリング（プロバイダー失敗時の処理）
  - [x] 既存の履歴機能との統合
  - [x] Noneチェックによる堅牢性向上

#### 1.5.3 履歴更新の拡張
- [x] `_store_in_history()` メソッドの修正
  - [x] コンテキストプロバイダーの更新
  - [x] エラーハンドリング（更新失敗時の処理）

#### 1.5.4 新しいメソッドの追加
- [x] `clear_context()` メソッドの実装
- [x] `get_context_provider_schemas()` クラスメソッドの実装

#### 1.5.5 テストの実装 ✅
- [x] `tests/test_gen_agent_context.py` テストファイル作成
  - [x] コンテキストプロバイダー付きエージェントの作成テスト
  - [x] プロンプト構築のテスト
  - [x] 履歴更新のテスト
  - [x] コンテキストクリアのテスト
  - [x] 設定スキーマ取得のテスト
  - [x] エラーハンドリングのテスト

#### 1.5.6 テストカバレッジ目標: 80% ✅

### 1.6 統合テストの実装 ✅

#### 1.6.1 エンドツーエンドテスト
- [x] `tests/test_context_integration.py` テストファイル作成
  - [x] 複数プロバイダーの統合テスト
  - [x] YAMLライク文字列指定のテスト
  - [x] 実際のLLM呼び出しを含むテスト
  - [x] パフォーマンステスト

#### 1.6.2 テストカバレッジ目標: 75% ✅

### 1.7 ドキュメントの更新 🔄 **進行中**

#### 1.7.1 APIドキュメントの更新
- [ ] `docs/api_reference.md` の更新
  - [ ] ContextProvider インターフェースの説明
  - [ ] 各プロバイダーの説明
  - [ ] RefinireAgent の拡張機能の説明
- [ ] `docs/api_reference_ja.md` の更新

#### 1.7.2 使用例の追加 🔄 **次の優先タスク**
- [ ] `examples/context_management_example.py` の作成
  - [ ] 基本的な使用例
  - [ ] 複数プロバイダーの使用例
  - [ ] YAMLライク文字列指定の例
- [ ] 既存の`examples/context_management_basic.py`の改善
- [ ] 既存の`examples/context_management_advanced.py`の改善

#### 1.7.3 チュートリアルの更新
- [ ] `docs/tutorials/quickstart.md` の更新
- [ ] `docs/tutorials/quickstart_ja.md` の更新

### 1.8 CutContextProviderの実装 ✅
#### 1.8.1 基本機能の実装
- [x] `src/refinire/agents/providers/cut_context.py` ファイル作成
- [x] `CutContextProvider` クラスの実装
  - [x] 最大長指定によるコンテキスト自動カット機能
  - [x] 文字数・トークン数両対応
- [x] テストの実装（カバレッジ目標: 85%）

## Phase 2: 高度なコンテキストプロバイダー 🔥

### 2.1 SourceCodeProviderの実装 ✅ **既に完了**

#### 2.1.1 基本機能の実装
- [x] `src/refinire/agents/providers/source_code.py` ファイル作成
- [x] `SourceCodeProvider` クラスの実装
  - [x] コードベース検索機能
  - [x] 関連ファイル特定機能
  - [x] ファイル内容抽出・整形機能
- [x] テストの実装（カバレッジ目標: 85%）

### 2.2 ContextCompressorProviderの実装

#### 2.2.1 基本機能の実装
- [ ] `src/refinire/agents/providers/compressor.py` ファイル作成
- [ ] `ContextCompressorProvider` クラスの実装
  - [ ] コンテキスト圧縮機能
  - [ ] トークン数最適化機能
  - [ ] 重要情報保持機能
- [ ] テストの実装（カバレッジ目標: 80%）

### 2.3 ContextFilterProviderの実装

#### 2.3.1 基本機能の実装
- [ ] `src/refinire/agents/providers/filter.py` ファイル作成
- [ ] `ContextFilterProvider` クラスの実装
  - [ ] 関連性フィルタリング機能
  - [ ] 重複除去機能
  - [ ] 重要度選択機能
- [ ] テストの実装（カバレッジ目標: 85%）

### 2.4 LongTermMemoryProviderの実装

#### 2.4.1 基本機能の実装
- [ ] `src/refinire/agents/providers/long_term_memory.py` ファイル作成
- [ ] `LongTermMemoryProvider` クラスの実装
  - [ ] 永続的記憶機能
  - [ ] データベース統合機能
  - [ ] 検索・更新機能
- [ ] テストの実装（カバレッジ目標: 80%）

## Phase 3: 最適化と拡張 ⚡

### 3.1 パフォーマンス最適化

#### 3.1.1 キャッシュ機能の実装
- [ ] コンテキスト取得のキャッシュ機能
- [ ] 非同期処理の導入
- [ ] メモリ使用量の最適化

#### 3.1.2 テストの実装（カバレッジ目標: 75%）

### 3.2 ドキュメントの完全更新

#### 3.2.1 APIリファレンスの完全更新
- [ ] 全プロバイダーの詳細説明
- [ ] 使用例の充実
- [ ] トラブルシューティングガイド

#### 3.2.1 チュートリアルの充実
- [ ] 段階的な学習ガイド
- [ ] 実践的な使用例
- [ ] ベストプラクティス

## 全体のテストカバレッジ目標

### Phase 1完了時: 60%以上 ✅ **達成**
- ContextProvider インターフェース: 95% ✅
- ConversationHistoryProvider: 90% ✅
- FixedFileProvider: 85% ✅
- ContextProviderFactory: 90% ✅
- RefinireAgent拡張: 80% ✅
- 統合テスト: 75% ✅

### Phase 2完了時: 70%以上
- 新規プロバイダー: 80-85%
- 既存機能の拡張テスト

### Phase 3完了時: 80%以上
- パフォーマンステスト: 75%
- 包括的テストの充実

## 品質保証

### コード品質 ✅ **完了**
- [x] Type hints の完全対応
- [x] Docstring の英語・日本語併記
- [x] PEP 8 コーディング規約の遵守

### テスト品質 ✅ **完了**
- [x] 単体テストの充実
- [x] 統合テストの実装
- [x] エラーハンドリングのテスト
- [x] パフォーマンステストの実装

### ドキュメント品質 🔄 **進行中**
- [ ] API リファレンスの完全性
- [ ] 使用例の実用性
- [ ] チュートリアルの分かりやすさ
- [ ] トラブルシューティングの充実

## リスク管理

### 技術的リスク ✅ **対応完了**
- [x] 既存機能への影響の最小化
- [x] パフォーマンス劣化の防止
- [x] メモリ使用量の監視

### スケジュールリスク ✅ **対応完了**
- [x] 段階的な実装によるリスク分散
- [x] 各フェーズでの動作確認
- [x] 必要に応じた計画調整

## 完了基準

### Phase 1完了基準 ✅ **達成**
- [x] 基本コンテキストプロバイダーが正常動作
- [x] YAMLライク文字列指定が機能
- [x] 既存RefinireAgentとの互換性維持
- [x] テストカバレッジ60%以上達成
- [x] 基本的なドキュメント完成

### Phase 2完了基準
- [ ] 高度なコンテキストプロバイダーが実装
- [ ] コンテキスト連鎖機能が動作
- [ ] テストカバレッジ70%以上達成
- [ ] 実用的なユースケースに対応

### Phase 3完了基準
- [ ] パフォーマンスが最適化
- [ ] テストカバレッジ80%以上達成
- [ ] 包括的なドキュメント完成
- [ ] 本番環境での運用準備完了

## 次の優先タスク 🔄

### 1. ドキュメント更新（高優先度）
- [ ] APIリファレンスの更新
- [ ] 使用例の充実
- [ ] チュートリアルの更新

### 2. 使用例の改善（高優先度）
- [ ] `examples/context_management_basic.py`の改善
- [ ] `examples/context_management_advanced.py`の改善
- [ ] 新しい使用例の追加

### 3. Phase 2の準備
- [ ] ContextCompressorProviderの設計
- [ ] ContextFilterProviderの設計
- [ ] LongTermMemoryProviderの設計 