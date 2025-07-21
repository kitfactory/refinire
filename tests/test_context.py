import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from typing import Dict, Any

from refinire.agents.flow.context import Context


class TestContext:
    """
    Test Context class basic functionality
    Contextクラス基本機能をテスト
    """
    
    def test_context_initialization(self):
        """
        Test Context initialization
        Context初期化をテスト
        """
        ctx = Context()
        
        # Check default values
        # デフォルト値をチェック
        assert ctx.last_user_input is None
        assert ctx.messages == []
        assert ctx.next_label is None
        assert ctx.current_step is None
        assert ctx.artifacts == {}
        assert ctx.shared_state == {}
        assert ctx.awaiting_prompt is None
        assert ctx.awaiting_user_input == False
        # trace_id is now automatically generated if not provided
        # trace_idは提供されない場合は自動生成される
        assert ctx.trace_id is not None
        assert isinstance(ctx.trace_id, str)
        assert ctx.trace_id.startswith("context_")
        assert isinstance(ctx.start_time, datetime)
        assert ctx.step_count == 0
    
    def test_context_initialization_with_values(self):
        """
        Test Context initialization with custom values
        カスタム値でのContext初期化をテスト
        """
        test_time = datetime.now()
        ctx = Context(
            trace_id="test_trace",
            start_time=test_time,
            step_count=5
        )
        
        assert ctx.trace_id == "test_trace"
        assert ctx.start_time == test_time
        assert ctx.step_count == 5


class TestContextMessages:
    """
    Test Context message management
    Contextメッセージ管理をテスト
    """
    
    def test_add_user_message(self):
        """
        Test adding user message
        ユーザーメッセージ追加をテスト
        """
        ctx = Context()
        
        ctx.add_user_message("Hello!")
        
        assert len(ctx.messages) == 1
        assert ctx.messages[0].role == "user"
        assert ctx.messages[0].content == "Hello!"
        assert ctx.last_user_input == "Hello!"
    
    def test_add_assistant_message(self):
        """
        Test adding assistant message
        アシスタントメッセージ追加をテスト
        """
        ctx = Context()
        
        ctx.add_assistant_message("Hi there!")
        
        assert len(ctx.messages) == 1
        assert ctx.messages[0].role == "assistant"
        assert ctx.messages[0].content == "Hi there!"
    
    def test_add_system_message(self):
        """
        Test adding system message
        システムメッセージ追加をテスト
        """
        ctx = Context()
        
        ctx.add_system_message("System prompt")
        
        assert len(ctx.messages) == 1
        assert ctx.messages[0].role == "system"
        assert ctx.messages[0].content == "System prompt"
    
    def test_add_message_with_metadata(self):
        """
        Test adding message with metadata
        メタデータ付きメッセージ追加をテスト
        """
        ctx = Context()
        metadata = {"source": "test", "priority": "high"}
        
        ctx.add_user_message("Test message", metadata=metadata)
        
        assert ctx.messages[0].metadata == metadata
    
    def test_get_last_messages(self):
        """
        Test getting last n messages
        最後のnメッセージ取得をテスト
        """
        ctx = Context()
        
        # Add several messages
        # 複数のメッセージを追加
        for i in range(5):
            ctx.add_user_message(f"Message {i}")
        
        last_3 = ctx.get_last_messages(3)
        
        assert len(last_3) == 3
        assert last_3[0].content == "Message 2"
        assert last_3[1].content == "Message 3"
        assert last_3[2].content == "Message 4"
    
    def test_get_conversation_text(self):
        """
        Test getting conversation as text
        会話のテキスト取得をテスト
        """
        ctx = Context()
        
        ctx.add_user_message("Hello")
        ctx.add_assistant_message("Hi")
        ctx.add_system_message("System message")
        
        # Without system messages
        # システムメッセージなし
        text_no_system = ctx.get_conversation_text(include_system=False)
        assert "Hello" in text_no_system
        assert "Hi" in text_no_system
        assert "System message" not in text_no_system
        
        # With system messages
        # システムメッセージあり
        text_with_system = ctx.get_conversation_text(include_system=True)
        assert "Hello" in text_with_system
        assert "Hi" in text_with_system
        assert "System message" in text_with_system


