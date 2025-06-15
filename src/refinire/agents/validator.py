"""
ValidatorAgent implementation for data validation and business rule enforcement.

ValidatorAgentはデータ検証とビジネスルール適用を行うエージェントです。
入力データの妥当性をチェックし、カスタム検証ルールを適用できます。
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict, Union, Callable
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import re

from .flow.context import Context
from .flow.step import Step

logger = logging.getLogger(__name__)


class ValidationRule(ABC):
    """
    Abstract base class for validation rules.
    検証ルールの抽象基底クラス。
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize validation rule.
        検証ルールを初期化します。
        
        Args:
            name: Rule name / ルール名
            description: Rule description / ルールの説明
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def validate(self, data: Any, context: Context) -> bool:
        """
        Validate data against this rule.
        このルールに対してデータを検証します。
        
        Args:
            data: Data to validate / 検証するデータ
            context: Execution context / 実行コンテキスト
            
        Returns:
            bool: True if valid, False otherwise / 有効な場合True、そうでなければFalse
        """
        pass
    
    @abstractmethod
    def get_error_message(self, data: Any) -> str:
        """
        Get error message for validation failure.
        検証失敗時のエラーメッセージを取得します。
        
        Args:
            data: Failed data / 失敗したデータ
            
        Returns:
            str: Error message / エラーメッセージ
        """
        pass


class RequiredRule(ValidationRule):
    """
    Rule to check if data is not None or empty.
    データがNoneまたは空でないことをチェックするルール。
    """
    
    def __init__(self, name: str = "required"):
        super().__init__(name, "Data must not be None or empty")
    
    def validate(self, data: Any, context: Context) -> bool:
        """Validate that data is not None or empty."""
        if data is None:
            return False
        if isinstance(data, str) and data.strip() == "":
            return False
        if isinstance(data, (list, dict)) and len(data) == 0:
            return False
        return True
    
    def get_error_message(self, data: Any) -> str:
        return f"Required field cannot be empty"


class EmailFormatRule(ValidationRule):
    """
    Rule to validate email format.
    メール形式を検証するルール。
    """
    
    def __init__(self, name: str = "email_format"):
        super().__init__(name, "Data must be a valid email format")
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def validate(self, data: Any, context: Context) -> bool:
        """Validate email format."""
        if not isinstance(data, str):
            return False
        return bool(self.email_pattern.match(data))
    
    def get_error_message(self, data: Any) -> str:
        return f"'{data}' is not a valid email format"


class LengthRule(ValidationRule):
    """
    Rule to validate data length.
    データ長を検証するルール。
    """
    
    def __init__(self, min_length: Optional[int] = None, max_length: Optional[int] = None, name: str = "length"):
        super().__init__(name, f"Data length must be between {min_length} and {max_length}")
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, data: Any, context: Context) -> bool:
        """Validate data length."""
        if data is None:
            return False
        
        length = len(str(data))
        
        if self.min_length is not None and length < self.min_length:
            return False
        if self.max_length is not None and length > self.max_length:
            return False
        
        return True
    
    def get_error_message(self, data: Any) -> str:
        length = len(str(data)) if data is not None else 0
        return f"Length {length} is not between {self.min_length} and {self.max_length}"


class RangeRule(ValidationRule):
    """
    Rule to validate numeric range.
    数値範囲を検証するルール。
    """
    
    def __init__(self, min_value: Optional[Union[int, float]] = None, 
                 max_value: Optional[Union[int, float]] = None, name: str = "range"):
        super().__init__(name, f"Value must be between {min_value} and {max_value}")
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, data: Any, context: Context) -> bool:
        """Validate numeric range."""
        try:
            value = float(data)
            
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    def get_error_message(self, data: Any) -> str:
        return f"Value '{data}' is not between {self.min_value} and {self.max_value}"


class RegexRule(ValidationRule):
    """
    Rule to validate data against a regular expression.
    正規表現に対してデータを検証するルール。
    """
    
    def __init__(self, pattern: str, name: str = "regex"):
        super().__init__(name, f"Data must match pattern: {pattern}")
        self.pattern = re.compile(pattern)
    
    def validate(self, data: Any, context: Context) -> bool:
        """Validate data against regex pattern."""
        if not isinstance(data, str):
            return False
        return bool(self.pattern.match(data))
    
    def get_error_message(self, data: Any) -> str:
        return f"'{data}' does not match required pattern"


