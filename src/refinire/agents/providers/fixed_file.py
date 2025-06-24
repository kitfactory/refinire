"""
Fixed File Provider
固定ファイルプロバイダー

This module provides fixed file context for RefinireAgent.
RefinireAgentの固定ファイルコンテキストを提供します。
"""

import os
from typing import Dict, Any, ClassVar, Optional
from refinire.agents.context_provider import ContextProvider


class FixedFileProvider(ContextProvider):
    """
    Provides fixed file content as context
    固定ファイル内容をコンテキストとして提供
    
    This provider reads the content of a specified file and provides it
    as context for the current query. It supports various encodings and
    can detect file changes.
    
    このプロバイダーは指定されたファイルの内容を読み取り、現在のクエリ用の
    コンテキストとして提供します。様々なエンコーディングをサポートし、
    ファイル変更を検出できます。
    """
    
    provider_name: ClassVar[str] = "fixed_file"
    
    def __init__(self, file_path: str, encoding: str = "utf-8", check_updates: bool = True):
        """
        Initialize fixed file provider
        固定ファイルプロバイダーを初期化
        
        Args:
            file_path: Path to the file to read / 読み取るファイルのパス
            encoding: File encoding (utf-8, shift_jis, etc.) / ファイルエンコーディング（utf-8、shift_jis等）
            check_updates: Whether to check for file updates / ファイル更新をチェックするかどうか
        """
        self.file_path = file_path
        self.encoding = encoding
        self.check_updates = check_updates
        self._cached_content = None
        self._last_modified = None
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """
        Get configuration schema for fixed file provider
        固定ファイルプロバイダーの設定スキーマを取得
        
        Returns:
            Dict[str, Any]: Configuration schema with parameter descriptions
            Dict[str, Any]: パラメータ説明を含む設定スキーマ
        """
        return {
            "description": "Provides fixed file content as context",
            "parameters": {
                "file_path": {
                    "type": "str",
                    "required": True,
                    "description": "Path to the file to read"
                },
                "encoding": {
                    "type": "str",
                    "default": "utf-8",
                    "description": "File encoding (utf-8, shift_jis, etc.)"
                },
                "check_updates": {
                    "type": "bool",
                    "default": True,
                    "description": "Whether to check for file updates"
                }
            },
            "example": "fixed_file:\n  file_path: './config.txt'\n  encoding: 'utf-8'"
        }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'FixedFileProvider':
        """
        Create fixed file provider from configuration
        設定から固定ファイルプロバイダーを作成
        
        Args:
            config: Configuration dictionary / 設定辞書
            
        Returns:
            FixedFileProvider: Provider instance / プロバイダーインスタンス
        """
        return cls(**config)
    
    def get_context(self, query: str, previous_context: Optional[str] = None, **kwargs) -> str:
        """
        Get file content as context
        ファイル内容をコンテキストとして取得
        
        Args:
            query: Current user query / 現在のユーザークエリ
            previous_context: Context provided by previous providers / 前のプロバイダーが提供したコンテキスト
            **kwargs: Additional parameters / 追加パラメータ
            
        Returns:
            str: File content as context string / コンテキスト文字列としてのファイル内容
        """
        try:
            # Check if file exists
            # ファイルが存在するかチェック
            if not os.path.exists(self.file_path):
                # File doesn't exist, clear cache and return empty string
                # ファイルが存在しない場合、キャッシュをクリアして空文字列を返す
                self._cached_content = None
                self._last_modified = None
                return ""
            
            # Check if file has been modified (if update checking is enabled)
            # ファイルが変更されたかチェック（更新チェックが有効な場合）
            if self.check_updates:
                current_modified = os.path.getmtime(self.file_path)
                current_size = os.path.getsize(self.file_path)
                
                # Check if file has been modified (timestamp or size change)
                # ファイルが変更されたかチェック（タイムスタンプまたはサイズ変更）
                if (self._last_modified is not None and 
                    (current_modified > self._last_modified or 
                     hasattr(self, '_last_size') and current_size != self._last_size)):
                    # File has been modified, clear cache
                    # ファイルが変更された、キャッシュをクリア
                    self._cached_content = None
                
                self._last_modified = current_modified
                self._last_size = current_size
            
            # Return cached content if available
            # キャッシュされた内容が利用可能な場合は返す
            if self._cached_content is not None:
                return self._cached_content
            
            # Read file content
            # ファイル内容を読み取り
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                content = file.read()
                self._cached_content = content
                return content
                
        except (OSError, IOError, UnicodeDecodeError) as e:
            # Return empty string on any file reading error
            # ファイル読み取りエラーの場合は空文字列を返す
            self._cached_content = None
            self._last_modified = None
            if hasattr(self, '_last_size'):
                delattr(self, '_last_size')
            return ""
    
    def update(self, interaction: Dict[str, Any]) -> None:
        """
        Update provider with new interaction (no-op for fixed file provider)
        新しい対話でプロバイダーを更新（固定ファイルプロバイダーでは何もしない）
        
        Args:
            interaction: Interaction data / 対話データ
        """
        # Fixed file provider doesn't need to update based on interactions
        # 固定ファイルプロバイダーは対話に基づいて更新する必要がない
        pass
    
    def clear(self) -> None:
        """
        Clear cached file content
        キャッシュされたファイル内容をクリア
        """
        self._cached_content = None
        self._last_modified = None
        if hasattr(self, '_last_size'):
            delattr(self, '_last_size')
    
    def file_exists(self) -> bool:
        """
        Check if the specified file exists
        指定されたファイルが存在するかチェック
        
        Returns:
            bool: True if file exists, False otherwise / ファイルが存在する場合はTrue、そうでなければFalse
        """
        return os.path.exists(self.file_path)
    
    def get_file_size(self) -> Optional[int]:
        """
        Get the size of the file in bytes
        ファイルのサイズをバイトで取得
        
        Returns:
            Optional[int]: File size in bytes, None if file doesn't exist / バイトでのファイルサイズ、ファイルが存在しない場合はNone
        """
        try:
            return os.path.getsize(self.file_path)
        except OSError:
            return None
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the file
        ファイルの情報を取得
        
        Returns:
            Dict[str, Any]: File information / ファイル情報
        """
        info = {
            "exists": self.file_exists(),
            "path": self.file_path,
            "encoding": self.encoding,
            "check_updates": self.check_updates
        }
        
        if self.file_exists():
            info["size"] = self.get_file_size()
            info["last_modified"] = self._last_modified
            info["cached"] = self._cached_content is not None
        
        return info
    
    def force_refresh(self) -> None:
        """
        Force refresh of file content (clear cache and re-read)
        ファイル内容の強制更新（キャッシュをクリアして再読み取り）
        """
        self.clear()
    
    def set_file_path(self, file_path: str) -> None:
        """
        Change the file path and clear cache
        ファイルパスを変更してキャッシュをクリア
        
        Args:
            file_path: New file path / 新しいファイルパス
        """
        self.file_path = file_path
        self.clear()
    
    def set_encoding(self, encoding: str) -> None:
        """
        Change the file encoding and clear cache
        ファイルエンコーディングを変更してキャッシュをクリア
        
        Args:
            encoding: New encoding / 新しいエンコーディング
        """
        self.encoding = encoding
        self.clear() 