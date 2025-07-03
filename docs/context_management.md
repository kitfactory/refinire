# コンテキスト管理設計書

## 概要

RefinireAgentのコンテキスト管理機能は、AIエージェントが効率的かつ効果的に会話履歴、文脈情報、長期記憶を管理し、適切なコンテキストをLLMに提供するためのシステムです。

## Contextとルーティングの関係

### Contextオブジェクトとは

FlowにおけるContextは、ステップ間でデータを共有し、状態を管理するための中核的なオブジェクトです。RefinireAgentの実行結果はContextに保存され、後続のステップや条件分岐で利用されます。

```python
from refinire import Context, Flow, ConditionStep, RefinireAgent

# Contextオブジェクトの基本構造
ctx = Context()
ctx.result            # 現在のステップの結果
ctx.shared_state      # ステップ間で共有される状態
ctx.evaluation_result # RefinireAgentの評価結果
ctx.prev_outputs      # 前のエージェントの出力
```

### ルーティングにおけるContextの活用

RefinireAgentの結果に基づいてルーティングを設定するには、ConditionStepと組み合わせて使用します：

```python
# 1. RefinireAgentによる分析
analyzer = RefinireAgent(
    name="content_analyzer",
    generation_instructions="入力内容を分析して以下のいずれかで回答: 技術的、ビジネス、一般的",
    model="gpt-4o-mini"
)

# 2. Contextの結果に基づくルーティング関数
def route_by_content_type(ctx):
    """RefinireAgentの結果に基づいてルーティング"""
    analysis_result = str(ctx.result).lower()
    if "技術的" in analysis_result:
        return "technical_handler"
    elif "ビジネス" in analysis_result:
        return "business_handler"
    else:
        return "general_handler"

# 3. Flowでの統合
routing_flow = Flow({
    "analyze": analyzer,
    "route": ConditionStep("route", route_by_content_type, 
                          {"technical_handler": "technical", 
                           "business_handler": "business", 
                           "general_handler": "general"}),
    "technical": RefinireAgent(name="tech_expert", generation_instructions="技術的な回答を提供"),
    "business": RefinireAgent(name="business_expert", generation_instructions="ビジネス視点で回答"),
    "general": RefinireAgent(name="general_assistant", generation_instructions="一般的な回答を提供")
})
```

### 評価結果を使ったルーティング

RefinireAgentの評価機能を活用したルーティングも可能です：

```python
# 評価機能付きRefinireAgent
quality_agent = RefinireAgent(
    name="quality_analyzer",
    generation_instructions="内容を分析してください",
    evaluation_instructions="分析の品質を0-100で評価してください",
    threshold=75.0,
    model="gpt-4o-mini"
)

# 評価スコアに基づくルーティング
def route_by_quality(ctx):
    """評価スコアに基づくルーティング"""
    if hasattr(ctx, 'evaluation_result') and ctx.evaluation_result:
        score = ctx.evaluation_result.get('score', 0)
        return score >= 85  # 85点以上なら高品質ルート
    return False

quality_flow = Flow({
    "analyze": quality_agent,
    "quality_check": ConditionStep("quality_check", route_by_quality, "high_quality", "needs_improvement"),
    "high_quality": RefinireAgent(name="publisher", generation_instructions="承認済みとして処理"),
    "needs_improvement": RefinireAgent(name="reviewer", generation_instructions="改善提案を提供")
})
```

## 設計原則

### 極限まで絞った設計思想

1. **単一責任**: 各クラスは一つの役割のみを持つ
2. **最小限のインターフェース**: 必要最小限のメソッドのみ
3. **直感的な統合**: RefinireAgentへの変更を最小限に
4. **拡張しやすい**: 新しい機能の追加が容易
5. **理解しやすい**: 複雑な抽象化を避ける
6. **文字列指定**: YAMLライクな文字列で直感的に設定
7. **コンテキスト連鎖**: 前のプロバイダーのコンテキストに依存する動作をサポート