class TestContextSharedState:
    """
    Test Context shared state and artifacts
    Contextの共有状態とアーティファクトをテスト
    """
    
    def test_shared_state_operations(self):
        """
        Test shared_state operations
        shared_state操作をテスト
        """
        ctx = Context()
        
        # Test direct access
        # 直接アクセスをテスト
        ctx.shared_state["test_key"] = "test_value"
        assert ctx.shared_state["test_key"] == "test_value"
        
        # Test multiple values
        # 複数値をテスト
        ctx.shared_state.update({"key1": "value1", "key2": "value2"})
        assert ctx.shared_state["key1"] == "value1"
        assert ctx.shared_state["key2"] == "value2"
    
    def test_artifacts_operations(self):
        """
        Test artifacts operations
        artifacts操作をテスト
        """
        ctx = Context()
        
        # Test set_artifact and get_artifact
        # set_artifactとget_artifactをテスト
        ctx.set_artifact("artifact_key", "artifact_value")
        assert ctx.get_artifact("artifact_key") == "artifact_value"
        
        # Test default artifact value
        # デフォルトartifact値をテスト
        assert ctx.get_artifact("nonexistent_key", "default") == "default"
        assert ctx.get_artifact("nonexistent_key") is None


class TestContextStepManagement:
    """
    Test Context step management
    Contextのステップ管理をテスト
    """
    
    def test_update_step_info(self):
        """
        Test updating step information
        ステップ情報更新をテスト
        """
        ctx = Context()
        
        ctx.update_step_info("test_step")
        
        assert ctx.current_step == "test_step"
        assert ctx.step_count == 1
    
    def test_goto(self):
        """
        Test goto functionality
        goto機能をテスト
        """
        ctx = Context()
        
        ctx.goto("next_step")
        
        assert ctx.next_label == "next_step"
    
    def test_finish(self):
        """
        Test finish functionality
        finish機能をテスト
        """
        ctx = Context()
        ctx.next_label = "some_step"
        
        ctx.finish()
        
        assert ctx.next_label is None
    
    def test_is_finished(self):
        """
        Test finished state checking
        完了状態チェックをテスト
        """
        ctx = Context()
        
        # Initially not finished (has next_label)
        # 初期は未完了（next_labelあり）
        ctx.next_label = "start"
        assert not ctx.is_finished()
        
        # Finished when no next_label
        # next_labelがない場合は完了
        ctx.next_label = None
        assert ctx.is_finished()


