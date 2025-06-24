#!/usr/bin/env python3
"""
Simple LLM Query Example

English: A simple example demonstrating how to query an LLM with RefinireAgent.
日本語: RefinireAgent を使って LLM に問い合わせる簡単な例。
"""
from refinire import RefinireAgent

def main():
    agent = RefinireAgent(
        name="simple_query_agent",
        generation_instructions="You are a helpful assistant.",
        model="gpt-4o"
    )
    user_input = "Translate 'Hello, world!' into French."
    result = agent.run(user_input)
    print("Response:")
    print(result)

if __name__ == '__main__':
    main() 
