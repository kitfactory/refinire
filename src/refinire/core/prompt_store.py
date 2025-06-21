"""
PromptStore class for managing prompts with multilingual support
プロンプトの多言語サポート付き管理クラス
"""

import os
import locale
import sqlite3
from typing import Dict, List, Optional, Set, Literal
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import logging

from .llm import get_llm

logger = logging.getLogger(__name__)

# Supported languages
LanguageCode = Literal["ja", "en"]
SUPPORTED_LANGUAGES: Set[LanguageCode] = {"ja", "en"}


@dataclass
class PromptReference:
    """
    A prompt content with metadata for tracing
    トレース用のメタデータ付きプロンプトコンテンツ
    """
    content: str
    name: str
    tag: Optional[str] = None
    language: LanguageCode = "en"
    retrieved_at: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        """Return the prompt content when used as string"""
        return self.content
    
    def get_metadata(self) -> Dict[str, str]:
        """Get metadata for tracing"""
        metadata = {
            "prompt_name": self.name,
            "prompt_language": self.language,
            "retrieved_at": self.retrieved_at.isoformat()
        }
        if self.tag:
            metadata["prompt_tag"] = self.tag
        return metadata


def get_default_storage_dir() -> Path:
    """
    Get the default storage directory for Refinire
    Refinireのデフォルト保存ディレクトリを取得
    
    Returns:
        Path to storage directory (REFINIRE_DIR env var or ~/.refinire)
    """
    refinire_dir = os.environ.get("REFINIRE_DIR")
    if refinire_dir:
        return Path(refinire_dir)
    else:
        return Path.home() / ".refinire"


def detect_system_language() -> LanguageCode:
    """
    Detect system language from environment variables or OS settings.
    環境変数やOS設定からシステム言語を検出します。
    
    Returns:
        'ja' for Japanese, 'en' for others
    """
    # Check environment variables commonly used for locale
    for env_var in ("LANG", "LC_ALL", "LC_MESSAGES"):
        lang_val = os.environ.get(env_var, "")
        if lang_val.lower().startswith("ja"):
            return "ja"
    
    # Fallback to system locale
    try:
        sys_loc = locale.getdefaultlocale()[0] or ""
        if sys_loc.lower().startswith("ja"):
            return "ja"
    except:
        pass
    
    return "en"


@dataclass
class StoredPrompt:
    """
    A prompt with metadata for storage
    保存用のメタデータ付きプロンプト
    """
    name: str
    content: Dict[LanguageCode, str]  # Language -> prompt content
    tag: Optional[str] = None  # Single tag for categorization
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def get_content(self, language: Optional[LanguageCode] = None) -> str:
        """Get prompt content in specified language"""
        if language is None:
            language = detect_system_language()
        
        # Return content in requested language if available
        if language in self.content:
            return self.content[language]
        
        # Fallback to any available language
        if self.content:
            return next(iter(self.content.values()))
        
        return ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "content": self.content,
            "tag": self.tag,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "StoredPrompt":
        """Create from dictionary"""
        # Handle backward compatibility for old format with tags
        tag = data.get("tag")
        if tag is None and "tags" in data and data["tags"]:
            # Convert old format: use first tag
            tag = data["tags"][0] if isinstance(data["tags"], list) else next(iter(data["tags"]))
        
        return cls(
            name=data["name"],
            content=data["content"],
            tag=tag,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )


