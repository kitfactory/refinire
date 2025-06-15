"""
Environment variable templates for Refinire platform

Minimal set of environment variables directly used by the library.
"""

def core_template():
    """Core LLM provider configuration template"""
    return {
        "ANTHROPIC_API_KEY": {
            "description": "Anthropic API key for Claude models\nGet from: https://console.anthropic.com/",
            "default": "",
            "required": False
        },
        "GOOGLE_API_KEY": {
            "description": "Google API key for Gemini models\nGet from: https://aistudio.google.com/app/apikey",
            "default": "",
            "required": False
        },
        "OLLAMA_BASE_URL": {
            "description": "Ollama server base URL for local models",
            "default": "http://localhost:11434",
            "required": False
        },
        "REFINIRE_DEFAULT_LLM_MODEL": {
            "description": "Default LLM model to use",
            "default": "gpt-4o-mini",
            "required": False
        }
    }