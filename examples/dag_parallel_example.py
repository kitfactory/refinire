#!/usr/bin/env python3
"""
DAG Parallel Processing Example
DAG並列処理の例

This example demonstrates how to use Refinire's DAG parallel processing capabilities
to execute multiple analysis tasks simultaneously and efficiently aggregate results.
この例では、RefinireのDAG並列処理機能を使用して複数の分析タスクを同時実行し、
効率的に結果を統合する方法を示します。
"""

import asyncio
import time
from refinire.flow import Flow, FunctionStep, Context


def create_text_analysis_flow():
    """
    Create a text analysis flow with parallel processing
    並列処理を使用したテキスト分析フローを作成
    """
    
    def preprocess_text(input_data, ctx):
        """
        Preprocess input text
        入力テキストを前処理
        """
        print(f"📝 前処理開始: {input_data}")
        processed_text = input_data.strip().lower()
        ctx.shared_state["preprocessed_text"] = processed_text
        print(f"✅ 前処理完了: {processed_text}")
        return ctx
    
    def analyze_sentiment(input_data, ctx):
        """
        Analyze sentiment of the text
        テキストの感情を分析
        """
        print("😊 感情分析開始...")
        text = ctx.shared_state.get("preprocessed_text", input_data)
        
        # Simulate sentiment analysis
        # 感情分析をシミュレート
        time.sleep(0.5)  # Simulate processing time
        
        if "good" in text or "great" in text or "excellent" in text:
            sentiment = "ポジティブ"
        elif "bad" in text or "terrible" in text or "awful" in text:
            sentiment = "ネガティブ"
        else:
            sentiment = "中立"
        
        ctx.shared_state["sentiment"] = sentiment
        print(f"✅ 感情分析完了: {sentiment}")
        return ctx
    
    def extract_keywords(input_data, ctx):
        """
        Extract keywords from the text
        テキストからキーワードを抽出
        """
        print("🔍 キーワード抽出開始...")
        text = ctx.shared_state.get("preprocessed_text", input_data)
        
        # Simulate keyword extraction
        # キーワード抽出をシミュレート
        time.sleep(0.3)
        
        # Simple keyword extraction (split and filter)
        # 簡単なキーワード抽出（分割とフィルタリング）
        words = text.split()
        keywords = [word for word in words if len(word) > 3][:5]
        
        ctx.shared_state["keywords"] = keywords
        print(f"✅ キーワード抽出完了: {keywords}")
        return ctx
    
    def classify_topic(input_data, ctx):
        """
        Classify the topic of the text
        テキストのトピックを分類
        """
        print("📂 トピック分類開始...")
        text = ctx.shared_state.get("preprocessed_text", input_data)
        
        # Simulate topic classification
        # トピック分類をシミュレート
        time.sleep(0.4)
        
        if any(tech_word in text for tech_word in ["ai", "technology", "computer", "software"]):
            topic = "技術"
        elif any(business_word in text for business_word in ["business", "market", "finance"]):
            topic = "ビジネス"
        elif any(health_word in text for health_word in ["health", "medical", "doctor"]):
            topic = "健康"
        else:
            topic = "一般"
        
        ctx.shared_state["topic"] = topic
        print(f"✅ トピック分類完了: {topic}")
        return ctx
    
    def calculate_readability(input_data, ctx):
        """
        Calculate readability score
        読みやすさスコアを計算
        """
        print("📊 読みやすさ分析開始...")
        text = ctx.shared_state.get("preprocessed_text", input_data)
        
        # Simulate readability calculation
        # 読みやすさ計算をシミュレート
        time.sleep(0.2)
        
        # Simple readability score based on word count and average word length
        # 単語数と平均単語長に基づく簡単な読みやすさスコア
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        if avg_word_length < 4:
            readability = "易しい"
        elif avg_word_length < 6:
            readability = "普通"
        else:
            readability = "難しい"
        
        ctx.shared_state["readability"] = readability
        print(f"✅ 読みやすさ分析完了: {readability}")
        return ctx
    
    def aggregate_analysis_results(input_data, ctx):
        """
        Aggregate all analysis results
        全ての分析結果を統合
        """
        print("📋 結果統合開始...")
        
        # Get all analysis results
        # 全分析結果を取得
        sentiment = ctx.shared_state.get("sentiment", "不明")
        keywords = ctx.shared_state.get("keywords", [])
        topic = ctx.shared_state.get("topic", "不明")
        readability = ctx.shared_state.get("readability", "不明")
        original_text = ctx.shared_state.get("preprocessed_text", input_data)
        
        # Create comprehensive analysis report
        # 包括的な分析レポートを作成
        analysis_report = {
            "original_text": original_text,
            "sentiment": sentiment,
            "keywords": keywords,
            "topic": topic,
            "readability": readability,
            "summary": f"このテキストは{topic}分野の{readability}文章で、{sentiment}な感情を表現しています。"
        }
        
        ctx.shared_state["analysis_report"] = analysis_report
        ctx.finish()
        
        print("✅ 結果統合完了!")
        return ctx
    
    # Create DAG flow with parallel analysis
    # 並列分析を含むDAGフローを作成
    flow_definition = {
        "preprocess": FunctionStep("preprocess", preprocess_text),
        "parallel_analysis": {
            "parallel": [
                FunctionStep("sentiment", analyze_sentiment),
                FunctionStep("keywords", extract_keywords),
                FunctionStep("topic", classify_topic),
                FunctionStep("readability", calculate_readability)
            ],
            "next_step": "aggregate",
            "max_workers": 4  # Allow up to 4 concurrent analysis tasks
        },
        "aggregate": FunctionStep("aggregate", aggregate_analysis_results)
    }
    
    # Set up sequential flow connections
    # 順次フロー接続を設定
    flow_definition["preprocess"].next_step = "parallel_analysis"
    
    return Flow(start="preprocess", steps=flow_definition, name="TextAnalysisFlow")


