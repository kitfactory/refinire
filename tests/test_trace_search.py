#!/usr/bin/env python3
"""
Test trace search functionality
トレース検索機能のテスト
"""

import asyncio
import pytest
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import (
    Flow, Context, FunctionStep, TraceRegistry, 
    get_global_registry, set_global_registry, TraceMetadata
)


class TestTraceRegistry:
    """
    Test TraceRegistry class
    TraceRegistryクラスをテスト
    """
    
    def setup_method(self):
        """Setup for each test / 各テストのセットアップ"""
        self.registry = TraceRegistry()
        
    def test_register_trace(self):
        """
        Test trace registration
        トレース登録をテスト
        """
        # Register a trace
        # トレースを登録
        self.registry.register_trace(
            trace_id="test_trace_001",
            flow_name="test_flow",
            flow_id="flow_001",
            agent_names=["Agent1", "Agent2"],
            tags={"environment": "test"}
        )
        
        # Verify registration
        # 登録を検証
        trace = self.registry.get_trace("test_trace_001")
        assert trace is not None
        assert trace.flow_name == "test_flow"
        assert trace.flow_id == "flow_001"
        assert "Agent1" in trace.agent_names
        assert "Agent2" in trace.agent_names
        assert trace.tags["environment"] == "test"
        assert trace.status == "running"
    
    def test_search_by_flow_name(self):
        """
        Test search by flow name
        フロー名による検索をテスト
        """
        # Register multiple traces
        # 複数のトレースを登録
        self.registry.register_trace("trace1", flow_name="customer_support")
        self.registry.register_trace("trace2", flow_name="customer_service")
        self.registry.register_trace("trace3", flow_name="data_processing")
        
        # Exact match search
        # 完全一致検索
        exact_results = self.registry.search_by_flow_name("customer_support", exact_match=True)
        assert len(exact_results) == 1
        assert exact_results[0].flow_name == "customer_support"
        
        # Partial match search
        # 部分一致検索
        partial_results = self.registry.search_by_flow_name("customer", exact_match=False)
        assert len(partial_results) == 2
        flow_names = [trace.flow_name for trace in partial_results]
        assert "customer_support" in flow_names
        assert "customer_service" in flow_names
    
    def test_search_by_agent_name(self):
        """
        Test search by agent name
        エージェント名による検索をテスト
        """
        # Register traces with different agents
        # 異なるエージェントでトレースを登録
        self.registry.register_trace("trace1", agent_names=["SupportAgent", "AnalysisAgent"])
        self.registry.register_trace("trace2", agent_names=["ExtractorAgent", "SupportAgent"])
        self.registry.register_trace("trace3", agent_names=["ProcessingAgent"])
        
        # Exact match search
        # 完全一致検索
        exact_results = self.registry.search_by_agent_name("SupportAgent", exact_match=True)
        assert len(exact_results) == 2
        
        # Partial match search
        # 部分一致検索
        partial_results = self.registry.search_by_agent_name("Agent", exact_match=False)
        print(f"Debug: Found {len(partial_results)} traces with 'Agent' in name")
        for trace in partial_results:
            print(f"  - {trace.trace_id}: {trace.agent_names}")
        assert len(partial_results) >= 2  # At least traces with SupportAgent should match


if __name__ == "__main__":
    # Run basic tests
    test_registry = TestTraceRegistry()
    test_registry.setup_method()
    
    print("🧪 Running basic trace search tests...")
    
    try:
        test_registry.test_register_trace()
        print("✅ test_register_trace passed")
        
        test_registry.test_search_by_flow_name()
        print("✅ test_search_by_flow_name passed")
        
        test_registry.test_search_by_agent_name()
        print("✅ test_search_by_agent_name passed")
        
        print("\n🎉 All basic tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 
