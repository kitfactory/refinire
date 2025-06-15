import pytest
import logging
from unittest.mock import MagicMock, patch, call
from datetime import datetime
import json
from io import StringIO

from refinire import (
    enable_console_tracing, disable_tracing, Context
)
from refinire.core.tracing import (
    ConsoleTracingProcessor, _merge_msgs, extract_output_texts
)


class TestConsoleTracingProcessor:
    """
    Test ConsoleTracingProcessor class
    ConsoleTracingProcessorクラスをテスト
    """
    
    def test_console_tracing_processor_initialization(self):
        """
        Test ConsoleTracingProcessor initialization
        ConsoleTracingProcessor初期化をテスト
        """
        import sys
        processor = ConsoleTracingProcessor()
        
        assert processor.output_stream == sys.stdout
    
    def test_console_tracing_processor_with_custom_stream(self):
        """
        Test ConsoleTracingProcessor with custom output stream
        カスタム出力ストリームでのConsoleTracingProcessorをテスト
        """
        custom_stream = StringIO()
        processor = ConsoleTracingProcessor(output_stream=custom_stream)
        
        assert processor.output_stream == custom_stream
    
    def test_console_tracing_processor_methods(self):
        """
        Test ConsoleTracingProcessor methods
        ConsoleTracingProcessorメソッドをテスト
        """
        custom_stream = StringIO()
        processor = ConsoleTracingProcessor(output_stream=custom_stream)
        
        # Test that methods don't raise errors
        # メソッドがエラーを発生させないことをテスト
        processor.on_trace_start(None)
        processor.on_trace_end(None)
        processor.on_span_start(None)
        processor.shutdown()
        processor.force_flush()
        
        # No exceptions should be raised
        # 例外は発生しないはず
        assert True


class TestTracingFunctions:
    """
    Test tracing utility functions
    トレーシングユーティリティ関数をテスト
    """
    
    def test_enable_console_tracing(self):
        """
        Test enable_console_tracing function
        enable_console_tracing関数をテスト
        """
        with patch('refinire.core.tracing.set_tracing_disabled') as mock_set_disabled:
            with patch('refinire.core.tracing.set_trace_processors') as mock_set_processors:
                enable_console_tracing()
                
                # Check that tracing was enabled
                # トレーシングが有効化されたことをチェック
                mock_set_disabled.assert_called_once_with(False)
                mock_set_processors.assert_called_once()
                
                # Check that a ConsoleTracingProcessor was registered
                # ConsoleTracingProcessorが登録されたことをチェック
                call_args = mock_set_processors.call_args[0][0]
                assert len(call_args) == 1
                assert isinstance(call_args[0], ConsoleTracingProcessor)
    
    def test_disable_tracing(self):
        """
        Test disable_tracing function
        disable_tracing関数をテスト
        """
        with patch('refinire.core.tracing.set_tracing_disabled') as mock_set_disabled:
            disable_tracing()
            
            # Check that tracing was disabled
            # トレーシングが無効化されたことをチェック
            mock_set_disabled.assert_called_once_with(True)


class TestTracingUtilities:
    """
    Test tracing utility functions
    トレーシングユーティリティ関数をテスト
    """
    
    def test_merge_msgs(self):
        """
        Test _merge_msgs function
        _merge_msgs関数をテスト
        """
        # Test with user messages
        # ユーザーメッセージでのテスト
        msgs = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "How are you?"}
        ]
        
        user_content = _merge_msgs(msgs, "user")
        assert user_content == "Hello\nHow are you?"
        
        assistant_content = _merge_msgs(msgs, "assistant")
        assert assistant_content == "Hi"
        
        # Test with empty messages
        # 空メッセージでのテスト
        empty_content = _merge_msgs([], "user")
        assert empty_content == ""
        
        # Test with None
        # Noneでのテスト
        none_content = _merge_msgs(None, "user")
        assert none_content == ""
    
    def test_extract_output_texts(self):
        """
        Test extract_output_texts function
        extract_output_texts関数をテスト
        """
        # Test with simple text object
        # 単純なテキストオブジェクトでのテスト
        class TextObject:
            def __init__(self, text):
                self.text = text
        
        text_obj = TextObject("Hello world")
        result = extract_output_texts(text_obj)
        assert result == ["Hello world"]
        
        # Test with dict containing text
        # テキストを含む辞書でのテスト
        text_dict = {"text": "Dictionary text"}
        result = extract_output_texts(text_dict)
        assert result == ["Dictionary text"]
        
        # Test with list of objects
        # オブジェクトのリストでのテスト
        text_list = [TextObject("Text 1"), TextObject("Text 2")]
        result = extract_output_texts(text_list)
        assert result == ["Text 1", "Text 2"]
        
        # Test with nested structure
        # ネストした構造でのテスト
        nested_dict = {
            "content": [
                {"text": "Nested text 1"},
                {"text": "Nested text 2"}
            ]
        }
        result = extract_output_texts(nested_dict)
        assert result == ["Nested text 1", "Nested text 2"]
        
        # Test with empty input
        # 空の入力でのテスト
        result = extract_output_texts([])
        assert result == []
        
        result = extract_output_texts({})
        assert result == []


