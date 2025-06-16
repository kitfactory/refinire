"""
Example: Retry generation based on evaluation comment importance
例: 評価コメントの重要度に基づくリトライ例
"""

from refinire import RefinireAgent


def main():
    # English: This example uses a strict evaluation and may fail even after retries.
    # 日本語: この例は厳しい評価を行い、リトライ後でも生成が失敗と判断される場合を示しています。
    # English: Create pipeline that retries only on serious comments
    # 日本語: シリアスなコメントがある場合のみリトライするパイプラインを作成
    pipeline = RefinireAgent(
        name="retry_example",
        generation_instructions="""
Write a short tagline for a new AI writing assistant.
        """.strip(),
        evaluation_instructions="""
Evaluate the tagline for clarity and creativity.:""".strip(),
        model="gpt-4o",
        evaluation_model="gpt-4o-mini",
        threshold=90,
        retries=3,
        retry_comment_importance=["serious","normal","minor"],  # retry only on serious feedback
    )

    user_input = "AI powered writing assistant"
    # 英語: Run pipeline and print final output
    # 日本語: パイプラインを実行して最終結果を表示
    result = pipeline.run(user_input)
    if result:
        print("Final output:", result)
    else:
        print("Failed after retries.")


if __name__ == "__main__":
    main() 