class CustomFunctionRule(ValidationRule):
    """
    Rule using a custom validation function.
    カスタム検証関数を使用するルール。
    """
    
    def __init__(self, validation_func: Callable[[Any, Context], bool], 
                 error_message: str, name: str = "custom"):
        super().__init__(name, "Custom validation rule")
        self.validation_func = validation_func
        self.error_message = error_message
    
    def validate(self, data: Any, context: Context) -> bool:
        """Validate using custom function."""
        try:
            return self.validation_func(data, context)
        except Exception as e:
            logger.warning(f"Custom validation function error: {e}")
            return False
    
    def get_error_message(self, data: Any) -> str:
        return self.error_message


class ValidationResult:
    """
    Result of validation operation.
    検証操作の結果。
    """
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        """
        Initialize validation result.
        検証結果を初期化します。
        
        Args:
            is_valid: Whether validation passed / 検証が通ったかどうか
            errors: List of error messages / エラーメッセージのリスト
            warnings: List of warning messages / 警告メッセージのリスト
        """
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.timestamp = datetime.now()
    
    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)
    
    def __str__(self) -> str:
        status = "VALID" if self.is_valid else "INVALID"
        return f"ValidationResult({status}, {len(self.errors)} errors, {len(self.warnings)} warnings)"


class ValidatorConfig(BaseModel):
    """
    Configuration for ValidatorAgent.
    ValidatorAgentの設定。
    """
    
    name: str = Field(description="Name of the validator agent / バリデーターエージェントの名前")
    
    rules: List[Dict[str, Any]] = Field(
        default=[],
        description="List of validation rules / 検証ルールのリスト"
    )
    
    fail_fast: bool = Field(
        default=False,
        description="Stop validation on first error / 最初のエラーで検証を停止"
    )
    
    store_result: bool = Field(
        default=True,
        description="Store validation result in context / 検証結果をコンテキストに保存"
    )
    
    raise_on_error: bool = Field(
        default=False,
        description="Raise exception on validation failure / 検証失敗時に例外を発生"
    )
    
    @field_validator("rules")
    @classmethod
    def rules_not_empty(cls, v):
        """Validate that rules are provided."""
        if not v:
            logger.warning("No validation rules provided")
        return v


