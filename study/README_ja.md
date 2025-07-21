# Refinire Study Samples（学習サンプル集）

このディレクトリには、Refinireフレームワークの学習と理解を助けるために厳選されたサンプルコードが含まれています。各ファイルは特定の機能とベストプラクティスを実演しています。

## はじめに

### 基本的な使用方法
1. **`refinire_simple.py`** - エラーハンドリング付きの最もシンプルな例
   - 基本的なRefinireAgent使用法
   - エラーハンドリングパターン
   - 初心者に最適な開始点

2. **`refinire_agent_basic_study.py`** - 基本機能の包括的なサンプル
   - RefinireAgentの設定
   - 生成と評価
   - 複数プロバイダー（OpenAI、Anthropic、Google）

### Flow（ワークフロー）の例
3. **`ultra_simple_flow.py`** - 最もシンプルなワークフロー（新機能！）
   - 超シンプルなSimpleFlow使用法
   - 最小コードで最大効果
   - 簡単ワークフローに最適

4. **`simple_flow_demo.py`** - 簡単ワークフロー作成（新機能！）
   - ビルダーパターン付きSimpleFlow
   - 3ステップコンテンツ作成ワークフロー
   - クリーンで読みやすい実装

5. **`flow_simple_clean.py`** - クリーンなFlow実装
   - シンプルなマルチステップワークフロー
   - Flowの使用方法のベストプラクティス
   - 明確なステップ定義

6. **`flow_sample.py`** - 複雑なワークフローの例
   - コンテンツ作成パイプライン
   - 複数エージェントの連携
   - 実世界のユースケース

7. **`flow_routing_sample.py`** - ルーティング付きFlow
   - Flow + RefinireAgent統合
   - ルーティング指示の使用
   - 動的フロー制御

### 高度な機能
8. **`advanced_features_demo.py`** - 高度機能の統合
   - ルーティング指示
   - 高速モード
   - Flow組み合わせ
   - 複数プロバイダー使用

9. **`fast_mode_sample.py`** - 高性能モード
   - 高速モード設定
   - パフォーマンス比較
   - 高速モードの使用タイミング

10. **`routing_instruction_sample.py`** - コンテンツルーティング
    - 基本的なルーティング機能
    - 分類の例
    - ルートベース処理

### 特殊な例
11. **`code_generation_routing.py`** - ルーティング付きコード生成
    - AI駆動コード生成
    - 複雑度評価
    - 品質アセスメント

12. **`code_generation_simple.py`** - シンプルコード生成（新機能！）
    - SimpleFlowベースコード生成
    - 簡単3ステップワークフロー
    - 複雑度評価と推奨事項

13. **`processing_with_routing.py`** - 品質分類
    - 処理結果の分類
    - 品質評価ルーティング
    - 多層処理

14. **`refinire_agent_tools_study.py`** - ツール統合
    - 外部ツール使用
    - ツール呼び出しパターン
    - 関数統合

### 比較と分析
15. **`compare_direct_vs_refinire.py`** - フレームワーク比較
    - 直接OpenAI Agents SDK vs Refinire
    - 利点の実演
    - 移行ガイダンス

### 監視とデバッグ
16. **`tracing_study.py`** - トレーシングと監視
    - 実行トレーシング
    - パフォーマンス監視
    - デバッグ機能

## 使用方法

1. **依存関係のインストール**: Refinireとすべての依存関係をインストール
   ```bash
   pip install -e .[dev]
   ```

2. **環境変数の設定**: APIキーを設定
   ```bash
   export OPENAI_API_KEY="your-key"
   export ANTHROPIC_API_KEY="your-key"
   ```

3. **サンプルの実行**: 任意のサンプルファイルを実行
   ```bash
   python study/refinire_simple.py
   ```

## 学習パス

### 初心者向けパス
1. `refinire_simple.py`から開始
2. `refinire_agent_basic_study.py`に進む
3. `flow_simple_clean.py`を試す
4. `fast_mode_sample.py`で実験

### 中級者向けパス
1. `flow_sample.py`を学習
2. `routing_instruction_sample.py`を理解
3. `processing_with_routing.py`を探索
4. `refinire_agent_tools_study.py`を試す

### 上級者向けパス
1. `advanced_features_demo.py`をマスター
2. `code_generation_routing.py`を学習
3. `compare_direct_vs_refinire.py`を分析
4. `tracing_study.py`で監視を活用

## 実演されている主要概念

- **RefinireAgent**: コアエージェント機能
- **Flow**: マルチステップワークフロー編成
- **ルーティング指示**: 動的コンテンツルーティング
- **高速モード**: 高性能実行
- **ツール統合**: 外部関数呼び出し
- **マルチプロバイダーサポート**: OpenAI、Anthropic、Google
- **エラーハンドリング**: 堅牢なエラー管理
- **トレーシング**: 実行監視

各サンプルは自己完結型で、主要概念と実装詳細を説明するコメントが含まれています。