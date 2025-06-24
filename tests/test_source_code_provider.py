"""
Tests for SourceCodeProvider
SourceCodeProviderのテスト
"""

import pytest
import tempfile
import os
from pathlib import Path
from refinire.agents.providers.source_code import SourceCodeProvider


class TestSourceCodeProvider:
    """Test cases for SourceCodeProvider"""
    
    def test_provider_initialization(self):
        """Test basic provider initialization"""
        provider = SourceCodeProvider()
        assert provider.base_path == Path.cwd()
        assert provider.max_files == 50
        assert provider.max_file_size == 10000
        assert '.py' in provider.file_extensions
    
    def test_provider_initialization_with_custom_params(self):
        """Test provider initialization with custom parameters"""
        provider = SourceCodeProvider(
            base_path="tests/sample_project",
            max_files=20,
            max_file_size=5000,
            file_extensions=['.py', '.js'],
            include_patterns=['src/**'],
            exclude_patterns=['**/test_*']
        )
        
        assert provider.base_path == Path("tests/sample_project").resolve()
        assert provider.max_files == 20
        assert provider.max_file_size == 5000
        assert provider.file_extensions == ['.py', '.js']
        assert provider.include_patterns == ['src/**']
        assert provider.exclude_patterns == ['**/test_*']
    
    def test_gitignore_patterns_loading(self):
        """Test loading gitignore patterns"""
        provider = SourceCodeProvider(base_path="tests/sample_project")
        patterns = provider._load_gitignore_patterns()
        
        # Check that common patterns are loaded
        assert "__pycache__/" in patterns
        assert "*.pyc" in patterns
        assert ".venv" in patterns
        assert "build/" in patterns
    
    def test_file_ignoring_with_gitignore(self):
        """Test that files are properly ignored based on gitignore patterns"""
        provider = SourceCodeProvider(base_path="tests/sample_project")
        provider._gitignore_patterns = provider._load_gitignore_patterns()
        
        # Test that ignored files are properly identified
        assert provider._is_ignored(Path("tests/sample_project/__pycache__/dummy.pyc"))
        assert provider._is_ignored(Path("tests/sample_project/.venv/bin/python"))
        assert provider._is_ignored(Path("tests/sample_project/build/dummy.so"))
        
        # Test that non-ignored files are not ignored
        assert not provider._is_ignored(Path("tests/sample_project/src/refinire/agents/context_provider.py"))
    
    def test_file_tree_scanning(self):
        """Test file tree scanning functionality"""
        provider = SourceCodeProvider(base_path="tests/sample_project")
        file_tree = provider._scan_file_tree()
        
        # Should find Python files in the sample project
        assert 'src/refinire/__init__.py' in file_tree
        assert 'src/refinire/agents/context_provider.py' in file_tree
        
        # Should not include ignored files
        assert '__pycache__/dummy.pyc' not in file_tree
        assert '.venv/bin/python' not in file_tree
    
    def test_file_tree_scanning_with_custom_extensions(self):
        """Test file tree scanning with custom file extensions"""
        provider = SourceCodeProvider(
            base_path="tests/sample_project",
            file_extensions=['.py', '.md']
        )
        file_tree = provider._scan_file_tree()
        
        # Should only include .py and .md files
        for file_path in file_tree:
            assert file_path.endswith(('.py', '.md'))
    
    def test_direct_related_files_detection(self):
        """Test detection of directly related files based on query and history"""
        provider = SourceCodeProvider(base_path="tests/sample_project")
        provider._file_tree = provider._scan_file_tree()
        
        # Test with query mentioning specific files
        query = "I want to modify context_provider.py and conversation_history.py"
        history = ["Let's look at the source_code.py file"]
        
        related_files = provider._find_related_files(query, history, provider._file_tree)
        
        # Should find mentioned files
        assert "src/refinire/agents/context_provider.py" in related_files
        assert "src/refinire/agents/providers/conversation_history.py" in related_files
        assert "src/refinire/agents/providers/source_code.py" in related_files
    
    def test_indirect_related_files_detection(self):
        """Test detection of indirectly related files through imports"""
        provider = SourceCodeProvider(base_path="tests/sample_project")
        provider._file_tree = provider._scan_file_tree()
        
        # Test with query mentioning a file that imports others
        query = "Let's work on conversation_history.py"
        
        related_files = provider._find_related_files(query, [query], provider._file_tree)
        
        # Should find the mentioned file and any files it imports
        assert "src/refinire/agents/providers/conversation_history.py" in related_files
        # conversation_history.py imports context_provider, so it should be included
        assert "src/refinire/agents/context_provider.py" in related_files
    
    def test_file_ordering_direct_then_indirect(self):
        """Test that files are ordered: direct related first, then indirect"""
        provider = SourceCodeProvider(base_path="tests/sample_project")
        provider._file_tree = provider._scan_file_tree()
        
        query = "Let's work on conversation_history.py"
        related_files = provider._find_related_files(query, [query], provider._file_tree)
        
        # Find positions of direct and indirect files
        direct_file = "src/refinire/agents/providers/conversation_history.py"
        indirect_file = "src/refinire/agents/context_provider.py"
        
        if direct_file in related_files and indirect_file in related_files:
            direct_index = related_files.index(direct_file)
            indirect_index = related_files.index(indirect_file)
            # Direct file should come before indirect file
            assert direct_index < indirect_index
    
    def test_file_count_and_size_limiting(self):
        """Test that file count and total size limits are respected"""
        provider = SourceCodeProvider(
            base_path="tests/sample_project",
            max_files=2,
            max_file_size=1000
        )
        provider._file_tree = provider._scan_file_tree()
        
        query = "Let's work on all Python files"
        related_files = provider._find_related_files(query, [query], provider._file_tree)
        
        # Should respect max_files limit
        assert len(related_files) <= 2
        
        # Should respect total size limit
        total_size = 0
        for file_path in related_files:
            full_path = provider.base_path / file_path
            total_size += full_path.stat().st_size
        
        assert total_size <= 2000  # max_files * max_file_size
    
    def test_file_content_reading(self):
        """Test reading file content with error handling"""
        provider = SourceCodeProvider(base_path="tests/sample_project")
        
        # Test reading a valid file
        content = provider._read_file_content("src/refinire/agents/context_provider.py")
        assert "# File: src/refinire/agents/context_provider.py" in content
        assert "class ContextProvider" in content
        
        # Test reading a non-existent file
        content = provider._read_file_content("nonexistent_file.py")
        assert "# Error reading file" in content
    
    def test_get_context_with_query(self):
        """Test getting context based on query"""
        provider = SourceCodeProvider(base_path="tests/sample_project")
        
        query = "Let's work on context_provider.py"
        context = provider.get_context(query)
        
        # Should include relevant file content
        assert "# File: src/refinire/agents/context_provider.py" in context
        assert "class ContextProvider" in context
    
    def test_get_context_with_history(self):
        """Test getting context based on query and history"""
        provider = SourceCodeProvider(base_path="tests/sample_project")
        
        query = "Let's continue working on this"
        history = ["I was working on conversation_history.py"]
        
        context = provider.get_context(query, history=history)
        
        # Should include files mentioned in history
        assert "# File: src/refinire/agents/providers/conversation_history.py" in context
    
    def test_update_method(self):
        """Test update method refreshes file tree"""
        provider = SourceCodeProvider(base_path="tests/sample_project")
        
        # Initial scan
        initial_tree = provider._scan_file_tree()
        provider._file_tree = initial_tree
        
        # Update should refresh the tree
        provider.update({"user_input": "test", "result": "test"})
        
        # Tree should be refreshed
        assert provider._file_tree is not None
    
    def test_clear_method(self):
        """Test clear method resets cached data"""
        provider = SourceCodeProvider(base_path="tests/sample_project")
        
        # Populate cache
        provider._file_tree = ["file1.py", "file2.py"]
        provider._gitignore_patterns = ["*.pyc"]
        provider._last_scan_time = 123.45
        
        # Clear cache
        provider.clear()
        
        assert provider._file_tree is None
        assert provider._gitignore_patterns is None
        assert provider._last_scan_time == 0
    
    def test_refresh_file_tree_method(self):
        """Test manual file tree refresh"""
        provider = SourceCodeProvider(base_path="tests/sample_project")
        
        # Initial state
        assert provider._file_tree is None
        
        # Manual refresh
        provider.refresh_file_tree()
        
        # Should have populated the tree
        assert provider._file_tree is not None
        assert len(provider._file_tree) > 0
    
    def test_get_file_count_method(self):
        """Test getting file count"""
        provider = SourceCodeProvider(base_path="tests/sample_project")
        
        count = provider.get_file_count()
        
        # Should return a positive number
        assert count > 0
        assert isinstance(count, int)
    
    def test_config_schema(self):
        """Test configuration schema"""
        schema = SourceCodeProvider.get_config_schema()
        
        assert 'description' in schema
        assert 'parameters' in schema
        assert 'example' in schema
        
        # Check parameters
        params = schema['parameters']
        assert 'base_path' in params
        assert 'max_files' in params
        assert 'max_file_size' in params
        assert 'file_extensions' in params
        assert 'include_patterns' in params
        assert 'exclude_patterns' in params
        
        assert params['base_path']['default'] == '.'
        assert params['max_files']['default'] == 50
        assert params['max_file_size']['default'] == 10000
    
    def test_from_config_method(self):
        """Test creating provider from configuration"""
        config = {
            'base_path': 'tests/sample_project',
            'max_files': 15,
            'max_file_size': 8000,
            'file_extensions': ['.py', '.md'],
            'include_patterns': ['src/**'],
            'exclude_patterns': ['**/test_*']
        }
        
        provider = SourceCodeProvider.from_config(config)
        
        assert provider.base_path == Path('tests/sample_project').resolve()
        assert provider.max_files == 15
        assert provider.max_file_size == 8000
        assert provider.file_extensions == ['.py', '.md']
        assert provider.include_patterns == ['src/**']
        assert provider.exclude_patterns == ['**/test_*']
    
    def test_llm_stub_method(self):
        """Test that LLM-based file selection stub returns empty list"""
        provider = SourceCodeProvider(base_path="tests/sample_project")
        
        result = provider._select_relevant_files_llm("test query", ["file1.py", "file2.py"])
        
        # Should return empty list (not implemented)
        assert result == []
    
    def test_provider_name(self):
        """Test provider name class variable"""
        assert SourceCodeProvider.provider_name == "source_code" 