class TestTracingIntegration:
    """
    Test tracing integration scenarios
    トレーシング統合シナリオをテスト
    """
    
    def test_console_tracing_with_context(self):
        """
        Test console tracing with Context integration
        Context統合でのコンソールトレーシングをテスト
        """
        custom_stream = StringIO()
        processor = ConsoleTracingProcessor(output_stream=custom_stream)
        
        # Test that processor can be created and used
        # プロセッサーが作成され使用できることをテスト
        processor.force_flush()
        
        # Get output
        # 出力を取得
        output = custom_stream.getvalue()
        assert isinstance(output, str)  # Should be a string (empty in this case)
    
    def test_tracing_enable_disable_cycle(self):
        """
        Test enabling and disabling tracing
        トレーシングの有効化・無効化サイクルをテスト
        """
        with patch('refinire.core.tracing.set_tracing_disabled') as mock_set_disabled:
            with patch('refinire.core.tracing.set_trace_processors') as mock_set_processors:
                # Enable tracing
                # トレーシングを有効化
                enable_console_tracing()
                
                # Disable tracing  
                # トレーシングを無効化
                disable_tracing()
                
                # Check calls were made
                # 呼び出しが行われたことをチェック
                assert mock_set_disabled.call_count == 2
                mock_set_processors.assert_called_once()


class TestTracingErrorHandling:
    """
    Test tracing error handling scenarios
    トレーシングエラーハンドリングシナリオをテスト
    """
    
    def test_console_processor_with_invalid_stream(self):
        """
        Test ConsoleTracingProcessor with invalid stream
        無効なストリームでのConsoleTracingProcessorをテスト
        """
        # Test with None stream (should not crash)
        # Noneストリームでのテスト（クラッシュしないはず）
        processor = ConsoleTracingProcessor(output_stream=None)
        
        # Methods should handle None stream gracefully
        # メソッドはNoneストリームを適切に処理するはず
        processor.on_trace_start(None)
        processor.on_trace_end(None)
        processor.on_span_start(None)
        processor.on_span_end(None)
        processor.shutdown()
        
        # Should not raise exceptions
        # 例外は発生しないはず
        assert True


class TestMessageLocalization:
    """
    Test message localization integration
    メッセージローカライゼーション統合をテスト
    """
    
    def test_localized_trace_labels(self):
        """
        Test that trace labels are localized
        トレースラベルがローカライズされることをテスト
        """
        from refinire.core.message import get_message
        
        # Test English labels
        # 英語ラベルをテスト
        en_instruction = get_message("trace_instruction", "en")
        en_prompt = get_message("trace_prompt", "en")
        en_output = get_message("trace_output", "en")
        
        assert "Instruction" in en_instruction
        assert "Prompt" in en_prompt
        assert "Output" in en_output
        
        # Test Japanese labels
        # 日本語ラベルをテスト
        ja_instruction = get_message("trace_instruction", "ja")
        ja_prompt = get_message("trace_prompt", "ja")
        ja_output = get_message("trace_output", "ja")
        
        assert "インストラクション" in ja_instruction
        assert "プロンプト" in ja_prompt
        assert "LLM出力" in ja_output


class TestTracingPerformance:
    """
    Test tracing performance characteristics
    トレーシングパフォーマンス特性をテスト
    """
    
    def test_console_processor_performance(self):
        """
        Test ConsoleTracingProcessor performance
        ConsoleTracingProcessorのパフォーマンスをテスト
        """
        custom_stream = StringIO()
        processor = ConsoleTracingProcessor(output_stream=custom_stream)
        
        # Simulate many span end calls
        # 多数のspan end呼び出しをシミュレート
        for i in range(100):
            processor.on_span_end(None)
        
        # Should complete without issues
        # 問題なく完了するはず
        processor.force_flush()
        assert True
    
    def test_extract_output_texts_performance(self):
        """
        Test extract_output_texts with large nested structures
        大きなネスト構造でのextract_output_textsをテスト
        """
        # Create large nested structure
        # 大きなネスト構造を作成
        large_structure = {
            "content": [
                {"text": f"Text {i}"} for i in range(1000)
            ]
        }
        
        result = extract_output_texts(large_structure)
        
        # Should handle large structures efficiently
        # 大きな構造を効率的に処理するはず
        assert len(result) == 1000
        assert result[0] == "Text 0"
        assert result[999] == "Text 999"