## 現在の実装状況

### 既存のコンテキスト管理機能

| 機能 | 実装状況 | 説明 |
|------|----------|------|
| セッション履歴 | ✅ 実装済み | `session_history`で会話履歴を管理 |
| 履歴サイズ制限 | ✅ 実装済み | `history_size`で履歴の最大数を制限 |
| パイプライン履歴 | ✅ 実装済み | `_pipeline_history`で詳細な実行履歴を管理 |
| プロンプト構築 | ✅ 実装済み | `_build_prompt`で指示文と履歴を組み合わせ |

### 現在の制限事項

1. **単純な履歴管理**: 時系列順の単純な履歴のみ
2. **コンテキスト圧縮なし**: 長い会話でコンテキスト長を超過する可能性
3. **文脈関連性の考慮なし**: 現在の質問に関連する履歴の選択機能なし
4. **外部情報の統合なし**: ファイル、ソースコード、長期記憶の統合機能なし

## コンテキスト管理ケース

### 1. 会話履歴の管理

**目的**: 過去の会話を現在のコンテキストに追加

**ユースケース**:
- 以前の会話で決定した内容を参照
- 継続的なプロジェクトの文脈を維持
- ユーザーの好みや設定の記憶

### 2. 固定ファイルの統合

**目的**: 特定のファイル内容を常にコンテキストに含める

**ユースケース**:
- プロジェクトの設定ファイル
- システムの仕様書
- ユーザーのプロフィール情報

### 3. ソースコードの検索

**目的**: 現在の会話に関連するソースコードを自動検索

**ユースケース**:
- コードレビューの際の関連ファイル参照
- バグ修正時の関連コード特定
- 機能追加時の既存実装確認

### 4. 長期記憶の統合

**目的**: 永続的な記憶システムとの統合

**ユースケース**:
- ユーザーの学習履歴
- プロジェクトの重要な決定事項
- システムの設定変更履歴

### 5. コンテキスト圧縮

**目的**: モデルのコンテキスト長に合わせてコンテキストを圧縮

**ユースケース**:
- 長い会話履歴の要約
- 重要な情報の抽出
- トークン数の最適化

### 6. コンテキストフィルタリング

**目的**: 前のプロバイダーのコンテキストを基にフィルタリング

**ユースケース**:
- 関連性の低いコンテキストの除去
- 重要度に基づくコンテキスト選択
- 重複コンテキストの除去

## 極限まで絞ったAPI設計

### ContextProvider インターフェース（唯一のインターフェース）

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, ClassVar, Optional

