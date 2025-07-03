# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Refinire** is an AI agent development platform that provides unified interfaces across multiple LLM providers (OpenAI, Anthropic, Google, Ollama). The project recently migrated from "agents-sdk-models" to "refinire" and focuses on simplifying AI agent development through three core pillars:

1. **Unified LLM Interface** - Single API across providers
2. **Autonomous Quality Assurance** - Built-in evaluation and improvement
3. **Composable Flow Architecture** - Flexible workflow orchestration

## Development Commands

### Testing
```bash
# Run all tests
source .venv/bin/activate && python -m pytest

# Run tests with coverage
source .venv/bin/activate && python -m pytest --cov=src/refinire --cov-report=html

# Run specific test file
source .venv/bin/activate && python -m pytest tests/test_anthropic.py

# Run tests for specific module
source .venv/bin/activate && python -m pytest tests/test_flow.py -v
```

### Type Checking
```bash
# Run mypy type checking (strict mode enabled)
source .venv/bin/activate && python -m mypy src/refinire
```

### Building and Installation
```bash
# Install in development mode
source .venv/bin/activate && pip install -e .

# Install with development dependencies
source .venv/bin/activate && pip install -e .[dev]

# Build package
source .venv/bin/activate && python -m build
```

### Documentation
```bash
# Serve documentation locally (MkDocs)
source .venv/bin/activate && mkdocs serve

# Build documentation
source .venv/bin/activate && mkdocs build
```

## Code Architecture

### Core Components

**src/refinire/core/** - Core functionality
- `llm.py` - Provider abstraction layer with `get_llm()` factory
- `anthropic.py` - Claude int
egration
- `gemini.py` - Google Gemini integration  
- `ollama.py` - Local Ollama integration
- `tracing.py` - Execution monitoring and observability
- `trace_registry.py` - Centralized trace storage and search
- `prompt_store.py` - Prompt management and storage
- `message.py` - Message handling and localization

**src/refinire/agents/** - Comprehensive agent framework
- **flow/** - Workflow orchestration
  - `flow.py` - Workflow orchestration engine for complex multi-step processes  
  - `step.py` - Individual workflow step implementations (Function, Condition, Parallel, etc.)
  - `context.py` - Shared state management between steps
- **pipeline/** - AI agent functionality
  - `llm_pipeline.py` - RefinireAgent with evaluation and tool support
- **Specialized agents**
  - `gen_agent.py` - General-purpose generation agents
  - `clarify_agent.py` - Requirement clarification workflows  
  - `extractor.py`, `validator.py`, `router.py`, `notification.py` - Specialized agents

**Provider Support** (unified under `get_llm()`)
- OpenAI support via base agents library
- Anthropic Claude via core.anthropic
- Google Gemini via core.gemini
- Local Ollama via core.ollama

### Key Architectural Patterns

**Factory Pattern**: `get_llm(provider="openai", model="gpt-4o-mini")` provides unified access across providers

**Flow-Based Architecture**: Complex workflows built from composable steps:
```python
Flow({
    "start": FunctionStep("analyze", analyze_input),
    "route": ConditionStep("route", route_by_complexity, "simple", "complex"),  
    "simple": SimpleAgent(),
    "complex": ExpertAgent()
})
```

**Context Management**: `Context` object carries shared state between steps with automatic lifecycle management

**Tracing & Observability**: All operations automatically traced via `TraceRegistry` for monitoring and debugging

**Evaluation Pipeline**: Built-in quality assessment with configurable thresholds and automatic improvement

## Development Guidelines

### Code Comments and Documentation

**Bilingual Comments**: All source code comments should be written in both Japanese and English. This ensures the codebase is accessible to both Japanese and international developers. Format:
```python
# This function processes user input
# この関数はユーザー入力を処理します
def process_input(data):
    pass
```

**Documentation**: Create both English and Japanese versions for all documentation:
- English version: `feature.md`
- Japanese version: `feature_ja.md`
- Both versions should contain equivalent information and be kept in sync

### Provider Integration
When adding provider support, implement the `Model` interface and integrate through `get_llm()` factory. All providers should support:
- Temperature control
- Structured output via Pydantic models
- Tool/function calling capabilities
- Async execution

### Flow Development  
Workflows should be built using composable steps rather than monolithic functions. Prefer:
- `FunctionStep` for pure functions
- `ConditionStep` for branching logic
- `{"parallel": [...]}` syntax for concurrent operations
- `RefinireAgent` for LLM integration

### Testing Strategy
Tests use dependency injection patterns with fixtures. Each provider has isolation through monkeypatching to avoid external API calls during testing. Key test categories:
- Unit tests for individual components
- Integration tests for provider interactions
- Flow execution tests for complex workflows

### Context and State Management
Use `Context.shared_state` for data passing between steps. Call `context.finish()` to terminate flows. Avoid direct step-to-step communication - use context as the single source of truth.

### Tracing and Debugging
All operations are automatically traced. Use `get_global_registry().search_by_flow_name()` for debugging. Enable console tracing via `enable_console_tracing()` for development.

### Git Commit Messages
When creating git commits, use clean, professional commit messages without external tool references:
- Do NOT include "Generated with Claude Code" or similar tool references
- Do NOT include links to claude.ai/code or other external tools
- Do NOT add "Co-Authored-By: Claude" signatures
- Focus on the actual changes made and their purpose
- Follow conventional commit format: `type: description`

Example good commit messages:
```
feat: Add LLMPipeline automatic evaluation support
docs: Update README to emphasize Flow architecture
fix: Resolve Context state management in parallel steps
```

## Dependencies

Core dependencies managed in `pyproject.toml`:
- **openai-agents**: Base SDK for agent functionality
- **pydantic**: Data validation and structured output
- **httpx**: HTTP client for API requests

Development dependencies include pytest, mypy (strict mode), mkdocs for documentation.

## File Organization

- `/examples/` - Comprehensive usage examples for all features
- `/docs/` - Detailed documentation (English/Japanese)  
- `/tests/` - Test suite with provider-specific test isolation
- `/src/refinire/` - Main source code
- `/scripts/` - Utility scripts for development


# 知見の集積
- 開発のサブフェーズが終わったら振り返りを行ってください。
- ユーザーが手直しを指示、特に設計の見直し指示した場合に、bad_generation.mdを記載してください。
- bad_generation.md には、事例として、どんな指示でどんな生成がされ、ユーザーからどのように指摘がされたかを記載してください。
- ユーザーの指示がなくてもフェーズが完了出来たら、good_generation.mdに記載してください。そこには、どうして生成がうまくできたかを自分なりに考えて書いてください。


# ガイド・設計文書
- 文書はソースコードのみの記載としない。ライブラリの利用者が実装しなければならないことを説明し、ソースコードの詳細すぎる箇所を説明をはぶくようにする。
- また設計文書でのソースコードの事例もコメントはユーザーが実装しなければならないことを伝えるようにする。
- 非推奨になったAPIの内容は記載しない

