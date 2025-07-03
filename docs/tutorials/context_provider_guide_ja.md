# ContextProvider 完全ガイド - インテリジェントメモリシステムの構築

この包括的なガイドでは、RefinireのContextProviderアーキテクチャを説明し、専門的なAIエージェントメモリと情報アクセスパターンのためのカスタムコンテキストプロバイダーの作成方法を示します。

## ContextProviderアーキテクチャの理解

### ContextProviderとは？

ContextProviderは、会話中にAIエージェントに関連情報を自動的に提供するモジュラーコンポーネントです。これらは以下のことができるインテリジェントメモリシステムとして機能します：

- 会話履歴の維持
- ファイルコンテンツとソースコードへのアクセス
- データベースと外部APIのクエリ
- ドメイン固有情報の提供
- 関連性に基づいたコンテキストのフィルタリングと最適化

### 核となる設計原則

**モジュラー性**: 各プロバイダーは特定のタイプのコンテキスト（会話、ファイル、APIなど）を処理

**組み合わせ可能性**: 複数のプロバイダーを連鎖させて豊富なコンテキストを構築

**設定可能性**: プロバイダーはコード変更なしに宣言的に設定

**コンテキストチェーン**: プロバイダーは前のプロバイダーからコンテキストを受け取り、洗練された情報の階層化を可能にする

**エラー回復力**: プロバイダーの障害が全体のコンテキストシステムを破綻させない

## 組み込みContextProviderタイプ

### 1. ConversationHistoryProvider

自動履歴管理付きの会話メモリを管理します。

**目的**: 自然な対話継続のために最近の会話ターンを維持します。

**設定オプション**:
- `max_items` (int): 記憶する会話ターンの最大数（デフォルト: 10）

**使用例**:
- マルチターン会話
- コンテキスト認識応答
- 前回のトピックへの参照

**設定例**:
```python
context_config = [
    {
        "type": "conversation_history",
        "max_items": 15  # 最後の15回のやり取りを記憶
    }
]
```

### 2. FixedFileProvider

変更検出付きで特定ファイルからコンテンツを提供します。

**目的**: 特定のドキュメント、設定、または参照ファイルをコンテキストに含める。

**設定オプション**:
- `file_path` (str, 必須): ファイルへのパス
- `encoding` (str): ファイルエンコーディング（デフォルト: "utf-8"）
- `check_updates` (bool): ファイル変更を監視するか（デフォルト: True）

**使用例**:
- APIドキュメント
- プロジェクト仕様
- 設定参照
- ナレッジベース記事

**設定例**:
```python
context_config = [
    {
        "type": "fixed_file",
        "file_path": "docs/api_reference.md",
        "encoding": "utf-8"
    },
    {
        "type": "fixed_file", 
        "file_path": "config/project_guidelines.txt"
    }
]
```

### 3. SourceCodeProvider

会話トピックとファイル分析に基づいて関連ソースコードコンテキストを知的に選択・提供します。

**目的**: 会話トピックとファイル分析に基づいて関連ソースファイルを自動的に含める。

**設定オプション**:
- `base_path` (str): コード分析のベースディレクトリ（デフォルト: "."）
- `max_files` (int): 含める最大ファイル数（デフォルト: 50）
- `max_file_size` (int): バイト単位の最大ファイルサイズ（デフォルト: 10000）
- `file_extensions` (list): 含めるファイルタイプ
- `include_patterns` (list): 含めるファイルパターン
- `exclude_patterns` (list): 除外するファイルパターン

**使用例**:
- コードレビュー支援
- 開発ガイダンス
- バグ分析
- アーキテクチャ議論

**設定例**:
```python
context_config = [
    {
        "type": "source_code",
        "base_path": "src/",
        "max_files": 10,
        "file_extensions": [".py", ".js", ".ts"],
        "include_patterns": ["**/core/**", "**/utils/**"],
        "exclude_patterns": ["**/__pycache__/**", "**/node_modules/**"]
    }
]
```

