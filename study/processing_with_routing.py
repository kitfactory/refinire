#!/usr/bin/env python3
"""
Processing with Routing Sample - 処理結果をrouting_instructionで分類するサンプル
処理・ルーティングサンプル - エージェントが処理を実行し、その結果の状態を分類

This demonstrates using routing_instruction to classify the state/quality of processing results.
処理結果の状態・品質をrouting_instructionで分類する方法を実演します。
"""

import asyncio
import os
from refinire import RefinireAgent


async def processing_with_routing_demo():
    """
    Demonstrate processing content and routing based on result quality
    コンテンツを処理し、結果の品質に基づいてルーティングするデモ
    """
    print("📝🔀 Processing with Routing Sample")
    print("📝🔀 処理・ルーティングサンプル")
    print("=" * 60)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        print("❌ OPENAI_API_KEY環境変数を設定してください。")
        return
    
    # Create text summarizer agent / テキスト要約エージェントを作成
    summarizer_agent = RefinireAgent(
        name="text_summarizer",
        generation_instructions="""
You are a text summarizer. Create a concise summary of the given text.
Analyze the content and provide a clear, informative summary that captures the main points.

あなたはテキスト要約者です。与えられたテキストの簡潔な要約を作成してください。
内容を分析し、主要なポイントを捉えた明確で情報豊富な要約を提供してください。
        """,
        routing_instruction="After providing the summary, add a quality assessment. End your response with exactly one of: QUALITY: excellent, QUALITY: good, or QUALITY: needs_improvement",
        model="gpt-4o-mini",
        timeout=60
    )
    
    # Test texts for summarization / 要約テスト用テキスト
    test_texts = [
        # Short, simple text / 短くシンプルなテキスト
        """
        Artificial Intelligence (AI) is revolutionizing healthcare. Machine learning algorithms can now 
        diagnose diseases faster than doctors. AI-powered robots assist in surgeries with precision. 
        The technology reduces medical errors and improves patient outcomes.
        """,
        
        # Medium complexity text / 中程度の複雑さのテキスト
        """
        Climate change represents one of the most pressing challenges of our time. Rising global temperatures 
        are causing ice caps to melt, sea levels to rise, and weather patterns to become increasingly erratic. 
        The primary driver of climate change is the emission of greenhouse gases, particularly carbon dioxide, 
        from burning fossil fuels. Governments worldwide are implementing policies to transition to renewable 
        energy sources like solar and wind power. However, the transition requires significant investment 
        and international cooperation to be effective.
        """,
        
        # Complex technical text / 複雑な技術テキスト
        """
        Quantum computing leverages the principles of quantum mechanics to process information in fundamentally 
        different ways than classical computers. While classical bits exist in either 0 or 1 states, quantum 
        bits (qubits) can exist in superposition, allowing them to be in multiple states simultaneously. 
        This property, combined with quantum entanglement and interference, enables quantum computers to 
        perform certain calculations exponentially faster than classical computers. However, quantum systems 
        are extremely fragile and require near-absolute zero temperatures to maintain quantum coherence. 
        Current challenges include quantum error correction, scaling up the number of stable qubits, and 
        developing practical algorithms that can leverage quantum advantages for real-world problems.
        """
    ]
    
    print("🚀 Starting text summarization with quality routing...")
    print("🚀 品質ルーティング付きテキスト要約開始...")
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{'='*60}")
        print(f"📄 Test {i}: Text Summary and Quality Assessment")
        print(f"📄 テスト{i}: テキスト要約と品質評価")
        print("-" * 40)
        
        # Show text preview / テキストプレビューを表示
        text_preview = text.strip()[:100] + "..." if len(text.strip()) > 100 else text.strip()
        print(f"📖 Original text preview: {text_preview}")
        print(f"📖 元テキストプレビュー: {text_preview}")
        
        try:
            print(f"\n📝 Processing summarization...")
            print(f"📝 要約処理中...")
            
            start_time = asyncio.get_event_loop().time()
            result = await summarizer_agent.run_async(f"Summarize this text: {text.strip()}")
            execution_time = asyncio.get_event_loop().time() - start_time
            
            if result.success:
                print(f"\n✅ Summarization completed!")
                print(f"✅ 要約完了！")
                print(f"⏱️  Execution time: {execution_time:.2f} seconds")
                print(f"⏱️  実行時間: {execution_time:.2f} 秒")
                
                # Extract quality routing from the response
                # レスポンスから品質ルーティングを抽出
                response = result.content
                
                # Extract quality assessment from the response
                # レスポンスから品質評価を抽出
                quality = "unknown"
                response_lower = response.lower()
                if "quality: excellent" in response_lower:
                    quality = "excellent"
                elif "quality: good" in response_lower:
                    quality = "good"
                elif "quality: needs_improvement" in response_lower:
                    quality = "needs_improvement"
                
                print(f"\n📊 Results:")
                print(f"📊 結果:")
                print(f"   🔀 Quality Assessment: {quality}")
                print(f"   📝 Summary: {response[:300]}{'...' if len(response) > 300 else ''}")
                
                # Handle different quality levels / 異なる品質レベルを処理
                await handle_quality_routing(quality, response)
                
            else:
                print(f"❌ Summarization failed: {result.content}")
                print(f"❌ 要約失敗: {result.content}")
                
        except Exception as e:
            print(f"💥 Error during processing: {e}")
            print(f"💥 処理中エラー: {e}")
    
    print(f"\n{'='*60}")
    print("🎉 Processing with routing demo completed!")
    print("🎉 処理・ルーティングデモ完了！")
    
    print(f"\n💡 What was demonstrated:")
    print(f"💡 実演された内容:")
    print(f"   • Text summarization processing")
    print(f"   • Quality assessment via routing_instruction")
    print(f"   • Different handling based on quality levels")
    print(f"   • Single agent performing both processing and evaluation")


async def handle_quality_routing(quality: str, summary: str):
    """
    Handle different actions based on quality assessment
    品質評価に基づいて異なるアクションを実行
    """
    print(f"\n🎯 Handling quality level: {quality}")
    print(f"🎯 品質レベル処理: {quality}")
    
    if quality == "excellent":
        print(f"   ⭐ EXCELLENT: Summary is ready for publication!")
        print(f"   ⭐ 優秀: 要約は公開準備完了！")
        print(f"   📤 Action: Archive as high-quality content")
        
    elif quality == "good":
        print(f"   ✅ GOOD: Summary is acceptable with minor polish needed")
        print(f"   ✅ 良好: 要約は軽微な調整で使用可能")
        print(f"   🔧 Action: Schedule for review and minor edits")
        
    elif quality == "needs_improvement":
        print(f"   ⚠️  NEEDS IMPROVEMENT: Summary requires significant revision")
        print(f"   ⚠️  要改善: 要約は大幅な修正が必要")
        print(f"   🔄 Action: Send back for re-processing")
        
    else:
        print(f"   ❓ UNKNOWN: Could not determine quality level")
        print(f"   ❓ 不明: 品質レベルを判定できませんでした")
        print(f"   🔍 Action: Manual review required")


if __name__ == "__main__":
    asyncio.run(processing_with_routing_demo())