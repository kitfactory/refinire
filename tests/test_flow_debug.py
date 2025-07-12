#!/usr/bin/env python3
"""
Debug the exact flow of orchestration mode
オーケストレーション・モードの正確なフローをデバッグ
"""

from refinire import RefinireAgent
import asyncio

def test_orchestration_flow():
    """Test the exact flow of orchestration mode"""
    print("Testing orchestration flow...")
    
    agent = RefinireAgent(
        name="flow_test_agent",
        generation_instructions="Analyze the provided data and give a simple summary",
        orchestration_mode=True,
        model="gpt-4o-mini"
    )
    
    # Hook into various methods to trace the flow
    original_execute = agent._execute_with_context
    original_run_standalone = agent._run_standalone
    original_parse_orch = agent._parse_orchestration_result
    
    async def debug_execute(user_input, ctx, span=None):
        print(f"DEBUG EXECUTE: Starting with user_input={user_input}")
        result_ctx = await original_execute(user_input, ctx, span)
        print(f"DEBUG EXECUTE: result_ctx.result type: {type(result_ctx.result)}")
        print(f"DEBUG EXECUTE: result_ctx.result value: {result_ctx.result}")
        print(f"DEBUG EXECUTE: hasattr(result_ctx, 'result'): {hasattr(result_ctx, 'result')}")
        print(f"DEBUG EXECUTE: isinstance(result_ctx.result, dict): {isinstance(result_ctx.result, dict)}")
        return result_ctx
    
    async def debug_run_standalone(user_input, ctx=None):
        print(f"DEBUG STANDALONE: Starting with user_input={user_input}")
        llm_result = await original_run_standalone(user_input, ctx)
        print(f"DEBUG STANDALONE: llm_result.success: {llm_result.success}")
        print(f"DEBUG STANDALONE: llm_result.content type: {type(llm_result.content)}")
        print(f"DEBUG STANDALONE: llm_result.content value: {llm_result.content}")
        return llm_result
    
    def debug_parse_orch(content):
        print(f"DEBUG PARSE: content type: {type(content)}")
        print(f"DEBUG PARSE: content value: {content}")
        result = original_parse_orch(content)
        print(f"DEBUG PARSE: result type: {type(result)}")
        print(f"DEBUG PARSE: result value: {result}")
        return result
    
    agent._execute_with_context = debug_execute
    agent._run_standalone = debug_run_standalone
    agent._parse_orchestration_result = debug_parse_orch
    
    try:
        result = agent.run("Analyze this: sales increased by 20%")
        print(f"FINAL RESULT type: {type(result)}")
        print(f"FINAL RESULT value: {result}")
        return result
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_orchestration_flow()