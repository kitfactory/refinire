"""
Source Code Provider
ソースコードプロバイダー

This module provides source code context for RefinireAgent.
RefinireAgentのソースコードコンテキストを提供します。
"""

import os
import re
import fnmatch
from pathlib import Path
from typing import List, Dict, Any, ClassVar, Optional, Set
from refinire.agents.context_provider import ContextProvider


class SourceCodeProvider(ContextProvider):
    """
    Provides source code context from codebase
    コードベースからソースコードコンテキストを提供
    
    This provider analyzes the codebase structure, identifies relevant files
    based on user input and conversation history, and provides them as context.
    It respects .gitignore files and can use internal RefinireAgent for
    intelligent file selection.
    
    このプロバイダーはコードベース構造を分析し、ユーザー入力と会話履歴に基づいて
    関連ファイルを特定し、コンテキストとして提供します。.gitignoreファイルを
    尊重し、インテリジェントなファイル選択のために内部RefinireAgentを使用できます。
    """
    
    provider_name: ClassVar[str] = "source_code"
    
    def __init__(
        self, 
        base_path: str | Path = ".", 
        max_files: int = 50,
        max_file_size: int = 10000,
        file_extensions: Optional[List[str]] = None,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ):
        """
        Initialize the source code provider
        ソースコードプロバイダーを初期化
        
        Args:
            base_path: Base directory path for codebase analysis / コードベース分析のベースディレクトリパス
            max_files: Maximum number of files to include in context / コンテキストに含める最大ファイル数
            max_file_size: Maximum file size in bytes to read / 読み込む最大ファイルサイズ（バイト）
            file_extensions: List of file extensions to include (None for all) / 含めるファイル拡張子のリスト（Noneで全て）
            include_patterns: List of patterns to include (None for all) / 含めるファイルパターンのリスト（Noneで全て）
            exclude_patterns: List of patterns to exclude (None for none) / 除外するファイルパターンのリスト（Noneでなし）
        """
        self.base_path = Path(base_path).resolve()
        self.max_files = max_files
        self.max_file_size = max_file_size
        self.file_extensions = file_extensions or ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp']
        self.include_patterns = include_patterns
        self.exclude_patterns = exclude_patterns
        self._gitignore_patterns = None
        
        # Internal agent for intelligent file selection
        # インテリジェントなファイル選択用の内部エージェント
        self._internal_agent: Optional[Any] = None
        
        # Cache for file tree and gitignore patterns
        # ファイルツリーとgitignoreパターンのキャッシュ
        self._file_tree: Optional[List[str]] = None
        self._last_scan_time: float = 0
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """
        Get configuration schema for source code provider
        ソースコードプロバイダーの設定スキーマを取得
        
        Returns:
            Dict[str, Any]: Configuration schema with parameter descriptions
            Dict[str, Any]: パラメータ説明を含む設定スキーマ
        """
        return {
            "description": "Provides source code context from codebase analysis",
            "parameters": {
                "base_path": {
                    "type": "str",
                    "default": ".",
                    "description": "Base directory path for codebase analysis"
                },
                "max_files": {
                    "type": "int",
                    "default": 50,
                    "description": "Maximum number of files to include in context"
                },
                "max_file_size": {
                    "type": "int",
                    "default": 10000,
                    "description": "Maximum file size in bytes to read"
                },
                "file_extensions": {
                    "type": "list",
                    "default": ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp'],
                    "description": "List of file extensions to include"
                },
                "include_patterns": {
                    "type": "list",
                    "default": None,
                    "description": "List of patterns to include"
                },
                "exclude_patterns": {
                    "type": "list",
                    "default": None,
                    "description": "List of patterns to exclude"
                }
            },
            "example": "source_code:\n  base_path: src\n  max_files: 5\n  file_extensions: ['.py', '.js']"
        }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'SourceCodeProvider':
        """
        Create source code provider from configuration
        設定からソースコードプロバイダーを作成
        
        Args:
            config: Configuration dictionary / 設定辞書
            
        Returns:
            SourceCodeProvider: Provider instance / プロバイダーインスタンス
        """
        return cls(**config)
    
    def _load_gitignore_patterns(self) -> List[str]:
        """
        Load .gitignore patterns from the base path
        ベースパスから.gitignoreパターンを読み込み
        
        Returns:
            List[str]: List of gitignore patterns / gitignoreパターンのリスト
        """
        patterns = []
        gitignore_path = self.base_path / ".gitignore"
        
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception as e:
                # Log warning but continue
                print(f"Warning: Could not read .gitignore: {e}")
        
        return patterns
    
    def _is_ignored(self, file_path: Path) -> bool:
        """
        Check if a file should be ignored based on gitignore patterns
        gitignoreパターンに基づいてファイルが無視されるべきかチェック
        """
        if not self._gitignore_patterns:
            return False
        try:
            # Convert file_path to absolute path before relative_to
            # file_pathを絶対パスに変換してからrelative_toを実行
            abs_file_path = Path(file_path).resolve()
            rel_path = abs_file_path.relative_to(self.base_path)
        except ValueError:
            return True  # Outside base path
        rel_path_str = str(rel_path)
        
        for pattern in self._gitignore_patterns:
            # 完全一致
            if rel_path_str == pattern:
                return True
            # ディレクトリ除外（/で終わるパターン）
            if pattern.endswith('/') and rel_path_str.startswith(pattern.rstrip('/')):
                return True
            # ディレクトリ除外（/で終わらないパターン）
            if not pattern.endswith('/') and rel_path_str.startswith(pattern + '/'):
                return True
            # サフィックス一致
            if pattern.startswith('*.') and rel_path_str.endswith(pattern.lstrip('*')):
                return True
            # ワイルドカード一致
            if '*' in pattern or '?' in pattern:
                if fnmatch.fnmatch(rel_path_str, pattern):
                    return True
        return False
    
    def _scan_file_tree(self) -> List[str]:
        """
        Scan the file tree and return list of relevant files
        ファイルツリーをスキャンして関連ファイルのリストを返す
        
        Returns:
            List[str]: List of relevant file paths / 関連ファイルパスのリスト
        """
        if not self.base_path.exists():
            return []
        
        # Load gitignore patterns if not cached
        # キャッシュされていない場合はgitignoreパターンを読み込み
        if self._gitignore_patterns is None:
            self._gitignore_patterns = self._load_gitignore_patterns()
        
        relevant_files = []
        
        for root, dirs, files in os.walk(self.base_path):
            # Remove ignored directories
            # 無視されるディレクトリを削除
            dirs[:] = [d for d in dirs if not self._is_ignored(Path(root) / d)]
            
            for file in files:
                file_path = Path(root) / file
                
                # Check if file should be ignored
                # ファイルが無視されるべきかチェック
                if self._is_ignored(file_path):
                    continue
                
                # Check file extension
                # ファイル拡張子をチェック
                if file_path.suffix not in self.file_extensions:
                    continue
                
                # Check file size
                # ファイルサイズをチェック
                try:
                    if file_path.stat().st_size > self.max_file_size:
                        continue
                except OSError:
                    continue
                
                # Convert to relative path
                # 相対パスに変換
                try:
                    rel_path = file_path.relative_to(self.base_path)
                    relevant_files.append(str(rel_path))
                except ValueError:
                    continue
        
        return relevant_files
    
    def _find_related_files(self, query: str, history: Optional[List[str]], available_files: List[str]) -> List[str]:
        """
        Find related files based on query and history using heuristics
        クエリと履歴に基づきヒューリスティックで関連ファイルを抽出
        
        Args:
            query: User query / ユーザークエリ
            history: Conversation history / 会話履歴
            available_files: List of available files / 利用可能なファイルリスト
        Returns:
            List[str]: List of related files (direct first, then indirect) / 関連ファイルリスト（直接→間接）
        """
        import os
        import difflib
        import re
        
        # 1. 直接関連ファイル: クエリ・履歴に現れるファイル名と類似するもの
        direct_related = set()
        all_text = query
        if history:
            all_text += '\n' + '\n'.join(history)
        # ファイル名らしき単語を抽出
        file_name_pattern = re.compile(r'\b[\w\-/]+\.[\w]+\b')
        mentioned = set(file_name_pattern.findall(all_text))
        # 類似一致（大文字小文字無視、部分一致も含む）
        for fname in available_files:
            for mention in mentioned:
                if mention.lower() in fname.lower() or os.path.basename(fname).lower() == mention.lower():
                    direct_related.add(fname)
        # 2. 間接関連ファイル: 直接関連ファイルがimportしているプロジェクトファイル
        indirect_related = set()
        project_files = set(available_files)
        for fname in direct_related:
            try:
                with open(self.base_path / fname, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue
            # Pythonのimport文、JSのimport/requireなどを簡易抽出
            import_pattern = re.compile(r'(?:import|from)\s+([\w\./_\-]+)')
            for match in import_pattern.findall(content):
                # 絶対import文（from src.refinire.agents.context_provider import ...）をファイルパスに変換
                if match.startswith('src.') or match.startswith('src/'):
                    mod_path = match.replace('.', '/').replace('src/', 'src/').replace('//', '/')
                    if not mod_path.endswith('.py'):
                        mod_path += '.py'
                    if mod_path in project_files:
                        indirect_related.add(mod_path)
                        continue
                # .py, .js, .tsなど拡張子がなければ.pyを補う
                if not os.path.splitext(match)[1]:
                    for ext in self.file_extensions:
                        candidate = match + ext
                        if candidate in project_files:
                            indirect_related.add(candidate)
                else:
                    if match in project_files:
                        indirect_related.add(match)
        # 3. 直接→間接の順でリストアップ
        ordered = list(direct_related) + [f for f in indirect_related if f not in direct_related]
        # 4. ファイル数・合計長で打ち切り
        total_len = 0
        result = []
        for fname in ordered:
            try:
                flen = (self.base_path / fname).stat().st_size
            except Exception:
                flen = 0
            if len(result) < self.max_files and (total_len + flen) <= self.max_file_size * self.max_files:
                result.append(fname)
                total_len += flen
            else:
                break
        return result

    def _select_relevant_files(self, query: str, available_files: List[str], history: Optional[List[str]] = None) -> List[str]:
        """
        Select relevant files based on query and history using heuristics
        クエリと履歴に基づきヒューリスティックで関連ファイルを選択
        """
        return self._find_related_files(query, history, available_files)

    def _select_relevant_files_llm(self, query: str, available_files: List[str], history: Optional[List[str]] = None) -> List[str]:
        """
        (Stub) Select relevant files using LLM (not implemented)
        LLMを用いた関連ファイル選択（未実装）
        """
        # TODO: LLMによる関連ファイル推定は将来実装
        return []

    def _read_file_content(self, file_path: str) -> str:
        """
        Read file content with error handling
        エラーハンドリング付きでファイル内容を読み込み
        
        Args:
            file_path: File path to read / 読み込むファイルパス
            
        Returns:
            str: File content or error message / ファイル内容またはエラーメッセージ
        """
        full_path = self.base_path / file_path
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return f"# File: {file_path}\n{content}\n"
        except UnicodeDecodeError:
            try:
                with open(full_path, 'r', encoding='shift_jis') as f:
                    content = f.read()
                    return f"# File: {file_path}\n{content}\n"
            except Exception as e:
                return f"# File: {file_path}\n# Error reading file: {e}\n"
        except Exception as e:
            return f"# File: {file_path}\n# Error reading file: {e}\n"
    
    def get_context(self, query: str, previous_context: Optional[str] = None, **kwargs) -> str:
        """
        Get source code context based on query and history
        クエリと履歴に基づいてソースコードコンテキストを取得
        """
        # Scan file tree if not cached
        if self._file_tree is None:
            self._file_tree = self._scan_file_tree()
        if not self._file_tree:
            return ""
        # 履歴を取得
        history = kwargs.get('history', None)
        # Select relevant files
        relevant_files = self._select_relevant_files(query, self._file_tree, history)
        if not relevant_files:
            return ""
        # Read and combine file contents
        context_parts = []
        for file_path in relevant_files:
            content = self._read_file_content(file_path)
            context_parts.append(content)
        return "\n".join(context_parts)
    
    def update(self, interaction: Dict[str, Any]) -> None:
        """
        Update provider with new interaction (refresh file tree)
        新しい対話でプロバイダーを更新（ファイルツリーを更新）
        
        Args:
            interaction: Interaction data / 対話データ
        """
        # Refresh file tree on update
        # 更新時にファイルツリーを更新
        self._file_tree = self._scan_file_tree()
    
    def clear(self) -> None:
        """
        Clear cached data
        キャッシュされたデータをクリア
        """
        self._file_tree = None
        self._gitignore_patterns = None
        self._last_scan_time = 0
    
    def refresh_file_tree(self) -> None:
        """
        Manually refresh the file tree cache
        ファイルツリーキャッシュを手動で更新
        """
        self._file_tree = self._scan_file_tree()
    
    def get_file_count(self) -> int:
        """
        Get the current number of available files
        現在の利用可能ファイル数を取得
        
        Returns:
            int: Number of available files / 利用可能ファイル数
        """
        if self._file_tree is None:
            self._file_tree = self._scan_file_tree()
        return len(self._file_tree) 