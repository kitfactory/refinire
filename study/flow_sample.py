#!/usr/bin/env python3
"""
Flow Sample - Refinireでのワークフロー機能サンプル
フローサンプル - 複数ステップからなる複雑なワークフローの実行

This demonstrates how to use Flow for complex multi-step workflows.
複雑な複数ステップワークフローにFlowを使用する方法を実演します。
"""

import asyncio
import os
from refinire.agents.flow import Flow, FunctionStep, ConditionStep, Context
from refinire import RefinireAgent


async def flow_demo():
    """
    Demonstrate Flow functionality with a content creation workflow
    コンテンツ作成ワークフローでFlow機能をデモンストレーション
    """
    print("🌊 Flow Sample - Content Creation Workflow")
    print("🌊 フローサンプル - コンテンツ作成ワークフロー")
    print("=" * 60)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        print("❌ OPENAI_API_KEY環境変数を設定してください。")
        return
    
    # Define workflow functions / ワークフロー関数を定義
    async def analyze_topic(context: Context) -> str:
        """Analyze the topic and determine content type"""
        print("📋 Step 1: Analyzing topic...")
        print("📋 ステップ1: トピック分析中...")
        
        analyzer = RefinireAgent(
            name="topic_analyzer",
            generation_instructions="""
Analyze the given topic and determine:
1. Content type (blog, tutorial, story, etc.)
2. Target audience
3. Key points to cover
4. Estimated complexity (simple, medium, complex)

与えられたトピックを分析し、以下を決定してください:
1. コンテンツタイプ（ブログ、チュートリアル、ストーリーなど）
2. ターゲットオーディエンス  
3. カバーすべきキーポイント
4. 推定複雑度（シンプル、中程度、複雑）
            """,
            model="gpt-4o-mini"
        )
        
        user_input = context.shared_state.get('user_topic', 'AI and the future of work')
        result = await analyzer.run_async(f"Analyze this topic: {user_input}")
        
        if result.success:
            analysis = result.content
            context.shared_state['analysis'] = analysis
            print(f"   ✅ Analysis complete: {analysis[:100]}...")
            
            # Determine complexity for routing
            if 'complex' in analysis.lower():
                context.shared_state['complexity'] = 'complex'
            elif 'medium' in analysis.lower():
                context.shared_state['complexity'] = 'medium'
            else:
                context.shared_state['complexity'] = 'simple'
            
            return analysis
        else:
            print(f"   ❌ Analysis failed: {result.content}")
            context.shared_state['complexity'] = 'simple'
            return "Analysis failed"
    
    def route_by_complexity(context: Context) -> str:
        """Route based on content complexity"""
        complexity = context.shared_state.get('complexity', 'simple')
        print(f"🔀 Routing by complexity: {complexity}")
        print(f"🔀 複雑度によるルーティング: {complexity}")
        
        return complexity  # Return the complexity directly for the condition mapping
    
    async def create_detailed_outline(context: Context) -> str:
        """Create detailed outline for complex content"""
        print("📝 Step 2a: Creating detailed outline...")
        print("📝 ステップ2a: 詳細アウトライン作成中...")
        
        outliner = RefinireAgent(
            name="detailed_outliner", 
            generation_instructions="""
Create a comprehensive, detailed outline for complex content.
Include:
- Introduction with hook
- 5-7 main sections with subsections
- Conclusion with call-to-action
- Estimated word count for each section

複雑なコンテンツの包括的で詳細なアウトラインを作成してください。
含めるべき要素:
- フック付きの導入部
- サブセクション付きの5-7つのメインセクション
- 行動喚起付きの結論
- 各セクションの推定文字数
            """,
            model="gpt-4o-mini"
        )
        
        analysis = context.shared_state.get('analysis', '')
        result = await outliner.run_async(f"Create detailed outline based on: {analysis}")
        
        if result.success:
            outline = result.content
            context.shared_state['outline'] = outline
            print(f"   ✅ Detailed outline created: {len(outline)} characters")
            return outline
        else:
            print(f"   ❌ Outline creation failed: {result.content}")
            return "Outline creation failed"
    
    async def create_standard_outline(context: Context) -> str:
        """Create standard outline for medium complexity content"""
        print("📝 Step 2b: Creating standard outline...")
        print("📝 ステップ2b: 標準アウトライン作成中...")
        
        outliner = RefinireAgent(
            name="standard_outliner",
            generation_instructions="""
Create a standard outline for medium complexity content.
Include:
- Introduction
- 3-4 main points
- Conclusion
- Keep it concise and focused

中程度の複雑度コンテンツの標準アウトラインを作成してください。
含めるべき要素:
- 導入部
- 3-4つのメインポイント
- 結論
- 簡潔で焦点を絞った内容
            """,
            model="gpt-4o-mini"
        )
        
        analysis = context.shared_state.get('analysis', '')
        result = await outliner.run_async(f"Create standard outline based on: {analysis}")
        
        if result.success:
            outline = result.content
            context.shared_state['outline'] = outline
            print(f"   ✅ Standard outline created: {len(outline)} characters")
            return outline
        else:
            print(f"   ❌ Outline creation failed: {result.content}")
            return "Outline creation failed"
    
    async def create_simple_content(context: Context) -> str:
        """Create simple content directly without outline"""
        print("📝 Step 2c: Creating simple content...")
        print("📝 ステップ2c: シンプルコンテンツ作成中...")
        
        writer = RefinireAgent(
            name="simple_writer",
            generation_instructions="""
Create simple, direct content based on the analysis.
Keep it:
- Short and to the point
- Easy to understand
- Engaging and practical

分析に基づいてシンプルで直接的なコンテンツを作成してください。
以下を心がけてください:
- 短く要点を絞った内容
- 理解しやすい
- 魅力的で実用的
            """,
            model="gpt-4o-mini"
        )
        
        analysis = context.shared_state.get('analysis', '')
        topic = context.shared_state.get('user_topic', '')
        result = await writer.run_async(f"Write simple content about: {topic}\nBased on analysis: {analysis}")
        
        if result.success:
            content = result.content
            context.shared_state['final_content'] = content
            print(f"   ✅ Simple content created: {len(content)} characters")
            return content
        else:
            print(f"   ❌ Content creation failed: {result.content}")
            return "Content creation failed"
    
    async def write_final_content(context: Context) -> str:
        """Write final content based on outline"""
        print("✍️  Step 3: Writing final content...")
        print("✍️  ステップ3: 最終コンテンツ作成中...")
        
        writer = RefinireAgent(
            name="content_writer",
            generation_instructions="""
Write engaging, well-structured content based on the provided outline.
Make it:
- Well-researched and informative
- Engaging and readable
- Professional but accessible
- Include practical examples where appropriate

提供されたアウトラインに基づいて、魅力的で良く構造化されたコンテンツを書いてください。
以下を心がけてください:
- よく調査された情報豊富な内容
- 魅力的で読みやすい
- プロフェッショナルだが親しみやすい
- 適切な場所に実践的な例を含める
            """,
            model="gpt-4o-mini"
        )
        
        outline = context.shared_state.get('outline', '')
        topic = context.shared_state.get('user_topic', '')
        result = await writer.run_async(f"Write content about: {topic}\nFollowing this outline: {outline}")
        
        if result.success:
            content = result.content
            context.shared_state['final_content'] = content
            print(f"   ✅ Final content created: {len(content)} characters")
            return content
        else:
            print(f"   ❌ Content writing failed: {result.content}")
            return "Content writing failed"
    
    async def review_content(context: Context) -> str:
        """Review and improve the final content"""
        print("🔍 Step 4: Reviewing content...")
        print("🔍 ステップ4: コンテンツレビュー中...")
        
        reviewer = RefinireAgent(
            name="content_reviewer",
            generation_instructions="""
Review the content and provide:
1. Overall quality assessment (1-10)
2. Strengths
3. Areas for improvement
4. Suggestions for enhancement

コンテンツをレビューして以下を提供してください:
1. 全体的な品質評価（1-10）
2. 強み
3. 改善点
4. 向上のための提案
            """,
            model="gpt-4o-mini"
        )
        
        content = context.shared_state.get('final_content', '')
        result = await reviewer.run_async(f"Review this content: {content}")
        
        if result.success:
            review = result.content
            context.shared_state['review'] = review
            print(f"   ✅ Review completed: {review[:100]}...")
            return review
        else:
            print(f"   ❌ Review failed: {result.content}")
            return "Review failed"
    
    # Create the workflow / ワークフローを作成
    workflow = Flow({
        "start": FunctionStep("analyze", analyze_topic),
        "route": ConditionStep("route", route_by_complexity, {"simple": "simple_content", "medium": "standard_outline", "complex": "detailed_outline"}),
        "simple_content": FunctionStep("simple", create_simple_content),
        "standard_outline": FunctionStep("std_outline", create_standard_outline),
        "detailed_outline": FunctionStep("det_outline", create_detailed_outline),
        "write": FunctionStep("write", write_final_content),
        "review": FunctionStep("review", review_content)
    })
    
    # Execute the workflow / ワークフローを実行
    print("\n🚀 Starting content creation workflow...")
    print("🚀 コンテンツ作成ワークフロー開始...")
    
    # Test with different topics / 異なるトピックでテスト
    test_topics = [
        "Getting started with Python programming",
        "The impact of artificial intelligence on healthcare",
        "Hello World"
    ]
    
    for i, topic in enumerate(test_topics, 1):
        print(f"\n🎯 Test {i}: {topic}")
        print(f"🎯 テスト{i}: {topic}")
        print("-" * 40)
        
        context = Context()
        context.shared_state['user_topic'] = topic
        
        try:
            result = await workflow.run(context)
            
            if result:
                print(f"\n✅ Workflow completed successfully!")
                print(f"✅ ワークフロー正常完了！")
                
                # Show results / 結果を表示
                final_content = context.shared_state.get('final_content', 'No content generated')
                review = context.shared_state.get('review', 'No review available')
                complexity = context.shared_state.get('complexity', 'unknown')
                
                print(f"\n📊 Results for '{topic}':")
                print(f"📊 '{topic}' の結果:")
                print(f"   🎯 Complexity: {complexity}")
                print(f"   📝 Content length: {len(final_content)} characters")
                print(f"   📄 Content preview: {final_content[:200]}...")
                print(f"   ⭐ Review: {review[:150]}...")
                
            else:
                print(f"❌ Workflow failed")
                print(f"❌ ワークフロー失敗")
                
        except Exception as e:
            print(f"❌ Workflow error: {e}")
            print(f"❌ ワークフローエラー: {e}")
    
    print("\n🎉 Flow demo completed!")
    print("🎉 フローデモ完了！")


if __name__ == "__main__":
    asyncio.run(flow_demo())