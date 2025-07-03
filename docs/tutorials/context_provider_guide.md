# ContextProvider Complete Guide - Building Intelligent Memory Systems

This comprehensive guide explains Refinire's ContextProvider architecture and shows you how to create custom context providers for specialized AI agent memory and information access patterns.

## Understanding ContextProvider Architecture

### What are ContextProviders?

ContextProviders are modular components that automatically supply relevant information to AI agents during conversations. They act as intelligent memory systems that can:

- Maintain conversation history
- Access file contents and source code
- Query databases and external APIs
- Provide domain-specific information
- Filter and optimize context based on relevance

### Core Design Principles

**Modularity**: Each provider handles a specific type of context (conversations, files, APIs, etc.)

**Composability**: Multiple providers can be chained together to build rich context

**Configurability**: Providers are configured declaratively without code changes

**Context Chaining**: Providers receive context from previous providers, enabling sophisticated information layering

**Error Resilience**: Provider failures don't break the entire context system

## Built-in ContextProvider Types

### 1. ConversationHistoryProvider

Manages conversation memory with automatic history management.

**Purpose**: Maintains recent conversation turns for natural dialogue continuity.

**Configuration Options**:
- `max_items` (int): Maximum conversation turns to remember (default: 10)

**Use Cases**:
- Multi-turn conversations
- Context-aware responses
- Reference to previous topics

**Example Configuration**:
```python
context_config = [
    {
        "type": "conversation_history",
        "max_items": 15  # Remember last 15 exchanges
    }
]
```

### 2. FixedFileProvider

Provides content from specific files with change detection.

**Purpose**: Include specific documentation, configuration, or reference files in context.

**Configuration Options**:
- `file_path` (str, required): Path to the file
- `encoding` (str): File encoding (default: "utf-8")
- `check_updates` (bool): Monitor file changes (default: True)

**Use Cases**:
- API documentation
- Project specifications
- Configuration references
- Knowledge base articles

**Example Configuration**:
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

Intelligently selects and provides relevant source code context.

**Purpose**: Automatically include relevant source files based on conversation topics and file analysis.

**Configuration Options**:
- `base_path` (str): Base directory for code analysis (default: ".")
- `max_files` (int): Maximum files to include (default: 50)
- `max_file_size` (int): Maximum file size in bytes (default: 10000)
- `file_extensions` (list): File types to include
- `include_patterns` (list): File patterns to include
- `exclude_patterns` (list): File patterns to exclude

**Use Cases**:
- Code review assistance
- Development guidance
- Bug analysis
- Architecture discussions

**Example Configuration**:
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

Wrapper provider that automatically manages context size limits.

**Purpose**: Ensure context doesn't exceed token/character limits while preserving important information.

**Configuration Options**:
- `provider` (dict): Configuration for the wrapped provider
- `max_chars` (int): Maximum character count
- `max_tokens` (int): Maximum token count  
- `cut_strategy` (str): How to truncate ("start", "end", "middle")
- `preserve_sections` (bool): Whether to keep complete sections

**Use Cases**:
- Large file handling
- API response management
- Memory optimization
- Token limit compliance

**Example Configuration**:
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

## Creating Custom ContextProviders

### Step 1: Understand the ContextProvider Interface

All custom providers must inherit from the `ContextProvider` base class and implement these abstract methods:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from refinire.agents.context_provider import ContextProvider

class CustomProvider(ContextProvider):
    provider_name = "custom_provider"  # Unique identifier
    
    def __init__(self, **config):
        """Initialize with configuration parameters"""
        super().__init__()
        # Initialize your provider with config parameters
    
    @abstractmethod
    def get_context(self, query: str, previous_context: str = "", **kwargs) -> str:
        """
        Generate context based on user query and previous context
        
        Args:
            query: User's current input/question
            previous_context: Context from previous providers in chain
            **kwargs: Additional parameters
            
        Returns:
            str: Context information to add to the prompt
        """
        pass
    
    @abstractmethod
    def update(self, interaction: Dict[str, Any]) -> None:
        """
        Update provider state with interaction results
        
        Args:
            interaction: Dict containing user input, agent response, etc.
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all stored state/cache"""
        pass
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """
        Return configuration schema for validation
        
        Returns:
            Dict describing expected configuration parameters
        """
        return {
            "type": "object",
            "properties": {
                # Define your configuration parameters here
            },
            "required": []  # List required parameters
        }