async def run_basic_parallel_example():
    """
    Run basic parallel processing example
    基本的な並列処理の例を実行
    """
    print("=" * 60)
    print("🚀 基本DAG並列処理デモ")
    print("=" * 60)
    
    # Create and run text analysis flow
    # テキスト分析フローを作成・実行
    flow = create_text_analysis_flow()
    
    sample_text = "This is a great example of AI technology in modern software development."
    
    print(f"📄 分析テキスト: {sample_text}")
    print("-" * 40)
    
    start_time = time.time()
    result = await flow.run(sample_text)
    end_time = time.time()
    
    print("-" * 40)
    print(f"⏱️ 実行時間: {end_time - start_time:.2f}秒")
    print()
    
    # Display results
    # 結果を表示
    if "analysis_report" in result.shared_state:
        report = result.shared_state["analysis_report"]
        print("📊 分析結果:")
        print(f"  感情: {report['sentiment']}")
        print(f"  キーワード: {', '.join(report['keywords'])}")
        print(f"  トピック: {report['topic']}")
        print(f"  読みやすさ: {report['readability']}")
        print(f"  要約: {report['summary']}")
    
    print()


async def compare_sequential_vs_parallel():
    """
    Compare sequential vs parallel execution performance
    順次実行と並列実行のパフォーマンスを比較
    """
    print("=" * 60)
    print("⚡ 順次 vs 並列実行パフォーマンス比較")
    print("=" * 60)
    
    def simulate_heavy_task(task_name, duration):
        """Simulate a computationally heavy task"""
        async def task_func(input_data, ctx):
            print(f"  🔄 {task_name} 開始...")
            await asyncio.sleep(duration)  # Use asyncio.sleep for proper parallel execution
            ctx.shared_state[f"{task_name}_result"] = f"{task_name} completed in {duration}s"
            print(f"  ✅ {task_name} 完了")
            return ctx
        return task_func
    
    # Sequential flow
    # 順次フロー
    print("📋 順次実行テスト...")
    sequential_flow = Flow(steps=[
        FunctionStep("task1", simulate_heavy_task("Task1", 0.5)),
        FunctionStep("task2", simulate_heavy_task("Task2", 0.5)),
        FunctionStep("task3", simulate_heavy_task("Task3", 0.5)),
        FunctionStep("task4", simulate_heavy_task("Task4", 0.5))
    ])
    
    start_time = time.time()
    await sequential_flow.run("test")
    sequential_time = time.time() - start_time
    
    print(f"⏱️ 順次実行時間: {sequential_time:.2f}秒")
    print()
    
    # Parallel flow
    # 並列フロー
    print("🚀 並列実行テスト...")
    parallel_flow = Flow(start="parallel_tasks", steps={
        "parallel_tasks": {
            "parallel": [
                FunctionStep("ptask1", simulate_heavy_task("PTask1", 0.5)),
                FunctionStep("ptask2", simulate_heavy_task("PTask2", 0.5)),
                FunctionStep("ptask3", simulate_heavy_task("PTask3", 0.5)),
                FunctionStep("ptask4", simulate_heavy_task("PTask4", 0.5))
            ]
        }
    })
    
    start_time = time.time()
    await parallel_flow.run("test")
    parallel_time = time.time() - start_time
    
    print(f"⏱️ 並列実行時間: {parallel_time:.2f}秒")
    print()
    
    # Performance comparison
    # パフォーマンス比較
    speedup = sequential_time / parallel_time
    print(f"🎯 パフォーマンス向上: {speedup:.2f}倍高速化")
    print(f"📈 時間短縮: {((sequential_time - parallel_time) / sequential_time * 100):.1f}%")


async def main():
    """
    Main function to run all examples
    全ての例を実行するメイン関数
    """
    print("🎉 Refinire DAG並列処理デモ")
    print()
    
    # Run all examples
    # 全ての例を実行
    await run_basic_parallel_example()
    await compare_sequential_vs_parallel()
    
    print("=" * 60)
    print("✨ デモ完了！")
    print("💡 詳細な技術仕様については docs/composable-flow-architecture.md をご覧ください")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