class ContextProvider(ABC):
    """Single interface for all context providers
    すべてのコンテキストプロバイダーの唯一のインターフェース
    """
    
    # Class variable for provider name
    # プロバイダー名のクラス変数
    provider_name: ClassVar[str] = "base"
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Get configuration schema for this provider
        このプロバイダーの設定スキーマを取得
        
        Returns:
            Dict[str, Any]: Configuration schema with parameter descriptions
            Dict[str, Any]: パラメータ説明を含む設定スキーマ
        """
        return {
            "description": "Base context provider",
            "parameters": {},
            "example": "base: {}"
        }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'ContextProvider':
        """Create provider instance from configuration
        設定からプロバイダーインスタンスを作成
        
        Args:
            config: Configuration dictionary / 設定辞書
            
        Returns:
            ContextProvider: Provider instance / プロバイダーインスタンス
        """
        return cls(**config)
    
    @abstractmethod
    def get_context(self, query: str, previous_context: Optional[str] = None, **kwargs) -> str:
        """Get context for the given query
        与えられたクエリ用のコンテキストを取得
        
        Args:
            query: Current user query / 現在のユーザークエリ
            previous_context: Context provided by previous providers / 前のプロバイダーが提供したコンテキスト
            **kwargs: Additional parameters / 追加パラメータ
            
        Returns:
            str: Context string (empty string if no context) / コンテキスト文字列（コンテキストがない場合は空文字列）
        """
        pass
    
    @abstractmethod
    def update(self, interaction: Dict[str, Any]) -> None:
        """Update provider with new interaction
        新しい対話でプロバイダーを更新
        
        Args:
            interaction: Interaction data / 対話データ
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all stored context
        保存されたすべてのコンテキストをクリア
        """
        pass
```

## 具体的な実装

### ConversationHistoryProvider

```python
from typing import List, Dict, Any, ClassVar, Optional

class ConversationHistoryProvider(ContextProvider):
    """Provides conversation history context
    会話履歴コンテキストを提供
    """
    
    provider_name: ClassVar[str] = "conversation"
    
    def __init__(self, history: List[str] = None, max_items: int = 10):
        self.history = history or []
        self.max_items = max_items
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Get configuration schema for conversation history provider
        会話履歴プロバイダーの設定スキーマを取得
        """
        return {
            "description": "Provides conversation history context",
            "parameters": {
                "max_items": {
                    "type": "int",
                    "default": 10,
                    "description": "Maximum number of conversation items to keep"
                }
            },
            "example": """
conversation:
  max_items: 5
            """.strip()
        }
    
    def get_context(self, query: str, previous_context: Optional[str] = None, **kwargs) -> str:
        """Get relevant conversation history
        関連する会話履歴を取得
        """
        if not self.history:
            return ""
        
        # Simple implementation: return recent history
        recent_history = self.history[-self.max_items:]
        return "\n".join(recent_history)
    
    def update(self, interaction: Dict[str, Any]) -> None:
        """Add new interaction to history
        新しい対話を履歴に追加
        """
        user_input = interaction.get("user_input", "")
        result = interaction.get("result", "")
        
        if user_input and result:
            entry = f"User: {user_input}\nAssistant: {result}"
            self.history.append(entry)
            
            # Keep only recent items
            if len(self.history) > self.max_items:
                self.history = self.history[-self.max_items:]
    
    def clear(self) -> None:
        """Clear conversation history
        会話履歴をクリア
        """
        self.history.clear()
```

### FixedFileProvider

```python
class FixedFileProvider(ContextProvider):
    """Provides fixed file content as context
    固定ファイルの内容をコンテキストとして提供
    """
    
    provider_name: ClassVar[str] = "fixed_file"
    
    def __init__(self, file_path: str, description: str = ""):
        self.file_path = file_path
        self.description = description
        self._content = ""
        self._load_content()
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Get configuration schema for fixed file provider
        固定ファイルプロバイダーの設定スキーマを取得
        """
        return {
            "description": "Provides fixed file content as context",
            "parameters": {
                "file_path": {
                    "type": "str",
                    "required": True,
                    "description": "Path to the file to include in context"
                },
                "description": {
                    "type": "str",
                    "default": "",
                    "description": "Description of the file content"
                }
            },
            "example": """
fixed_file:
  file_path: "project_config.json"
  description: "Project Configuration"
            """.strip()
        }
    
    def _load_content(self) -> None:
        """Load file content
        ファイル内容を読み込み
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self._content = f.read()
        except Exception as e:
            self._content = f"Error loading file: {e}"
    
    def get_context(self, query: str, previous_context: Optional[str] = None, **kwargs) -> str:
        """Get fixed file content
        固定ファイルの内容を取得
        """
        if not self._content:
            return ""
        
        context = f"Fixed Context ({self.description}):\n{self._content}"
        return context
    
    def update(self, interaction: Dict[str, Any]) -> None:
        """Reload file content
        ファイル内容を再読み込み
        """
        self._load_content()
    
    def clear(self) -> None:
        """Clear file content
        ファイル内容をクリア
        """
        self._content = ""
```

### SourceCodeProvider

```python
import os
from typing import List, ClassVar, Optional