```

### Step 2: Example - Database ContextProvider

Let's create a custom provider that queries a database for relevant information:

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
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.database_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
        except Exception as e:
            raise RuntimeError(f"Failed to connect to database: {e}")
    
    def _search_database(self, query: str) -> List[Dict[str, Any]]:
        """Search database for relevant entries"""
        if not self.connection:
            self._connect()
        
        # Simple keyword-based search (enhance with vector search, FTS, etc.)
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
        """Get relevant database entries as context"""
        try:
            results = self._search_database(query)
            
            if not results:
                return ""
            
            context_parts = ["=== Database Information ==="]
            
            for i, result in enumerate(results, 1):
                # Format database results for context
                entry_text = f"Entry {i}:\n"
                for key, value in result.items():
                    if value:  # Skip empty values
                        entry_text += f"  {key}: {value}\n"
                context_parts.append(entry_text)
            
            return "\n".join(context_parts)
            
        except Exception as e:
            # Log error but don't break the context chain
            print(f"Database context provider error: {e}")
            return ""
    
    def update(self, interaction: Dict[str, Any]) -> None:
        """Update with interaction results (optional for database provider)"""
        # Could log successful queries, update search rankings, etc.
        pass
    
    def clear(self) -> None:
        """Clear any cached data"""
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
                    "description": "Path to SQLite database file"
                },
                "table_name": {
                    "type": "string", 
                    "description": "Database table to query"
                },
                "query_column": {
                    "type": "string",
                    "default": "content",
                    "description": "Column to search in"
                },
                "limit": {
                    "type": "integer",
                    "default": 5,
                    "description": "Maximum results to return"
                }
            },
            "required": ["database_path", "table_name"]
        }
```

### Step 3: Example - API ContextProvider

Create a provider that fetches information from external APIs:

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
        
        # Add API key to headers if provided
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def _make_api_request(self, query: str) -> Optional[Dict[str, Any]]:
        """Make API request for query"""
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
            print(f"API request failed: {e}")
            return None
    
    def _format_api_response(self, data: Dict[str, Any]) -> str:
        """Format API response for context"""
        if not data:
            return ""
        
        context_parts = ["=== External Information ==="]
        
        # Adapt this based on your API response structure
        results = data.get("results", [])
        if isinstance(results, list):
            for i, item in enumerate(results[:self.max_results], 1):
                if isinstance(item, dict):
                    title = item.get("title", f"Result {i}")
                    content = item.get("content", item.get("description", ""))
                    if content:
                        context_parts.append(f"{title}:\n{content}\n")
        
        return "\n".join(context_parts)
    
    def get_context(self, query: str, previous_context: str = "", **kwargs) -> str:
        """Get information from API based on query"""
        api_data = self._make_api_request(query)
        return self._format_api_response(api_data)
    
    def update(self, interaction: Dict[str, Any]) -> None:
        """Update with interaction results"""
        # Could cache successful queries, update usage metrics, etc.
        pass
    
    def clear(self) -> None:
        """Clear any cached data"""
        # Clear request cache if implemented
        pass
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "base_url": {
                    "type": "string",
                    "description": "API endpoint URL"
                },
                "api_key": {
                    "type": "string",
                    "description": "API authentication key"
                },
                "headers": {
                    "type": "object",
                    "description": "Additional HTTP headers"
                },
                "query_param": {
                    "type": "string",
                    "default": "q",
                    "description": "Query parameter name"
                },
                "max_results": {
                    "type": "integer",
                    "default": 3,
                    "description": "Maximum results to return"
                }
            },
            "required": ["base_url"]
        }
```

### Step 4: Registering Custom Providers

To use custom providers with RefinireAgent, register them with the ContextProviderFactory:

```python
from refinire.agents.context_provider_factory import ContextProviderFactory

# Register your custom providers
ContextProviderFactory.register_provider("database", DatabaseContextProvider)
ContextProviderFactory.register_provider("api", APIContextProvider)