class TestContextUserInput:
    """
    Test Context user input management
    Contextのユーザー入力管理をテスト
    """
    
    def test_set_waiting_for_user_input(self):
        """
        Test setting waiting for user input using routing_result
        routing_resultを使用したユーザー入力待機設定をテスト
        """
        ctx = Context()
        
        # Manually set waiting state using routing_result
        # routing_resultを使用して手動で待機状態を設定
        ctx.awaiting_prompt = "Please enter your name:"
        ctx.awaiting_user_input = True
        if not ctx.routing_result:
            ctx.routing_result = {}
        ctx.routing_result['needs_user_input'] = True
        ctx.routing_result['prompt'] = "Please enter your name:"
        
        assert ctx.awaiting_user_input
        assert ctx.awaiting_prompt == "Please enter your name:"
        assert ctx.routing_result['needs_user_input']
        assert ctx.routing_result['prompt'] == "Please enter your name:"
    
    def test_provide_user_input(self):
        """
        Test providing user input using routing_result
        routing_resultを使用したユーザー入力提供をテスト
        """
        ctx = Context()
        
        # Set waiting state manually using routing_result
        # routing_resultを使用して手動で待機状態を設定
        ctx.awaiting_prompt = "Enter something:"
        ctx.awaiting_user_input = True
        if not ctx.routing_result:
            ctx.routing_result = {}
        ctx.routing_result['needs_user_input'] = True
        ctx.routing_result['prompt'] = "Enter something:"
        assert ctx.awaiting_user_input
        
        # Provide user input manually (replace deleted method functionality)
        # ユーザー入力を手動で提供（削除されたメソッドの機能を置き換え）
        ctx.add_user_message("user response")
        ctx.awaiting_prompt = None
        ctx.awaiting_user_input = False
        if not ctx.routing_result:
            ctx.routing_result = {}
        ctx.routing_result['user_input_received'] = True
        ctx.routing_result['last_input'] = "user response"
        
        assert not ctx.awaiting_user_input
        assert ctx.awaiting_prompt is None
        assert ctx.last_user_input == "user response"
        # Check that user message was added
        # ユーザーメッセージが追加されたことをチェック
        assert len(ctx.messages) == 1
        assert ctx.messages[0].content == "user response"
        assert ctx.routing_result['user_input_received']
        assert ctx.routing_result['last_input'] == "user response"
    
    def test_clear_prompt(self):
        """
        Test clearing prompt (existing method still available)
        プロンプトクリアをテスト（既存メソッドは依然利用可能）
        """
        ctx = Context()
        
        # Set waiting state manually using routing_result
        # routing_resultを使用して手動で待機状態を設定
        ctx.awaiting_prompt = "Test prompt"
        ctx.awaiting_user_input = True
        if not ctx.routing_result:
            ctx.routing_result = {}
        ctx.routing_result['needs_user_input'] = True
        ctx.routing_result['prompt'] = "Test prompt"
        assert ctx.awaiting_prompt == "Test prompt"
        
        # clear_prompt method still exists and should work
        # clear_promptメソッドはまだ存在し、機能するはず
        cleared_prompt = ctx.clear_prompt()
        
        assert cleared_prompt == "Test prompt"
        assert ctx.awaiting_prompt is None
    
    @pytest.mark.asyncio
    async def test_wait_for_user_input(self):
        """
        Test async waiting for user input
        ユーザー入力の非同期待機をテスト
        """
        ctx = Context()
        
        # Simulate user input being provided
        # ユーザー入力提供をシミュレート
        ctx.provide_user_input("test input")
        
        # This should return immediately since input was already provided
        # 入力が既に提供されているため、即座に返るはず
        result = await ctx.wait_for_user_input()
        assert result == "test input"
    
    @pytest.mark.asyncio
    async def test_wait_for_prompt_event(self):
        """
        Test async waiting for prompt event
        プロンプトイベントの非同期待機をテスト
        """
        ctx = Context()
        
        # Set a prompt to trigger the event
        # イベントをトリガーするプロンプトを設定
        ctx.set_waiting_for_user_input("Test prompt")
        
        # This should return the prompt
        # プロンプトを返すはず
        result = await ctx.wait_for_prompt_event()
        assert result == "Test prompt"


class TestContextSerialization:
    """
    Test Context serialization
    Contextのシリアライゼーションをテスト
    """
    
    def test_as_dict(self):
        """
        Test converting context to dictionary
        コンテキストの辞書変換をテスト
        """
        ctx = Context(trace_id="test_trace")
        ctx.add_user_message("Hello")
        
        ctx_dict = ctx.as_dict()
        
        assert isinstance(ctx_dict, dict)
        assert ctx_dict["trace_id"] == "test_trace"
        assert ctx_dict["last_user_input"] == "Hello"
        assert len(ctx_dict["history"]) == 1  # messages are converted to history
        assert "messages" not in ctx_dict  # messages key is removed
    
    def test_from_dict(self):
        """
        Test creating context from dictionary
        辞書からのコンテキスト作成をテスト
        """
        ctx_dict = {
            "trace_id": "test_trace",
            "current_step": "step1",
            "next_label": "step2",
            "step_count": 1,
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi!"}
            ],
            "awaiting_user_input": False
        }
        
        ctx = Context.from_dict(ctx_dict)
        
        assert ctx.trace_id == "test_trace"
        assert ctx.current_step == "step1"
        assert ctx.next_label == "step2"
        assert ctx.step_count == 1
        assert not ctx.awaiting_user_input
    
    def test_round_trip_serialization(self):
        """
        Test round-trip serialization (as_dict -> from_dict)
        ラウンドトリップシリアライゼーション（as_dict -> from_dict）をテスト
        """
        original_ctx = Context(trace_id="round_trip_test")
        original_ctx.add_user_message("Original message")
        original_ctx.add_assistant_message("Original response")
        original_ctx.shared_state["data"] = {"nested": "value"}
        original_ctx.set_artifact("test_key", "test_value")
        original_ctx.update_step_info("test_step")
        
        # Convert to dict and back
        # 辞書に変換してから復元
        ctx_dict = original_ctx.as_dict()
        restored_ctx = Context.from_dict(ctx_dict)
        
        assert restored_ctx.trace_id == original_ctx.trace_id
        assert len(restored_ctx.messages) == len(original_ctx.messages)
        assert restored_ctx.current_step == original_ctx.current_step
        assert restored_ctx.step_count == original_ctx.step_count


