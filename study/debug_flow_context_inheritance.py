#!/usr/bin/env python3
"""
Debug script for investigating Flow Context inheritance between steps.
フローでのステップ間のContext継承を調査するデバッグスクリプト。

This script creates a simple Flow with two RefinireAgent steps and shows:
- Context object identity (same object vs new object) 
- Message history preservation
- Shared state preservation
- Any differences between what Context contains vs what agents can access

このスクリプトは2つのRefinireAgentステップを持つシンプルなフローを作成し、以下を表示します：
- Contextオブジェクト識別（同一オブジェクト vs 新オブジェクト）
- メッセージ履歴の保持
- 共有状態の保持
- Contextが持つ内容とエージェントがアクセスできる内容の違い
"""

import asyncio
import sys
import os

# Add src to path for import
# インポートのためのsrcパス追加
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from refinire.agents.flow.flow import Flow
from refinire.agents.flow.step import FunctionStep
from refinire.agents.flow.context import Context
from refinire.agents.pipeline.llm_pipeline import RefinireAgent


class ContextDebugger:
    """Context debugging helper class / Context デバッグヘルパークラス"""
    
    def __init__(self):
        self.context_history = []
        self.step_counter = 0
    
    def log_context_state(self, stage: str, context: Context, step_name: str = ""):
        """Log context state at different stages / 異なる段階でのコンテキスト状態をログ記録"""
        self.step_counter += 1
        
        context_info = {
            'stage': stage,
            'step_name': step_name,
            'step_counter': self.step_counter,
            'context_id': id(context),
            'context_trace_id': getattr(context, 'trace_id', None),
            'messages_count': len(context.messages),
            'shared_state_keys': list(context.shared_state.keys()),
            'shared_state_values': dict(context.shared_state),
            'result_exists': context.result is not None,
            'result_content': getattr(context.result, 'content', None) if context.result else None,
            'content_property': context.content,
            'current_step': context.current_step,
            'next_label': context.next_label,
            'step_count': context.step_count,
            'last_user_input': context.last_user_input,
            'routing_result': context.routing_result,
            'evaluation_result': context.evaluation_result,
            'error': context.error
        }
        
        # Get last few messages
        # 最新のメッセージを取得
        context_info['recent_messages'] = []
        for msg in context.messages[-3:]:  # Last 3 messages
            context_info['recent_messages'].append({
                'role': msg.role,
                'content': msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
                'timestamp': str(msg.timestamp)
            })
        
        self.context_history.append(context_info)
        
        print(f"\n{'='*60}")
        print(f"CONTEXT STATE - {stage}")
        if step_name:
            print(f"Step: {step_name}")
        print(f"{'='*60}")
        print(f"Context ID: {context_info['context_id']}")
        print(f"Trace ID: {context_info['context_trace_id']}")
        print(f"Messages Count: {context_info['messages_count']}")
        print(f"Shared State Keys: {context_info['shared_state_keys']}")
        print(f"Shared State Values: {context_info['shared_state_values']}")
        print(f"Result Exists: {context_info['result_exists']}")
        print(f"Content Property: {context_info['content_property']}")
        print(f"Current Step: {context_info['current_step']}")
        print(f"Next Label: {context_info['next_label']}")
        print(f"Step Count: {context_info['step_count']}")
        print(f"Last User Input: {context_info['last_user_input']}")
        
        if context_info['recent_messages']:
            print("\nRecent Messages:")
            for i, msg in enumerate(context_info['recent_messages']):
                print(f"  {i+1}. [{msg['role']}] {msg['content']}")
        
        print(f"{'='*60}")
    
    def analyze_context_changes(self):
        """Analyze context changes between steps / ステップ間のContext変更を分析"""
        print(f"\n{'#'*80}")
        print("CONTEXT INHERITANCE ANALYSIS")
        print(f"{'#'*80}")
        
        if len(self.context_history) < 2:
            print("Not enough context history to analyze changes.")
            return
        
        for i in range(1, len(self.context_history)):
            prev_ctx = self.context_history[i-1]
            curr_ctx = self.context_history[i]
            
            print(f"\nTransition: {prev_ctx['stage']} → {curr_ctx['stage']}")
            print(f"Step: {prev_ctx['step_name']} → {curr_ctx['step_name']}")
            print("-" * 50)
            
            # Check object identity
            # オブジェクト識別をチェック
            same_object = prev_ctx['context_id'] == curr_ctx['context_id']
            print(f"Same Context Object: {same_object}")
            if not same_object:
                print(f"  Previous ID: {prev_ctx['context_id']}")
                print(f"  Current ID: {curr_ctx['context_id']}")
            
            # Check trace ID preservation
            # トレースID保持をチェック
            same_trace = prev_ctx['context_trace_id'] == curr_ctx['context_trace_id']
            print(f"Same Trace ID: {same_trace}")
            if not same_trace:
                print(f"  Previous: {prev_ctx['context_trace_id']}")
                print(f"  Current: {curr_ctx['context_trace_id']}")
            
            # Check message preservation
            # メッセージ保持をチェック
            msg_delta = curr_ctx['messages_count'] - prev_ctx['messages_count']
            print(f"Message Count Change: {msg_delta} (from {prev_ctx['messages_count']} to {curr_ctx['messages_count']})")
            
            # Check shared state preservation  
            # 共有状態保持をチェック
            prev_keys = set(prev_ctx['shared_state_keys'])
            curr_keys = set(curr_ctx['shared_state_keys'])
            added_keys = curr_keys - prev_keys
            removed_keys = prev_keys - curr_keys
            
            print(f"Shared State Changes:")
            print(f"  Added keys: {list(added_keys)}")
            print(f"  Removed keys: {list(removed_keys)}")
            print(f"  Preserved keys: {list(prev_keys & curr_keys)}")
            
            # Check content changes
            # コンテンツ変更をチェック
            prev_content = prev_ctx['content_property']
            curr_content = curr_ctx['content_property']
            content_changed = prev_content != curr_content
            print(f"Content Property Changed: {content_changed}")
            if content_changed:
                print(f"  Previous: {prev_content}")
                print(f"  Current: {curr_content}")


