#!/usr/bin/env python3
"""
Test script to demonstrate the fix for duplicate context issue
重複コンテキスト問題の修正を実証するテストスクリプト

Before the fix: RefinireAgent would show both "Context:" and "Previous context:" sections
After the fix: Only "Context:" section appears when using context_providers_config

修正前: RefinireAgentは「Context:」と「Previous context:」の両方のセクションを表示
修正後: context_providers_configを使用する場合は「Context:」セクションのみ表示
"""

import sys
import os

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent


def test_no_duplicate_context():
    """Test that there's no duplicate context when using conversation_history provider"""
    print("=== Testing No Duplicate Context ===")
    
    # Agent with conversation history provider
    agent = RefinireAgent(
        name="test_agent",
        generation_instructions="You are a helpful assistant.",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 3}
        ],
        model="gpt-4o-mini"
    )
    
    # Add some history manually for testing
    agent.session_history = [
        "User: Hello, I'm John",
        "Assistant: Nice to meet you, John!",
        "User: What's your name?",
        "Assistant: I'm your helpful assistant."
    ]
    
    # Update context provider with history using the proper format
    for provider in agent.context_providers:
        if hasattr(provider, 'update') and hasattr(provider, 'history'):
            # Add conversation entries directly to the history
            provider.history = [
                "User: Hello, I'm John\nAssistant: Nice to meet you, John!",
                "User: What's your name?\nAssistant: I'm your helpful assistant."
            ]
    
    # Build prompt
    prompt = agent._build_prompt("How are you today?")
    
    print("\n--- Generated Prompt ---")
    print(prompt)
    print("\n--- Analysis ---")
    
    # Check for duplicate sections
    context_count = prompt.count("Context:")
    previous_context_count = prompt.count("Previous context:")
    
    print(f"'Context:' appears {context_count} time(s)")
    print(f"'Previous context:' appears {previous_context_count} time(s)")
    
    if context_count == 1 and previous_context_count == 0:
        print("✅ SUCCESS: No duplicate context sections!")
        print("✅ Only 'Context:' section appears (from conversation_history provider)")
    elif context_count == 0 and previous_context_count == 1:
        print("⚠️  Only 'Previous context:' section appears (from session_history)")
    elif context_count == 1 and previous_context_count == 1:
        print("❌ ISSUE: Both 'Context:' and 'Previous context:' sections appear")
        print("❌ This indicates duplicate content issue")
    else:
        print(f"❓ Unexpected result: Context:{context_count}, Previous context:{previous_context_count}")
    
    return context_count == 1 and previous_context_count == 0


def test_explicit_no_context_providers():
    """Test that no context sections appear when explicitly disabling providers"""
    print("\n=== Testing Explicit No Context Providers ===")
    
    # Agent with explicitly disabled context providers
    agent = RefinireAgent(
        name="test_agent",
        generation_instructions="You are a helpful assistant.",
        context_providers_config=[],  # Explicitly empty
        model="gpt-4o-mini"
    )
    
    # Add some session history
    agent.session_history = [
        "User: Hello",
        "Assistant: Hi there!"
    ]
    
    # Build prompt
    prompt = agent._build_prompt("How are you?")
    
    print("\n--- Generated Prompt ---")
    print(prompt)
    print("\n--- Analysis ---")
    
    # Check for context sections
    context_count = prompt.count("Context:")
    previous_context_count = prompt.count("Previous context:")
    
    print(f"'Context:' appears {context_count} time(s)")
    print(f"'Previous context:' appears {previous_context_count} time(s)")
    
    if context_count == 0 and previous_context_count == 1:
        print("✅ SUCCESS: Only session history appears as 'Previous context:'")
        print("✅ No context providers are active")
    elif context_count == 0 and previous_context_count == 0:
        print("✅ SUCCESS: No context sections (no history)")
    else:
        print(f"❓ Unexpected result: Context:{context_count}, Previous context:{previous_context_count}")
    
    return context_count == 0


def test_default_behavior():
    """Test default behavior (should create conversation_history provider automatically)"""
    print("\n=== Testing Default Behavior ===")
    
    # Agent with default settings (no explicit config)
    agent = RefinireAgent(
        name="test_agent",
        generation_instructions="You are a helpful assistant.",
        model="gpt-4o-mini"
    )
    
    print(f"Number of context providers: {len(agent.context_providers)}")
    if agent.context_providers:
        print(f"Provider type: {agent.context_providers[0].__class__.__name__}")
    
    # Build prompt without history
    prompt = agent._build_prompt("Hello")
    
    print("\n--- Generated Prompt ---")
    print(prompt)
    print("\n--- Analysis ---")
    
    # Should have conversation provider but no content yet
    context_count = prompt.count("Context:")
    previous_context_count = prompt.count("Previous context:")
    
    print(f"'Context:' appears {context_count} time(s)")
    print(f"'Previous context:' appears {previous_context_count} time(s)")
    
    if len(agent.context_providers) == 1 and context_count == 0 and previous_context_count == 0:
        print("✅ SUCCESS: Default conversation provider created, no content yet")
    else:
        print(f"❓ Unexpected result")
    
    return len(agent.context_providers) == 1


def main():
    """Run all tests"""
    print("Testing RefinireAgent Context Duplication Fix")
    print("=" * 50)
    
    test1_result = test_no_duplicate_context()
    test2_result = test_explicit_no_context_providers()
    test3_result = test_default_behavior()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"✅ No duplicate context test: {'PASSED' if test1_result else 'FAILED'}")
    print(f"✅ Explicit no providers test: {'PASSED' if test2_result else 'FAILED'}")
    print(f"✅ Default behavior test: {'PASSED' if test3_result else 'FAILED'}")
    
    if all([test1_result, test2_result, test3_result]):
        print("\n🎉 ALL TESTS PASSED!")
        print("The duplicate context issue has been successfully fixed.")
    else:
        print("\n❌ Some tests failed.")


if __name__ == "__main__":
    main()