class PromptStore:
    """
    Store and manage prompts with multilingual support using SQLite
    SQLiteを使用した多言語対応のプロンプト保存・管理クラス
    
    Prompts are identified by name and tag combination
    プロンプトは名前とタグの組み合わせで識別されます
    
    All methods are class methods that use an internal singleton instance
    全てのメソッドは内部シングルトンインスタンスを使用するクラスメソッドです
    """
    
    _instance: Optional['PromptStore'] = None
    _storage_dir: Optional[Path] = None
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize PromptStore with SQLite database
        SQLiteデータベースでPromptStoreを初期化
        
        Args:
            storage_dir: Directory to store database. If None, uses default directory.
        """
        if storage_dir is None:
            storage_dir = get_default_storage_dir()
        
        self.storage_dir = storage_dir
        self.db_path = storage_dir / "prompts.db"
        
        # Create directory if it doesn't exist
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    @classmethod
    def _get_instance(cls, storage_dir: Optional[Path] = None) -> 'PromptStore':
        """
        Get or create singleton instance
        シングルトンインスタンスを取得または作成
        """
        if storage_dir is None:
            storage_dir = get_default_storage_dir()
        
        # Create new instance if none exists or storage directory changed
        if cls._instance is None or cls._storage_dir != storage_dir:
            cls._instance = cls(storage_dir)
            cls._storage_dir = storage_dir
        
        return cls._instance
    
    @classmethod
    def set_storage_dir(cls, storage_dir: Path):
        """
        Set the storage directory for all operations
        全ての操作用の保存ディレクトリを設定
        
        Args:
            storage_dir: Directory to store database
        """
        cls._instance = None  # Force recreation with new directory
        cls._storage_dir = storage_dir
    
    def _init_database(self):
        """
        Initialize SQLite database and create tables
        SQLiteデータベースを初期化してテーブルを作成
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    tag TEXT,
                    content_en TEXT,
                    content_ja TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(name, tag)
                )
            """)
            conn.commit()
    
    @classmethod
    def store(
        cls, 
        name: str, 
        content: str,
        tag: Optional[str] = None,
        language: Optional[LanguageCode] = None,
        auto_translate: bool = True,
        storage_dir: Optional[Path] = None
    ) -> StoredPrompt:
        """
        Store a prompt with automatic translation
        
        Args:
            name: Unique name for the prompt
            content: Prompt content
            tag: Optional single tag for categorization
            language: Language of the content. If None, detects from system.
            auto_translate: Whether to automatically translate to other languages
            
        Returns:
            StoredPrompt object
        """
        instance = cls._get_instance(storage_dir)
        
        if language is None:
            language = detect_system_language()
        
        now = datetime.now().isoformat()
        
        with sqlite3.connect(instance.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if prompt exists
            cursor.execute("""
                SELECT content_en, content_ja, created_at FROM prompts 
                WHERE name = ? AND tag IS ?
            """, (name, tag))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing prompt
                content_en, content_ja, created_at = existing
                if language == "en":
                    content_en = content
                else:
                    content_ja = content
                
                cursor.execute("""
                    UPDATE prompts 
                    SET content_en = ?, content_ja = ?, updated_at = ?
                    WHERE name = ? AND tag IS ?
                """, (content_en, content_ja, now, name, tag))
            else:
                # Insert new prompt
                content_en = content if language == "en" else None
                content_ja = content if language == "ja" else None
                
                cursor.execute("""
                    INSERT INTO prompts (name, tag, content_en, content_ja, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, tag, content_en, content_ja, now, now))
                created_at = now
            
            conn.commit()
            
            # Auto-translate if requested
            if auto_translate:
                instance._translate_and_update(name, tag, language, content)
            
            # Create and return StoredPrompt object
            cursor.execute("""
                SELECT content_en, content_ja, created_at, updated_at FROM prompts 
                WHERE name = ? AND tag IS ?
            """, (name, tag))
            
            row = cursor.fetchone()
            content_en, content_ja, created_at, updated_at = row
            
            content_dict = {}
            if content_en:
                content_dict["en"] = content_en
            if content_ja:
                content_dict["ja"] = content_ja
            
            return StoredPrompt(
                name=name,
                content=content_dict,
                tag=tag,
                created_at=datetime.fromisoformat(created_at),
                updated_at=datetime.fromisoformat(updated_at)
            )
    
    
    @classmethod
    def get_prompt(cls, name: str, tag: Optional[str] = None, storage_dir: Optional[Path] = None) -> Optional[StoredPrompt]:
        """
        Get the full StoredPrompt object by name and tag
        
        Args:
            name: Prompt name
            tag: Specific tag to identify the prompt
            storage_dir: Storage directory override
            
        Returns:
            StoredPrompt object or None if not found
        """
        instance = cls._get_instance(storage_dir)
        
        with sqlite3.connect(instance.db_path) as conn:
            cursor = conn.cursor()
            
            if tag is not None:
                cursor.execute("""
                    SELECT name, tag, content_en, content_ja, created_at, updated_at 
                    FROM prompts WHERE name = ? AND tag = ?
                """, (name, tag))
            else:
                # First try to find untagged prompt
                cursor.execute("""
                    SELECT name, tag, content_en, content_ja, created_at, updated_at 
                    FROM prompts WHERE name = ? AND tag IS NULL
                """, (name,))
                row = cursor.fetchone()
                
                if not row:
                    # No untagged prompt, check if there's exactly one with this name
                    cursor.execute("""
                        SELECT name, tag, content_en, content_ja, created_at, updated_at 
                        FROM prompts WHERE name = ?
                    """, (name,))
                    rows = cursor.fetchall()
                    if len(rows) == 1:
                        row = rows[0]
                    else:
                        return None
            
            if tag is not None:
                row = cursor.fetchone()
            
            if not row:
                return None
            
            name, tag, content_en, content_ja, created_at, updated_at = row
            
            content_dict = {}
            if content_en:
                content_dict["en"] = content_en
            if content_ja:
                content_dict["ja"] = content_ja
            
            return StoredPrompt(
                name=name,
                content=content_dict,
                tag=tag,
                created_at=datetime.fromisoformat(created_at),
                updated_at=datetime.fromisoformat(updated_at)
            )
    
    @classmethod
    def list_prompts(cls, name: Optional[str] = None, storage_dir: Optional[Path] = None) -> List[StoredPrompt]:
        """
        List all prompts with the specified name
        指定された名前のプロンプトを全てリスト
        
        Args:
            name: If provided, only return prompts with this name
            storage_dir: Storage directory override
            
        Returns:
            List of StoredPrompt objects
        """
        instance = cls._get_instance(storage_dir)
        
        with sqlite3.connect(instance.db_path) as conn:
            cursor = conn.cursor()
            
            if name:
                cursor.execute("""
                    SELECT name, tag, content_en, content_ja, created_at, updated_at 
                    FROM prompts WHERE name = ?
                    ORDER BY name, tag
                """, (name,))
            else:
                cursor.execute("""
                    SELECT name, tag, content_en, content_ja, created_at, updated_at 
                    FROM prompts
                    ORDER BY name, tag
                """)
            
            prompts = []
            for row in cursor.fetchall():
                name, tag, content_en, content_ja, created_at, updated_at = row
                
                content_dict = {}
                if content_en:
                    content_dict["en"] = content_en
                if content_ja:
                    content_dict["ja"] = content_ja
                
                prompts.append(StoredPrompt(
                    name=name,
                    content=content_dict,
                    tag=tag,
                    created_at=datetime.fromisoformat(created_at),
                    updated_at=datetime.fromisoformat(updated_at)
                ))
            
            return prompts
    
    @classmethod
    def delete(cls, name: str, tag: Optional[str] = None, storage_dir: Optional[Path] = None) -> int:
        """
        Delete prompts by name and optionally tag
        名前とタグでプロンプトを削除
        
        Args:
            name: Prompt name to delete
            tag: If provided, only delete prompts with this exact tag.
                 If None, delete all prompts with the given name.
            storage_dir: Storage directory override
            
        Returns:
            Number of prompts deleted
        """
        instance = cls._get_instance(storage_dir)
        
        with sqlite3.connect(instance.db_path) as conn:
            cursor = conn.cursor()
            
            if tag is not None:
                cursor.execute("""
                    DELETE FROM prompts WHERE name = ? AND tag = ?
                """, (name, tag))
            else:
                cursor.execute("""
                    DELETE FROM prompts WHERE name = ?
                """, (name,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return deleted_count
    
    @classmethod
    def get(
        cls, 
        name: str,
        tag: Optional[str] = None,
        language: Optional[LanguageCode] = None,
        storage_dir: Optional[Path] = None
    ) -> Optional[PromptReference]:
        """
        Get a prompt with metadata for tracing
        トレース用のメタデータ付きでプロンプトを取得
        
        Args:
            name: Prompt name
            tag: Specific tag to identify the prompt
            language: Desired language. If None, uses system language.
            storage_dir: Storage directory override
            
        Returns:
            PromptReference object with metadata or None if not found
        """
        instance = cls._get_instance(storage_dir)
        
        if language is None:
            language = detect_system_language()
        
        with sqlite3.connect(instance.db_path) as conn:
            cursor = conn.cursor()
            
            if tag is not None:
                # Look for exact match with name and tag
                cursor.execute("""
                    SELECT content_en, content_ja FROM prompts 
                    WHERE name = ? AND tag = ?
                """, (name, tag))
            else:
                # Look for prompt without tag, or if only one exists with this name
                cursor.execute("""
                    SELECT content_en, content_ja FROM prompts 
                    WHERE name = ? AND tag IS NULL
                """, (name,))
                
                row = cursor.fetchone()
                if not row:
                    # No untagged prompt, check if there's exactly one with this name
                    cursor.execute("""
                        SELECT content_en, content_ja FROM prompts 
                        WHERE name = ?
                    """, (name,))
                    rows = cursor.fetchall()
                    if len(rows) == 1:
                        row = rows[0]
                    else:
                        return None
                else:
                    pass  # Use the untagged prompt
            
            if tag is not None:
                row = cursor.fetchone()
            
            if not row:
                return None
            
            content_en, content_ja = row
            
            # Get content in preferred language
            if language == "en" and content_en:
                content = content_en
            elif language == "ja" and content_ja:
                content = content_ja
            elif content_en:
                content = content_en
            elif content_ja:
                content = content_ja
            else:
                return None
        
        return PromptReference(
            content=content,
            name=name,
            tag=tag,
            language=language
        )
    
    def _translate_and_update(
        self,
        name: str,
        tag: Optional[str],
        source_language: LanguageCode,
        source_content: str
    ):
        """
        Translate prompt and update database
        プロンプトを翻訳してデータベースを更新
        """
        target_language = "ja" if source_language == "en" else "en"
        
        # Create translation prompt
        if source_language == "en" and target_language == "ja":
            translation_prompt = f"""Translate the following English prompt to Japanese.
Keep the technical meaning and intent exactly the same.
Maintain any placeholders or variables as-is.

English prompt:
{source_content}

Japanese translation:"""
        elif source_language == "ja" and target_language == "en":
            translation_prompt = f"""次の日本語のプロンプトを英語に翻訳してください。
技術的な意味と意図を正確に保持してください。
プレースホルダーや変数はそのまま維持してください。

日本語プロンプト:
{source_content}

英語翻訳:"""
        else:
            return
        
        # Get translation from LLM
        try:
            llm = get_llm()
            response = llm.agent.run(translation_prompt)
            
            if hasattr(response, 'messages') and response.messages:
                translated_content = response.messages[-1].text.strip()
                
                # Update database with translation
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    if target_language == "en":
                        cursor.execute("""
                            UPDATE prompts SET content_en = ? 
                            WHERE name = ? AND tag IS ?
                        """, (translated_content, name, tag))
                    else:
                        cursor.execute("""
                            UPDATE prompts SET content_ja = ? 
                            WHERE name = ? AND tag IS ?
                        """, (translated_content, name, tag))
                    
                    conn.commit()
        except Exception as e:
            # Translation failed, but don't crash
            logger.warning(f"Translation failed: {e}")


def P(
    name: str,
    tag: Optional[str] = None,
    language: Optional[LanguageCode] = None,
    storage_dir: Optional[Path] = None
) -> Optional[PromptReference]:
    """
    Short alias for PromptStore.get() - convenient function for prompt retrieval
    PromptStore.get()の短縮エイリアス - プロンプト取得用の便利関数
    
    Args:
        name: Prompt name / プロンプト名
        tag: Specific tag to identify the prompt / プロンプト識別用の特定タグ
        language: Desired language. If None, uses system language / 希望言語。Noneの場合はシステム言語を使用
        storage_dir: Storage directory override / ストレージディレクトリの上書き
        
    Returns:
        PromptReference object with metadata or None if not found
        メタデータ付きPromptReferenceオブジェクト、見つからない場合はNone
        
    Example:
        # Long form / 通常の書き方
        prompt = PromptStore.get("greeting", tag="formal", language="en")
        
        # Short form / 短縮形
        prompt = P("greeting", tag="formal", language="en")
        prompt = P("greeting")  # Uses default tag and system language
    """
    return PromptStore.get(name=name, tag=tag, language=language, storage_dir=storage_dir)
    
