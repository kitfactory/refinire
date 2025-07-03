# MCP Memory 統合例 - Refinireによる実践的メモリ管理

このチュートリアルでは、人気の高い`mcp-memory`サーバーを実例として、RefinireとMCP（Model Context Protocol）サーバーを統合する方法を説明します。会話間で情報を記憶できるAIエージェントのメモリ管理の設定方法を学びます。

## MCP Memoryとは？

MCP Memoryは、AI会話用の永続ストレージを提供する標準化されたメモリサーバーです。エージェントが以下のことを可能にします：

- 会話履歴の保存と取得
- ユーザー設定とコンテキストの記憶
- セッション間でのナレッジ維持
- 複数エージェント間でのメモリ共有

## 前提条件

開始前に以下が必要です：

- Python 3.10+ がインストール済み
- Refinireパッケージがインストール済み（`pip install refinire`）
- Node.js 18+ がインストール済み（MCPサーバー用）
- Refinireエージェントの基本的な理解

## ステップ1: MCP Memoryサーバーのインストール

まず、npmを使用してMCPメモリサーバーをインストールします：

```bash
# MCPメモリサーバーをグローバルにインストール
npm install -g @modelcontextprotocol/server-memory

# インストールを確認
mcp-memory --help
```

代替インストール方法：

```bash
# npxを使用（グローバルインストール不要）
npx @modelcontextprotocol/server-memory --help

# uvxを使用（uvがインストールされている場合）
uvx @modelcontextprotocol/server-memory --help
```

## ステップ2: 基本的なMCP Memory設定

### MCP Memoryサーバーの理解

MCPメモリサーバーは以下の主要ツールを提供します：
- `memory_store`: キーを使って情報を保存
- `memory_retrieve`: キーで情報を取得
- `memory_list`: 保存されたメモリキーをすべて一覧表示
- `memory_delete`: 保存された情報を削除
- `memory_search`: 保存されたメモリを検索

### シンプルなメモリエージェント

メモリを保存・取得できる基本的なエージェントを作成します：

```python
from refinire import RefinireAgent
import asyncio

# MCPメモリサーバー付きエージェントを作成
memory_agent = RefinireAgent(
    name="memory_assistant",
    generation_instructions="""
    あなたはメモリ機能を持つ親切なアシスタントです。以下のことができます：
    1. memory_storeで後で使用する情報を保存
    2. memory_retrieveで以前に保存した情報を取得
    3. memory_searchでメモリを検索
    4. memory_listですべてのメモリを一覧表示
    
    常にメモリツールを使用して、個人化されたコンテキスト適応型の応答を提供してください。
    ユーザーが重要な情報を共有したら、将来の参照のために保存してください。
    """,
    mcp_servers=[
        "stdio://@modelcontextprotocol/server-memory"
    ],
    model="gpt-4o-mini"
)

async def main():
    # 最初の会話 - 情報を保存
    print("=== 最初の会話 ===")
    result1 = await memory_agent.run_async(
        "こんにちは！私の名前はアリスで、Pythonプロジェクトに取り組んでいるソフトウェアエンジニアです。"
        "詳細な技術的説明を好みます。"
    )
    print(f"エージェント: {result1.content}")
    
    # 二番目の会話 - 保存された情報を取得
    print("\n=== 二番目の会話 ===")
    result2 = await memory_agent.run_async(
        "私について何を覚えていますか？どのような説明を好むと言いましたか？"
    )
    print(f"エージェント: {result2.content}")
    
    # 三番目の会話 - さらに情報を追加
    print("\n=== 三番目の会話 ===")
    result3 = await memory_agent.run_async(
        "現在、機械学習について学んでいて、特にPyTorchに興味があります。"
    )
    print(f"エージェント: {result3.content}")
    
    # 四番目の会話 - 蓄積されたメモリを使用
    print("\n=== 四番目の会話 ===")
    result4 = await memory_agent.run_async(
        "私の現在の興味に役立つPythonライブラリを推薦してもらえますか？"
    )
    print(f"エージェント: {result4.content}")

if __name__ == "__main__":
    asyncio.run(main())
```

## ステップ3: 高度なメモリ管理

### 構造化メモリエージェント

より洗練されたメモリ管理を持つエージェントを作成します：