async def create_info_collector_agent() -> RefinireAgent:
    """Create an agent that collects information and stores it in Context"""
    
    agent = RefinireAgent(
        name="InfoCollector",
        generation_instructions="You are an information collector. Ask the user for their name and favorite color, then store this information for the next agent.",
        model="gpt-4o-mini",
        temperature=0.7
    )
    return agent


async def create_info_accessor_agent() -> RefinireAgent:
    """Create an agent that tries to access information from Context"""
    
    agent = RefinireAgent(
        name="InfoAccessor", 
        generation_instructions="You are an information accessor. Look at the conversation history and any shared state to find the user's name and favorite color that was collected by the previous agent. Summarize what you found.",
        model="gpt-4o-mini",
        temperature=0.7
    )
    return agent


async def debug_context_flow():
    """Debug Context flow through Flow steps / FlowステップでのContext流れをデバッグ"""
    
    debugger = ContextDebugger()
    
    # Create agents
    # エージェントを作成
    print("Creating agents...")
    collector_agent = await create_info_collector_agent()
    accessor_agent = await create_info_accessor_agent()
    
    # Wrap agents in FunctionSteps with debugging
    # エージェントをデバッグ付きFunctionStepでラップ
    async def collector_step_with_debug(user_input: str, context: Context) -> Context:
        """Collector step wrapper with debug logging"""
        debugger.log_context_state("BEFORE_COLLECTOR_STEP", context, "collector")
        
        # Store some test data in shared state before calling agent
        # エージェントを呼び出す前に共有状態にテストデータを保存
        context.shared_state['debug_info'] = 'Added by collector step wrapper'
        context.shared_state['step_sequence'] = ['collector_started']
        
        # Call the agent
        # エージェントを呼び出し
        result_context = await collector_agent.run_async(user_input, context)
        
        # Add some additional data to shared state after agent execution
        # エージェント実行後に共有状態に追加データを追加
        result_context.shared_state['collector_completed'] = True
        result_context.shared_state['step_sequence'].append('collector_finished')
        result_context.shared_state['collected_data'] = {
            'user_name': 'John Doe',  # Simulated collected data
            'favorite_color': 'blue'
        }
        
        debugger.log_context_state("AFTER_COLLECTOR_STEP", result_context, "collector")
        
        # Route to next step
        # 次ステップにルーティング  
        print(f"Setting next step to 'accessor'. Before: next_label={result_context.next_label}")
        result_context.goto("accessor")
        print(f"After goto: next_label={result_context.next_label}")
        return result_context
    
    async def accessor_step_with_debug(user_input: str, context: Context) -> Context:
        """Accessor step wrapper with debug logging"""
        debugger.log_context_state("BEFORE_ACCESSOR_STEP", context, "accessor")
        
        # Check what data is available in Context
        # Contextで利用可能なデータをチェック
        print(f"\nAccessor step sees context shared_state: {context.shared_state}")
        print(f"Accessor step sees {len(context.messages)} messages in history")
        
        # Update step sequence
        # ステップシーケンスを更新
        if 'step_sequence' in context.shared_state:
            context.shared_state['step_sequence'].append('accessor_started')
        
        # Call the agent 
        # エージェントを呼び出し
        result_context = await accessor_agent.run_async(user_input, context)
        
        # Mark completion
        # 完了をマーク
        result_context.shared_state['accessor_completed'] = True
        if 'step_sequence' in result_context.shared_state:
            result_context.shared_state['step_sequence'].append('accessor_finished')
        
        debugger.log_context_state("AFTER_ACCESSOR_STEP", result_context, "accessor")
        
        # Finish flow
        # フローを終了
        result_context.finish()
        return result_context
    
    # Create Flow with the wrapped steps
    # ラップされたステップでFlowを作成
    flow = Flow(
        start="collector",
        steps={
            "collector": FunctionStep("collector", collector_step_with_debug),
            "accessor": FunctionStep("accessor", accessor_step_with_debug)
        },
        name="ContextDebugFlow"
    )
    
    # Log initial context state
    # 初期コンテキスト状態をログ記録
    debugger.log_context_state("INITIAL", flow.context, "flow_start")
    
    print("\n" + "="*80)
    print("RUNNING FLOW - Context Inheritance Debug")
    print("="*80)
    
    # Run the flow
    # フローを実行
    try:
        initial_input = "Hi, my name is Alice and my favorite color is green."
        final_context = await flow.run(initial_input)
        
        debugger.log_context_state("FINAL", final_context, "flow_end")
        
    except Exception as e:
        print(f"Error during flow execution: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Analyze the context changes
    # コンテキスト変更を分析
    debugger.analyze_context_changes()
    
    # Final summary
    # 最終サマリー
    print(f"\n{'#'*80}")
    print("FINAL SUMMARY")
    print(f"{'#'*80}")
    print(f"Final Context Content: {final_context.content}")
    print(f"Final Shared State: {final_context.shared_state}")
    print(f"Final Message Count: {len(final_context.messages)}")
    print(f"Flow Success: {final_context.success}")


async def main():
    """Main function / メイン関数"""
    print("Flow Context Inheritance Debug Script")
    print("フローContext継承デバッグスクリプト")
    print("="*80)
    
    try:
        await debug_context_flow()
    except Exception as e:
        print(f"Script failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())