### 4. CutContextProvider

コンテキストサイズ制限を自動的に管理するラッパープロバイダー。

**目的**: 重要な情報を保持しながらコンテキストがトークン/文字制限を超えないことを保証。

**設定オプション**:
- `provider` (dict): ラップされたプロバイダーの設定
- `max_chars` (int): 最大文字数
- `max_tokens` (int): 最大トークン数
- `cut_strategy` (str): 切り詰め方法（"start", "end", "middle"）
- `preserve_sections` (bool): 完全なセクションを保持するか

**使用例**:
- 大きなファイルの処理
- APIレスポンス管理
- メモリ最適化
- トークン制限への対応

**設定例**:
```python
context_config = [
    {
        "type": "cut_context",
        "provider": {
            "type": "fixed_file",
            "file_path": "large_document.md"
        },
        "max_chars": 5000,
        "cut_strategy": "middle",
        "preserve_sections": True
    }
]
```

## カスタムContextProviderの作成

### ステップ1: ContextProviderインターフェースの理解

すべてのカスタムプロバイダーは`ContextProvider`ベースクラスを継承し、以下の抽象メソッドを実装する必要があります：

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from refinire.agents.context_provider import ContextProvider

class CustomProvider(ContextProvider):
    provider_name = "custom_provider"  # 一意識別子
    
    def __init__(self, **config):
        """設定パラメータで初期化"""
        super().__init__()
        # 設定パラメータでプロバイダーを初期化
    
    @abstractmethod
    def get_context(self, query: str, previous_context: str = "", **kwargs) -> str:
        """
        ユーザークエリと前のコンテキストに基づいてコンテキストを生成
        
        Args:
            query: ユーザーの現在の入力/質問
            previous_context: チェーン内の前のプロバイダーからのコンテキスト
            **kwargs: 追加パラメータ
            
        Returns:
            str: プロンプトに追加するコンテキスト情報
        """
        pass
    
    @abstractmethod
    def update(self, interaction: Dict[str, Any]) -> None:
        """
        インタラクション結果でプロバイダー状態を更新
        
        Args:
            interaction: ユーザー入力、エージェントレスポンスなどを含む辞書
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """すべての保存状態/キャッシュをクリア"""
        pass
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """
        検証用の設定スキーマを返す
        
        Returns:
            期待される設定パラメータを記述する辞書
        """
        return {
            "type": "object",
            "properties": {
                # ここに設定パラメータを定義
            },
            "required": []  # 必須パラメータのリスト
        }
```

### ステップ2: 例 - DatabaseContextProvider

関連情報をデータベースに問い合わせるカスタムプロバイダーを作成しましょう：

```python
import sqlite3
from typing import Dict, Any, List
from refinire.agents.context_provider import ContextProvider

class DatabaseContextProvider(ContextProvider):
    provider_name = "database"
    
    def __init__(self, database_path: str, table_name: str, query_column: str = "content", 
                 limit: int = 5, **kwargs):
        super().__init__()
        self.database_path = database_path
        self.table_name = table_name
        self.query_column = query_column
        self.limit = limit
        self.connection = None
        self._connect()
    
    def _connect(self):
        """データベース接続を確立"""
        try:
            self.connection = sqlite3.connect(self.database_path)
            self.connection.row_factory = sqlite3.Row  # 名前によるカラムアクセスを有効化
        except Exception as e:
            raise RuntimeError(f"データベースへの接続に失敗しました: {e}")
    
    def _search_database(self, query: str) -> List[Dict[str, Any]]:
        """関連エントリをデータベースで検索"""
        if not self.connection:
            self._connect()
        
        # シンプルなキーワードベース検索（ベクトル検索、FTSなどで拡張可能）
        keywords = query.lower().split()
        search_conditions = " OR ".join([f"{self.query_column} LIKE ?" for _ in keywords])
        search_params = [f"%{keyword}%" for keyword in keywords]
        
        sql = f"""
            SELECT * FROM {self.table_name} 
            WHERE {search_conditions}
            ORDER BY rowid DESC
            LIMIT ?
        """
        
        cursor = self.connection.execute(sql, search_params + [self.limit])
        return [dict(row) for row in cursor.fetchall()]
    
    def get_context(self, query: str, previous_context: str = "", **kwargs) -> str:
        """関連データベースエントリをコンテキストとして取得"""
        try:
            results = self._search_database(query)
            
            if not results:
                return ""
            
            context_parts = ["=== データベース情報 ==="]
            
            for i, result in enumerate(results, 1):
                # データベース結果をコンテキスト用にフォーマット
                entry_text = f"エントリ {i}:\n"
                for key, value in result.items():
                    if value:  # 空の値はスキップ
                        entry_text += f"  {key}: {value}\n"
                context_parts.append(entry_text)
            
            return "\n".join(context_parts)
            
        except Exception as e:
            # エラーをログに記録するがコンテキストチェーンを壊さない
            print(f"データベースコンテキストプロバイダーエラー: {e}")
            return ""
    
    def update(self, interaction: Dict[str, Any]) -> None:
        """インタラクション結果で更新（データベースプロバイダーではオプション）"""
        # 成功したクエリをログ、検索ランキングの更新などが可能
        pass
    
    def clear(self) -> None:
        """キャッシュされたデータをクリア"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "database_path": {
                    "type": "string",
                    "description": "SQLiteデータベースファイルへのパス"
                },
                "table_name": {
                    "type": "string", 
                    "description": "クエリするデータベーステーブル"
                },
                "query_column": {
                    "type": "string",
                    "default": "content",
                    "description": "検索するカラム"
                },
                "limit": {
                    "type": "integer",
                    "default": 5,
                    "description": "返す最大結果数"
                }
            },
            "required": ["database_path", "table_name"]
        }
