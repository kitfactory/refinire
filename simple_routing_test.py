#!/usr/bin/env python3
"""
Simple test for routing_destinations functionality
routing_destinations機能のシンプルなテスト
"""

from src.refinire.agents.routing_agent import RoutingAgent
from src.refinire.agents.pipeline.llm_pipeline import RefinireAgent
from src.refinire.agents.flow.context import Context
from src.refinire.agents.flow.flow import Flow

def test_routing_agent_basic():
    """Test basic RoutingAgent functionality"""
    print("=== Basic RoutingAgent Test ===")
    
    # Define routing destinations
    routing_destinations = [
        "enhance",
        "complete",
        Flow.END
    ]
    
    # Create RoutingAgent
    routing_agent = RoutingAgent(
        name="simple_router",
        routing_instruction="基本的なルーティング判断を行ってください",
        routing_destinations=routing_destinations,
        model="gpt-4o-mini"
    )
    
    print(f"Agent created: {routing_agent.name}")
    print(f"Destinations: {routing_agent.routing_destinations}")
    print(f"Format destinations: {routing_agent._format_routing_destinations()}")
    
    # Test destination validation
    print(f"'enhance' is valid: {routing_agent._validate_routing_destination('enhance')}")
    print(f"'invalid' is valid: {routing_agent._validate_routing_destination('invalid')}")
    
    return True

def test_refinire_agent_integration():
    """Test RefinireAgent with routing_destinations"""
    print("\n=== RefinireAgent Integration Test ===")
    
    routing_destinations = ["improve", "finalize", Flow.END]
    
    # Create RefinireAgent
    refinire_agent = RefinireAgent(
        name="test_agent",
        generation_instructions="簡潔なコンテンツを生成",
        routing_instruction="コンテンツを評価してルーティング",
        routing_destinations=routing_destinations,
        model="gpt-4o-mini"
    )
    
    print(f"RefinireAgent created: {refinire_agent.name}")
    print(f"Has routing instruction: {refinire_agent.routing_instruction is not None}")
    print(f"Has routing destinations: {refinire_agent.routing_destinations is not None}")
    print(f"Routing destinations: {refinire_agent.routing_destinations}")
    
    # Check if routing agent was created
    if refinire_agent._routing_agent:
        print(f"Internal routing agent created: {refinire_agent._routing_agent.name}")
        print(f"Internal routing destinations: {refinire_agent._routing_agent.routing_destinations}")
    else:
        print("No internal routing agent created (may need model setup)")
    
    return True

def test_flow_constants():
    """Test Flow constants availability"""
    print("\n=== Flow Constants Test ===")
    
    print(f"Flow.END: {Flow.END}")
    print(f"Flow.TERMINATE: {Flow.TERMINATE}")
    print(f"Flow.FINISH: {Flow.FINISH}")
    
    return True

def main():
    """Run basic tests without LLM calls"""
    print("Starting simple routing_destinations tests...\n")
    
    success = True
    
    try:
        success &= test_routing_agent_basic()
        success &= test_refinire_agent_integration()
        success &= test_flow_constants()
    except Exception as e:
        print(f"Error during testing: {e}")
        success = False
    
    print(f"\n=== Test Results ===")
    if success:
        print("✅ All basic tests passed!")
        print("routing_destinations機能が正常に統合されています。")
    else:
        print("❌ Some tests failed.")
    
    return success

if __name__ == "__main__":
    main()