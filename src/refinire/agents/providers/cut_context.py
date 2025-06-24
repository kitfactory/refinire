"""
Cut Context Provider for RefinireAgent
RefinireAgent用のコンテキストカットプロバイダー

This provider automatically cuts context when it exceeds a specified length,
supporting both character count and token count limits.
このプロバイダーは、指定された長さを超えた場合にコンテキストを自動的にカットし、
文字数とトークン数の両方の制限に対応します。
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from refinire.agents.context_provider import ContextProvider


class CutContextProvider(ContextProvider):
    """
    Provider that automatically cuts context when it exceeds specified limits
    指定された制限を超えた場合にコンテキストを自動的にカットするプロバイダー
    
    This provider wraps another context provider and automatically truncates
    the context when it exceeds the specified character or token limits.
    It can be used to prevent context overflow in LLM interactions.
    
    このプロバイダーは他のコンテキストプロバイダーをラップし、指定された文字数
    またはトークン数の制限を超えた場合にコンテキストを自動的に切り詰めます。
    LLM対話でのコンテキストオーバーフローを防ぐために使用できます。
    """
    
    provider_name: str = "cut_context"
    
    def __init__(
        self,
        provider: ContextProvider,
        max_chars: Optional[int] = None,
        max_tokens: Optional[int] = None,
        cut_strategy: str = "end",  # "start", "end", "middle"
        preserve_sections: bool = True
    ):
        """
        Initialize the cut context provider
        カットコンテキストプロバイダーを初期化
        
        Args:
            provider: The wrapped context provider / ラップするコンテキストプロバイダー
            max_chars: Maximum character count (None for no limit) / 最大文字数（Noneで制限なし）
            max_tokens: Maximum token count (None for no limit) / 最大トークン数（Noneで制限なし）
            cut_strategy: How to cut the context ("start", "end", "middle") / カット戦略（"start", "end", "middle"）
            preserve_sections: Whether to preserve complete sections when cutting / カット時に完全なセクションを保持するか
        """
        self.provider = provider
        self.max_chars = max_chars
        self.max_tokens = max_tokens
        self.cut_strategy = cut_strategy
        self.preserve_sections = preserve_sections
        
        if cut_strategy not in ["start", "end", "middle"]:
            raise ValueError("cut_strategy must be 'start', 'end', or 'middle'")
        
        if max_chars is None and max_tokens is None:
            raise ValueError("Either max_chars or max_tokens must be specified")
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """
        Get configuration schema for cut context provider
        カットコンテキストプロバイダーの設定スキーマを取得
        
        Returns:
            Dict[str, Any]: Configuration schema with parameter descriptions
            Dict[str, Any]: パラメータ説明を含む設定スキーマ
        """
        return {
            "description": "Automatically cuts context when it exceeds specified limits",
            "parameters": {
                "provider": {
                    "type": "dict",
                    "description": "Configuration for the wrapped context provider"
                },
                "max_chars": {
                    "type": "int",
                    "default": None,
                    "description": "Maximum character count (None for no limit)"
                },
                "max_tokens": {
                    "type": "int",
                    "default": None,
                    "description": "Maximum token count (None for no limit)"
                },
                "cut_strategy": {
                    "type": "str",
                    "default": "end",
                    "description": "How to cut the context ('start', 'end', 'middle')"
                },
                "preserve_sections": {
                    "type": "bool",
                    "default": True,
                    "description": "Whether to preserve complete sections when cutting"
                }
            },
            "example": "cut_context:\n  provider:\n    type: conversation_history\n    max_items: 10\n  max_chars: 4000\n  cut_strategy: end"
        }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'CutContextProvider':
        """
        Create cut context provider from configuration
        設定からカットコンテキストプロバイダーを作成
        
        Args:
            config: Configuration dictionary / 設定辞書
            
        Returns:
            CutContextProvider: Provider instance / プロバイダーインスタンス
        """
        from refinire.agents.context_provider_factory import ContextProviderFactory
        
        # Create the wrapped provider
        # ラップするプロバイダーを作成
        provider_config = config.get('provider', {})
        if isinstance(provider_config, str):
            # Parse the string configuration
            # 文字列設定を解析
            providers = ContextProviderFactory.parse_config_string(provider_config)
            if not providers:
                raise ValueError("No valid provider configuration found in string")
            # Use the first provider and add type field
            # 最初のプロバイダーを使用し、typeフィールドを追加
            provider_dict = providers[0]["config"].copy()
            provider_dict["type"] = providers[0]["name"].rstrip(':')  # Remove trailing colon
            provider = ContextProviderFactory.create_provider(provider_dict)
        else:
            provider = ContextProviderFactory.create_provider(provider_config)
        
        return cls(
            provider=provider,
            max_chars=config.get('max_chars'),
            max_tokens=config.get('max_tokens'),
            cut_strategy=config.get('cut_strategy', 'end'),
            preserve_sections=config.get('preserve_sections', True)
        )
    
    def _count_tokens(self, text: str) -> int:
        """
        Estimate token count for text (simple implementation)
        テキストのトークン数を推定（簡易実装）
        
        Args:
            text: Text to count tokens for / トークン数を数えるテキスト
            
        Returns:
            int: Estimated token count / 推定トークン数
        """
        # Simple token estimation: split by whitespace and punctuation
        # 簡易トークン推定: 空白と句読点で分割
        tokens = re.findall(r'\S+', text)
        return len(tokens)
    
    def _cut_text(self, text: str, max_length: int, strategy: str) -> str:
        """
        Cut text to specified length using the given strategy
        指定された戦略を使用してテキストを指定された長さにカット
        
        Args:
            text: Text to cut / カットするテキスト
            max_length: Maximum length / 最大長
            strategy: Cutting strategy / カット戦略
            
        Returns:
            str: Cut text / カットされたテキスト
        """
        if len(text) <= max_length:
            return text
        
        if strategy == "start":
            # Cut from the beginning (keep end)
            # 先頭からカット（末尾を保持）
            if self.preserve_sections:
                # Try to cut at section boundaries
                # セクション境界でカットを試行
                sections = self._split_into_sections(text)
                result = ""
                for section in reversed(sections):
                    if len(result + section) <= max_length:
                        result = section + result
                    else:
                        break
                return result if result else text[-max_length:]
            else:
                return text[-max_length:]
        
        elif strategy == "end":
            # Cut from the end (keep beginning)
            # 末尾からカット（先頭を保持）
            if self.preserve_sections:
                # Try to cut at section boundaries
                # セクション境界でカットを試行
                sections = self._split_into_sections(text)
                result = ""
                for section in sections:
                    if len(result + section) <= max_length:
                        result += section
                    else:
                        break
                return result if result else text[:max_length]
            else:
                return text[:max_length]
        
        elif strategy == "middle":
            # Cut from the middle
            # 中央からカット
            if self.preserve_sections:
                # Try to preserve beginning and end sections
                # 先頭と末尾のセクションを保持を試行
                sections = self._split_into_sections(text)
                if len(sections) <= 2:
                    return self._cut_text(text, max_length, "end")
                
                # Keep first and last sections, cut middle
                # 最初と最後のセクションを保持し、中央をカット
                first_section = sections[0]
                last_section = sections[-1]
                middle_length = max_length - len(first_section) - len(last_section) - 7  # Account for "\n...\n"
                
                if middle_length > 0:
                    return first_section + "\n...\n" + last_section
                else:
                    return self._cut_text(text, max_length, "end")
            else:
                # Cut from middle, keeping equal parts from start and end
                # 中央からカットし、先頭と末尾から等しい部分を保持
                half_length = max_length // 2
                return text[:half_length] + "\n...\n" + text[-half_length:]
        
        return text[:max_length]
    
    def _split_into_sections(self, text: str) -> List[str]:
        """
        Split text into logical sections for better cutting
        より良いカットのためにテキストを論理的なセクションに分割
        
        Args:
            text: Text to split / 分割するテキスト
            
        Returns:
            List[str]: List of sections / セクションのリスト
        """
        # Split by double newlines, headers, or file markers
        # 二重改行、ヘッダー、またはファイルマーカーで分割
        sections = re.split(r'\n\s*\n|^#\s+|^File:\s+', text, flags=re.MULTILINE)
        # Filter out empty sections and add back the markers
        # 空のセクションをフィルタリングし、マーカーを戻す
        result = []
        for i, section in enumerate(sections):
            if section.strip():
                # Add back the marker if it was a header or file marker
                # ヘッダーまたはファイルマーカーの場合はマーカーを戻す
                if i > 0 and text.find(section) > 0:
                    prev_char = text[text.find(section) - 1]
                    if prev_char == '\n':
                        # Check if there's a marker before this section
                        # このセクションの前にマーカーがあるかチェック
                        start_pos = text.find(section)
                        if start_pos > 0:
                            # Look for the marker
                            # マーカーを探す
                            marker_match = re.search(r'(^|\n)(#\s+|File:\s+)', text[:start_pos], re.MULTILINE)
                            if marker_match:
                                section = marker_match.group(2) + section
                result.append(section.strip())
        return result
    
    def get_context(self, query: str, previous_context: Optional[str] = None, **kwargs) -> str:
        """
        Get context from wrapped provider and cut if necessary
        ラップされたプロバイダーからコンテキストを取得し、必要に応じてカット
        
        Args:
            query: User query / ユーザークエリ
            previous_context: Previous context from other providers / 他のプロバイダーからの前のコンテキスト
            **kwargs: Additional arguments / 追加の引数
            
        Returns:
            str: Cut context / カットされたコンテキスト
        """
        # Get context from wrapped provider
        # ラップされたプロバイダーからコンテキストを取得
        context = self.provider.get_context(query, previous_context, **kwargs)
        
        if not context:
            return ""
        
        # Determine the limit to apply
        # 適用する制限を決定
        if self.max_tokens is not None:
            # Token-based cutting
            # トークンベースのカット
            current_tokens = self._count_tokens(context)
            if current_tokens > self.max_tokens:
                # Estimate characters per token for rough conversion
                # トークンあたりの文字数を推定して大まかな変換
                chars_per_token = len(context) / current_tokens
                max_chars = int(self.max_tokens * chars_per_token)
                context = self._cut_text(context, max_chars, self.cut_strategy)
        
        elif self.max_chars is not None:
            # Character-based cutting
            # 文字ベースのカット
            if len(context) > self.max_chars:
                context = self._cut_text(context, self.max_chars, self.cut_strategy)
        
        return context
    
    def update(self, interaction: Dict[str, Any]) -> None:
        """
        Update the wrapped provider
        ラップされたプロバイダーを更新
        
        Args:
            interaction: Interaction data / 対話データ
        """
        self.provider.update(interaction)
    
    def clear(self) -> None:
        """
        Clear the wrapped provider
        ラップされたプロバイダーをクリア
        """
        self.provider.clear() 