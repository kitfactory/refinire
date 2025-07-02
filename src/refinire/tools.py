"""
Refinire Tool Decorators and Utilities
Refinireツールデコレータとユーティリティ

This module provides convenient tool decorators that wrap the OpenAI Agents SDK
function_tool decorator for better user experience and import simplicity.
このモジュールは、より良いユーザー体験とインポートの簡素化のために
OpenAI Agents SDKのfunction_toolデコレータをラップする便利なツールデコレータを提供します。
"""

import functools
from typing import Any, Callable, TypeVar, Union
from agents import function_tool

# Type variable for generic function decoration
# ジェネリック関数デコレーション用の型変数
F = TypeVar('F', bound=Callable[..., Any])


def tool(func: F = None, *, name: str = None, description: str = None) -> Union[F, Callable[[F], F]]:
    """
    Refinire tool decorator that wraps the OpenAI Agents SDK function_tool.
    OpenAI Agents SDKのfunction_toolをラップするRefinireツールデコレータ。
    
    This decorator provides a cleaner import experience for Refinire users
    while maintaining full compatibility with the underlying Agents SDK.
    このデコレータは、基盤となるAgents SDKとの完全な互換性を維持しながら、
    Refinireユーザーにクリーンなインポート体験を提供します。
    
    Args:
        func: The function to decorate / デコレートする関数
        name: Optional name for the tool (defaults to function name) / ツールの名前（デフォルトは関数名）
        description: Optional description for the tool (defaults to docstring) / ツールの説明（デフォルトはdocstring）
        
    Returns:
        Decorated function ready for use with RefinireAgent / RefinireAgentで使用可能なデコレート済み関数
        
    Example:
        ```python
        from refinire import tool, RefinireAgent
        
        @tool
        def get_weather(city: str) -> str:
            \"\"\"Get weather information for a city\"\"\"
            return f"Weather in {city}: Sunny, 22°C"
            
        @tool(name="math_calc", description="Perform mathematical calculations")
        def calculate(expression: str) -> float:
            \"\"\"Calculate mathematical expressions\"\"\"
            return eval(expression)
            
        agent = RefinireAgent(
            name="assistant",
            generation_instructions="Help users with weather and math",
            tools=[get_weather, calculate],
            model="gpt-4o-mini"
        )
        ```
    """
    def decorator(f: F) -> F:
        # Use provided name or fall back to function name
        # 提供された名前を使用するか、関数名にフォールバック
        tool_name = name or f.__name__
        
        # Use provided description or fall back to docstring
        # 提供された説明を使用するか、docstringにフォールバック
        tool_description = description if description is not None else f.__doc__
        
        # Apply the OpenAI Agents SDK function_tool decorator
        # OpenAI Agents SDKのfunction_toolデコレータを適用
        tool_obj = function_tool(f)
        
        # Create a wrapper that preserves the original function's callable behavior
        # 元の関数の呼び出し可能な動作を保持するラッパーを作成
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        
        # Store the tool object as an attribute for RefinireAgent to use
        # RefinireAgentが使用するためにツールオブジェクトを属性として保存
        wrapper._function_tool = tool_obj
        
        # Add Refinire-specific metadata for debugging and introspection
        # デバッグと内省用のRefinire固有のメタデータを追加
        wrapper._refinire_tool = True
        wrapper._refinire_tool_name = tool_name
        wrapper._refinire_tool_description = tool_description
        wrapper._original_function = f
        
        return wrapper
    
    # Handle both @tool and @tool(...) syntax
    # @toolと@tool(...)の両方の構文を処理
    if func is None:
        # Called as @tool(...) with arguments
        # 引数付きで@tool(...)として呼び出された場合
        return decorator
    else:
        # Called as @tool without arguments
        # 引数なしで@toolとして呼び出された場合
        return decorator(func)


def function_tool_compat(func: F) -> F:
    """
    Compatibility alias for the original function_tool decorator.
    元のfunction_toolデコレータの互換性エイリアス。
    
    This provides a bridge for existing code that uses function_tool
    while encouraging migration to the new @tool decorator.
    これは、新しい@toolデコレータへの移行を促進しながら、
    function_toolを使用する既存のコードにブリッジを提供します。
    
    Args:
        func: The function to decorate / デコレートする関数
        
    Returns:
        Decorated function / デコレート済み関数
        
    Example:
        ```python
        from refinire import function_tool_compat as function_tool
        
        @function_tool
        def legacy_tool(data: str) -> str:
            return f"Processed: {data}"
        ```
    """
    # Apply the OpenAI Agents SDK function_tool decorator
    # OpenAI Agents SDKのfunction_toolデコレータを適用
    tool_obj = function_tool(func)
    
    # Create a wrapper that preserves the original function's callable behavior
    # 元の関数の呼び出し可能な動作を保持するラッパーを作成
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    
    # Store the tool object as an attribute for RefinireAgent to use
    # RefinireAgentが使用するためにツールオブジェクトを属性として保存
    wrapper._function_tool = tool_obj
    wrapper._original_function = func
    
    return wrapper


def get_tool_info(func: Callable) -> dict:
    """
    Get metadata information about a Refinire tool function.
    Refinireツール関数のメタデータ情報を取得します。
    
    Args:
        func: Tool function to inspect / 検査するツール関数
        
    Returns:
        Dictionary containing tool metadata / ツールメタデータを含む辞書
        
    Example:
        ```python
        @tool(name="weather", description="Get weather data")
        def get_weather(city: str) -> str:
            return f"Weather in {city}"
            
        info = get_tool_info(get_weather)
        print(info)  # {'is_refinire_tool': True, 'name': 'weather', 'description': 'Get weather data'}
        ```
    """
    return {
        'is_refinire_tool': getattr(func, '_refinire_tool', False),
        'name': getattr(func, '_refinire_tool_name', func.__name__),
        'description': getattr(func, '_refinire_tool_description', func.__doc__),
        'function_name': func.__name__,
        'docstring': func.__doc__
    }


def list_tools(tools: list) -> list:
    """
    List information about all tools in a collection.
    コレクション内のすべてのツールに関する情報をリストします。
    
    Args:
        tools: List of tool functions / ツール関数のリスト
        
    Returns:
        List of tool metadata dictionaries / ツールメタデータ辞書のリスト
        
    Example:
        ```python
        tools = [get_weather, calculate]
        tool_list = list_tools(tools)
        for tool_info in tool_list:
            print(f"Tool: {tool_info['name']} - {tool_info['description']}")
        ```
    """
    return [get_tool_info(func) for func in tools]


# Re-export the original function_tool for compatibility
# 互換性のために元のfunction_toolを再エクスポート
__all__ = [
    'tool',
    'function_tool_compat', 
    'get_tool_info',
    'list_tools'
]