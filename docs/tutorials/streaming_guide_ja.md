# ストリーミングガイド - リアルタイム応答表示

このガイドでは、Refinireのストリーミング機能を網羅的に説明し、即座のユーザーフィードバックを提供するレスポンシブなリアルタイムAIアプリケーションの構築方法を学べます。

## 概要

Refinireは`RefinireAgent`と`Flow`の両方で強力なストリーミング機能を提供し、以下を実現します：
- **リアルタイム応答表示** - コンテンツ生成と同時の表示
- **カスタムチャンク処理** - コールバック関数による処理
- **コンテキスト対応ストリーミング** - 会話型アプリケーション対応
- **フローレベルストリーミング** - 複雑な多段階ワークフロー対応
- **構造化出力ストリーミング** - JSONチャンク配信

## 目次

1. [基本的なRefinireAgentストリーミング](#基本的なrefinireagentストリーミング)
2. [コールバック付きストリーミング](#コールバック付きストリーミング)
3. [コンテキスト対応ストリーミング](#コンテキスト対応ストリーミング)
4. [Flowストリーミング](#flowストリーミング)
5. [構造化出力ストリーミング](#構造化出力ストリーミング)
6. [エラーハンドリング](#エラーハンドリング)
7. [パフォーマンス考慮事項](#パフォーマンス考慮事項)
8. [統合パターン](#統合パターン)
9. [ベストプラクティス](#ベストプラクティス)

## 基本的なRefinireAgentストリーミング

最も簡単なストリーミング方法は`run_streamed()`メソッドの使用です：

```python
import asyncio
from refinire import RefinireAgent

async def basic_streaming_example():
    agent = RefinireAgent(
        name="streaming_assistant",
        generation_instructions="詳細で役立つ回答を提供してください",
        model="gpt-4o-mini"
    )
    
    print("ユーザー: 量子コンピューティングを説明してください")
    print("アシスタント: ", end="", flush=True)
    
    # レスポンスチャンクを到着と同時にストリーミング
    async for chunk in agent.run_streamed("量子コンピューティングを説明してください"):
        print(chunk, end="", flush=True)
    
    print()  # 完了時に改行

# 例を実行
asyncio.run(basic_streaming_example())
```

### 主な機能
- **即座の応答**: チャンクが生成されると同時に表示
- **ノンブロッキング**: アプリケーションの応答性を維持
- **簡単な統合**: `run()`メソッドの置き換えとして使用可能

## コールバック付きストリーミング

高度な処理には、各チャンクを処理するコールバック関数を使用します：

```python
import asyncio
from refinire import RefinireAgent

async def callback_streaming_example():
    agent = RefinireAgent(
        name="callback_agent",
        generation_instructions="詳細な技術解説を書いてください",
        model="gpt-4o-mini"
    )
    
    # ストリーミングメトリクスを追跡
    chunks_received = []
    total_characters = 0
    
    def chunk_processor(chunk: str):
        """到着した各チャンクを処理"""
        nonlocal total_characters
        chunks_received.append(chunk)
        total_characters += len(chunk)
        
        # カスタム処理の例:
        # - WebSocketクライアントに送信
        # - リアルタイムUIを更新
        # - ファイル/データベースに保存
        # - 通知をトリガー
        
        print(f"[チャンク {len(chunks_received)}]: {len(chunk)} 文字")
    
    print("コールバック処理付きストリーミング...")
    full_response = ""
    
    async for chunk in agent.run_streamed(
        "機械学習アルゴリズムを説明してください", 
        callback=chunk_processor
    ):
        full_response += chunk
        print(chunk, end="", flush=True)
    
    print(f"\n\nストリーミング完了!")
    print(f"📊 総チャンク数: {len(chunks_received)}")
    print(f"📏 総文字数: {total_characters}")
    print(f"💾 完全な応答: {len(full_response)} 文字")

asyncio.run(callback_streaming_example())
```

### コールバックの使用例
- **WebSocket配信**: 複数のクライアントにチャンクを送信
- **リアルタイムUI更新**: プログレスバー、文字数カウンターを更新
- **データ永続化**: ストリーミングデータをデータベースに保存
- **アナリティクス**: パフォーマンスメトリクスとユーザーエンゲージメントを追跡

## コンテキスト対応ストリーミング

ストリーミングインタラクション全体で会話コンテキストを維持：

```python
import asyncio
from refinire import RefinireAgent, Context

async def context_streaming_example():
    agent = RefinireAgent(
        name="context_agent",
        generation_instructions="会話を自然に続け、前のメッセージを参照してください",
        model="gpt-4o-mini"
    )
    
    # 会話用の共有コンテキストを作成
    ctx = Context()
    
    conversation = [
        "こんにちは、Pythonの学習を手伝ってもらえますか？",
        "PythonのAsync/awaitについてはどうですか？", 
        "実際の例を見せてもらえますか？",
        "これをWebアプリケーションでどう使いますか？"
    ]
    
    for i, user_input in enumerate(conversation):
        print(f"\n--- メッセージ {i + 1} ---")
        print(f"ユーザー: {user_input}")
        print("アシスタント: ", end="", flush=True)
        
        # ストリーミング前にユーザーメッセージをコンテキストに追加
        ctx.add_user_message(user_input)
        
        # 共有コンテキストで応答をストリーミング
        response = ""
        async for chunk in agent.run_streamed(user_input, ctx=ctx):
            response += chunk
            print(chunk, end="", flush=True)
        
        # コンテキストは自動的に将来の参照用に応答を保存
        print()  # 読みやすさのため改行

asyncio.run(context_streaming_example())
```

### コンテキストの利点
- **会話継続性**: エージェントが以前のやり取りを記憶
- **パーソナライズされた応答**: ユーザーの好みと履歴に適応
- **セッション管理**: 複数のインタラクション間で状態を維持
- **自動保存**: 応答が自動的にコンテキストに保存

## Flowストリーミング

複雑な多段階ワークフローをストリーミング：

```python
import asyncio
from refinire import Flow, FunctionStep, RefinireAgent

def analyze_input(user_input, context):
    """ユーザーリクエストの複雑さを分析"""
    context.shared_state["analysis"] = {
        "complexity": "high" if len(user_input) > 50 else "low",
        "topic": "detected_topic"
    }
    return "分析完了"

def format_results(user_input, context):
    """最終結果をフォーマット"""
    return f"フォーマット済み出力: {context.result}"

async def flow_streaming_example():
    # ストリーミング対応エージェントを含むフローを作成
    flow = Flow({
        "analyze": FunctionStep("analyze", analyze_input),
        "generate": RefinireAgent(
            name="content_generator",
            generation_instructions="分析に基づいて包括的で詳細なコンテンツを生成してください",
            model="gpt-4o-mini"
        ),
        "format": FunctionStep("format", format_results)
    })
    
    print("ユーザー: Pythonデコレータの包括的なガイドを作成してください")
    print("フロー出力: ", end="", flush=True)
    
    # フロー実行全体をストリーミング
    async for chunk in flow.run_streamed("Pythonデコレータの包括的なガイドを作成してください"):
        print(chunk, end="", flush=True)
    
    print("\n\nフローストリーミング完了!")

asyncio.run(flow_streaming_example())
```

### Flowストリーミング機能
- **混合ストリーミング/非ストリーミング**: ストリーミングステップのみがチャンクを生成
- **逐次実行**: ステップがストリーミング出力と共に順番に実行
- **コンテキスト保持**: 共有状態がストリーミング全体で維持
- **エラー伝播**: ストリーミングエラーが適切に処理

## 構造化出力ストリーミング

**重要**: 構造化出力（Pydanticモデル）をストリーミングで使用すると、レスポンスは解析されたオブジェクトではなく**JSONチャンク**としてストリーミングされます：

```python
import asyncio
from pydantic import BaseModel
from refinire import RefinireAgent

class BlogPost(BaseModel):
    title: str
    content: str
    tags: list[str]
    word_count: int

async def structured_streaming_example():
    agent = RefinireAgent(
        name="structured_writer",
        generation_instructions="よく構造化されたブログ投稿を生成してください",
        output_model=BlogPost,  # 構造化出力を有効化
        model="gpt-4o-mini"
    )
    
    print("構造化出力をJSONチャンクとしてストリーミング:")
    print("生JSON: ", end="", flush=True)
    
    json_content = ""
    async for json_chunk in agent.run_streamed("AI倫理についてのブログ投稿を書いて"):
        json_content += json_chunk
        print(json_chunk, end="", flush=True)
    
    print(f"\n\n完全なJSON: {json_content}")
    
    # 解析されたオブジェクトが必要な場合は、通常のrun()メソッドを使用:
    print("\n解析されたオブジェクトの例:")
    result = await agent.run_async("AI倫理についてのブログ投稿を書いて")
    blog_post = result.content  # BlogPostオブジェクトを返す
    print(f"タイトル: {blog_post.title}")
    print(f"タグ: {blog_post.tags}")
    print(f"語数: {blog_post.word_count}")

asyncio.run(structured_streaming_example())
```

### 構造化ストリーミングの動作
- **JSONチャンク**: 構造化出力は解析されたオブジェクトではなく生JSONとしてストリーミング
- **プログレッシブ解析**: JSONが完成に近づくにつれて解析可能
- **混合使用**: リアルタイム表示にストリーミング、解析されたオブジェクトに通常メソッドを使用
- **クライアントサイド解析**: フロントエンドアプリケーションが必要に応じてJSONチャンクを解析

## エラーハンドリング

ストリーミングシナリオで堅牢なエラーハンドリングを実装：

```python
import asyncio
from refinire import RefinireAgent

async def error_handling_example():
    agent = RefinireAgent(
        name="error_test_agent",
        generation_instructions="ユーザー入力に役立つ回答をしてください",
        model="gpt-4o-mini"
    )
    
    test_cases = [
        "",  # 空の入力
        "Pythonについての通常のリクエスト",
        "A" * 10000,  # 非常に長い入力
    ]
    
    for i, test_input in enumerate(test_cases):
        print(f"\n--- テストケース {i + 1}: {len(test_input)} 文字 ---")
        
        try:
            chunks_received = 0
            async for chunk in agent.run_streamed(test_input):
                chunks_received += 1
                print(chunk, end="", flush=True)
                
                # 処理エラーをシミュレート
                if chunks_received > 100:  # チャンクが多すぎる
                    print("\n[警告] チャンクが多すぎます、停止中...")
                    break
            
            print(f"\n✅ {chunks_received}チャンクの処理に成功")
            
        except Exception as e:
            print(f"\n❌ ストリーミングエラー: {e}")
            # フォールバックロジックを実装
            print("🔄 非ストリーミングにフォールバック中...")
            try:
                result = await agent.run_async(test_input)
                print(f"フォールバック結果: {result.content[:100]}...")
            except Exception as fallback_error:
                print(f"❌ フォールバックも失敗: {fallback_error}")

asyncio.run(error_handling_example())
```

### エラーハンドリングのベストプラクティス
- **グレースフルデグラデーション**: ストリーミングが失敗した場合の非ストリーミングへのフォールバック
- **タイムアウト処理**: ストリーミング操作に適切なタイムアウトを設定
- **チャンク検証**: 処理前にチャンクを検証
- **リソースクリーンアップ**: ストリーミングリソースを適切にクリーンアップ

## パフォーマンス考慮事項

### ストリーミングパフォーマンスのヒント

1. **バッファ管理**:
```python
async def optimized_streaming():
    buffer = []
    buffer_size = 10  # 10チャンクごとに処理
    
    async for chunk in agent.run_streamed("長いコンテンツリクエスト"):
        buffer.append(chunk)
        
        if len(buffer) >= buffer_size:
            # チャンクのバッチを処理
            process_chunk_batch(buffer)
            buffer.clear()
    
    # 残りのチャンクを処理
    if buffer:
        process_chunk_batch(buffer)
```

2. **メモリ管理**:
```python
async def memory_efficient_streaming():
    total_chars = 0
    max_memory = 10000  # 10KB制限
    
    async for chunk in agent.run_streamed("大きなコンテンツを生成"):
        total_chars += len(chunk)
        
        if total_chars > max_memory:
            print("\n[情報] メモリ制限に達しました、切り詰めます...")
            break
        
        process_chunk(chunk)
```

3. **並行ストリーミング**:
```python
async def concurrent_streaming():
    agents = [
        RefinireAgent(name=f"agent_{i}", generation_instructions="コンテンツを生成", model="gpt-4o-mini")
        for i in range(3)
    ]
    
    tasks = [
        agent.run_streamed(f"トピック {i}")
        for i, agent in enumerate(agents)
    ]
    
    # 複数のストリームを並行処理
    async for chunk_data in asyncio.as_completed(tasks):
        async for chunk in chunk_data:
            print(f"[{time.time()}] {chunk}", end="", flush=True)
```

## 統合パターン

### WebSocket統合

```python
import asyncio
import websockets
from refinire import RefinireAgent

async def websocket_streaming_handler(websocket, path):
    agent = RefinireAgent(
        name="websocket_agent",
        generation_instructions="リアルタイム応答を提供",
        model="gpt-4o-mini"
    )
    
    try:
        async for message in websocket:
            # クライアントに応答をストリーミングで返す
            async for chunk in agent.run_streamed(message):
                await websocket.send(chunk)
            
            # 完了シグナルを送信
            await websocket.send("[完了]")
            
    except websockets.exceptions.ConnectionClosed:
        print("クライアントが切断されました")

# WebSocketサーバーを開始
start_server = websockets.serve(websocket_streaming_handler, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
```

### FastAPI統合

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from refinire import RefinireAgent
import json

app = FastAPI()
agent = RefinireAgent(
    name="api_agent",
    generation_instructions="役立つAPI応答を提供",
    model="gpt-4o-mini"
)

@app.post("/stream")
async def stream_response(request: dict):
    async def generate():
        async for chunk in agent.run_streamed(request["message"]):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield f"data: {json.dumps({'complete': True})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")
```

## ベストプラクティス

### 1. **適切なストリーミング方法を選択**
- リアルタイムユーザーインターフェースには`run_streamed()`を使用
- 複雑な処理パイプラインにはコールバックを使用
- 多段階ワークフローにはFlowストリーミングを使用
- ストリーミングが不要な場合は通常の`run()`を使用

### 2. **ネットワーク問題を処理**
- WebSocketストリーミング用の再接続ロジックを実装
- 接続のハングを防ぐためにタイムアウトを使用
- 不安定なネットワーク条件のためにチャンクをバッファ

### 3. **ユーザー体験を最適化**
- ストリーミング中にタイピングインジケーターを表示
- チャンク数やプログレス情報を表示
- "ストリーミング停止"機能を実装
- 空の応答やエラー応答を適切に処理

### 4. **リソース管理**
- 長時間実行ストリームのメモリ制限を設定
- ストリーミングリソースを適切にクリーンアップ
- ストリーミングパフォーマンスメトリクスを監視
- 高トラフィックシナリオでレート制限を実装

### 5. **テスト戦略**
- 様々な入力サイズと型でテスト
- ネットワーク中断をシミュレート
- 並行ストリーミングシナリオをテスト
- チャンクの整合性と順序を検証

## まとめ

Refinireのストリーミング機能により、最小限の複雑さでレスポンシブなリアルタイムAIアプリケーションを構築できます。チャットインターフェース、ライブダッシュボード、複雑なワークフローシステムのいずれを構築する場合でも、ストリーミングはモダンなアプリケーションでユーザーが期待する即座のフィードバックを提供します。

より多くの例については以下を参照：
- [`examples/streaming_example.py`](../../examples/streaming_example.py) - 包括的なストリーミング例
- [`examples/flow_streaming_example.py`](../../examples/flow_streaming_example.py) - Flowストリーミングデモンストレーション  
- [`tests/test_streaming.py`](../../tests/test_streaming.py) - 完全なテストスイート

**次のステップ**: [Flowアーキテクチャ](flow_complete_guide_ja.md)を探索して、複雑なストリーミングワークフローの構築方法を学びましょう。