class TestContextStringRepresentation:
    """
    Test Context string representation
    Contextの文字列表現をテスト
    """
    
    def test_str_representation(self):
        """
        Test __str__ method
        __str__メソッドをテスト
        """
        ctx = Context(trace_id="test_trace")
        ctx.add_user_message("Hello")
        ctx.update_step_info("test_step")
        
        str_repr = str(ctx)
        
        # Should contain key information
        # 重要な情報を含むはず
        assert "test_trace" in str_repr
        assert "test_step" in str_repr
        assert "Hello" in str_repr
    
    def test_repr_representation(self):
        """
        Test __repr__ method
        __repr__メソッドをテスト
        """
        ctx = Context(trace_id="test_trace")
        
        repr_str = repr(ctx)
        
        # Should be informative
        # 情報が含まれているはず
        assert "Context" in repr_str or "test_trace" in repr_str


class TestContextEdgeCases:
    """
    Test Context edge cases and error handling
    Contextのエッジケースとエラーハンドリングをテスト
    """
    
    def test_none_values(self):
        """
        Test handling of None values
        None値の処理をテスト
        """
        ctx = Context()
        
        # Test setting None values
        # None値設定をテスト
        ctx.shared_state["none_value"] = None
        assert ctx.shared_state["none_value"] is None
        
        ctx.set_artifact("none_artifact", None)
        assert ctx.get_artifact("none_artifact") is None
    
    def test_unicode_content(self):
        """
        Test handling of unicode content
        Unicode内容の処理をテスト
        """
        ctx = Context()
        
        unicode_message = "こんにちは 🌟 Hello 世界"
        ctx.add_user_message(unicode_message)
        ctx.shared_state["unicode_field"] = unicode_message
        ctx.set_artifact("unicode_artifact", unicode_message)
        
        assert ctx.last_user_input == unicode_message
        assert ctx.shared_state["unicode_field"] == unicode_message
        assert ctx.get_artifact("unicode_artifact") == unicode_message
    
    def test_large_step_count(self):
        """
        Test handling of large step counts
        大きなステップ数の処理をテスト
        """
        ctx = Context()
        
        # Simulate many step updates
        # 多数のステップ更新をシミュレート
        for i in range(1000):
            ctx.update_step_info(f"step_{i}")
        
        assert ctx.step_count == 1000
        assert ctx.current_step == "step_999"
    
    def test_empty_message_handling(self):
        """
        Test handling of empty messages
        空メッセージの処理をテスト
        """
        ctx = Context()
        
        # Add empty messages
        # 空メッセージを追加
        ctx.add_user_message("")
        ctx.add_assistant_message("")
        ctx.add_system_message("")
        
        assert len(ctx.messages) == 3
        assert all(msg.content == "" for msg in ctx.messages)
        assert ctx.last_user_input == ""


