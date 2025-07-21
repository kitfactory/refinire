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
    async def analyze_topic(user_input: str, context: Context) -> Context:
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
        
        topic = context.shared_state.get('user_topic', user_input)
        result = await analyzer.run_async(f"Analyze this topic: {topic}")
        
        if result.success:
            analysis = result.content
            context.shared_state['analysis'] = analysis
            print(f"   ✅ Analysis complete: {analysis[:100]}...")
            
            # Determine complexity for routing
            analysis_lower = analysis.lower()
            if 'complex' in analysis_lower and 'simple' not in analysis_lower:
                context.shared_state['complexity'] = 'complex'
            elif 'medium' in analysis_lower:
                context.shared_state['complexity'] = 'medium' 
            elif 'simple' in analysis_lower:
                context.shared_state['complexity'] = 'simple'
            else:
                context.shared_state['complexity'] = 'simple'
        else:
            print(f"   ❌ Analysis failed: {result.content}")
            context.shared_state['complexity'] = 'simple'
            context.shared_state['analysis'] = "Analysis failed"
        
        return context
    
    def is_simple(context: Context) -> bool:
        """Check if content is simple"""
        complexity = context.shared_state.get('complexity', 'simple')
        print(f"🔀 Checking if simple: {complexity}")
        print(f"🔀 シンプルかチェック: {complexity}")
        return complexity == 'simple'
    
    def is_complex(context: Context) -> bool:
        """Check if content is complex"""
        complexity = context.shared_state.get('complexity', 'simple')
        print(f"🔀 Checking if complex: {complexity}")
        print(f"🔀 複雑度かチェック: {complexity}")
        return complexity == 'complex'
    
    async def create_detailed_outline(user_input: str, context: Context) -> Context:
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
        else:
            print(f"   ❌ Outline creation failed: {result.content}")
            context.shared_state['outline'] = "Outline creation failed"
        
        return context
    
    async def create_standard_outline(user_input: str, context: Context) -> Context:
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
        else:
            print(f"   ❌ Outline creation failed: {result.content}")
            context.shared_state['outline'] = "Outline creation failed"
        
        return context
    
    async def create_simple_content(user_input: str, context: Context) -> Context:
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
        else:
            print(f"   ❌ Content creation failed: {result.content}")
            context.shared_state['final_content'] = "Content creation failed"
        
        return context
    
    async def write_final_content(user_input: str, context: Context) -> Context:
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
        else:
            print(f"   ❌ Content writing failed: {result.content}")
            context.shared_state['final_content'] = "Content writing failed"
        
        return context
    
    async def review_content(user_input: str, context: Context) -> Context:
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
        else:
            print(f"   ❌ Review failed: {result.content}")
            context.shared_state['review'] = "Review failed"
        
        return context
    
    # Create the workflow / ワークフローを作成
    # This workflow uses step sequencing and conditional routing
    # analyze -> route_simple -> (simple_content OR route_complex) -> review/write -> review
    workflow = Flow(
        start="start",
        steps={
            "start": FunctionStep("analyze", analyze_topic, next_step="route_simple"),
            "route_simple": ConditionStep("route_simple", is_simple, "simple_content", "route_complex"),
            "route_complex": ConditionStep("route_complex", is_complex, "detailed_outline", "standard_outline"),
            "simple_content": FunctionStep("simple", create_simple_content, next_step="review"),
            "standard_outline": FunctionStep("std_outline", create_standard_outline, next_step="write"),
            "detailed_outline": FunctionStep("det_outline", create_detailed_outline, next_step="write"),
            "write": FunctionStep("write", write_final_content, next_step="review"),
            "review": FunctionStep("review", review_content)
        },
        name="content_creation_workflow"
    )
    
    # Execute the workflow / ワークフローを実行
    print("\n🚀 Starting content creation workflow...")
    print("🚀 コンテンツ作成ワークフロー開始...")
    
    # Test with different topics / 異なるトピックでテスト  
    test_topics = [
        "Hello World"  # Simple test case only
    ]
    
    for i, topic in enumerate(test_topics, 1):
        print(f"\n🎯 Test {i}: {topic}")
        print(f"🎯 テスト{i}: {topic}")
        print("-" * 40)
        
        context = Context()
        context.shared_state['user_topic'] = topic
        
        try:
            result = await workflow.run(topic, context)
            
            if result:
                print(f"\n✅ Workflow completed successfully!")
                print(f"✅ ワークフロー正常完了！")
                
                # Show results / 結果を表示
                final_content = result.shared_state.get('final_content', 'No content generated')
                review = result.shared_state.get('review', 'No review available')
                complexity = result.shared_state.get('complexity', 'unknown')
                
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