class SourceCodeProvider(ContextProvider):
    """Provides relevant source code as context
    関連するソースコードをコンテキストとして提供
    """
    
    provider_name: ClassVar[str] = "source_code"
    
    def __init__(self, codebase_path: str = "./src", max_files: int = 5):
        self.codebase_path = codebase_path
        self.max_files = max_files
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Get configuration schema for source code provider
        ソースコードプロバイダーの設定スキーマを取得
        """
        return {
            "description": "Provides relevant source code as context",
            "parameters": {
                "codebase_path": {
                    "type": "str",
                    "default": "./src",
                    "description": "Path to the codebase to search"
                },
                "max_files": {
                    "type": "int",
                    "default": 5,
                    "description": "Maximum number of files to include"
                }
            },
            "example": """
source_code:
  codebase_path: "./src"
  max_files: 3
            """.strip()
        }
    
    def get_context(self, query: str, previous_context: Optional[str] = None, **kwargs) -> str:
        """Get relevant source code
        関連するソースコードを取得
        """
        relevant_files = self._find_relevant_files(query)
        
        if not relevant_files:
            return ""
        
        context_parts = ["Relevant Source Code:"]
        for file_path in relevant_files[:self.max_files]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    context_parts.append(f"File: {file_path}\n{content}")
            except Exception:
                continue
        
        return "\n\n".join(context_parts)
    
    def _find_relevant_files(self, query: str) -> List[str]:
        """Find files relevant to the query
        クエリに関連するファイルを検索
        """
        relevant_files = []
        search_terms = query.lower().split()
        
        for root, dirs, files in os.walk(self.codebase_path):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.h')):
                    file_path = os.path.join(root, file)
                    file_lower = file.lower()
                    
                    if any(term in file_lower for term in search_terms):
                        relevant_files.append(file_path)
        
        return relevant_files
    
    def update(self, interaction: Dict[str, Any]) -> None:
        """No update needed for source code provider
        ソースコードプロバイダーでは更新は不要
        """
        pass
    
    def clear(self) -> None:
        """No clear needed for source code provider
        ソースコードプロバイダーではクリアは不要
        """
        pass
```

### ContextCompressorProvider

```python
import re
from typing import ClassVar, Optional

class ContextCompressorProvider(ContextProvider):
    """Compresses context to fit within token limits
    トークン制限内に収めるためにコンテキストを圧縮
    """
    
    provider_name: ClassVar[str] = "compressor"
    
    def __init__(self, max_tokens: int = 8000, compression_ratio: float = 0.7):
        self.max_tokens = max_tokens
        self.compression_ratio = compression_ratio
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Get configuration schema for context compressor provider
        コンテキスト圧縮プロバイダーの設定スキーマを取得
        """
        return {
            "description": "Compresses context to fit within token limits",
            "parameters": {
                "max_tokens": {
                    "type": "int",
                    "default": 8000,
                    "description": "Maximum number of tokens to allow"
                },
                "compression_ratio": {
                    "type": "float",
                    "default": 0.7,
                    "description": "Compression ratio (0.0 to 1.0)"
                }
            },
            "example": """
compressor:
  max_tokens: 6000
  compression_ratio: 0.8
            """.strip()
        }
    
    def get_context(self, query: str, previous_context: Optional[str] = None, **kwargs) -> str:
        """Compress previous context to fit within token limits
        前のコンテキストをトークン制限内に収めるように圧縮
        """
        if not previous_context:
            return ""
        
        # Simple token estimation (rough approximation)
        estimated_tokens = len(previous_context.split()) * 1.3
        
        if estimated_tokens <= self.max_tokens:
            return previous_context
        
        # Compress context by keeping important parts
        compressed_context = self._compress_context(previous_context)
        return compressed_context
    
    def _compress_context(self, context: str) -> str:
        """Compress context by keeping important parts
        重要な部分を保持してコンテキストを圧縮
        """
        lines = context.split('\n')
        compressed_lines = []
        
        # Keep first and last parts, compress middle
        if len(lines) <= 10:
            return context
        
        # Keep first 30% and last 30%
        first_count = int(len(lines) * 0.3)
        last_count = int(len(lines) * 0.3)
        
        compressed_lines.extend(lines[:first_count])
        compressed_lines.append("... (compressed content) ...")
        compressed_lines.extend(lines[-last_count:])
        
        return '\n'.join(compressed_lines)
    
    def update(self, interaction: Dict[str, Any]) -> None:
        """No update needed for compressor provider
        圧縮プロバイダーでは更新は不要
        """
        pass
    
    def clear(self) -> None:
        """No clear needed for compressor provider
        圧縮プロバイダーではクリアは不要
        """
        pass
