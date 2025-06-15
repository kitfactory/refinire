#!/usr/bin/env python3
"""
Generate AI tool definitions for better IDE completion
IDE補完を向上させるためのAIツール定義を生成します

This script generates openai_tools.json and .aidef files
このスクリプトはopenai_tools.jsonと.aidefファイルを生成します
"""

import json
import inspect
import importlib
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import ast


def extract_function_info(func) -> Dict[str, Any]:
    """
    Extract function information for AI tools
    AI用ツールの関数情報を抽出します
    
    Args:
        func: Function to extract information from
             情報を抽出する関数
    
    Returns:
        Dictionary containing function information
        関数情報を含む辞書
    """
    signature = inspect.signature(func)
    doc = inspect.getdoc(func) or ""
    
    # Extract parameters
    # パラメータを抽出
    parameters = {}
    for name, param in signature.parameters.items():
        param_info = {
            "type": str(param.annotation) if param.annotation != param.empty else "Any",
            "required": param.default == param.empty,
        }
        if param.default != param.empty:
            param_info["default"] = param.default
        
        parameters[name] = param_info
    
    return {
        "name": func.__name__,
        "description": doc.split('\n')[0] if doc else "",
        "parameters": parameters,
        "return_type": str(signature.return_annotation) if signature.return_annotation != signature.empty else "Any"
    }


def extract_class_info(cls) -> Dict[str, Any]:
    """
    Extract class information for AI tools
    AI用ツールのクラス情報を抽出します
    
    Args:
        cls: Class to extract information from
            情報を抽出するクラス
    
    Returns:
        Dictionary containing class information
        クラス情報を含む辞書
    """
    doc = inspect.getdoc(cls) or ""
    methods = []
    
    for name, method in inspect.getmembers(cls, predicate=inspect.ismethod):
        if not name.startswith('_'):
            methods.append(extract_function_info(method))
    
    return {
        "name": cls.__name__,
        "description": doc.split('\n')[0] if doc else "",
        "methods": methods
    }


def scan_module(module_name: str) -> Dict[str, Any]:
    """
    Scan a module and extract AI tool information
    モジュールをスキャンしてAIツール情報を抽出します
    
    Args:
        module_name: Name of the module to scan
                    スキャンするモジュール名
    
    Returns:
        Dictionary containing module information
        モジュール情報を含む辞書
    """
    try:
        module = importlib.import_module(module_name)
        
        functions = []
        classes = []
        
        for name, obj in inspect.getmembers(module):
            if not name.startswith('_'):
                if inspect.isfunction(obj):
                    functions.append(extract_function_info(obj))
                elif inspect.isclass(obj):
                    classes.append(extract_class_info(obj))
        
        return {
            "module": module_name,
            "functions": functions,
            "classes": classes
        }
    except ImportError as e:
        print(f"Warning: Could not import {module_name}: {e}")
        return {"module": module_name, "functions": [], "classes": []}


