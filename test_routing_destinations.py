#!/usr/bin/env python3
"""
Test script for routing_destinations functionality
routing_destinations機能のテストスクリプト
"""

import asyncio
from src.refinire.agents.routing_agent import RoutingAgent
from src.refinire.agents.pipeline.llm_pipeline import RefinireAgent
from src.refinire.agents.flow.context import Context
from src.refinire.agents.flow.flow import Flow

def test_routing_agent_with_destinations():
    """Test RoutingAgent with routing_destinations parameter"""
    print("=== Testing RoutingAgent with routing_destinations ===")
    
    # Define routing destinations
    routing_destinations = [
        "enhance",      # 品質向上処理
        "validate",     # 検証処理 
        "complete",     # 完了処理
        Flow.END        # フロー終了
    ]
    
    # Create RoutingAgent
    routing_agent = RoutingAgent(
        name="test_router",
        routing_instruction="""
        コンテンツの品質と完成度に基づいて判断してください：
        - 不完全・改善必要 → 'enhance'
        - 完成したが検証必要 → 'validate'  
        - 高品質で完成 → 'complete'
        - 処理完了・終了 → '_FLOW_END_'
        """,
        routing_destinations=routing_destinations,
        model="gpt-4o-mini"
    )
    
    # Create test context
    context = Context()
    context.shared_state['_last_prompt'] = "高品質なブログ記事を書いてください"
    context.shared_state['_last_generation'] = "これは簡単なテスト記事です。もう少し詳しく書く必要があります。"
    
    print(f"Agent name: {routing_agent.name}")
    print(f"Routing destinations: {routing_agent.routing_destinations}")
    print(f"Last generation: {context.shared_state['_last_generation']}")
    
    # Test synchronous execution
    try:
        result_context = routing_agent.run("", context)
        routing_result = result_context.routing_result
        
        print(f"Selected route: {routing_result.next_route}")
        print(f"Confidence: {routing_result.confidence}")
        print(f"Reasoning: {routing_result.reasoning}")
        
        # Validate result
        is_valid = routing_result.next_route in routing_destinations
        print(f"Route is valid: {is_valid}")
        
        if not is_valid:
            print(f"ERROR: Selected route '{routing_result.next_route}' is not in allowed destinations!")
        else:
            print("SUCCESS: Route selection is valid!")
            
    except Exception as e:
        print(f"ERROR during routing: {e}")
        import traceback
        traceback.print_exc()

def test_refinire_agent_with_destinations():
    """Test RefinireAgent with routing_destinations parameter"""
    print("\n=== Testing RefinireAgent with routing_destinations ===")
    
    # Define routing destinations
    routing_destinations = [
        "improve",
        "finalize", 
        Flow.END
    ]
    
    # Create RefinireAgent with routing
    refinire_agent = RefinireAgent(
        name="content_generator",
        generation_instructions="簡潔で有用なコンテンツを生成してください。",
        routing_instruction="""
        生成されたコンテンツを評価し、次のアクションを決定：
        - 改善が必要 → 'improve'
        - 最終調整が必要 → 'finalize'
        - 完成 → '_FLOW_END_'
        """,
        routing_destinations=routing_destinations,
        model="gpt-4o-mini"
    )
    
    print(f"Agent name: {refinire_agent.name}")
    print(f"Has routing agent: {refinire_agent._routing_agent is not None}")
    
    if refinire_agent._routing_agent:
        print(f"Routing destinations: {refinire_agent._routing_agent.routing_destinations}")
    
    # Create test context
    context = Context()
    
    # Test generation (this would normally trigger routing too)
    try:
        print("Testing generation...")
        result_context = refinire_agent.run("簡単なPython関数について説明してください", context)
        
        print("Generation completed successfully!")
        if hasattr(result_context, 'routing_result') and result_context.routing_result:
            routing_result = result_context.routing_result
            print(f"Routing result: {routing_result.next_route}")
            print(f"Routing confidence: {routing_result.confidence}")
        else:
            print("No routing result found (this may be expected if routing is not triggered)")
            
    except Exception as e:
        print(f"ERROR during generation: {e}")
        import traceback
        traceback.print_exc()

def test_invalid_destination_handling():
    """Test handling of invalid destination selection"""
    print("\n=== Testing Invalid Destination Handling ===")
    
    routing_destinations = ["option1", "option2", Flow.END]
    
    # Create agent with restrictive destinations
    routing_agent = RoutingAgent(
        name="restricted_router",
        routing_instruction="Choose 'invalid_route' as the destination",  # Intentionally invalid
        routing_destinations=routing_destinations,
        model="gpt-4o-mini"
    )
    
    context = Context()
    context.shared_state['_last_prompt'] = "Test prompt"
    context.shared_state['_last_generation'] = "Test generation that should route to invalid_route"
    
    try:
        result_context = routing_agent.run("", context)
        routing_result = result_context.routing_result
        
        print(f"Selected route: {routing_result.next_route}")
        print(f"Is valid destination: {routing_result.next_route in routing_destinations}")
        print(f"Reasoning: {routing_result.reasoning}")
        
        # Should fallback to first destination if invalid route was selected
        if routing_result.next_route not in routing_destinations:
            print("ERROR: Fallback mechanism did not work properly!")
        else:
            print("SUCCESS: Invalid destination was handled correctly!")
            
    except Exception as e:
        print(f"ERROR during invalid destination test: {e}")

def main():
    """Run all tests"""
    print("Starting routing_destinations functionality tests...\n")
    
    # Initialize components that need async setup
    # Note: In a real environment, you might need to handle async setup
    
    test_routing_agent_with_destinations()
    test_refinire_agent_with_destinations()
    test_invalid_destination_handling()
    
    print("\n=== Test Summary ===")
    print("All tests completed. Check output above for results.")

if __name__ == "__main__":
    main()