```

### ステップ3: 例 - APIContextProvider

外部APIから情報を取得するプロバイダーを作成：

```python
import requests
from typing import Dict, Any, Optional
import json
from refinire.agents.context_provider import ContextProvider

class APIContextProvider(ContextProvider):
    provider_name = "api"
    
    def __init__(self, base_url: str, api_key: str = "", headers: Dict[str, str] = None,
                 query_param: str = "q", max_results: int = 3, **kwargs):
        super().__init__()
        self.base_url = base_url
        self.api_key = api_key
        self.headers = headers or {}
        self.query_param = query_param
        self.max_results = max_results
        
        # APIキーが提供されている場合はヘッダーに追加
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def _make_api_request(self, query: str) -> Optional[Dict[str, Any]]:
        """クエリのためのAPIリクエストを作成"""
        try:
            params = {self.query_param: query, "limit": self.max_results}
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"APIリクエストに失敗しました: {e}")
            return None
    
    def _format_api_response(self, data: Dict[str, Any]) -> str:
        """APIレスポンスをコンテキスト用にフォーマット"""
        if not data:
            return ""
        
        context_parts = ["=== 外部情報 ==="]
        
        # APIレスポンス構造に基づいて調整
        results = data.get("results", [])
        if isinstance(results, list):
            for i, item in enumerate(results[:self.max_results], 1):
                if isinstance(item, dict):
                    title = item.get("title", f"結果 {i}")
                    content = item.get("content", item.get("description", ""))
                    if content:
                        context_parts.append(f"{title}:\n{content}\n")
        
        return "\n".join(context_parts)
    
    def get_context(self, query: str, previous_context: str = "", **kwargs) -> str:
        """クエリに基づいてAPIから情報を取得"""
        api_data = self._make_api_request(query)
        return self._format_api_response(api_data)
    
    def update(self, interaction: Dict[str, Any]) -> None:
        """インタラクション結果で更新"""
        # 成功したクエリのキャッシュ、使用統計の更新などが可能
        pass
    
    def clear(self) -> None:
        """キャッシュされたデータをクリア"""
        # 実装されている場合はリクエストキャッシュをクリア
        pass
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "base_url": {
                    "type": "string",
                    "description": "APIエンドポイントURL"
                },
                "api_key": {
                    "type": "string",
                    "description": "API認証キー"
                },
                "headers": {
                    "type": "object",
                    "description": "追加のHTTPヘッダー"
                },
                "query_param": {
                    "type": "string",
                    "default": "q",
                    "description": "クエリパラメータ名"
                },
                "max_results": {
                    "type": "integer",
                    "default": 3,
                    "description": "返す最大結果数"
                }
            },
            "required": ["base_url"]
        }