class ValidatorAgent(Step):
    """
    Validator agent for data validation and business rule enforcement.
    データ検証とビジネスルール適用を行うバリデーターエージェント。
    
    The ValidatorAgent checks input data against configured validation rules
    and returns validation results with detailed error messages.
    ValidatorAgentは設定された検証ルールに対して入力データをチェックし、
    詳細なエラーメッセージと共に検証結果を返します。
    """
    
    def __init__(self, config: ValidatorConfig, custom_rules: List[ValidationRule] = None):
        """
        Initialize ValidatorAgent.
        ValidatorAgentを初期化します。
        
        Args:
            config: Validator configuration / バリデーター設定
            custom_rules: Optional custom validation rules / オプションのカスタム検証ルール
        """
        super().__init__(name=config.name)
        self.config = config
        self.validation_rules = self._build_validation_rules(custom_rules or [])
    
    def _build_validation_rules(self, custom_rules: List[ValidationRule]) -> List[ValidationRule]:
        """
        Build validation rules from configuration and custom rules.
        設定とカスタムルールから検証ルールを構築します。
        """
        rules = list(custom_rules)
        
        # Build rules from configuration
        # 設定からルールを構築
        for rule_config in self.config.rules:
            rule_type = rule_config.get("type")
            rule_name = rule_config.get("name", rule_type)
            
            if rule_type == "required":
                rules.append(RequiredRule(rule_name))
                
            elif rule_type == "email":
                rules.append(EmailFormatRule(rule_name))
                
            elif rule_type == "length":
                min_len = rule_config.get("min_length")
                max_len = rule_config.get("max_length")
                rules.append(LengthRule(min_len, max_len, rule_name))
                
            elif rule_type == "range":
                min_val = rule_config.get("min_value")
                max_val = rule_config.get("max_value")
                rules.append(RangeRule(min_val, max_val, rule_name))
                
            elif rule_type == "regex":
                pattern = rule_config.get("pattern")
                if pattern:
                    rules.append(RegexRule(pattern, rule_name))
                    
            else:
                logger.warning(f"Unknown rule type: {rule_type}")
        
        return rules
    
    async def run(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute the validation logic.
        検証ロジックを実行します。
        
        Args:
            user_input: User input to validate / 検証するユーザー入力
            ctx: Execution context / 実行コンテキスト
            
        Returns:
            Context: Updated context with validation results / 検証結果を含む更新されたコンテキスト
        """
        # Update step info
        # ステップ情報を更新
        ctx.update_step_info(self.name)
        
        try:
            # Determine data to validate
            # 検証するデータを決定
            data_to_validate = user_input
            if data_to_validate is None:
                data_to_validate = ctx.get_user_input()
            
            # Perform validation
            # 検証を実行
            validation_result = self._validate_data(data_to_validate, ctx)
            
            # Store result in context if requested
            # 要求された場合は結果をコンテキストに保存
            if self.config.store_result:
                ctx.shared_state[f"{self.name}_result"] = {
                    "is_valid": validation_result.is_valid,
                    "errors": validation_result.errors,
                    "warnings": validation_result.warnings,
                    "timestamp": validation_result.timestamp.isoformat()
                }
            
            # Handle validation failure
            # 検証失敗を処理
            if not validation_result.is_valid:
                error_summary = f"Validation failed: {', '.join(validation_result.errors)}"
                
                if self.config.raise_on_error:
                    raise ValueError(error_summary)
                
                logger.warning(f"ValidatorAgent '{self.name}': {error_summary}")
                ctx.shared_state[f"{self.name}_status"] = "failed"
            else:
                logger.info(f"ValidatorAgent '{self.name}': Validation successful")
                ctx.shared_state[f"{self.name}_status"] = "success"
            
            # Add warnings to context if any
            # 警告があればコンテキストに追加
            if validation_result.warnings:
                ctx.shared_state[f"{self.name}_warnings"] = validation_result.warnings
            
            return ctx
            
        except Exception as e:
            logger.error(f"ValidatorAgent '{self.name}' error: {e}")
            
            if self.config.store_result:
                ctx.shared_state[f"{self.name}_result"] = {
                    "is_valid": False,
                    "errors": [str(e)],
                    "warnings": [],
                    "timestamp": datetime.now().isoformat()
                }
                ctx.shared_state[f"{self.name}_status"] = "error"
            
            if self.config.raise_on_error:
                raise
            
            return ctx
    
    def _validate_data(self, data: Any, context: Context) -> ValidationResult:
        """
        Validate data against all configured rules.
        設定された全てのルールに対してデータを検証します。
        """
        result = ValidationResult(is_valid=True)
        
        for rule in self.validation_rules:
            try:
                is_valid = rule.validate(data, context)
                
                if not is_valid:
                    error_message = rule.get_error_message(data)
                    result.add_error(f"[{rule.name}] {error_message}")
                    
                    # Stop on first error if fail_fast is enabled
                    # fail_fastが有効な場合は最初のエラーで停止
                    if self.config.fail_fast:
                        break
                        
            except Exception as e:
                error_message = f"Rule '{rule.name}' execution error: {e}"
                result.add_error(error_message)
                logger.warning(error_message)
                
                if self.config.fail_fast:
                    break
        
        return result
    
    def add_rule(self, rule: ValidationRule):
        """
        Add a validation rule to the agent.
        エージェントに検証ルールを追加します。
        """
        self.validation_rules.append(rule)
    
    def get_rules(self) -> List[ValidationRule]:
        """
        Get all validation rules.
        全ての検証ルールを取得します。
        """
        return self.validation_rules.copy()


# Utility functions for creating common validators
# 一般的なバリデーターを作成するためのユーティリティ関数

def create_email_validator(name: str = "email_validator") -> ValidatorAgent:
    """
    Create a validator for email format.
    メール形式用のバリデーターを作成します。
    """
    config = ValidatorConfig(
        name=name,
        rules=[
            {"type": "required", "name": "email_required"},
            {"type": "email", "name": "email_format"}
        ]
    )
    return ValidatorAgent(config)


def create_required_validator(name: str = "required_validator") -> ValidatorAgent:
    """
    Create a validator for required fields.
    必須フィールド用のバリデーターを作成します。
    """
    config = ValidatorConfig(
        name=name,
        rules=[{"type": "required", "name": "required_check"}]
    )
    return ValidatorAgent(config)


def create_length_validator(min_length: int = None, max_length: int = None, 
                          name: str = "length_validator") -> ValidatorAgent:
    """
    Create a validator for length constraints.
    長さ制約用のバリデーターを作成します。
    """
    config = ValidatorConfig(
        name=name,
        rules=[{
            "type": "length",
            "name": "length_check",
            "min_length": min_length,
            "max_length": max_length
        }]
    )
    return ValidatorAgent(config)


def create_custom_validator(validation_func: Callable[[Any, Context], bool], 
                          error_message: str, name: str = "custom_validator") -> ValidatorAgent:
    """
    Create a validator with custom validation function.
    カスタム検証関数を持つバリデーターを作成します。
    """
    config = ValidatorConfig(name=name)
    custom_rule = CustomFunctionRule(validation_func, error_message, "custom_rule")
    return ValidatorAgent(config, [custom_rule]) 
