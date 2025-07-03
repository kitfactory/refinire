#!/usr/bin/env python3
"""
MCP Server Integration Example with RefinireAgent
RefinireAgentでのMCPサーバー統合例

This example demonstrates how to use RefinireAgent with MCP servers.
この例では、RefinireAgentでMCPサーバーを使用する方法を示します。

Note: This example assumes you have MCP servers configured and available.
注意: この例では、MCPサーバーが設定され利用可能であることを前提としています。
"""

import asyncio
import sys
import os

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Context


async def main():
    """
    Main function to demonstrate MCP server integration
    MCPサーバー統合を実証するメイン関数
    """
    print("🔌 MCP Server Integration Example")
    print("MCPサーバー統合例")
    print("=" * 50)
    
    # Example 1: Basic MCP server integration
    # 例1: 基本的なMCPサーバー統合
    print("\n📡 Example 1: Basic MCP Server Integration")
    print("例1: 基本的なMCPサーバー統合")
    
    try:
        # Note: Replace with actual MCP server configurations
        # 注意: 実際のMCPサーバー設定に置き換えてください
        mcp_servers = [
            # Example MCP server configurations
            # MCPサーバー設定の例
            # These would be actual MCP server endpoints in practice
            # 実際には、これらは実際のMCPサーバーエンドポイントになります
            "stdio://path/to/mcp-server",
            "http://localhost:8000/mcp"
        ]
        
        agent = RefinireAgent(
            name="mcp_agent",
            generation_instructions="""
            You are an AI assistant with access to MCP (Model Context Protocol) servers.
            Use the tools available through MCP servers to help users with their requests.
            
            あなたはMCP（Model Context Protocol）サーバーにアクセスできるAIアシスタントです。
            MCPサーバーで利用可能なツールを使用して、ユーザーのリクエストを支援してください。
            """,
            mcp_servers=mcp_servers,
            model="gpt-4o-mini"
        )
        
        print(f"✅ Agent created with {len(mcp_servers)} MCP servers")
        print(f"✅ {len(mcp_servers)}個のMCPサーバーでエージェントを作成")
        print(f"   - MCP Servers: {agent.mcp_servers}")
        
        # Example interaction
        # 相互作用の例
        user_input = "What tools are available through the MCP servers?"
        print(f"\n💬 User: {user_input}")
        
        # Note: This will work if you have actual MCP servers running
        # 注意: 実際のMCPサーバーが動作している場合に機能します
        ctx = Context()
        result = await agent.run_async(user_input, ctx)
        print(f"🤖 Agent: {result.result}")
        
    except Exception as e:
        print(f"❌ Error with MCP integration: {e}")
        print(f"❌ MCP統合エラー: {e}")
        print("💡 Tip: Make sure you have MCP servers configured and running")
        print("💡 ヒント: MCPサーバーが設定され、動作していることを確認してください")
    
    # Example 2: MCP with Context and Flow
    # 例2: コンテキストとFlowでのMCP
    print("\n📊 Example 2: MCP with Context Integration")
    print("例2: コンテキスト統合でのMCP")
    
    try:
        agent_with_context = RefinireAgent(
            name="mcp_context_agent",
            generation_instructions="""
            You have access to MCP servers and context information.
            Use both MCP tools and context data to provide comprehensive responses.
            
            MCPサーバーとコンテキスト情報にアクセスできます。
            MCPツールとコンテキストデータの両方を使用して、包括的な回答を提供してください。
            """,
            mcp_servers=mcp_servers,
            context_providers_config=[
                {
                    "type": "conversation_history",
                    "max_items": 5
                }
            ],
            model="gpt-4o-mini"
        )
        
        # Use with Context
        ctx = Context()
        ctx.shared_state = {
            "user_preference": "detailed technical explanations",
            "session_type": "development assistance"
        }
        
        user_input = "Can you help me analyze this project using available MCP tools?"
        print(f"\n💬 User: {user_input}")
        
        result = await agent_with_context.run_async(user_input, ctx)
        print(f"🤖 Agent: {result.result}")
        
        print(f"📋 Context after execution:")
        print(f"   - Shared state: {ctx.shared_state}")
        print(f"   - Messages count: {len(ctx.messages)}")
        
    except Exception as e:
        print(f"❌ Error with MCP + Context: {e}")
        print(f"❌ MCP + コンテキストエラー: {e}")
    
    # Example 3: MCP Server Configuration Examples
    # 例3: MCPサーバー設定例
    print("\n⚙️  Example 3: MCP Server Configuration Examples")
    print("例3: MCPサーバー設定例")
    
    # Different types of MCP server configurations
    # 異なるタイプのMCPサーバー設定
    mcp_config_examples = {
        "stdio_server": [
            "stdio://mcp-filesystem",
            "stdio://mcp-database --config db.json"
        ],
        "http_server": [
            "http://localhost:8001/mcp",
            "https://api.example.com/mcp/v1"
        ],
        "websocket_server": [
            "ws://localhost:9000/mcp",
            "wss://secure.example.com/mcp"
        ]
    }
    
    for server_type, servers in mcp_config_examples.items():
        print(f"\n📋 {server_type.replace('_', ' ').title()}:")
        for server in servers:
            print(f"   - {server}")
            
        try:
            example_agent = RefinireAgent(
                name=f"example_{server_type}",
                generation_instructions="Example agent with specific MCP server type",
                mcp_servers=servers,
                model="gpt-4o-mini"
            )
            print(f"   ✅ Agent created successfully with {len(servers)} {server_type}")
            
        except Exception as e:
            print(f"   ⚠️  Configuration example only (servers not running): {e}")
    
    print("\n" + "=" * 50)
    print("🎯 MCP Integration Summary:")
    print("MCPサーバー統合まとめ:")
    print("- RefinireAgent now supports mcp_servers parameter")
    print("- MCPサーバーをエージェントに簡単に統合可能")
    print("- Context and Flow integration works seamlessly")
    print("- コンテキストとFlow統合もシームレスに動作")
    print("- Compatible with OpenAI Agents SDK MCP features")
    print("- OpenAI Agents SDK のMCP機能と互換性あり")


if __name__ == "__main__":
    asyncio.run(main())