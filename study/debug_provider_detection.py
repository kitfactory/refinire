#!/usr/bin/env python3
"""
Debug Provider Detection - Check provider detection logic
プロバイダー検出デバッグ - プロバイダー検出ロジックをチェック

This debugs the provider detection logic in get_llm.
get_llmのプロバイダー検出ロジックをデバッグします。
"""

import os


def debug_provider_detection():
    """
    Debug provider detection logic
    プロバイダー検出ロジックをデバッグ
    """
    print("🔍 Debug Provider Detection Logic")
    print("=" * 40)
    
    try:
        from refinire.core.model_parser import parse_model_id, detect_provider_from_environment
        
        # Test model parsing
        print("\n📋 Test 1: Model ID Parsing")
        test_models = ["gpt-4o-mini", "openai:gpt-4o-mini", "ollama:gpt-4o-mini"]
        
        for model in test_models:
            parsed_provider, model_name, model_tag = parse_model_id(model)
            print(f"   {model} -> provider: {parsed_provider}, name: {model_name}, tag: {model_tag}")
        
        # Test environment detection  
        print("\n📋 Test 2: Environment Detection")
        env_provider = detect_provider_from_environment(None)
        print(f"   Environment provider: {env_provider}")
        
        # Test provider candidate logic
        print("\n📋 Test 3: Provider Candidate Logic")
        def get_provider_candidate(model: str):
            """Copy of the logic from get_llm"""
            if "gpt" in model:
                return "openai"
            if "o3" in model or "o4" in model:
                return "openai"
            elif "gemini" in model:
                return "google"
            elif "claude" in model:
                return "anthropic"
            else:
                return "ollama"
        
        test_models = ["gpt-4o-mini", "gpt-4o", "gemini-pro", "claude-3-opus", "llama-3"]
        for model in test_models:
            candidate = get_provider_candidate(model)
            print(f"   {model} -> candidate: {candidate}")
        
        # Test full provider resolution for gpt-4o-mini
        print("\n📋 Test 4: Full Provider Resolution for gpt-4o-mini")
        model = "gpt-4o-mini"
        parsed_provider, model_name, model_tag = parse_model_id(model)
        print(f"   Parsed provider: {parsed_provider}")
        print(f"   Model name: {model_name}")
        
        if parsed_provider:
            final_provider = parsed_provider
            print(f"   Using parsed provider: {final_provider}")
        else:
            env_provider = detect_provider_from_environment(None)
            if env_provider:
                final_provider = env_provider
                print(f"   Using environment provider: {final_provider}")
            else:
                final_provider = get_provider_candidate(model_name)
                print(f"   Using candidate provider: {final_provider}")
        
        print(f"   Final provider for gpt-4o-mini: {final_provider}")
        
        # Check environment variables that might affect detection
        print("\n📋 Test 5: Environment Variables")
        env_vars = [
            "REFINIRE_DEFAULT_LLM_PROVIDER",
            "REFINIRE_DEFAULT_LLM_MODEL", 
            "OPENAI_API_KEY",
            "OLLAMA_BASE_URL",
            "CLAUDE_API_KEY",
            "GEMINI_API_KEY",
        ]
        
        for var in env_vars:
            value = os.environ.get(var, "Not set")
            print(f"   {var}: {value}")
        
    except Exception as e:
        print(f"❌ Provider detection debug failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_provider_detection()