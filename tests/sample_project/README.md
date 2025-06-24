# Sample Project for Testing

This is a sample project for testing SourceCodeProvider functionality.

## Structure

```
tests/sample_project/
├── .gitignore          # Git ignore patterns
├── .venv/              # Virtual environment (dummy)
├── __pycache__/        # Python cache (dummy)
├── build/              # Build directory (dummy)
├── src/
│   └── refinire/
│       ├── __init__.py
│       └── agents/
│           ├── __init__.py
│           ├── context_provider.py
│           └── providers/
│               ├── __init__.py
│               ├── conversation_history.py
│               └── source_code.py
├── tests/
│   └── test_context_provider.py
└── docs/
    └── README.md
```

## Purpose

This project is used to test the SourceCodeProvider's ability to:
- Respect .gitignore patterns
- Scan file trees
- Identify relevant files
- Handle different file types and structures 