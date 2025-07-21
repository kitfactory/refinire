#!/usr/bin/env python3
"""
Debug get_llm - Check what get_llm returns for gpt-4o-mini
get_llmデバッグ - gpt-4o-miniに対してget_llmが何を返すかチェック

This debugs what model get_llm creates for gpt-4o-mini.
gpt-4o-miniに対してget_llmがどのモデルを作成するかデバッグします。
"""

import os


def debug_get_llm():
    """
    Debug get_llm model creation
    get_llmモデル作成をデバッグ
    """
    print("🔍 Debug get_llm Model Creation")
    print("=" * 40)
    
    try:
        from refinire.core.llm import get_llm
        
        # Test different model specifications
        test_models = [
            "gpt-4o-mini",
            {"model": "gpt-4o-mini"},
            {"model": "gpt-4o-mini", "provider": "openai"},
        ]
        
        for i, model_spec in enumerate(test_models):
            print(f"\n📋 Test {i+1}: get_llm({model_spec})")
            try:
                model = get_llm(model=model_spec)
                print(f"   Model type: {type(model)}")
                print(f"   Model: {model}")
                
                # Check model attributes
                if hasattr(model, 'model'):
                    print(f"   Model.model: {model.model}")
                if hasattr(model, 'provider'):
                    print(f"   Model.provider: {model.provider}")
                if hasattr(model, 'ollama_client'):
                    print(f"   Has ollama_client: True")
                if hasattr(model, 'openai_client'):
                    print(f"   Has openai_client: True")
                    
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        # Test with explicit provider
        print(f"\n📋 Test with explicit OpenAI provider:")
        try:
            model = get_llm(provider="openai", model="gpt-4o-mini")
            print(f"   OpenAI model type: {type(model)}")
            print(f"   OpenAI model: {model}")
        except Exception as e:
            print(f"   ❌ OpenAI provider failed: {e}")
        
        # Test Ollama provider for comparison
        print(f"\n📋 Test with explicit Ollama provider:")
        try:
            model = get_llm(provider="ollama", model="gpt-4o-mini")
            print(f"   Ollama model type: {type(model)}")
            print(f"   Ollama model: {model}")
        except Exception as e:
            print(f"   ❌ Ollama provider failed: {e}")
            
        # Check default provider detection
        print(f"\n📋 Check provider detection logic:")
        try:
            from refinire.core.llm import _determine_provider
            provider = _determine_provider("gpt-4o-mini")
            print(f"   Provider for 'gpt-4o-mini': {provider}")
        except Exception as e:
            print(f"   ❌ Provider detection failed: {e}")
        
    except Exception as e:
        print(f"❌ get_llm debug failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_get_llm()