"""
GenAgent example with retry generation based on evaluation comment importance
評価コメントの重要度に基づくリトライ機能付きGenAgentの例

This example demonstrates how to use GenAgent with retry functionality (Flow/Step architecture).
この例は、リトライ機能付きGenAgent（Flow/Stepアーキテクチャ）の使用方法を示しています。
"""

import asyncio
from refinire import create_evaluated_gen_agent, create_simple_flow

async def main():
    """
    Main function demonstrating GenAgent with retry functionality
    リトライ機能付きGenAgentをデモンストレーションするメイン関数
    """
    
    print("=== GenAgent with Retry Functionality Example ===")

    # Method 1: Basic retry with evaluation threshold
    # 方法1: 評価閾値による基本的なリトライ
    print("\n--- Basic Retry with High Threshold ---")
    
    retry_agent = create_evaluated_gen_agent(
        name="retry_generator",
        generation_instructions="""
        Write a short tagline for a new AI writing assistant.
        新しいAIライティングアシスタントの短いキャッチフレーズを書いてください。
        
        Make it creative, memorable, and professional.
        創造的で記憶に残り、プロフェッショナルなものにしてください。
        """,
        evaluation_instructions="""
        Evaluate the tagline for clarity, creativity, and professional appeal.
        キャッチフレーズの明確さ、創造性、プロフェッショナルな魅力を評価してください。
        
        Consider:
        以下を考慮してください：
        1. Clarity (0-100) - Is the message clear?
           明確性（0-100） - メッセージは明確か？
        2. Creativity (0-100) - Is it creative and unique?
           創造性（0-100） - 創造的で独特か？
        3. Professional appeal (0-100) - Does it sound professional?
           プロフェッショナルな魅力（0-100） - プロフェッショナルに聞こえるか？
           
        Calculate the average score and provide detailed feedback.
        平均スコアを計算し、詳細なフィードバックを提供してください。
        """,
        model="gpt-4o",
        evaluation_model="gpt-4o-mini",
        threshold=85,  # High threshold to trigger retries / リトライを発生させる高い閾値
        retries=3
    )

    flow = create_simple_flow(retry_agent)
    
    test_inputs = [
        "AI powered writing assistant",
        "Creative writing tool for professionals"
    ]

    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        try:
            result = await flow.run(input_data=user_input)
            response = result.get_result("retry_generator_result")
            
            if response:
                print("✅ Final output (passed evaluation):")
                print(response)
            else:
                print("❌ Failed after all retries.")
                
            # Show retry history
            # リトライ履歴を表示
            history = retry_agent.get_pipeline_history()
            print(f"   Total attempts: {len(history)}")
            for i, entry in enumerate(history, 1):
                if 'evaluation' in entry:
                    eval_result = entry['evaluation']
                    print(f"   Attempt {i}: Score {eval_result.score}/100")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

    # Method 2: Retry with specific comment importance filtering
    # 方法2: 特定のコメント重要度フィルタリングによるリトライ
    print("\n\n--- Retry with Comment Importance Filtering ---")
    
    from refinire import GenAgent
    
    selective_retry_agent = GenAgent(
        name="selective_retry_generator",
        generation_instructions="""
        Write a professional marketing slogan for a tech startup.
        テックスタートアップ向けのプロフェッショナルなマーケティングスローガンを書いてください。
        
        Focus on innovation, reliability, and user experience.
        イノベーション、信頼性、ユーザーエクスペリエンスに焦点を当ててください。
        """,
        evaluation_instructions="""
        Evaluate the marketing slogan comprehensively.
        マーケティングスローガンを包括的に評価してください。
        
        Rate each aspect and provide comments with appropriate importance levels:
        各側面を評価し、適切な重要度レベルでコメントを提供してください：
        
        - Use "serious" for critical flaws that make the slogan unusable
          使用不可能にする重大な欠陥には "serious" を使用
        - Use "normal" for significant improvements needed  
          必要な重要な改善には "normal" を使用
        - Use "minor" for small suggestions
          小さな提案には "minor" を使用
        """,
        model="gpt-4o",
        evaluation_model="gpt-4o-mini",
        threshold=80,
        retries=3,
        retry_comment_importance=["serious", "normal"],  # Only retry on serious/normal comments
        store_result_key="selective_retry_result"
    )
    
    selective_flow = create_simple_flow(selective_retry_agent)
    
    selective_inputs = [
        "Innovative tech solutions for modern businesses",
        "Revolutionary software platform"
    ]
    
    for user_input in selective_inputs:
        print(f"\nSelective Input: {user_input}")
        try:
            result = await selective_flow.run(input_data=user_input)
            response = result.get_result("selective_retry_result")
            
            if response:
                print("✅ Final output (passed selective evaluation):")
                print(response)
            else:
                print("❌ Failed after selective retries.")
                
            # Show detailed retry analysis
            # 詳細なリトライ分析を表示
            history = selective_retry_agent.get_pipeline_history()
            print(f"\nRetry Analysis ({len(history)} attempts):")
            for i, entry in enumerate(history, 1):
                if 'evaluation' in entry:
                    eval_result = entry['evaluation']
                    print(f"  Attempt {i}: Score {eval_result.score}/100")
                    
                    # Show comment importance distribution
                    # コメント重要度分布を表示
                    serious_count = sum(1 for comment in eval_result.comment if comment.importance.value == "serious")
                    normal_count = sum(1 for comment in eval_result.comment if comment.importance.value == "normal")
                    minor_count = sum(1 for comment in eval_result.comment if comment.importance.value == "minor")
                    
                    print(f"    Comments - Serious: {serious_count}, Normal: {normal_count}, Minor: {minor_count}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

    # Method 3: Multi-Agent Flow with retry logic
    # 方法3: リトライロジック付きマルチエージェントフロー
    print("\n\n--- Multi-Agent Flow with Retry Logic ---")
    
    from refinire import Flow
    
    # Agent 1: Content generator with retry
    # エージェント1: リトライ付きコンテンツ生成者
    content_agent = GenAgent(
        name="content_creator",
        generation_instructions="""
        Create engaging social media content for a new product launch.
        新製品発売のための魅力的なソーシャルメディアコンテンツを作成してください。
        """,
        evaluation_instructions="""
        Evaluate social media content for engagement potential and brand alignment.
        エンゲージメントの可能性とブランド整合性についてソーシャルメディアコンテンツを評価してください。
        """,
        model="gpt-4o-mini",
        evaluation_model="gpt-4o-mini",
        threshold=75,
        retries=2,
        store_result_key="content_result",
        next_step="optimizer"
    )
    
    # Agent 2: Content optimizer (no retry needed)
    # エージェント2: コンテンツ最適化者（リトライ不要）
    optimizer_agent = GenAgent(
        name="optimizer", 
        generation_instructions="""
        Optimize the social media content for better performance.
        より良いパフォーマンスのためにソーシャルメディアコンテンツを最適化してください。
        
        Add relevant hashtags, improve call-to-action, and enhance readability.
        関連ハッシュタグを追加し、コールトゥアクションを改善し、読みやすさを向上させてください。
        """,
        model="gpt-4o-mini",
        threshold=70,  # Lower threshold, less likely to retry
        retries=1,
        store_result_key="optimized_result"
    )
    
    # Create multi-agent flow
    # マルチエージェントフローを作成
    retry_flow = Flow("retry_content_flow")
    retry_flow.add_step(content_agent)
    retry_flow.add_step(optimizer_agent)
    
    flow_inputs = [
        "Launch of our new AI-powered productivity app",
        "Revolutionary smart home device release"
    ]
    
    for user_input in flow_inputs:
        print(f"\nFlow Input: {user_input}")
        try:
            result = await retry_flow.run(input_data=user_input)
            
            # Show results from both agents
            # 両エージェントからの結果を表示
            content = result.get_result("content_result")
            optimized = result.get_result("optimized_result")
            
            if content:
                print("✅ Content Created:")
                print(content)
            if optimized:
                print("✅ Optimized Version:")
                print(optimized)
                
            # Show retry statistics for both agents
            # 両エージェントのリトライ統計を表示
            content_history = content_agent.get_pipeline_history()
            optimizer_history = optimizer_agent.get_pipeline_history()
            print(f"   Content retries: {len(content_history)}, Optimizer retries: {len(optimizer_history)}")
            
        except Exception as e:
            print(f"❌ Flow Error: {e}")

def sync_main():
    """
    Synchronous wrapper for the async main function
    非同期main関数の同期ラッパー
    """
    asyncio.run(main())

if __name__ == "__main__":
    sync_main() 
