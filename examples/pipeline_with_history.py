"""
RefinireAgent example with conversation history
会話履歴（history）を活用したRefinireAgentの例
"""

from refinire import RefinireAgent

def main():
    # 直近2件の履歴をプロンプトに含める
    pipeline = RefinireAgent(
        name="history_example",
        generation_instructions="""
        You are a helpful assistant. Answer concisely.
        あなたは親切なアシスタントです。簡潔に答えてください。
        """,
        evaluation_instructions=None,
        model="gpt-4o",
        history_size=2,  # 直近2件のみ履歴に含める
    )

    # 連続した会話を実施
    user_inputs = [
        "What is the capital of France?",
        "And what is the population?",
        "What was my first question?",
        "Summarize our conversation so far in one sentence."
    ]

    for i, user_input in enumerate(user_inputs, 1):
        print(f"\n[{i}] User: {user_input}")
        result = pipeline.run(user_input)
        print(f"AI: {result}")

if __name__ == "__main__":
    main() 