```

### ステップ4: カスタムプロバイダーの登録

RefinireAgentでカスタムプロバイダーを使用するには、ContextProviderFactoryに登録します：

```python
from refinire.agents.context_provider_factory import ContextProviderFactory

# カスタムプロバイダーを登録
ContextProviderFactory.register_provider("database", DatabaseContextProvider)
ContextProviderFactory.register_provider("api", APIContextProvider)

# エージェント設定で使用
from refinire import RefinireAgent

agent = RefinireAgent(
    name="enhanced_assistant",
    generation_instructions="提供されたコンテキストを使用して詳細な回答を提供してください。",
    context_providers_config=[
        {
            "type": "conversation_history",
            "max_items": 5
        },
        {
            "type": "database",
            "database_path": "knowledge.db",
            "table_name": "articles",
            "query_column": "content",
            "limit": 3
        },
        {
            "type": "api",
            "base_url": "https://api.example.com/search",
            "api_key": "your-api-key",
            "max_results": 2
        }
    ],
    model="gpt-4o-mini"
)
```

## 高度なContextProviderパターン

### 1. キャッシュとパフォーマンス最適化

```python
from functools import lru_cache
import hashlib
from typing import Dict, Any

class CachedContextProvider(ContextProvider):
    def __init__(self, cache_size: int = 100, **kwargs):
        super().__init__()
        self.cache_size = cache_size
        self._cache = {}
    
    def _cache_key(self, query: str) -> str:
        """クエリのキャッシュキーを生成"""
        return hashlib.md5(query.lower().encode()).hexdigest()
    
    @lru_cache(maxsize=100)
    def _expensive_operation(self, query: str) -> str:
        """キャッシュされた高コスト操作"""
        # ここに高コストなコンテキスト生成を実装
        pass
    
    def get_context(self, query: str, previous_context: str = "", **kwargs) -> str:
        cache_key = self._cache_key(query)
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = self._expensive_operation(query)
        self._cache[cache_key] = result
        return result
```

### 2. 条件付きコンテキストプロバイダー

```python
class ConditionalContextProvider(ContextProvider):
    def __init__(self, condition_func, true_provider, false_provider, **kwargs):
        super().__init__()
        self.condition_func = condition_func
        self.true_provider = true_provider
        self.false_provider = false_provider
    
    def get_context(self, query: str, previous_context: str = "", **kwargs) -> str:
        if self.condition_func(query, previous_context):
            return self.true_provider.get_context(query, previous_context, **kwargs)
        else:
            return self.false_provider.get_context(query, previous_context, **kwargs)
```

### 3. マルチソース集約プロバイダー

```python
class AggregatedContextProvider(ContextProvider):
    def __init__(self, providers: List[ContextProvider], aggregation_strategy: str = "concat", **kwargs):
        super().__init__()
        self.providers = providers
        self.aggregation_strategy = aggregation_strategy
    
    def get_context(self, query: str, previous_context: str = "", **kwargs) -> str:
        results = []
        
        for provider in self.providers:
            try:
                context = provider.get_context(query, previous_context, **kwargs)
                if context:
                    results.append(context)
            except Exception as e:
                continue  # 失敗したプロバイダーをスキップ
        
        if self.aggregation_strategy == "concat":
            return "\n\n".join(results)
        elif self.aggregation_strategy == "prioritized":
            return results[0] if results else ""
        # 必要に応じて他の集約戦略を追加
