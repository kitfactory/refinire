"""
Source Code Provider
ソースコードプロバイダー

This is a test file for SourceCodeProvider testing.
SourceCodeProviderのテスト用ファイルです。
"""

from typing import List, Dict, Any, Optional
from ..context_provider import ContextProvider


class SourceCodeProvider(ContextProvider):
    """
    Provides source code context
    ソースコードコンテキストを提供
    """
    
    def __init__(self, base_path: str = ".", max_files: int = 10):
        self.base_path = base_path
        self.max_files = max_files
    
    def get_context(self, query: str, previous_context: Optional[str] = None, **kwargs) -> str:
        """Get source code context"""
        return f"# Source code context for: {query}\n# Base path: {self.base_path}\n# Max files: {self.max_files}"
    
    def update(self, interaction: Dict[str, Any]) -> None:
        """Update with new interaction"""
        pass
    
    def clear(self) -> None:
        """Clear stored data"""
        pass 