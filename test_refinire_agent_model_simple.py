"""Test RefinireAgent model parameter handling (simplified)
RefinireAgentのmodelパラメータ処理のテスト（簡略版）
"""

import os
from unittest.mock import Mock, patch
from refinire.agents.pipeline.llm_pipeline import RefinireAgent
from agents import Model


def test_refinire_agent_model_handling():
    """Test RefinireAgent model parameter handling logic
    RefinireAgentのmodelパラメータ処理ロジックのテスト
    """
    # Mock the get_llm function to avoid API calls
    # API呼び出しを避けるためget_llm関数をモック
    mock_model = Mock(spec=Model)
    mock_model.model = "gpt-4o-mini"
    
    with patch('refinire.agents.pipeline.llm_pipeline.get_llm') as mock_get_llm:
        mock_get_llm.return_value = mock_model
        
        # Test 1: String model name
        # テスト1: 文字列モデル名
        print("Test 1: String model name")
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a test assistant.",
            model="gpt-4o-mini"
        )
        
        # Verify get_llm was called with correct parameters
        # get_llmが正しいパラメータで呼ばれたことを確認
        mock_get_llm.assert_called_with(model="gpt-4o-mini", temperature=0.7)
        assert agent.model_name == "gpt-4o-mini"
        assert agent.model == mock_model
        print("✓ String model name test passed")
        
        # Test 2: Model instance
        # テスト2: Modelインスタンス
        print("\nTest 2: Model instance")
        existing_model = Mock(spec=Model)
        existing_model.model = "claude-opus-4"
        
        agent2 = RefinireAgent(
            name="test_agent2",
            generation_instructions="You are a test assistant.",
            model=existing_model
        )
        
        # Verify model is used directly
        # modelが直接使用されることを確認
        assert agent2.model == existing_model
        assert agent2.model_name == "claude-opus-4"
        print("✓ Model instance test passed")
        
        # Test 3: Evaluation model
        # テスト3: 評価モデル
        print("\nTest 3: Evaluation model")
        mock_eval_model = Mock(spec=Model)
        mock_eval_model.model = "gpt-4o"
        
        # Reset mock for new call
        # 新しい呼び出しのためモックをリセット
        mock_get_llm.reset_mock()
        mock_get_llm.side_effect = [mock_model, mock_eval_model]
        
        agent3 = RefinireAgent(
            name="test_agent3",
            generation_instructions="You are a test assistant.",
            evaluation_instructions="Evaluate the response.",
            model="gpt-4o-mini",
            evaluation_model="gpt-4o"
        )
        
        # Verify both models were created
        # 両方のモデルが作成されたことを確認
        assert mock_get_llm.call_count == 2
        assert agent3.model_name == "gpt-4o-mini"
        assert agent3.evaluation_model_name == "gpt-4o"
        assert agent3.model != agent3.evaluation_model
        print("✓ Evaluation model test passed")
        
        # Test 4: Default evaluation model
        # テスト4: デフォルト評価モデル
        print("\nTest 4: Default evaluation model")
        mock_get_llm.reset_mock()
        mock_get_llm.side_effect = None  # Clear side_effect
        mock_get_llm.return_value = mock_model
        
        agent4 = RefinireAgent(
            name="test_agent4",
            generation_instructions="You are a test assistant.",
            evaluation_instructions="Evaluate the response.",
            model="gpt-4o-mini"
        )
        
        # Evaluation model should default to main model
        # 評価モデルはメインモデルにデフォルト設定される
        assert agent4.model == agent4.evaluation_model
        assert agent4.model_name == agent4.evaluation_model_name
        print("✓ Default evaluation model test passed")


def test_agent_sdk_initialization():
    """Test that SDK agent is initialized with Model instance
    SDKエージェントがModelインスタンスで初期化されることをテスト
    """
    mock_model = Mock(spec=Model)
    mock_model.model = "gpt-4o-mini"
    
    with patch('refinire.agents.pipeline.llm_pipeline.get_llm') as mock_get_llm:
        mock_get_llm.return_value = mock_model
        
        with patch('refinire.agents.pipeline.llm_pipeline.Agent') as mock_agent_class:
            agent = RefinireAgent(
                name="test_agent",
                generation_instructions="Test instructions",
                model="gpt-4o-mini"
            )
            
            # Verify Agent was initialized with model instance
            # AgentがModelインスタンスで初期化されたことを確認
            mock_agent_class.assert_called_once()
            call_args = mock_agent_class.call_args[1]
            assert call_args['model'] == mock_model
            assert call_args['name'] == "test_agent_sdk_agent"
            assert call_args['instructions'] == "Test instructions"
            print("✓ SDK agent initialization test passed")


if __name__ == "__main__":
    print("Testing RefinireAgent model parameter handling (simplified)...")
    print("=" * 60)
    
    try:
        test_refinire_agent_model_handling()
        print("\n" + "-" * 60 + "\n")
        test_agent_sdk_initialization()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("\nSummary:")
        print("- RefinireAgent now accepts both string model names and Model instances")
        print("- String model names are converted to Model instances using get_llm()")
        print("- Model instances are passed directly to the SDK Agent")
        print("- Evaluation models can be specified separately")
        print("\n文字列モデル名とModelインスタンスの両方を適切に処理できるようになりました。")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()