```python
from refinire import RefinireAgent, Context
import asyncio
import json

class AdvancedMemoryAgent:
    def __init__(self):
        self.agent = RefinireAgent(
            name="advanced_memory_assistant",
            generation_instructions="""
            あなたは洗練されたメモリ管理を持つ高度なアシスタントです。以下を行ってください：
            
            1. 応答前に常にmemory_searchまたはmemory_listで既存メモリを確認
            2. ユーザー情報を構造化フォーマットで保存：
               - 個人情報（名前、役割、設定）
               - プロジェクト情報
               - 会話コンテキスト
               - 重要な日付とイベント
            
            3. メモリ保存に説明的なキーを使用：
               - user_profile_{ユーザー名}
               - project_{プロジェクト名}
               - conversation_{日付}_{トピック}
               - preference_{カテゴリ}
            
            4. 新しい情報が提供されたら既存メモリを更新
            5. 応答で保存されたメモリを参照して継続性を示す
            
            メモリツール使用ガイドライン：
            - memory_store: 説明的なキーで新しい情報を保存
            - memory_retrieve: キーで特定の情報を取得
            - memory_search: キーワードで関連情報を検索
            - memory_list: 利用可能なすべてのメモリを表示
            - memory_delete: 古い情報を削除
            """,
            mcp_servers=[
                "stdio://@modelcontextprotocol/server-memory"
            ],
            model="gpt-4o-mini"
        )
    
    async def chat(self, message: str, user_id: str = "default_user") -> str:
        """ユーザーコンテキスト付きの拡張チャット"""
        # メッセージにユーザーコンテキストを追加
        enhanced_message = f"[ユーザーID: {user_id}] {message}"
        
        result = await self.agent.run_async(enhanced_message)
        return result.content
    
    async def get_memory_summary(self) -> str:
        """保存されたすべてのメモリの要約を取得"""
        result = await self.agent.run_async(
            "memory_listを使用してすべての保存されたメモリを表示し、記憶していることの要約を提供してください。"
        )
        return result.content

# 高度なメモリエージェントの使用例
async def advanced_memory_demo():
    agent = AdvancedMemoryAgent()
    
    print("=== 高度なメモリ管理デモ ===\n")
    
    # マルチセッション会話をシミュレート
    conversations = [
        {
            "user": "alice",
            "message": "こんにちは！私はアリスで、TechCorpのデータサイエンティストです。PythonとSckit-learnを使った顧客セグメンテーションプロジェクトに取り組んでいます。"
        },
        {
            "user": "alice", 
            "message": "クラスタリングアルゴリズムについて助けが必要です。15の特徴量を持つ10,000の顧客レコードがあります。"
        },
        {
            "user": "bob",
            "message": "こんにちは、私はボブでウェブ開発者です。主にReactとNode.jsで作業しています。"
        },
        {
            "user": "alice",
            "message": "また来ました！私の顧客セグメンテーションプロジェクトはどうですか？クラスタリングについて新しい洞察はありますか？"
        },
        {
            "user": "bob",
            "message": "リアルタイムチャットアプリケーションを構築しています。私がどの技術で作業しているか覚えていますか？"
        }
    ]
    
    for conv in conversations:
        print(f"👤 {conv['user'].title()}: {conv['message']}")
        response = await agent.chat(conv['message'], conv['user'])
        print(f"🤖 アシスタント: {response}\n")
        
        # 実際の会話をシミュレートするために小さな遅延を追加
        await asyncio.sleep(1)
    
    # メモリ要約を表示
    print("=== メモリ要約 ===")
    summary = await agent.get_memory_summary()
    print(f"🧠 メモリ要約: {summary}")

if __name__ == "__main__":
    asyncio.run(advanced_memory_demo())
```

## ステップ4: プロジェクトメモリ管理

### プロジェクト専用メモリエージェント

プロジェクト関連のメモリを管理するエージェントを作成します：

