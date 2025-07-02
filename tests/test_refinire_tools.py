"""
Tests for Refinire tool decorators and utilities
Refinireツールデコレータとユーティリティのテスト
"""

import pytest
from refinire import tool, function_tool_compat, get_tool_info, list_tools


def test_tool_decorator_basic():
    """Test basic @tool decorator functionality"""
    @tool
    def sample_tool(text: str) -> str:
        """A sample tool for testing"""
        return f"Processed: {text}"
    
    # Check that the function works
    # 関数が動作することを確認
    result = sample_tool("test")
    assert result == "Processed: test"
    
    # Check Refinire metadata
    # Refinireメタデータを確認
    assert hasattr(sample_tool, '_refinire_tool')
    assert sample_tool._refinire_tool is True
    assert sample_tool._refinire_tool_name == "sample_tool"
    assert sample_tool._refinire_tool_description == "A sample tool for testing"


def test_tool_decorator_with_params():
    """Test @tool decorator with custom name and description"""
    @tool(name="custom_name", description="Custom description")
    def another_tool(data: int) -> int:
        """Original docstring"""
        return data * 2
    
    # Check functionality
    # 機能を確認
    result = another_tool(5)
    assert result == 10
    
    # Check custom metadata
    # カスタムメタデータを確認
    assert another_tool._refinire_tool is True
    assert another_tool._refinire_tool_name == "custom_name"
    assert another_tool._refinire_tool_description == "Custom description"
    
    # Original function name should be preserved
    # 元の関数名は保持されているべき
    assert another_tool.__name__ == "another_tool"


def test_function_tool_compat():
    """Test compatibility alias for function_tool"""
    @function_tool_compat
    def compat_tool(value: str) -> str:
        """Compatibility test tool"""
        return f"Compatible: {value}"
    
    # Should work like the original
    # オリジナルのように動作するべき
    result = compat_tool("test")
    assert result == "Compatible: test"


def test_get_tool_info():
    """Test tool information extraction"""
    @tool(name="info_tool", description="Tool for info testing")
    def test_tool(x: int) -> int:
        """Test tool docstring"""
        return x + 1
    
    info = get_tool_info(test_tool)
    
    assert info['is_refinire_tool'] is True
    assert info['name'] == "info_tool"
    assert info['description'] == "Tool for info testing"
    assert info['function_name'] == "test_tool"
    assert info['docstring'] == "Test tool docstring"


def test_get_tool_info_non_refinire():
    """Test tool info for non-Refinire functions"""
    def regular_function(x: int) -> int:
        """Just a regular function"""
        return x
    
    info = get_tool_info(regular_function)
    
    assert info['is_refinire_tool'] is False
    assert info['name'] == "regular_function"
    assert info['description'] == "Just a regular function"
    assert info['function_name'] == "regular_function"


def test_list_tools():
    """Test listing multiple tools"""
    @tool
    def tool1(x: str) -> str:
        """First tool"""
        return x
    
    @tool(name="second", description="Second tool desc")
    def tool2(y: int) -> int:
        """Second tool"""
        return y
    
    def regular_func(z: float) -> float:
        """Not a tool"""
        return z
    
    tools = [tool1, tool2, regular_func]
    tool_list = list_tools(tools)
    
    assert len(tool_list) == 3
    
    # Check first tool
    # 最初のツールを確認
    assert tool_list[0]['is_refinire_tool'] is True
    assert tool_list[0]['name'] == "tool1"
    assert tool_list[0]['description'] == "First tool"
    
    # Check second tool
    # 2番目のツールを確認
    assert tool_list[1]['is_refinire_tool'] is True
    assert tool_list[1]['name'] == "second"
    assert tool_list[1]['description'] == "Second tool desc"
    
    # Check regular function
    # 通常の関数を確認
    assert tool_list[2]['is_refinire_tool'] is False
    assert tool_list[2]['name'] == "regular_func"
    assert tool_list[2]['description'] == "Not a tool"


def test_tool_preserves_original_metadata():
    """Test that @tool preserves original function metadata"""
    @tool
    def original_function(param: str) -> str:
        """Original docstring with details"""
        return param.upper()
    
    # Function should still work normally
    # 関数は通常通り動作するべき
    assert original_function("hello") == "HELLO"
    
    # Original metadata should be preserved
    # 元のメタデータは保持されているべき
    assert original_function.__name__ == "original_function"
    assert original_function.__doc__ == "Original docstring with details"
    
    # But Refinire metadata should be added
    # しかしRefinireメタデータが追加されているべき
    assert original_function._refinire_tool is True


def test_tool_without_docstring():
    """Test @tool with function that has no docstring"""
    @tool
    def no_docstring_tool(x: int) -> int:
        return x * 3
    
    # Should handle missing docstring gracefully
    # docstringがない場合を適切に処理するべき
    info = get_tool_info(no_docstring_tool)
    assert info['description'] is None
    assert info['docstring'] is None
    assert info['is_refinire_tool'] is True


def test_tool_decorator_edge_cases():
    """Test edge cases for tool decorator"""
    # Test with empty description
    # 空の説明でテスト
    @tool(description="")
    def empty_desc_tool() -> str:
        return "empty"
    
    assert empty_desc_tool._refinire_tool_description == ""
    
    # Test with None description but function has docstring
    # 説明がNoneだが関数にdocstringがある場合のテスト
    @tool(description=None)
    def none_desc_tool() -> str:
        """Function docstring"""
        return "none"
    
    # Should fall back to docstring
    # docstringにフォールバックするべき
    assert none_desc_tool._refinire_tool_description == "Function docstring"