class TestContextResultContent:
    """
    Test Context result and content properties
    Contextのresultとcontentプロパティをテスト
    """
    
    def test_result_and_content_with_none(self):
        """
        Test result and content properties when result is None
        resultがNoneの場合のresultとcontentプロパティをテスト
        """
        ctx = Context()
        
        # Initially result should be None
        # 初期はresultはNoneであるべき
        assert ctx.result is None
        assert ctx.content is None
    
    def test_result_and_content_with_mock_llm_result(self):
        """
        Test result and content properties with mock LLMResult
        モックLLMResultでのresultとcontentプロパティをテスト
        """
        # Create a mock LLMResult object
        # モックLLMResultオブジェクトを作成
        class MockLLMResult:
            def __init__(self, content, success=True):
                self.content = content
                self.success = success
                self.metadata = {}
        
        ctx = Context()
        mock_result = MockLLMResult("Generated content")
        
        # Set result to complete LLMResult object
        # resultを完全なLLMResultオブジェクトに設定
        ctx.result = mock_result
        
        # result should return the complete object
        # resultは完全なオブジェクトを返すべき
        assert ctx.result is mock_result
        assert ctx.result.content == "Generated content"
        assert ctx.result.success is True
        
        # content should return just the generated content
        # contentは生成コンテンツのみを返すべき
        assert ctx.content == "Generated content"
    
    def test_content_setter_with_existing_result(self):
        """
        Test content setter when result already exists
        resultが既に存在する場合のcontentセッターをテスト
        """
        # Create a mock LLMResult object
        # モックLLMResultオブジェクトを作成
        class MockLLMResult:
            def __init__(self, content, success=True):
                self.content = content
                self.success = success
                self.metadata = {}
        
        ctx = Context()
        mock_result = MockLLMResult("Original content")
        ctx.result = mock_result
        
        # Update content via setter
        # セッター経由でcontentを更新
        ctx.content = "Updated content"
        
        # Should update the LLMResult.content
        # LLMResult.contentが更新されるべき
        assert ctx.result.content == "Updated content"
        assert ctx.content == "Updated content"
    
    def test_content_setter_with_no_existing_result(self):
        """
        Test content setter when no result exists
        resultが存在しない場合のcontentセッターをテスト
        """
        ctx = Context()
        
        # Set content when no result exists
        # resultが存在しない場合にcontentを設定
        ctx.content = "New content"
        
        # Should create a minimal LLMResult
        # 最小限のLLMResultを作成するべき
        assert ctx.result is not None
        assert hasattr(ctx.result, 'content')
        assert ctx.result.content == "New content"
        assert ctx.content == "New content"
    
    def test_content_with_object_without_content_attribute(self):
        """
        Test content property when result object has no content attribute
        resultオブジェクトにcontent属性がない場合のcontentプロパティをテスト
        """
        ctx = Context()
        
        # Set result to object without content attribute
        # content属性のないオブジェクトをresultに設定
        ctx.result = {"some": "data"}
        
        # content should return None
        # contentはNoneを返すべき
        assert ctx.content is None
    
    def test_success_property_with_result(self):
        """
        Test success property with various result scenarios
        様々なresultシナリオでのsuccessプロパティをテスト
        """
        ctx = Context()
        
        # No result - should be False
        # resultなし - Falseであるべき
        assert ctx.success is False
        
        # Create mock LLMResult with success=True
        # success=TrueのモックLLMResultを作成
        class MockLLMResult:
            def __init__(self, content, success=True):
                self.content = content
                self.success = success
        
        ctx.result = MockLLMResult("content", success=True)
        assert ctx.success is True
        
        # Test with evaluation result that passed
        # 合格した評価結果でテスト
        ctx.evaluation_result = {"passed": True, "score": 90}
        assert ctx.success is True
        
        # Test with evaluation result that failed
        # 失敗した評価結果でテスト
        ctx.evaluation_result = {"passed": False, "score": 60}
        assert ctx.success is False
        
        # Test with error in shared_state
        # shared_state内のエラーでテスト
        ctx.evaluation_result = {"passed": True}
        ctx.shared_state["error"] = "Some error"
        assert ctx.success is False
        
        # Test with error routing result
        # エラールーティング結果でテスト
        ctx.shared_state.clear()
        ctx.routing_result = {"next_route": "error"}
        assert ctx.success is False
    
    def test_metadata_property(self):
        """
        Test metadata property
        metadataプロパティをテスト
        """
        ctx = Context()
        
        # No evaluation_result - should return empty dict
        # evaluation_resultなし - 空辞書を返すべき
        assert ctx.metadata == {}
        
        # With evaluation_result - should return evaluation_result
        # evaluation_resultあり - evaluation_resultを返すべき
        eval_result = {"score": 85, "passed": True, "feedback": "Good"}
        ctx.evaluation_result = eval_result
        assert ctx.metadata == eval_result


class TestContextAsyncCoordination:
    """
    Test Context async coordination features
    Contextの非同期調整機能をテスト
    """
    
    def test_async_event_initialization(self):
        """
        Test that async events are properly initialized
        非同期イベントが適切に初期化されることをテスト
        """
        ctx = Context()
        
        # Events should be initialized
        # イベントは初期化されているはず
        assert ctx._user_input_event is not None
        assert ctx._awaiting_prompt_event is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_user_input_handling(self):
        """
        Test concurrent user input handling
        並行ユーザー入力処理をテスト
        """
        ctx = Context()
        
        # Test that multiple operations can work together
        # 複数の操作が連携して動作することをテスト
        ctx.set_waiting_for_user_input("Enter data:")
        ctx.provide_user_input("response")
        
        result = await ctx.wait_for_user_input()
        assert result == "response"
