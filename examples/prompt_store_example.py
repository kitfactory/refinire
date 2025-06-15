"""
Example of using PromptStore for multilingual prompt management
多言語プロンプト管理のためのPromptStore使用例
"""

from pathlib import Path
from refinire.core import PromptStore, detect_system_language, get_default_storage_dir


def main():
    # PromptStore uses class methods with internal instance management
    # Uses REFINIRE_DIR environment variable or ~/.refinire by default
    
    print(f"Storage directory: {get_default_storage_dir()}")
    
    # Get the internal instance to show database path (for demo purposes)
    instance = PromptStore._get_instance()
    print(f"Database path: {instance.db_path}")
    
    print(f"System language detected: {detect_system_language()}")
    print()
    
    # Store a prompt in English (will auto-translate to Japanese)
    print("Storing English prompt...")
    greeting_prompt = PromptStore.store(
        name="greeting",
        content="Hello! I'm an AI assistant. How can I help you today?",
        tag="introduction",
        language="en"
    )
    print(f"Stored prompt: {greeting_prompt.name}")
    print(f"Available languages: {list(greeting_prompt.content.keys())}")
    print()
    
    # Store a prompt in Japanese (will auto-translate to English)
    print("Storing Japanese prompt...")
    analysis_prompt = PromptStore.store(
        name="analysis",
        content="以下のテキストを分析し、重要なポイントを3つ挙げてください：\n{text}",
        tag="task",
        language="ja"
    )
    print(f"Stored prompt: {analysis_prompt.name}")
    print()
    
    # Retrieve prompts in different languages
    print("Retrieving prompts:")
    greeting_en = PromptStore.get('greeting', language='en')
    greeting_ja = PromptStore.get('greeting', language='ja')
    analysis_ja = PromptStore.get('analysis', language='ja')
    analysis_en = PromptStore.get('analysis', language='en')
    
    print(f"Greeting (EN): {greeting_en}")
    print(f"Greeting (JA): {greeting_ja}")
    print()
    print(f"Analysis (JA): {analysis_ja}")
    print(f"Analysis (EN): {analysis_en}")
    print()
    
    # Get prompt with specific tag
    greeting_tagged = PromptStore.get('greeting', tag='introduction', language='en')
    print(f"Greeting with 'introduction' tag: {greeting_tagged}")
    print()
    
    # Show metadata
    print("Prompt metadata examples:")
    if greeting_en:
        print(f"Greeting metadata: {greeting_en.get_metadata()}")
    if analysis_ja:
        print(f"Analysis metadata: {analysis_ja.get_metadata()}")
    print()
    
    # List all prompts
    print("All stored prompts:")
    for prompt in PromptStore.list_prompts():
        print(f"- {prompt.name} (tag: {prompt.tag or 'None'})")
    print()
    
    # List prompts with specific name
    print("All 'greeting' prompts:")
    for prompt in PromptStore.list_prompts(name="greeting"):
        print(f"- {prompt.name} (tag: {prompt.tag or 'None'})")
    print()
    
    # Delete specific prompt by name and tag
    print("Deleting greeting prompts with 'introduction' tag:")
    deleted = PromptStore.delete("greeting", tag="introduction")
    print(f"Deleted {deleted} prompt(s)")
    
    # Store without auto-translation
    print("\nStoring without translation:")
    technical_prompt = PromptStore.store(
        name="technical",
        content="Generate Python code for {task}",
        tag="generation",
        language="en",
        auto_translate=False
    )
    print(f"Languages available: {list(technical_prompt.content.keys())}")
    
    print(f"\nDatabase is automatically persisted at: {instance.db_path}")
    print("The database will persist between runs unless manually deleted.")


if __name__ == "__main__":
    main()