"""
RefinireAgent example with generation and evaluation
生成と評価を行うRefinireAgentの例
"""

from refinire import RefinireAgent

def main():
    # Initialize pipeline with both generation and evaluation templates
    # 生成と評価のテンプレートでパイプラインを初期化
    pipeline = RefinireAgent(
        name="evaluated_generator",
        generation_instructions="""
        You are a helpful assistant that generates creative stories.
        あなたは創造的な物語を生成する役立つアシスタントです。

        Please generate a short story based on the user's input.
        ユーザーの入力に基づいて短い物語を生成してください。
        """,
        evaluation_instructions="""
        You are a story evaluator. Please evaluate the generated story based on:
        あなたは物語の評価者です。以下の基準で生成された物語を評価してください：

        1. Creativity (0-100)
           創造性（0-100）
        2. Coherence (0-100)
           一貫性（0-100）
        3. Emotional impact (0-100)
           感情的な影響（0-100）

        Calculate the average score and provide specific comments for each aspect.
        平均スコアを計算し、各側面について具体的なコメントを提供してください。
        """,
        # English: Use GPT-4o for generation. Japanese: 生成にGPT-4oを使用
        model="gpt-4o",
        # English: Use GPT-4o-mini for evaluation. Japanese: 評価にGPT-4o-miniを使用
        evaluation_model="gpt-4o-mini",
        threshold=70  # Minimum acceptable score
    )

    # Run the pipeline
    # パイプラインを実行
    user_input = "A story about a robot learning to paint"
    result = pipeline.run(user_input)
    
    if result:
        print("\nGenerated Story:")
        print(result)
    else:
        print("\nStory generation failed to meet quality threshold")

if __name__ == "__main__":
    main() 