```python
from refinire import RefinireAgent
import asyncio
from datetime import datetime

class ProjectMemoryAgent:
    def __init__(self):
        self.agent = RefinireAgent(
            name="project_memory_assistant",
            generation_instructions="""
            あなたはメモリ機能を持つプロジェクト管理アシスタントです。以下のことを追跡します：
            
            1. プロジェクトの詳細とステータス
            2. タスクの割り当てと期限
            3. 会議メモと決定事項
            4. チームメンバー情報
            5. プロジェクトのマイルストーンと目標
            
            メモリ構成：
            - project_info_{プロジェクト名}: 基本プロジェクト情報
            - task_{プロジェクト名}_{タスクID}: 個別タスクの詳細
            - meeting_{プロジェクト名}_{日付}: 会議メモ
            - team_{プロジェクト名}: チームメンバー情報
            - milestone_{プロジェクト名}_{マイルストーン名}: マイルストーン追跡
            
            常に：
            1. 応答前に既存のプロジェクトメモリを検索
            2. 新しいプロジェクト情報を体系的に保存
            3. 通知されたらタスクステータスを更新
            4. 以前の決定とコンテキストを参照
            5. 要求されたらプロジェクト要約を提供
            """,
            mcp_servers=[
                "stdio://@modelcontextprotocol/server-memory"
            ],
            model="gpt-4o-mini"
        )
    
    async def create_project(self, project_name: str, description: str, team_members: list):
        """メモリに新しいプロジェクトを初期化"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        message = f"""
        以下の詳細で新しいプロジェクトを作成してください：
        - プロジェクト名: {project_name}
        - 説明: {description}
        - チームメンバー: {', '.join(team_members)}
        - 開始日: {current_date}
        - ステータス: アクティブ
        
        この情報を保存してプロジェクト作成を確認してください。
        """
        
        result = await self.agent.run_async(message)
        return result.content
    
    async def add_task(self, project_name: str, task_name: str, assignee: str, deadline: str):
        """プロジェクトにタスクを追加"""
        message = f"""
        プロジェクト「{project_name}」に新しいタスクを追加してください：
        - タスク名: {task_name}
        - 担当者: {assignee}
        - 期限: {deadline}
        - ステータス: 未開始
        
        このタスクを保存してプロジェクトステータスの更新を提供してください。
        """
        
        result = await self.agent.run_async(message)
        return result.content
    
    async def update_task_status(self, project_name: str, task_name: str, new_status: str):
        """タスクステータスを更新"""
        message = f"""
        プロジェクト「{project_name}」のタスク「{task_name}」のステータスを「{new_status}」に更新してください。
        現在のタスク情報を取得し、更新して、プロジェクトステータス要約を提供してください。
        """
        
        result = await self.agent.run_async(message)
        return result.content
    
    async def get_project_summary(self, project_name: str):
        """包括的なプロジェクト要約を取得"""
        message = f"""
        プロジェクト「{project_name}」の包括的な要約を以下を含めて提供してください：
        1. プロジェクト概要と現在のステータス
        2. すべてのタスクとその現在のステータス
        3. チームメンバーの割り当て
        4. 今後の期限
        5. 会議メモや重要な決定事項
        
        この情報をまとめるためにすべての関連メモリを検索してください。
        """
        
        result = await self.agent.run_async(message)
        return result.content

# プロジェクト管理ワークフローの例
async def project_management_demo():
    pm_agent = ProjectMemoryAgent()
    
    print("=== プロジェクトメモリ管理デモ ===\n")
    
    # 新しいプロジェクトを作成
    print("📋 新しいプロジェクトを作成中...")
    result = await pm_agent.create_project(
        "ウェブサイトリデザイン",
        "モダンなUI/UXでの会社ウェブサイトの完全リデザイン",
        ["アリス (デザイナー)", "ボブ (開発者)", "チャーリー (QA)"]
    )
    print(f"✅ {result}\n")
    
    # タスクを追加
    print("📝 プロジェクトタスクを追加中...")
    tasks = [
        ("デザインワイヤーフレーム", "アリス", "2024-02-15"),
        ("フロントエンド開発", "ボブ", "2024-02-28"),
        ("バックエンドAPI統合", "ボブ", "2024-03-05"),
        ("品質保証テスト", "チャーリー", "2024-03-10")
    ]
    
    for task_name, assignee, deadline in tasks:
        result = await pm_agent.add_task("ウェブサイトリデザイン", task_name, assignee, deadline)
        print(f"📌 追加済み: {task_name}")
        await asyncio.sleep(0.5)
    
    print()
    
    # タスクステータスを更新
    print("🔄 タスクステータスを更新中...")
    updates = [
        ("デザインワイヤーフレーム", "完了"),
        ("フロントエンド開発", "進行中"),
    ]
    
    for task_name, status in updates:
        result = await pm_agent.update_task_status("ウェブサイトリデザイン", task_name, status)
        print(f"✏️ {task_name}を{status}に更新")
        await asyncio.sleep(0.5)
    
    print()
    
    # プロジェクト要約を取得
    print("📊 プロジェクト要約を取得中...")
    summary = await pm_agent.get_project_summary("ウェブサイトリデザイン")
    print(f"📈 プロジェクト要約:\n{summary}")

if __name__ == "__main__":
    asyncio.run(project_management_demo())
```