# Now use them in agent configuration
from refinire import RefinireAgent

agent = RefinireAgent(
    name="enhanced_assistant",
    generation_instructions="Use provided context to give detailed answers.",
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

## Advanced ContextProvider Patterns

### 1. Caching and Performance Optimization

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
        """Generate cache key for query"""
        return hashlib.md5(query.lower().encode()).hexdigest()
    
    @lru_cache(maxsize=100)
    def _expensive_operation(self, query: str) -> str:
        """Cached expensive operation"""
        # Implement your expensive context generation here
        pass
    
    def get_context(self, query: str, previous_context: str = "", **kwargs) -> str:
        cache_key = self._cache_key(query)
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = self._expensive_operation(query)
        self._cache[cache_key] = result
        return result
```

### 2. Conditional Context Providers

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

### 3. Multi-Source Aggregation Provider

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
                continue  # Skip failed providers
        
        if self.aggregation_strategy == "concat":
            return "\n\n".join(results)
        elif self.aggregation_strategy == "prioritized":
            return results[0] if results else ""
        # Add more aggregation strategies as needed
```

## Best Practices for Custom ContextProviders

### 1. Error Handling and Resilience

- Always wrap external calls in try-catch blocks
- Return empty strings rather than raising exceptions
- Log errors for debugging but don't break the context chain
- Implement timeouts for external API calls

### 2. Performance Considerations

- Cache expensive operations when possible
- Implement reasonable timeouts for external calls
- Limit the amount of context returned to avoid token limits
- Use lazy loading for resource-intensive operations

### 3. Configuration Design

- Provide sensible defaults for all parameters
- Use clear, descriptive parameter names
- Include comprehensive configuration schema
- Support both simple and advanced configuration options

### 4. Context Quality

- Format context clearly with headers and structure
- Remove unnecessary information to focus on relevance
- Consider context ordering and priority
- Ensure context is actionable and useful for the AI

### 5. Testing and Validation

```python
import unittest
from unittest.mock import patch, MagicMock

class TestCustomContextProvider(unittest.TestCase):
    def setUp(self):
        self.provider = CustomContextProvider(
            # Test configuration
        )
    
    def test_get_context_success(self):
        """Test successful context retrieval"""
        result = self.provider.get_context("test query")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_get_context_failure(self):
        """Test graceful failure handling"""
        with patch.object(self.provider, '_external_api_call', side_effect=Exception("API Error")):
            result = self.provider.get_context("test query")
            self.assertEqual(result, "")  # Should return empty string, not raise
    
    def test_configuration_validation(self):
        """Test configuration schema validation"""
        schema = self.provider.get_config_schema()
        self.assertIn("properties", schema)
        self.assertIn("required", schema)
```

## Integration Examples

### Complete Agent with Multiple Custom Providers

```python
from refinire import RefinireAgent
from your_providers import DatabaseContextProvider, APIContextProvider

# Register custom providers
ContextProviderFactory.register_provider("database", DatabaseContextProvider)
ContextProviderFactory.register_provider("api", APIContextProvider)

# Create agent with rich context
agent = RefinireAgent(
    name="knowledge_assistant",
    generation_instructions="""
    You are a knowledgeable assistant with access to multiple information sources.
    Use the provided context from conversations, database, and external APIs to give
    comprehensive and accurate answers. Always cite your sources when possible.
    """,
    context_providers_config=[
        # Remember recent conversation
        {
            "type": "conversation_history",
            "max_items": 10
        },
        # Include project documentation
        {
            "type": "fixed_file",
            "file_path": "docs/project_overview.md"
        },
        # Query internal knowledge base
        {
            "type": "database",
            "database_path": "knowledge_base.db",
            "table_name": "documents",
            "query_column": "content",
            "limit": 5
        },
        # Get external information when needed
        {
            "type": "api",
            "base_url": "https://api.knowledge-source.com/search",
            "api_key": "your-api-key",
            "max_results": 3
        },
        # Wrap everything in size limits
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

# Use the enhanced agent
result = agent.run("How do I implement user authentication in our system?")
print(result.content)
```

This comprehensive guide provides everything needed to understand and extend Refinire's ContextProvider system for sophisticated AI agent memory and information access patterns.