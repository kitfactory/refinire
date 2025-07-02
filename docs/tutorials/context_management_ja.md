# コンテキスト管理機能チュートリアル

このチュートリアルでは、Refinireのコンテキスト管理機能の使用方法を段階的に説明します。

## 目次

1. [基本概念](#基本概念)
2. [基本的な使用方法](#基本的な使用方法)
3. [コンテキストプロバイダーの種類](#コンテキストプロバイダーの種類)
4. [高度な設定](#高度な設定)
5. [実用的な例](#実用的な例)
6. [ベストプラクティス](#ベストプラクティス)

## 基本概念

コンテキスト管理機能は、AIエージェントがより適切な応答を生成するために必要な情報を自動的に提供するシステムです。

### 主な特徴

- **会話履歴の管理**: 過去の対話を適切に保持・管理
- **ファイルコンテキスト**: 関連ファイルの内容を自動的に提供
- **ソースコード検索**: ユーザーの質問に関連するコードを自動検索
- **コンテキスト圧縮**: 長いコンテキストを適切なサイズに圧縮
- **動的選択**: 状況に応じて最適なコンテキストを選択

## 基本的な使用方法

### 1. シンプルな設定

```python
from refinire.agents.pipeline import RefinireAgent

# 基本的なコンテキスト設定
context_config = [
    {
        "type": "conversation_history",
        "max_items": 5,
        "max_tokens": 1000
    }
]

agent = RefinireAgent(
    model="gpt-3.5-turbo",
    context_providers_config=context_config
)
```

### 2. 複数のプロバイダーを使用

```python
context_config = [
    {
        "type": "conversation_history",
        "max_items": 5
    },
    {
        "type": "fixed_file",
        "file_path": "README.md"
    },
    {
        "type": "source_code",
        "max_files": 3,
        "max_file_size": 500
    }
]
```

## コンテキストプロバイダーの種類

### 1. ConversationHistoryProvider

会話履歴を管理するプロバイダーです。

```python
{
    "type": "conversation_history",
    "max_items": 10        # 保持するメッセージ数
}
```

### 2. FixedFileProvider

指定されたファイルの内容を常に提供するプロバイダーです。

```python
{
    "type": "fixed_file",
    "file_path": "config.yaml"
}
```

### 3. SourceCodeProvider

ユーザーの質問に関連するソースコードを自動検索するプロバイダーです。

```python
{
    "type": "source_code",
    "max_files": 5,                    # 最大ファイル数
    "max_file_size": 1000              # ファイルあたりの最大サイズ（バイト）
}
```

### 4. CutContextProvider

コンテキストを指定された長さに圧縮するプロバイダーです。

```python
{
    "type": "cut_context",
    "provider": {
        "type": "source_code",
        "max_files": 10,
        "max_file_size": 2000
    },
    "max_chars": 3000,           # 最大文字数
    "cut_strategy": "middle",     # 圧縮戦略 (start/end/middle)
    "preserve_sections": True     # セクションを保持
}
```

## 高度な設定

### 1. 文字列ベース設定

YAMLライクな文字列で設定を記述できます。

```python
string_config = """
- type: conversation_history
  max_items: 5
- type: source_code
  max_files: 3
  max_file_size: 500
"""

agent = RefinireAgent(
    model="gpt-3.5-turbo",
    context_providers_config=string_config
)
```

### 2. 連鎖的処理

プロバイダーは前のプロバイダーのコンテキストを受け取って処理できます。

```python
context_config = [
    {
        "type": "source_code",
        "max_files": 10,
        "max_file_size": 2000
    },
    {
        "type": "cut_context",
        "provider": {
            "type": "source_code",
            "max_files": 10,
            "max_file_size": 2000
        },
        "max_chars": 3000,
        "cut_strategy": "middle"
    }
]
```

## 実用的な例

### 1. コードレビュー支援

```python
context_config = [
    {
        "type": "source_code",
        "max_files": 10,
        "max_file_size": 2000
    },
    {
        "type": "fixed_file",
        "file_path": "CONTRIBUTING.md"
    },
    {
        "type": "conversation_history",
        "max_items": 5
    }
]
```

agent = RefinireAgent(
    name="CodeReviewAgent",
    generation_instructions="コードレビューを行い、品質、ベストプラクティス、エラーハンドリング、パフォーマンス、ドキュメントの完全性を評価してください。",
    model="gpt-4",
    context_providers_config=context_config
)

response = await agent.run_async("このコードの品質をレビューしてください")
```

### 2. ドキュメント生成

```python
context_config = [
    {
        "type": "source_code",
        "max_files": 15,
        "max_file_size": 1500
    },
    {
        "type": "cut_context",
        "provider": {
            "type": "source_code",
            "max_files": 15,
            "max_file_size": 1500
        },
        "max_chars": 4000,
        "cut_strategy": "start"
    }
]
```

agent = RefinireAgent(
    name="DocRefinireAgent",
    generation_instructions="提供されたソースコードと既存のドキュメントに基づいて、包括的で構造化されたドキュメントを生成してください。",
    model="gpt-4",
    context_providers_config=context_config
)

response = await agent.run_async("APIドキュメントを生成してください")
```

### 3. デバッグ支援

```python
context_config = [
    {
        "type": "source_code",
        "max_files": 8,
        "max_file_size": 1000
    },
    {
        "type": "conversation_history",
        "max_items": 10
    }
]
```

agent = RefinireAgent(
    name="DebugAgent",
    generation_instructions="エラーの原因を調査し、解決策を提供してください。",
    model="gpt-4",
    context_providers_config=context_config
)

response = await agent.run_async("このエラーの原因を調べてください")
```

## ベストプラクティス

### 1. プロバイダーの順序

1. **情報収集プロバイダー** (source_code, fixed_file)
2. **処理プロバイダー** (cut_context, filter)
3. **履歴プロバイダー** (conversation_history)

### 2. 適切なサイズ設定

- **max_files**: 3-10個程度
- **max_file_size**: 500-2000バイト程度
- **max_chars**: 1000-3000文字程度

### 3. エラーハンドリング

```python
try:
    response = await agent.run_async("質問")
except Exception as e:
    print(f"エラーが発生しました: {e}")
    # コンテキストをクリアして再試行
    agent.clear_context()
```

### 4. パフォーマンス最適化

- 不要なプロバイダーは削除
- 適切なサイズ制限を設定
- キャッシュを活用

## トラブルシューティング

### よくある問題

1. **ファイルが見つからない**
   - ファイルパスが正しいか確認
   - 相対パスと絶対パスの使い分け

2. **コンテキストが長すぎる**
   - CutContextProviderを使用
   - サイズ制限を調整

3. **関連ファイルが検索されない**
   - SourceCodeProviderの設定を確認
   - ファイル名の類似性を調整

### デバッグ方法

```python
# 利用可能なプロバイダーのスキーマを確認
schemas = agent.get_context_provider_schemas()
for schema in schemas:
    print(f"- {schema['name']}: {schema['description']}")

# コンテキストをクリア
agent.clear_context()
```

## 次のステップ

- [APIリファレンス](../api_reference_ja.md)で詳細な仕様を確認
- [使用例](../../examples/)で実際のコードを参考
- [アーキテクチャ設計書](../architecture.md)でシステム全体を理解 