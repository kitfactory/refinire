"""
Routing system for RefinireAgent flow control.
RefinireAgent のフローコントロール用ルーティングシステム

This module provides the core routing functionality for the new flow control system,
including routing result data structures and related utilities.
このモジュールは新しいフローコントロールシステムの中核となるルーティング機能を提供します。
ルーティング結果のデータ構造と関連ユーティリティが含まれています。
"""

from typing import Union, Any, Dict, Optional, Type, Pattern
from pydantic import BaseModel, Field, field_validator
import re


class RoutingResult(BaseModel):
    """
    Standard output format for routing decisions.
    ルーティング判断の標準出力形式
    
    This class represents the result of a routing decision, containing both the
    generated content and routing information for the next step in the flow.
    このクラスはルーティング決定の結果を表し、生成されたコンテンツと
    フローの次のステップへのルーティング情報を含みます。
    
    Attributes:
        content: Generated content (custom type when output_model is specified, string otherwise)
                 生成されたコンテンツ（output_model指定時はその型、未指定時は文字列）
        next_route: Name of the next route to execute
                   次に実行するルート名
        confidence: Confidence level of the routing decision (0.0-1.0)
                   ルーティング判断の信頼度 (0.0-1.0)
        reasoning: Reason for the routing decision
                  ルーティング判断の理由
    """
    
    content: Union[str, Any] = Field(
        description="Generated content (custom type when output_model is specified, string otherwise)",
        examples=["Generated text content", {"task_result": "completed", "score": 0.85}]
    )
    
    next_route: str = Field(
        description="Name of the next route to execute",
        examples=["simple_processor", "complex_analyzer", "end", "retry", "complete"]
    )
    
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence level of the routing decision (0.0-1.0)",
        examples=[0.95, 0.78, 0.65]
    )
    
    reasoning: str = Field(
        description="Reason for the routing decision",
        examples=[
            "Content is sufficiently detailed, no additional processing needed",
            "コンテンツは十分に詳細で、追加処理は不要",
            "Partial information detected, requires expert agent processing",
            "部分的な情報のため、専門エージェントが必要"
        ]
    )
    
    @field_validator('next_route')
    @classmethod
    def validate_next_route(cls, v: str) -> str:
        """
        Validate the next_route field format.
        next_route フィールドの形式を検証
        
        Args:
            v: The next_route value to validate
        
        Returns:
            The validated next_route value
            
        Raises:
            ValueError: If the route name format is invalid
        """
        if not v:
            raise ValueError("next_route cannot be empty")
        
        # Check route name pattern: must start with letter, can contain letters, numbers, underscore, hyphen
        # ルート名パターンをチェック: 文字で始まり、文字、数字、アンダースコア、ハイフンを含むことができる
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', v):
            raise ValueError(
                f"Invalid route name format: '{v}'. "
                "Route names must start with a letter and contain only letters, numbers, underscores, and hyphens."
            )
        
        # Check maximum length
        # 最大長をチェック
        if len(v) > 50:
            raise ValueError(f"Route name too long: '{v}'. Maximum length is 50 characters.")
        
        return v
    
    @field_validator('reasoning')
    @classmethod
    def validate_reasoning(cls, v: str) -> str:
        """
        Validate the reasoning field.
        reasoning フィールドを検証
        
        Args:
            v: The reasoning value to validate
        
        Returns:
            The validated reasoning value
            
        Raises:
            ValueError: If the reasoning is invalid
        """
        if not v or not v.strip():
            raise ValueError("reasoning cannot be empty")
        
        # Check minimum and maximum length
        # 最小長と最大長をチェック
        if len(v.strip()) < 10:
            raise ValueError(f"Reasoning too short: minimum 10 characters required, got {len(v.strip())}")
        
        if len(v.strip()) > 500:
            raise ValueError(f"Reasoning too long: maximum 500 characters allowed, got {len(v.strip())}")
        
        return v.strip()