```

### ContextFilterProvider

```python
import re
from typing import ClassVar, Optional, List

class ContextFilterProvider(ContextProvider):
    """Filters context based on relevance to query
    クエリとの関連性に基づいてコンテキストをフィルタリング
    """
    
    provider_name: ClassVar[str] = "filter"
    
    def __init__(self, relevance_threshold: float = 0.3, max_sections: int = 5):
        self.relevance_threshold = relevance_threshold
        self.max_sections = max_sections
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Get configuration schema for context filter provider
        コンテキストフィルタープロバイダーの設定スキーマを取得
        """
        return {
            "description": "Filters context based on relevance to query",
            "parameters": {
                "relevance_threshold": {
                    "type": "float",
                    "default": 0.3,
                    "description": "Minimum relevance score to keep context"
                },
                "max_sections": {
                    "type": "int",
                    "default": 5,
                    "description": "Maximum number of context sections to keep"
                }
            },
            "example": """
filter:
  relevance_threshold: 0.5
  max_sections: 3
            """.strip()
        }
    
    def get_context(self, query: str, previous_context: Optional[str] = None, **kwargs) -> str:
        """Filter previous context based on relevance to query
        クエリとの関連性に基づいて前のコンテキストをフィルタリング
        """
        if not previous_context:
            return ""
        
        # Split context into sections
        sections = self._split_into_sections(previous_context)
        
        # Calculate relevance for each section
        relevant_sections = []
        for section in sections:
            relevance = self._calculate_relevance(section, query)
            if relevance >= self.relevance_threshold:
                relevant_sections.append((section, relevance))
        
        # Sort by relevance and keep top sections
        relevant_sections.sort(key=lambda x: x[1], reverse=True)
        filtered_sections = [section for section, _ in relevant_sections[:self.max_sections]]
        
        return '\n\n'.join(filtered_sections)
    
    def _split_into_sections(self, context: str) -> List[str]:
        """Split context into logical sections
        コンテキストを論理的なセクションに分割
        """
        # Split by double newlines or section headers
        sections = re.split(r'\n\s*\n', context)
        return [section.strip() for section in sections if section.strip()]
    
    def _calculate_relevance(self, section: str, query: str) -> float:
        """Calculate relevance score between section and query
        セクションとクエリの間の関連性スコアを計算
        """
        query_words = set(query.lower().split())
        section_words = set(section.lower().split())
        
        if not query_words:
            return 0.0
        
        # Simple word overlap calculation
        overlap = len(query_words.intersection(section_words))
        return overlap / len(query_words)
    
    def update(self, interaction: Dict[str, Any]) -> None:
        """No update needed for filter provider
        フィルタープロバイダーでは更新は不要
        """
        pass
    
    def clear(self) -> None:
        """No clear needed for filter provider
        フィルタープロバイダーではクリアは不要
        """
        pass
```

## コンテキストプロバイダーファクトリー

### ContextProviderFactory

```python
import yaml
from typing import List, Dict, Any, Type
from .context_providers import (
    ConversationHistoryProvider,
    FixedFileProvider,
    SourceCodeProvider,
    ContextCompressorProvider,
    ContextFilterProvider
)

class ContextProviderFactory:
    """Factory for creating context providers from configuration
    設定からコンテキストプロバイダーを作成するファクトリー
    """
    
    _providers: Dict[str, Type[ContextProvider]] = {
        "conversation": ConversationHistoryProvider,
        "fixed_file": FixedFileProvider,
        "source_code": SourceCodeProvider,
        "compressor": ContextCompressorProvider,
        "filter": ContextFilterProvider,
    }
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[ContextProvider]) -> None:
        """Register a new context provider
        新しいコンテキストプロバイダーを登録
        """
        cls._providers[name] = provider_class
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, Dict[str, Any]]:
        """Get available providers and their schemas
        利用可能なプロバイダーとそのスキーマを取得
        """
        schemas = {}
        for name, provider_class in cls._providers.items():
            schemas[name] = provider_class.get_config_schema()
        return schemas
    
    @classmethod
    def create_from_yaml(cls, yaml_config: str) -> List[ContextProvider]:
        """Create context providers from YAML configuration string
        YAML設定文字列からコンテキストプロバイダーを作成
        """
        try:
            config = yaml.safe_load(yaml_config)
            return cls.create_from_config(config)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    @classmethod
    def create_from_config(cls, config: List[Dict[str, Any]]) -> List[ContextProvider]:
        """Create context providers from configuration list
        設定リストからコンテキストプロバイダーを作成
        """
        providers = []
        
        for item in config:
            if not isinstance(item, dict):
                raise ValueError(f"Invalid configuration item: {item}")
            
            for provider_name, provider_config in item.items():
                if provider_name not in cls._providers:
                    raise ValueError(f"Unknown provider: {provider_name}")
                
                provider_class = cls._providers[provider_name]
                provider = provider_class.from_config(provider_config or {})
                providers.append(provider)
        
        return providers
```

## RefinireAgentへの統合

### RefinireAgentの拡張

RefinireAgentのコンストラクタに`context_providers_config`パラメータを追加し、YAMLライクな文字列でコンテキストプロバイダーを指定できるようにします。

```python
from typing import List, Optional, Union
from .pipeline.llm_pipeline import RefinireAgent, LLMResult
from .context_provider_factory import ContextProviderFactory

class RefinireAgent:
    """
    Refinire Agent - AI agent with automatic evaluation and tool integration
    Refinireエージェント - 自動評価とツール統合を備えたAIエージェント
    """
    
    def __init__(
        self,
        name: str,
        generation_instructions: str,
        evaluation_instructions: Optional[str] = None,
        *,
        model: str = "gpt-4o-mini",
        evaluation_model: Optional[str] = None,
        output_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: float = 30.0,
        threshold: float = 85.0,
        max_retries: int = 3,
        input_guardrails: Optional[List[Callable[[str], bool]]] = None,
        output_guardrails: Optional[List[Callable[[Any], bool]]] = None,
        session_history: Optional[List[str]] = None,
        history_size: int = 10,
        improvement_callback: Optional[Callable[[LLMResult, EvaluationResult], str]] = None,
        locale: str = "en",
        tools: Optional[List[Callable]] = None,
        mcp_servers: Optional[List[str]] = None,
        context_providers: Optional[List[ContextProvider]] = None,
        context_providers_config: Optional[str] = None  # 新規追加
    ) -> None:
        """
        Initialize Refinire Agent
        Refinireエージェントを初期化する
        
        Args:
            name: Agent name / エージェント名
            generation_instructions: Instructions for generation / 生成用指示
            evaluation_instructions: Instructions for evaluation / 評価用指示
            model: OpenAI model name / OpenAIモデル名
            evaluation_model: Model for evaluation / 評価用モデル
            output_model: Pydantic model for structured output / 構造化出力用Pydanticモデル
            temperature: Sampling temperature / サンプリング温度
            max_tokens: Maximum tokens / 最大トークン数
            timeout: Request timeout / リクエストタイムアウト
            threshold: Evaluation threshold / 評価閾値
            max_retries: Maximum retry attempts / 最大リトライ回数
            input_guardrails: Input validation functions / 入力検証関数
            output_guardrails: Output validation functions / 出力検証関数
            session_history: Session history / セッション履歴
            history_size: History size limit / 履歴サイズ制限
            improvement_callback: Callback for improvement suggestions / 改善提案コールバック
            locale: Locale for messages / メッセージ用ロケール
            tools: OpenAI function tools / OpenAI関数ツール
            mcp_servers: MCP server identifiers / MCPサーバー識別子
            context_providers: List of context providers / コンテキストプロバイダーリスト
            context_providers_config: YAML-like string configuration for context providers / コンテキストプロバイダー用のYAMLライクな文字列設定
        """
        # 既存の初期化処理...
        
        # Context providers initialization
        # コンテキストプロバイダーの初期化
        if context_providers_config:
            self.context_providers = ContextProviderFactory.create_from_yaml(context_providers_config)
        else:
            self.context_providers = context_providers or []
        
        # OpenAI Agents SDK Agentを初期化
        self._sdk_agent = Agent(
            name=f"{name}_sdk_agent",
            instructions=self.generation_instructions,
            tools=self.tools
        )
    
    @classmethod
    def get_context_provider_schemas(cls) -> Dict[str, Dict[str, Any]]:
        """Get available context provider schemas
        利用可能なコンテキストプロバイダーのスキーマを取得
        """
        return ContextProviderFactory.get_available_providers()
    
    def _build_prompt(self, user_input: str, include_instructions: bool = True) -> str:
        """
        Build complete prompt with instructions, history, and context providers
        指示、履歴、コンテキストプロバイダーを含む完全なプロンプトを構築
        
        Args:
            user_input: User input / ユーザー入力
            include_instructions: Whether to include instructions (for OpenAI Agents SDK, set to False)
            include_instructions: 指示文を含めるかどうか（OpenAI Agents SDKの場合はFalse）
        """
        prompt_parts = []
        
        # Add instructions only if requested (not for OpenAI Agents SDK)
        # 要求された場合のみ指示文を追加（OpenAI Agents SDKの場合は除く）
        if include_instructions:
            prompt_parts.append(self.generation_instructions)
        
        # Add context from context providers with chaining
        # コンテキストプロバイダーからコンテキストを連鎖的に追加
        current_context = ""
        for provider in self.context_providers:
            try:
                context = provider.get_context(user_input, previous_context=current_context, agent_name=self.name)
                if context:
                    current_context = context
            except Exception as e:
                logger.warning(f"Context provider {provider.__class__.__name__} failed: {e}")
        
        if current_context:
            prompt_parts.append("Context:\n" + current_context)
        
        # Add history if available (existing functionality)
        # 履歴が利用可能な場合は追加（既存機能）
        if self.session_history:
            history_text = "\n".join(self.session_history[-self.history_size:])
            prompt_parts.append(f"Previous context:\n{history_text}")
        
        prompt_parts.append(f"User input: {user_input}")
        
        return "\n\n".join(prompt_parts)
    
    def _store_in_history(self, user_input: str, result: LLMResult) -> None:
        """Store interaction in history and update context providers
        対話を履歴に保存し、コンテキストプロバイダーを更新
        """
        # Existing history storage logic
        # 既存の履歴保存ロジック
        interaction = {
            "user_input": user_input,
            "result": result.content,
            "success": result.success,
            "metadata": result.metadata,
            "timestamp": json.dumps({"pipeline": self.name}, ensure_ascii=False)
        }
        
        self._pipeline_history.append(interaction)
        
        # Add to session history for context
        session_entry = f"User: {user_input}\nAssistant: {result.content}"
        self.session_history.append(session_entry)
        
        # Trim history if needed
        if len(self.session_history) > self.history_size:
            self.session_history = self.session_history[-self.history_size:]
        
        # Update context providers
        # コンテキストプロバイダーを更新
        for provider in self.context_providers:
            try:
                provider.update(interaction)
            except Exception as e:
                logger.warning(f"Failed to update context provider {provider.__class__.__name__}: {e}")
    
    def clear_context(self) -> None:
        """Clear all context providers
        すべてのコンテキストプロバイダーをクリア
        """
        for provider in self.context_providers:
            try:
                provider.clear()
            except Exception as e:
                logger.warning(f"Failed to clear context provider {provider.__class__.__name__}: {e}")
```

## 使用例

### YAMLライクな文字列指定（コンテキスト連鎖）

```python
# YAMLライクな文字列でコンテキストプロバイダーを指定（連鎖的な処理）
context_config = """
- conversation:
    max_items: 10
