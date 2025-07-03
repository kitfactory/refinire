#!/usr/bin/env python3
"""
Flow Show Method Demonstration
Flowクラスのshow()メソッドのデモンストレーション

This example demonstrates how to use the show() method to visualize Flow structures.
この例では、show()メソッドを使用してFlow構造を可視化する方法を示します。
"""

import asyncio
from refinire import (
    Flow, 
    FunctionStep, 
    ConditionStep, 
    RefinireAgent,
    Context
)


def analyze_input(ctx: Context) -> Context:
    """Simple analysis function"""
    # Simulate analysis
    text = ctx.user_input or ""
    ctx.shared_state["analysis"] = {
        "length": len(text),
        "word_count": len(text.split()),
        "complexity": "high" if len(text) > 50 else "low"
    }
    ctx.add_system_message(f"Analysis completed: {ctx.shared_state['analysis']}")
    return ctx


def check_complexity(ctx: Context) -> bool:
    """Check if the input is complex"""
    analysis = ctx.shared_state.get("analysis", {})
    return analysis.get("complexity") == "high"


def combine_results(ctx: Context) -> Context:
    """Combine results from parallel processing"""
    ctx.add_system_message("Results combined successfully")
    return ctx


def main():
    """Main demonstration function"""
    
    print("=== Flow Show Method Demonstration ===\n")
    
    # Create a complex flow with various step types
    flow = Flow(start="analyze", steps={
        "analyze": FunctionStep("analyze", analyze_input, next_step="route"),
        
        "route": ConditionStep(
            "route", 
            check_complexity, 
            if_true="complex_processing", 
            if_false="simple_processing"
        ),
        
        "simple_processing": RefinireAgent(
            name="simple_agent",
            generation_instructions="Provide a simple, concise response",
            model="gpt-4o-mini",
            next_step="end"
        ),
        
        "complex_processing": {
            "parallel": [
                RefinireAgent(
                    name="expert1",
                    generation_instructions="Provide detailed technical analysis",
                    model="gpt-4o-mini"
                ),
                RefinireAgent(
                    name="expert2", 
                    generation_instructions="Provide alternative perspective",
                    model="gpt-4o-mini"
                )
            ],
            "next_step": "combine",
            "max_workers": 2
        },
        
        "combine": FunctionStep("combine", combine_results, next_step="end"),
        
        "end": FunctionStep("end", lambda ctx: ctx)
    })
    
    print("1. Flow Structure (Mermaid format):")
    print("-" * 40)
    mermaid_diagram = flow.show(format="mermaid", include_history=False)
    print(mermaid_diagram)
    print()
    
    print("2. Flow Structure (Text format):")
    print("-" * 40)
    text_diagram = flow.show(format="text", include_history=False)
    print(text_diagram)
    print()
    
    # Run the flow to demonstrate execution history
    print("3. Running the flow...")
    print("-" * 40)
    
    async def run_flow():
        result = await flow.run("This is a simple test input for the flow demonstration")
        return result
    
    # Execute the flow
    result = asyncio.run(run_flow())
    print(f"Flow execution completed. Final result: {result.result}")
    print()
    
    print("4. Flow with Execution History (Mermaid format):")
    print("-" * 40)
    mermaid_with_history = flow.show(format="mermaid", include_history=True)
    print(mermaid_with_history)
    print()
    
    print("5. Flow with Execution History (Text format):")
    print("-" * 40)
    text_with_history = flow.show(format="text", include_history=True)
    print(text_with_history)
    print()
    
    # Demonstrate simple sequential flow
    print("6. Simple Sequential Flow:")
    print("-" * 40)
    
    simple_flow = Flow(steps=[
        FunctionStep("step1", lambda ctx: ctx),
        FunctionStep("step2", lambda ctx: ctx),
        FunctionStep("step3", lambda ctx: ctx)
    ])
    
    print("Sequential Flow (Text format):")
    print(simple_flow.show(format="text"))
    print()
    
    # Demonstrate single step flow
    print("7. Single Step Flow:")
    print("-" * 40)
    
    single_flow = Flow(steps=RefinireAgent(
        name="single_agent",
        generation_instructions="You are a helpful assistant",
        model="gpt-4o-mini"
    ))
    
    print("Single Step Flow (Text format):")
    print(single_flow.show(format="text"))
    print()
    
    print("=== Demonstration Complete ===")
    print()
    print("💡 Tips:")
    print("- Use format='mermaid' for detailed flowcharts (great for documentation)")
    print("- Use format='text' for quick console inspection")
    print("- Set include_history=True to see execution paths")
    print("- Mermaid diagrams can be rendered in tools like GitHub, GitLab, or Mermaid Live Editor")


if __name__ == "__main__":
    main()