## ステップ5: 設定とトラブルシューティング

### 設定オプション

MCPメモリサーバーをさまざまなオプションで設定できます：

```bash
# 基本的な使用法
mcp-memory

# カスタムポートで
mcp-memory --port 3001

# 特定のメモリファイル場所で
mcp-memory --memory-file ./custom-memory.json

# デバッグログ付きで
mcp-memory --debug
```

### 代替サーバー設定

```python
# 異なるMCPサーバー設定
memory_configs = [
    # 標準stdio設定
    "stdio://@modelcontextprotocol/server-memory",
    
    # 特定のメモリファイル付き
    "stdio://@modelcontextprotocol/server-memory --memory-file ./project-memory.json",
    
    # HTTPサーバー（利用可能な場合）
    "http://localhost:3001/mcp",
    
    # 異なる目的のための複数メモリサーバー
    [
        "stdio://@modelcontextprotocol/server-memory --memory-file ./user-memory.json",
        "stdio://@modelcontextprotocol/server-memory --memory-file ./project-memory.json"
    ]
]

# RefinireAgentで使用
agent = RefinireAgent(
    name="multi_memory_agent",
    generation_instructions="異なるタイプの情報に異なるメモリサーバーを使用してください。",
    mcp_servers=memory_configs[3],  # 複数サーバー
    model="gpt-4o-mini"
)
```

### 一般的な問題のトラブルシューティング

#### 1. MCPサーバーが見つからない

```bash
# エラー: mcp-memoryコマンドが見つからない
# 解決策: サーバーをインストール
npm install -g @modelcontextprotocol/server-memory

# またはnpxを使用
npx @modelcontextprotocol/server-memory
```

#### 2. 権限の問題

```bash
# エラー: 権限が拒否された
# 解決策: ファイル権限を確認するか別のディレクトリを使用
chmod 755 ./memory-file.json

# または別の場所を指定
mcp-memory --memory-file ~/Documents/memory.json
```

#### 3. エージェントがメモリツールを使用しない

```python
# 問題: エージェントがメモリツールを使用しない
# 解決策: 指示を改善

agent = RefinireAgent(
    name="memory_agent",
    generation_instructions="""
    重要: 永続ストレージにはメモリツールを必ず使用してください：
    
    1. 応答前に常にmemory_searchで既存メモリを確認
    2. 重要なユーザー情報は常にmemory_storeで保存
    3. 特定の保存情報にアクセスするためにmemory_retrieveを使用
    4. 利用可能なすべてのメモリを見るためにmemory_listを使用
    
    ワークフロー例：
    1. ユーザーが情報を共有 → memory_storeを使用
    2. ユーザーが過去の情報を尋ねる → memory_searchまたはmemory_retrieveを使用
    3. 応答前 → まず関連メモリを確認
    """,
    mcp_servers=["stdio://@modelcontextprotocol/server-memory"],
    model="gpt-4o-mini"
)
```

## MCP Memory統合のベストプラクティス

### 1. メモリキー命名規則

構造化された説明的なキーを使用：

```python
# 良いキー命名パターン
memory_keys = [
    "user_profile_alice_2024",
    "project_website_redesign_tasks",
    "meeting_2024_01_15_planning",
    "preference_alice_communication_style",
    "deadline_project_website_2024_03_01"
]

# これらのパターンは避ける
bad_keys = [
    "data1",
    "info",
    "temp",
    "user_stuff"
]
```