```

## カスタムContextProviderのベストプラクティス

### 1. エラーハンドリングと回復力

- 外部呼び出しは常にtry-catchブロックで囲む
- 例外を発生させるのではなく空の文字列を返す
- デバッグ用にエラーをログに記録するがコンテキストチェーンを壊さない
- 外部API呼び出しには適切なタイムアウトを実装

### 2. パフォーマンスの考慮事項

- 可能な場合は高コスト操作をキャッシュする
- 外部呼び出しには適切なタイムアウトを実装
- トークン制限を避けるために返すコンテキストの量を制限
- リソース集約的な操作には遅延読み込みを使用

### 3. 設定設計

- すべてのパラメータに妥当なデフォルトを提供
- 明確で説明的なパラメータ名を使用
- 包括的な設定スキーマを含める
- シンプルと高度な設定オプションの両方をサポート

### 4. コンテキスト品質

- ヘッダーと構造でコンテキストを明確にフォーマット
- 関連性に焦点を当てるために不要な情報を削除
- コンテキストの順序と優先度を考慮
- コンテキストがAIにとって実行可能で有用であることを確保

### 5. テストと検証

```python
import unittest
from unittest.mock import patch, MagicMock

class TestCustomContextProvider(unittest.TestCase):
    def setUp(self):
        self.provider = CustomContextProvider(
            # テスト設定
        )
    
    def test_get_context_success(self):
        """成功したコンテキスト取得のテスト"""
        result = self.provider.get_context("test query")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_get_context_failure(self):
        """適切な失敗処理のテスト"""
        with patch.object(self.provider, '_external_api_call', side_effect=Exception("API Error")):
            result = self.provider.get_context("test query")
            self.assertEqual(result, "")  # 例外ではなく空文字列を返すべき
    
    def test_configuration_validation(self):
        """設定スキーマ検証のテスト"""
        schema = self.provider.get_config_schema()
        self.assertIn("properties", schema)
        self.assertIn("required", schema)
```

## 統合例

### 複数のカスタムプロバイダーを持つ完全なエージェント

```python
from refinire import RefinireAgent
from your_providers import DatabaseContextProvider, APIContextProvider

# カスタムプロバイダーを登録
ContextProviderFactory.register_provider("database", DatabaseContextProvider)
ContextProviderFactory.register_provider("api", APIContextProvider)

# 豊富なコンテキストを持つエージェントを作成
agent = RefinireAgent(
    name="knowledge_assistant",
    generation_instructions="""
    あなたは複数の情報源にアクセス可能な知識豊富なアシスタントです。
    会話、データベース、外部APIから提供されるコンテキストを使用して
    包括的で正確な回答を提供してください。可能な場合は常に情報源を引用してください。
    """,
    context_providers_config=[
        # 最近の会話を記憶
        {
            "type": "conversation_history",
            "max_items": 10
        },
        # プロジェクトドキュメントを含める
        {
            "type": "fixed_file",
            "file_path": "docs/project_overview.md"
        },
        # 内部ナレッジベースをクエリ
        {
            "type": "database",
            "database_path": "knowledge_base.db",
            "table_name": "documents",
            "query_column": "content",
            "limit": 5
        },
        # 必要時に外部情報を取得
        {
            "type": "api",
            "base_url": "https://api.knowledge-source.com/search",
            "api_key": "your-api-key",
            "max_results": 3
        },
        # すべてをサイズ制限でラップ
        {
            "type": "cut_context",
            "provider": {
                "type": "source_code",
                "base_path": "src/",
                "max_files": 5
            },
            "max_chars": 8000,
            "cut_strategy": "middle"
        }
    ],
    model="gpt-4o-mini"
)

# 拡張エージェントを使用
result = agent.run("システムでユーザー認証を実装するにはどうすればよいですか？")
print(result.content)
```

この包括的なガイドは、洗練されたAIエージェントメモリと情報アクセスパターンのためのRefinireのContextProviderシステムを理解し拡張するために必要なすべてを提供します。