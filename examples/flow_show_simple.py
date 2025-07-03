#!/usr/bin/env python3
"""
Simple Flow Show Method Demonstration
シンプルなFlowクラスのshow()メソッドのデモンストレーション

This example focuses only on the show() method without executing the flow.
この例では、フローを実行せずにshow()メソッドのみに焦点を当てます。
"""

from refinire import (
    Flow, 
    FunctionStep, 
    ConditionStep, 
    RefinireAgent,
    Context
)


def analyze_input(ctx: Context) -> Context:
    """Simple analysis function"""
    return ctx


def check_complexity(ctx: Context) -> bool:
    """Check if the input is complex"""
    return True


def combine_results(ctx: Context) -> Context:
    """Combine results"""
    return ctx


def main():
    """Main demonstration function"""
    
    print("=== Flow Show Method Demonstration ===\n")
    
    # 1. Simple sequential flow
    print("1. Simple Sequential Flow:")
    print("-" * 40)
    
    simple_flow = Flow(steps=[
        FunctionStep("step1", analyze_input),
        FunctionStep("step2", combine_results),
        FunctionStep("step3", analyze_input)
    ])
    
    print("Text format:")
    print(simple_flow.show(format="text"))
    print()
    
    print("Mermaid format:")
    print(simple_flow.show(format="mermaid"))
    print()
    
    # 2. Single step flow
    print("2. Single Step Flow:")
    print("-" * 40)
    
    single_flow = Flow(steps=RefinireAgent(
        name="single_agent",
        generation_instructions="You are a helpful assistant",
        model="gpt-4o-mini"
    ))
    
    print("Text format:")
    print(single_flow.show(format="text"))
    print()
    
    # 3. Complex flow with conditions and parallel processing
    print("3. Complex Flow with Conditions and Parallel Processing:")
    print("-" * 40)
    
    complex_flow = Flow(start="analyze", steps={
        "analyze": FunctionStep("analyze", analyze_input, next_step="route"),
        
        "route": ConditionStep(
            "route", 
            check_complexity, 
            if_true="complex_processing", 
            if_false="simple_processing"
        ),
        
        "simple_processing": RefinireAgent(
            name="simple_agent",
            generation_instructions="Provide a simple response",
            model="gpt-4o-mini",
            next_step="end"
        ),
        
        "complex_processing": {
            "parallel": [
                RefinireAgent(
                    name="expert1",
                    generation_instructions="Provide detailed analysis",
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
    
    print("Text format:")
    print(complex_flow.show(format="text"))
    print()
    
    print("Mermaid format:")
    print(complex_flow.show(format="mermaid"))
    print()
    
    # 4. Demonstrate different flow construction methods
    print("4. Different Flow Construction Methods:")
    print("-" * 40)
    
    # Dictionary-based construction
    dict_flow = Flow(start="start", steps={
        "start": FunctionStep("start", analyze_input, next_step="middle"),
        "middle": FunctionStep("middle", combine_results, next_step="end"),
        "end": FunctionStep("end", analyze_input)
    })
    
    print("Dictionary-based Flow (Text):")
    print(dict_flow.show(format="text"))
    print()
    
    print("=== Show Method Features ===")
    print()
    print("✅ Features demonstrated:")
    print("- format='text' for console-friendly display")
    print("- format='mermaid' for detailed flowcharts")
    print("- Support for all flow construction methods (dict, list, single)")
    print("- Visualization of different step types:")
    print("  • FunctionStep")
    print("  • ConditionStep with True/False branches")
    print("  • ParallelStep with multiple agents")
    print("  • RefinireAgent")
    print()
    print("💡 Tips:")
    print("- Mermaid diagrams can be copy-pasted into:")
    print("  • GitHub README files")
    print("  • GitLab documentation")
    print("  • Mermaid Live Editor (https://mermaid.live/)")
    print("  • Notion, Obsidian, and other markdown editors")
    print("- Text format is perfect for quick debugging and console inspection")
    print("- Use include_history=True after running flows to see execution paths")


if __name__ == "__main__":
    main()