### 2. メモリ管理戦略

```python
# メモリライフサイクル管理
async def memory_cleanup_example():
    agent = RefinireAgent(
        name="cleanup_agent",
        generation_instructions="""
        メモリを効率的に管理：
        1. 古い情報の定期的なクリーンアップ
        2. 完了したプロジェクトのアーカイブ
        3. 変更時のユーザー設定の更新
        4. 重複または競合するメモリの削除
        """,
        mcp_servers=["stdio://@modelcontextprotocol/server-memory"],
        model="gpt-4o-mini"
    )
    
    # クリーンアップ操作の例
    cleanup_tasks = [
        "すべてのメモリを一覧表示し、古いプロジェクト情報を特定",
        "昨年の完了したプロジェクトのメモリをアーカイブ",
        "変更されたユーザー設定を更新",
        "重複するユーザープロファイル情報を削除"
    ]
    
    for task in cleanup_tasks:
        result = await agent.run_async(task)
        print(f"クリーンアップ: {task}")
        print(f"結果: {result.content}\n")
```

### 3. エラーハンドリングと検証

```python
from refinire import RefinireAgent
import asyncio

class RobustMemoryAgent:
    def __init__(self):
        self.agent = RefinireAgent(
            name="robust_memory_agent",
            generation_instructions="""
            あなたは堅牢なメモリアシスタントです。常に：
            1. 保存前に情報を検証
            2. メモリエラーを適切に処理
            3. メモリが失敗した場合のフォールバック応答を提供
            4. 成功したメモリ操作を確認
            5. メモリ問題をユーザーに報告
            """,
            mcp_servers=["stdio://@modelcontextprotocol/server-memory"],
            model="gpt-4o-mini"
        )
    
    async def safe_store_memory(self, key: str, value: str):
        """検証付きで安全にメモリを保存"""
        try:
            message = f"""
            以下の情報を安全に保存してください：
            キー: {key}
            値: {value}
            
            保存前に：
            1. キーフォーマットが適切か検証
            2. このキーが既に存在するか確認
            3. 情報を保存
            4. 保存が成功したことを確認
            """
            
            result = await self.agent.run_async(message)
            return result.content
            
        except Exception as e:
            return f"メモリ保存エラー: {str(e)}"
    
    async def safe_retrieve_memory(self, key: str):
        """フォールバック付きで安全にメモリを取得"""
        try:
            message = f"""
            キー「{key}」でメモリを取得してください
            
            キーが存在しない場合：
            1. 類似のキーを検索
            2. 代替案を提供
            3. 利用可能な情報を説明
            """
            
            result = await self.agent.run_async(message)
            return result.content
            
        except Exception as e:
            return f"メモリ取得エラー: {str(e)}"

# 使用例
async def robust_memory_demo():
    agent = RobustMemoryAgent()
    
    # 安全な保存
    result = await agent.safe_store_memory(
        "user_alice_preferences", 
        "詳細な技術的説明を好み、PythonとMLで作業"
    )
    print(f"保存結果: {result}")
    
    # 安全な取得
    result = await agent.safe_retrieve_memory("user_alice_preferences")
    print(f"取得結果: {result}")

if __name__ == "__main__":
    asyncio.run(robust_memory_demo())
```

## まとめ

RefinireとのMCP Memory統合は、AIエージェントに強力な永続メモリ機能を提供します。主な利点は以下の通りです：

- **永続メモリ**: 情報がセッション間で保持される
- **構造化ストレージ**: 組織化されたメモリ管理
- **簡単な統合**: Refinireでのシンプルな設定
- **柔軟な使用**: さまざまなアプリケーションに適用可能

この統合により、コンテキストを維持し、ユーザー設定を記憶し、複数のインタラクションにわたって個人化された体験を提供する洗練されたAIアシスタントの構築が可能になります。

### 次のステップ

1. 提供された例を試してみる
2. 特定の使用例にパターンを適用
3. 異なる機能のための他のMCPサーバーを探索
4. カスタムメモリ管理ワークフローを構築
5. 既存のアプリケーションと統合

より高度なMCP統合については、[高度機能ガイド](advanced_ja.md)と[ContextProviderガイド](context_provider_guide_ja.md)を参照してください。