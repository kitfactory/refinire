#!/usr/bin/env python3
"""
Debug the run_async method specifically
run_asyncメソッドを特別にデバッグ
"""

from refinire import RefinireAgent
from refinire.agents.flow.context import Context
import asyncio

async def test_run_async_flow():
    """Test the run_async method flow"""
    print("Testing run_async flow...")
    
    agent = RefinireAgent(
        name="async_test_agent",
        generation_instructions="Analyze the provided data",
        orchestration_mode=True,
        model="gpt-4o-mini"
    )
    
    # Hook into run_async to see what it returns
    original_run_async = agent.run_async
    
    async def debug_run_async(user_input, ctx):
        print(f"DEBUG RUN_ASYNC: Starting with user_input={user_input}")
        print(f"DEBUG RUN_ASYNC: ctx type: {type(ctx)}")
        print(f"DEBUG RUN_ASYNC: orchestration_mode: {agent.orchestration_mode}")
        
        result = await original_run_async(user_input, ctx)
        
        print(f"DEBUG RUN_ASYNC: result type: {type(result)}")
        print(f"DEBUG RUN_ASYNC: result value: {result}")
        
        if isinstance(result, Context):
            print(f"DEBUG RUN_ASYNC: result.result type: {type(result.result)}")
            print(f"DEBUG RUN_ASYNC: result.result value: {result.result}")
            print(f"DEBUG RUN_ASYNC: isinstance(result.result, dict): {isinstance(result.result, dict)}")
        
        return result
    
    agent.run_async = debug_run_async
    
    ctx = Context()
    try:
        async_result = await agent.run_async("Analyze this: revenue up 30%", ctx)
        print(f"ASYNC RESULT type: {type(async_result)}")
        print(f"ASYNC RESULT value: {async_result}")
        return async_result
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

def test_sync_wrapper():
    """Test the sync run method wrapper"""
    print("\nTesting sync run method...")
    
    agent = RefinireAgent(
        name="sync_test_agent",
        generation_instructions="Analyze the provided data",
        orchestration_mode=True,
        model="gpt-4o-mini"
    )
    
    # Hook into run method to trace the flow
    original_run = agent.run
    
    def debug_run(user_input, ctx=None):
        print(f"DEBUG RUN: Starting with user_input={user_input}")
        print(f"DEBUG RUN: ctx: {ctx}")
        print(f"DEBUG RUN: orchestration_mode: {agent.orchestration_mode}")
        
        try:
            # Check the async call result before the orchestration check
            import asyncio
            
            if ctx is None:
                ctx = Context()
                ctx.add_user_message(user_input)
            
            # Manually call run_async to debug
            try:
                loop = asyncio.get_running_loop()
                import nest_asyncio
                nest_asyncio.apply()
                future = asyncio.ensure_future(agent.run_async(user_input, ctx))
                result_ctx = loop.run_until_complete(future)
            except RuntimeError:
                result_ctx = asyncio.run(agent.run_async(user_input, ctx))
            
            print(f"DEBUG RUN: result_ctx type: {type(result_ctx)}")
            print(f"DEBUG RUN: result_ctx value: {result_ctx}")
            
            if hasattr(result_ctx, 'result'):
                print(f"DEBUG RUN: result_ctx.result type: {type(result_ctx.result)}")
                print(f"DEBUG RUN: result_ctx.result value: {result_ctx.result}")
                print(f"DEBUG RUN: isinstance(result_ctx.result, dict): {isinstance(result_ctx.result, dict)}")
            
            # Apply the orchestration logic manually
            if agent.orchestration_mode:
                print("DEBUG RUN: In orchestration mode check")
                if hasattr(result_ctx, 'result') and isinstance(result_ctx.result, dict):
                    print("DEBUG RUN: Returning orchestration result")
                    return result_ctx.result
                else:
                    print("DEBUG RUN: Returning error format")
                    return {
                        "status": "failed",
                        "result": result_ctx.result if hasattr(result_ctx, 'result') else None,
                        "reasoning": "Orchestration mode enabled but structured output not generated",
                        "next_hint": {
                            "task": "retry",
                            "confidence": 0.3,
                            "rationale": "Retry with clearer instructions or check agent configuration"
                        }
                    }
            return result_ctx
            
        except Exception as e:
            print(f"DEBUG RUN: Exception: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    result = debug_run("Analyze this: profit increased by 25%")
    print(f"SYNC RESULT type: {type(result)}")
    print(f"SYNC RESULT value: {result}")
    return result

async def main():
    await test_run_async_flow()
    test_sync_wrapper()

if __name__ == "__main__":
    asyncio.run(main())