- source_code:
    codebase_path: "./src"
    max_files: 5
- filter:
    relevance_threshold: 0.4
    max_sections: 3
- compressor:
    max_tokens: 6000
    compression_ratio: 0.8
"""

agent = RefinireAgent(
    name="AdvancedContextAgent",
    generation_instructions="You are a coding assistant with intelligent context management.",
    context_providers_config=context_config
)

result = agent.run("How should I implement the new feature?")
```

### 基本的な使用例

```python
# 会話履歴プロバイダー付きエージェント
context_config = """
- conversation:
    max_items: 5
"""

agent = RefinireAgent(
    name="HistoryAwareAgent",
    generation_instructions="You are a helpful assistant with conversation history.",
    context_providers_config=context_config
)

result = agent.run("What did we discuss about the project?")
```

### 既存のRefinireAgentとの互換性

```python
# 既存の使用方法（コンテキストプロバイダーなし）
agent = RefinireAgent(
    name="SimpleAgent",
    generation_instructions="You are a helpful assistant."
)

# 新しい使用方法（YAMLライクな文字列指定）
context_config = """
- conversation:
    max_items: 5
"""

agent = RefinireAgent(
    name="EnhancedAgent",
    generation_instructions="You are a helpful assistant.",
    context_providers_config=context_config
)
```

### 利用可能なプロバイダーの確認

```python
# 利用可能なコンテキストプロバイダーとその設定スキーマを確認
schemas = RefinireAgent.get_context_provider_schemas()
for provider_name, schema in schemas.items():
    print(f"Provider: {provider_name}")
    print(f"Description: {schema['description']}")
    print(f"Parameters: {schema['parameters']}")
    print(f"Example:\n{schema['example']}")
    print()
```

## 実装計画

### Phase 1: 基本コンテキストプロバイダー
- [ ] ContextProvider インターフェースの実装
- [ ] ConversationHistoryProviderの実装
- [ ] FixedFileProviderの実装
- [ ] ContextProviderFactoryの実装
- [ ] RefinireAgentのコンストラクタ拡張

### Phase 2: 高度なコンテキストプロバイダー
- [ ] SourceCodeProviderの実装
- [ ] ContextCompressorProviderの実装
- [ ] ContextFilterProviderの実装
- [ ] LongTermMemoryProviderの実装

### Phase 3: 最適化と拡張
- [ ] パフォーマンス最適化
- [ ] テストケースの作成
- [ ] ドキュメントの更新

## まとめ

この設計により、RefinireAgentは以下の機能を獲得します：

1. **直感的な設定**: YAMLライクな文字列でコンテキストプロバイダーを指定
2. **後方互換性**: 既存のRefinireAgentとの互換性を維持
3. **柔軟なコンテキスト管理**: 複数のコンテキストソースを統合
4. **自動更新**: 対話時にコンテキストプロバイダーも自動更新
5. **拡張しやすい**: 新しいコンテキストプロバイダーの簡単な追加
6. **設定スキーマ**: 各プロバイダーの設定方法を明確に定義
7. **コンテキスト連鎖**: 前のプロバイダーのコンテキストに依存する動作をサポート

この設計により、RefinireAgentは必要最小限の変更で高度なコンテキスト管理機能を獲得でき、直感的な文字列指定の利点も維持できます。 