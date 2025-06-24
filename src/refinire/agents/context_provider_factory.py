"""
Context Provider Factory
コンテキストプロバイダーファクトリー

This module provides a factory for creating context providers from configuration.
このモジュールは設定からコンテキストプロバイダーを作成するファクトリーを提供します。
"""

import re
from typing import Dict, Any, List, Type, Optional
from refinire.agents.context_provider import ContextProvider
from refinire.agents.providers.conversation_history import ConversationHistoryProvider
from refinire.agents.providers.fixed_file import FixedFileProvider
from refinire.agents.providers.source_code import SourceCodeProvider
from refinire.agents.providers.cut_context import CutContextProvider


class ContextProviderFactory:
    """
    Factory for creating context providers from configuration
    設定からコンテキストプロバイダーを作成するファクトリー
    
    This factory can create context providers from YAML-like configuration strings
    or from configuration dictionaries. It supports validation and error handling.
    
    このファクトリーはYAMLライクな設定文字列または設定辞書から
    コンテキストプロバイダーを作成できます。検証とエラーハンドリングをサポートします。
    """
    
    # Registry of available providers
    # 利用可能なプロバイダーのレジストリ
    _provider_classes: Dict[str, Type] = {
        "conversation_history": ConversationHistoryProvider,
        "fixed_file": FixedFileProvider,
        "source_code": SourceCodeProvider,
        "cut_context": CutContextProvider,
    }
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[ContextProvider]) -> None:
        """
        Register a new provider class
        新しいプロバイダークラスを登録
        
        Args:
            name: Provider name / プロバイダー名
            provider_class: Provider class / プロバイダークラス
        """
        cls._provider_classes[name] = provider_class
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, Type[ContextProvider]]:
        """
        Get all available providers
        利用可能なすべてのプロバイダーを取得
        
        Returns:
            Dict[str, Type[ContextProvider]]: Available providers / 利用可能なプロバイダー
        """
        return cls._provider_classes.copy()
    
    @classmethod
    def parse_config_string(cls, config_string: str) -> List[Dict[str, Any]]:
        """
        Parse YAML-like configuration string
        YAMLライクな設定文字列を解析
        
        Args:
            config_string: YAML-like configuration string / YAMLライクな設定文字列
            
        Returns:
            List[Dict[str, Any]]: List of provider configurations / プロバイダー設定のリスト
            
        Raises:
            ValueError: If configuration string is invalid / 設定文字列が無効な場合
        """
        if not config_string.strip():
            return []
        
        providers = []
        lines = config_string.strip().split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            # 空行をスキップ
            if not line:
                i += 1
                continue
            
            # Check if line starts with provider name
            # 行がプロバイダー名で始まるかチェック
            if line.startswith('- '):
                provider_name = line[2:].strip()
                if not provider_name:
                    raise ValueError(f"Invalid provider name at line {i + 1}: {line}")
                
                # Parse provider configuration
                # プロバイダー設定を解析
                config = {}
                i += 1
                
                while i < len(lines):
                    next_line = lines[i].strip()
                    
                    # Check for next provider or end of configuration
                    # 次のプロバイダーまたは設定の終了をチェック
                    if next_line.startswith('- ') or not next_line:
                        break
                    
                    # Parse key-value pair
                    # キー・値ペアを解析
                    if ':' in next_line:
                        key, value = next_line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Convert value to appropriate type
                        # 値を適切な型に変換
                        if value.lower() == 'true':
                            config[key] = True
                        elif value.lower() == 'false':
                            config[key] = False
                        elif value.isdigit():
                            config[key] = int(value)
                        elif value.startswith("'") and value.endswith("'"):
                            config[key] = value[1:-1]
                        elif value.startswith('"') and value.endswith('"'):
                            config[key] = value[1:-1]
                        else:
                            config[key] = value
                    
                    i += 1
                
                providers.append({
                    "name": provider_name,
                    "config": config
                })
            else:
                i += 1
        
        return providers
    
    @classmethod
    def validate_config(cls, provider_config: Dict[str, Any]) -> None:
        """
        Validate provider configuration
        プロバイダー設定を検証
        """
        if not isinstance(provider_config, dict):
            raise ValueError("Provider configuration must be a dictionary")
        provider_type = provider_config.get("type")
        if not provider_type:
            raise ValueError("Provider type is required")
        provider_cls = cls._provider_classes.get(provider_type)
        if not provider_cls:
            raise ValueError("Unknown provider type")
        schema = provider_cls.get_config_schema()
        params = schema.get("parameters", {})
        for key, param in params.items():
            if param.get("required") and key not in provider_config:
                raise ValueError(f"Missing required parameter: {key}")
            if key in provider_config:
                expected_type = param.get("type")
                value = provider_config[key]
                if expected_type == "int" and not isinstance(value, int):
                    raise ValueError(f"Parameter '{key}' must be int")
                if expected_type == "str" and not isinstance(value, str):
                    raise ValueError(f"Parameter '{key}' must be str")
                if expected_type == "bool" and not isinstance(value, bool):
                    raise ValueError(f"Parameter '{key}' must be bool")
    
    @classmethod
    def create_provider(cls, provider_config: Dict[str, Any], validate: bool = False) -> ContextProvider:
        """
        Create a single provider from configuration
        設定から単一のプロバイダーを作成
        
        Args:
            provider_config: Provider configuration / プロバイダー設定
            
        Returns:
            ContextProvider: Created provider instance / 作成されたプロバイダーインスタンス
            
        Raises:
            ValueError: If configuration is invalid / 設定が無効な場合
        """
        if provider_config is None:
            raise ValueError("Configuration is required")
        if validate:
            cls.validate_config(provider_config)
        provider_type = provider_config.get("type")
        if not provider_type:
            raise ValueError("Provider type is required")
        provider_cls = cls._provider_classes.get(provider_type)
        if not provider_cls:
            raise ValueError(f"Unknown provider type: {provider_type}")
        # Remove 'type' key before passing to provider
        config = dict(provider_config)
        config.pop("type", None)
        return provider_cls.from_config(config)
    
    @classmethod
    def create_providers(cls, configs: List[Dict[str, Any]], validate: bool = False) -> List[ContextProvider]:
        """
        Create multiple providers from list of configuration dictionaries
        設定辞書のリストから複数のプロバイダーを作成
        
        Args:
            provider_configs: List of provider configurations / プロバイダー設定のリスト
            
        Returns:
            List[ContextProvider]: List of created providers / 作成されたプロバイダーのリスト
            
        Raises:
            ValueError: If any configuration is invalid / 設定が無効な場合
        """
        if configs is None:
            raise ValueError("Configuration list is required")
        return [cls.create_provider(cfg, validate=validate) for cfg in configs]
    
    @classmethod
    def get_available_provider_types(cls) -> List[str]:
        """
        Get available provider types
        利用可能なプロバイダータイプ一覧を取得
        """
        return list(cls._provider_classes.keys())
    
    @classmethod
    def get_provider_schema(cls, provider_type: str) -> Dict[str, Any]:
        """
        Get schema for a provider type
        プロバイダータイプのスキーマを取得
        """
        provider_cls = cls._provider_classes.get(provider_type)
        if not provider_cls:
            raise ValueError("Unknown provider type")
        return provider_cls.get_config_schema()
    
    @classmethod
    def get_all_provider_schemas(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get all provider schemas
        すべてのプロバイダースキーマを取得
        """
        return {ptype: cls.get_provider_schema(ptype) for ptype in cls.get_available_provider_types()}
    
    @classmethod
    def validate_config_string(cls, config_string: str) -> List[str]:
        """
        Validate YAML-like configuration string and return errors
        YAMLライクな設定文字列を検証してエラーを返す
        
        Args:
            config_string: YAML-like configuration string / YAMLライクな設定文字列
            
        Returns:
            List[str]: List of validation errors (empty if valid) / 検証エラーのリスト（有効な場合は空）
        """
        errors = []
        
        try:
            provider_configs = cls.parse_config_string(config_string)
            
            for i, provider_config in enumerate(provider_configs):
                try:
                    cls.validate_config(provider_config)
                except ValueError as e:
                    errors.append(f"Provider {i + 1} ({provider_config.get('name', 'unknown')}): {str(e)}")
        except ValueError as e:
            errors.append(f"Configuration parsing error: {str(e)}")
        
        return errors 