def generate_openai_tools_json(modules: List[str]) -> Dict[str, Any]:
    """
    Generate openai_tools.json format
    openai_tools.json形式を生成します
    
    Args:
        modules: List of module names to scan
                スキャンするモジュール名のリスト
    
    Returns:
        Dictionary in openai_tools.json format
        openai_tools.json形式の辞書
    """
    tools = []
    
    for module_name in modules:
        module_info = scan_module(module_name)
        
        # Add functions as tools
        # 関数をツールとして追加
        for func_info in module_info["functions"]:
            tool = {
                "type": "function",
                "function": {
                    "name": f"{module_name}.{func_info['name']}",
                    "description": func_info["description"],
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            
            for param_name, param_info in func_info["parameters"].items():
                tool["function"]["parameters"]["properties"][param_name] = {
                    "type": param_info["type"],
                    "description": f"Parameter {param_name}"
                }
                if param_info["required"]:
                    tool["function"]["parameters"]["required"].append(param_name)
            
            tools.append(tool)
        
        # Add class methods as tools
        # クラスメソッドをツールとして追加
        for class_info in module_info["classes"]:
            for method_info in class_info["methods"]:
                tool = {
                    "type": "function",
                    "function": {
                        "name": f"{module_name}.{class_info['name']}.{method_info['name']}",
                        "description": method_info["description"],
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                }
                
                for param_name, param_info in method_info["parameters"].items():
                    if param_name != "self":
                        tool["function"]["parameters"]["properties"][param_name] = {
                            "type": param_info["type"],
                            "description": f"Parameter {param_name}"
                        }
                        if param_info["required"]:
                            tool["function"]["parameters"]["required"].append(param_name)
                
                tools.append(tool)
    
    return {"tools": tools}


def generate_aidef(modules: List[str]) -> str:
    """
    Generate .aidef format
    .aidef形式を生成します
    
    Args:
        modules: List of module names to scan
                スキャンするモジュール名のリスト
    
    Returns:
        String in .aidef format
        .aidef形式の文字列
    """
    aidef_content = []
    aidef_content.append("# AI Definition for agents-sdk-models")
    aidef_content.append("# agents-sdk-modelsのAI定義")
    aidef_content.append("")
    
    for module_name in modules:
        module_info = scan_module(module_name)
        
        aidef_content.append(f"## Module: {module_name}")
        aidef_content.append("")
        
        # Add functions
        # 関数を追加
        if module_info["functions"]:
            aidef_content.append("### Functions / 関数")
            aidef_content.append("")
            
            for func_info in module_info["functions"]:
                aidef_content.append(f"- **{func_info['name']}**: {func_info['description']}")
                if func_info["parameters"]:
                    aidef_content.append("  - Parameters / パラメータ:")
                    for param_name, param_info in func_info["parameters"].items():
                        required = "required / 必須" if param_info["required"] else "optional / オプション"
                        aidef_content.append(f"    - `{param_name}` ({param_info['type']}): {required}")
                aidef_content.append(f"  - Returns / 戻り値: {func_info['return_type']}")
                aidef_content.append("")
        
        # Add classes
        # クラスを追加
        if module_info["classes"]:
            aidef_content.append("### Classes / クラス")
            aidef_content.append("")
            
            for class_info in module_info["classes"]:
                aidef_content.append(f"- **{class_info['name']}**: {class_info['description']}")
                if class_info["methods"]:
                    aidef_content.append("  - Methods / メソッド:")
                    for method_info in class_info["methods"]:
                        aidef_content.append(f"    - `{method_info['name']}`: {method_info['description']}")
                aidef_content.append("")
    
    return "\n".join(aidef_content)


def main():
    """
    Main function to generate AI tool definitions
    AIツール定義を生成するメイン関数
    """
    # Define modules to scan
    # スキャンするモジュールを定義
    modules = [
        "agents_sdk_models.pipeline",
        "agents_sdk_models.llm",
        "agents_sdk_models.context",
        "agents_sdk_models.flow",
        "agents_sdk_models.step",
        "agents_sdk_models.gen_agent",
        "agents_sdk_models.clearify_agent",
        "agents_sdk_models.llm_pipeline"
    ]
    
    # Add src to Python path
    # srcをPythonパスに追加
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Generate openai_tools.json
    # openai_tools.jsonを生成
    print("Generating openai_tools.json...")
    print("openai_tools.jsonを生成中...")
    
    tools_data = generate_openai_tools_json(modules)
    
    with open("openai_tools.json", "w", encoding="utf-8") as f:
        json.dump(tools_data, f, indent=2, ensure_ascii=False)
    
    print(f"Generated openai_tools.json with {len(tools_data['tools'])} tools")
    print(f"{len(tools_data['tools'])}個のツールでopenai_tools.jsonを生成しました")
    
    # Generate .aidef
    # .aidefを生成
    print("\nGenerating .aidef...")
    print(".aidefを生成中...")
    
    aidef_content = generate_aidef(modules)
    
    with open(".aidef", "w", encoding="utf-8") as f:
        f.write(aidef_content)
    
    print("Generated .aidef")
    print(".aidefを生成しました")


if __name__ == "__main__":
    main() 