class RoutingConstraints:
    """
    Routing data constraint definitions.
    ルーティングデータの制約定義
    
    This class contains constants and patterns for validating routing data.
    このクラスはルーティングデータの検証用の定数とパターンを含みます。
    """
    
    # next_route constraints
    # next_route 制約
    VALID_ROUTE_PATTERN: Pattern[str] = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]*$')
    MAX_ROUTE_LENGTH: int = 50
    
    # confidence constraints
    # confidence 制約
    CONFIDENCE_MIN: float = 0.0
    CONFIDENCE_MAX: float = 1.0
    CONFIDENCE_PRECISION: int = 2
    
    # reasoning constraints
    # reasoning 制約
    MIN_REASONING_LENGTH: int = 10
    MAX_REASONING_LENGTH: int = 500
    
    # content_type constraints (for reference)
    # content_type 制約 (参考用)
    VALID_CONTENT_TYPES: set[str] = {
        "text", "json", "structured", "mixed", "unknown"
    }
    
    # complexity_level constraints (for reference)
    # complexity_level 制約 (参考用)
    VALID_COMPLEXITY_LEVELS: set[str] = {
        "simple", "moderate", "complex", "expert_level"
    }
    
    # completion_status constraints (for reference)
    # completion_status 制約 (参考用)
    VALID_COMPLETION_STATUSES: set[str] = {
        "complete", "partial", "needs_refinement", 
        "requires_validation", "failed", "unknown"
    }
    
    @classmethod
    def is_valid_route_name(cls, route_name: str) -> bool:
        """
        Check if a route name is valid.
        ルート名が有効かどうかをチェック
        
        Args:
            route_name: The route name to validate
        
        Returns:
            True if the route name is valid, False otherwise
        """
        if not route_name or len(route_name) > cls.MAX_ROUTE_LENGTH:
            return False
        
        return bool(cls.VALID_ROUTE_PATTERN.match(route_name))
    
    @classmethod
    def is_valid_confidence(cls, confidence: float) -> bool:
        """
        Check if a confidence value is valid.
        信頼度の値が有効かどうかをチェック
        
        Args:
            confidence: The confidence value to validate
        
        Returns:
            True if the confidence value is valid, False otherwise
        """
        return cls.CONFIDENCE_MIN <= confidence <= cls.CONFIDENCE_MAX
    
    @classmethod
    def is_valid_reasoning(cls, reasoning: str) -> bool:
        """
        Check if a reasoning string is valid.
        理由付けの文字列が有効かどうかをチェック
        
        Args:
            reasoning: The reasoning string to validate
        
        Returns:
            True if the reasoning is valid, False otherwise
        """
        if not reasoning or not reasoning.strip():
            return False
        
        length = len(reasoning.strip())
        return cls.MIN_REASONING_LENGTH <= length <= cls.MAX_REASONING_LENGTH


def create_routing_result_model(content_type: Type[BaseModel]) -> Type[BaseModel]:
    """
    Create a dynamic RoutingResult model with custom content type.
    カスタムコンテンツ型を持つ動的 RoutingResult モデルを作成
    
    This function creates a new RoutingResult class with the specified content type
    instead of the default Union[str, Any].
    この関数は、デフォルトの Union[str, Any] の代わりに指定されたコンテンツ型を持つ
    新しい RoutingResult クラスを作成します。
    
    Args:
        content_type: The Pydantic model class to use for the content field
    
    Returns:
        A new RoutingResult class with the specified content type
    
    Example:
        >>> from pydantic import BaseModel, Field
        >>> class TaskResult(BaseModel):
        ...     task: str
        ...     score: float
        >>> RoutingResultWithTaskResult = create_routing_result_model(TaskResult)
        >>> result = RoutingResultWithTaskResult(
        ...     content=TaskResult(task="completed", score=0.85),
        ...     next_route="complete",
        ...     confidence=0.9,
        ...     reasoning="Task completed successfully"
        ... )
    """
    from pydantic import create_model
    
    # Create fields dictionary with custom content type
    # カスタムコンテンツ型でフィールド辞書を作成
    fields = {
        'content': (content_type, Field(description="Generated content")),
        'next_route': (str, Field(description="Name of the next route to execute")),
        'confidence': (float, Field(ge=0.0, le=1.0, description="Confidence level of the routing decision")),
        'reasoning': (str, Field(description="Reason for the routing decision")),
    }
    
    # Create the dynamic model
    # 動的モデルを作成
    DynamicRoutingResult = create_model(
        'RoutingResult',
        **fields
    )
    
    # Copy validators from the original RoutingResult class if they exist
    # 元の RoutingResult クラスからバリデーターをコピー（存在する場合）
    if hasattr(RoutingResult, '__validators__'):
        DynamicRoutingResult.__validators__ = RoutingResult.__validators__.copy()
    
    return DynamicRoutingResult


# Default routing instructions for common use cases
# 一般的なユースケース用のデフォルトルーティング指示
DEFAULT_ROUTING_INSTRUCTIONS = {
    "simple": "コンテンツが完成していれば'end'、追加処理が必要なら'enhance'を選択",
    
    "quality_based": """
    品質基準で判断してください：
    - 高品質（85点以上）: 'publish'
    - 中品質（70-84点）: 'improve' 
    - 低品質（70点未満）: 'regenerate'
    """,
    
    "complexity_based": """
    複雑さに応じて判断：
    - 簡単な内容: 'simple_processor'
    - 中程度の内容: 'standard_processor'
    - 複雑な内容: 'expert_processor'
    """,
    
    "content_type_based": """
    コンテンツの種類に応じて選択：
    - テキスト形式: 'text_formatter'
    - データ形式: 'data_validator'
    - 混合形式: 'mixed_processor'
    """,
    
    "completion_based": """
    完了状態に応じて選択：
    - 完了: 'complete'
    - 部分的完了: 'continue'
    - 再試行が必要: 'retry'
    - 失敗: 'fallback'
    """
}