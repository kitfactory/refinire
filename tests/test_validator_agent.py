#!/usr/bin/env python3
"""
Test ValidatorAgent implementation.

ValidatorAgentの実装をテストします。
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire.agents.validator import (
    ValidatorAgent, ValidatorConfig, ValidationRule, ValidationResult,
    RequiredRule, EmailFormatRule, LengthRule, RangeRule, RegexRule, CustomFunctionRule,
    create_email_validator, create_required_validator, create_length_validator, create_custom_validator
)
from refinire import Context


class TestValidationRules:
    """Test cases for individual validation rules."""
    
    def test_required_rule_valid(self):
        """Test RequiredRule with valid data."""
        rule = RequiredRule()
        ctx = Context()
        
        assert rule.validate("test", ctx) == True
        assert rule.validate(123, ctx) == True
        assert rule.validate([1, 2, 3], ctx) == True
        assert rule.validate({"key": "value"}, ctx) == True
    
    def test_required_rule_invalid(self):
        """Test RequiredRule with invalid data."""
        rule = RequiredRule()
        ctx = Context()
        
        assert rule.validate(None, ctx) == False
        assert rule.validate("", ctx) == False
        assert rule.validate("   ", ctx) == False
        assert rule.validate([], ctx) == False
        assert rule.validate({}, ctx) == False
    
    def test_email_format_rule_valid(self):
        """Test EmailFormatRule with valid emails."""
        rule = EmailFormatRule()
        ctx = Context()
        
        assert rule.validate("test@example.com", ctx) == True
        assert rule.validate("user.name@domain.co.jp", ctx) == True
        assert rule.validate("admin+tag@company.org", ctx) == True
    
    def test_email_format_rule_invalid(self):
        """Test EmailFormatRule with invalid emails."""
        rule = EmailFormatRule()
        ctx = Context()
        
        assert rule.validate("invalid-email", ctx) == False
        assert rule.validate("@example.com", ctx) == False
        assert rule.validate("test@", ctx) == False
        assert rule.validate("test@.com", ctx) == False
        assert rule.validate(123, ctx) == False
    
    def test_length_rule_valid(self):
        """Test LengthRule with valid lengths."""
        rule = LengthRule(min_length=3, max_length=10)
        ctx = Context()
        
        assert rule.validate("test", ctx) == True
        assert rule.validate("hello", ctx) == True
        assert rule.validate("1234567890", ctx) == True
    
    def test_length_rule_invalid(self):
        """Test LengthRule with invalid lengths."""
        rule = LengthRule(min_length=3, max_length=10)
        ctx = Context()
        
        assert rule.validate("ab", ctx) == False
        assert rule.validate("12345678901", ctx) == False
        assert rule.validate(None, ctx) == False
    
    def test_range_rule_valid(self):
        """Test RangeRule with valid values."""
        rule = RangeRule(min_value=1, max_value=100)
        ctx = Context()
        
        assert rule.validate(50, ctx) == True
        assert rule.validate("75", ctx) == True
        assert rule.validate(1.5, ctx) == True
    
    def test_range_rule_invalid(self):
        """Test RangeRule with invalid values."""
        rule = RangeRule(min_value=1, max_value=100)
        ctx = Context()
        
        assert rule.validate(0, ctx) == False
        assert rule.validate(101, ctx) == False
        assert rule.validate("not_a_number", ctx) == False
    
    def test_regex_rule_valid(self):
        """Test RegexRule with valid patterns."""
        rule = RegexRule(r"^\d{3}-\d{3}-\d{4}$")  # Phone number pattern
        ctx = Context()
        
        assert rule.validate("123-456-7890", ctx) == True
        assert rule.validate("999-888-7777", ctx) == True
    
    def test_regex_rule_invalid(self):
        """Test RegexRule with invalid patterns."""
        rule = RegexRule(r"^\d{3}-\d{3}-\d{4}$")  # Phone number pattern
        ctx = Context()
        
        assert rule.validate("1234567890", ctx) == False
        assert rule.validate("123-45-6789", ctx) == False
        assert rule.validate(123, ctx) == False
    
    def test_custom_function_rule_valid(self):
        """Test CustomFunctionRule with valid data."""
        def is_even(data, context):
            return isinstance(data, int) and data % 2 == 0
        
        rule = CustomFunctionRule(is_even, "Must be even number")
        ctx = Context()
        
        assert rule.validate(2, ctx) == True
        assert rule.validate(100, ctx) == True
    
    def test_custom_function_rule_invalid(self):
        """Test CustomFunctionRule with invalid data."""
        def is_even(data, context):
            return isinstance(data, int) and data % 2 == 0
        
        rule = CustomFunctionRule(is_even, "Must be even number")
        ctx = Context()
        
        assert rule.validate(1, ctx) == False
        assert rule.validate(3, ctx) == False
        assert rule.validate("not_int", ctx) == False


class TestValidationResult:
    """Test cases for ValidationResult class."""
    
    def test_validation_result_valid(self):
        """Test ValidationResult with valid state."""
        result = ValidationResult(is_valid=True)
        
        assert result.is_valid == True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert result.timestamp is not None
    
    def test_validation_result_invalid(self):
        """Test ValidationResult with invalid state."""
        result = ValidationResult(is_valid=False, errors=["Error 1", "Error 2"])
        
        assert result.is_valid == False
        assert len(result.errors) == 2
        assert "Error 1" in result.errors
        assert "Error 2" in result.errors
    
    def test_validation_result_add_error(self):
        """Test adding errors to ValidationResult."""
        result = ValidationResult(is_valid=True)
        result.add_error("New error")
        
        assert result.is_valid == False
        assert "New error" in result.errors
    
    def test_validation_result_add_warning(self):
        """Test adding warnings to ValidationResult."""
        result = ValidationResult(is_valid=True)
        result.add_warning("Warning message")
        
        assert result.is_valid == True
        assert "Warning message" in result.warnings


class TestValidatorConfig:
    """Test cases for ValidatorConfig class."""
    
    def test_validator_config_creation(self):
        """Test ValidatorConfig creation."""
        config = ValidatorConfig(
            name="test_validator",
            rules=[{"type": "required"}],
            fail_fast=True
        )
        
        assert config.name == "test_validator"
        assert len(config.rules) == 1
        assert config.fail_fast == True
    
    def test_validator_config_defaults(self):
        """Test ValidatorConfig default values."""
        config = ValidatorConfig(name="test")
        
        assert config.name == "test"
        assert config.rules == []
        assert config.fail_fast == False
        assert config.store_result == True
        assert config.raise_on_error == False


class TestValidatorAgent:
    """Test cases for ValidatorAgent class."""
    
    @pytest.fixture
    def email_validator_config(self):
        """Create email validator configuration."""
        return ValidatorConfig(
            name="email_validator",
            rules=[
                {"type": "required", "name": "email_required"},
                {"type": "email", "name": "email_format"}
            ]
        )
    
    @pytest.fixture
    def length_validator_config(self):
        """Create length validator configuration."""
        return ValidatorConfig(
            name="length_validator",
            rules=[
                {"type": "length", "name": "length_check", "min_length": 3, "max_length": 10}
            ]
        )
    
    @pytest.fixture
    def range_validator_config(self):
        """Create range validator configuration."""
        return ValidatorConfig(
            name="range_validator",
            rules=[
                {"type": "range", "name": "range_check", "min_value": 1, "max_value": 100}
            ]
        )
    
    @pytest.mark.asyncio
    async def test_validator_agent_email_valid(self, email_validator_config):
        """Test ValidatorAgent with valid email."""
        validator = ValidatorAgent(email_validator_config)
        ctx = Context()
        
        result_ctx = await validator.run("test@example.com", ctx)
        
        assert result_ctx.shared_state["email_validator_status"] == "success"
        assert result_ctx.shared_state["email_validator_result"]["is_valid"] == True
    
    @pytest.mark.asyncio
    async def test_validator_agent_email_invalid(self, email_validator_config):
        """Test ValidatorAgent with invalid email."""
        validator = ValidatorAgent(email_validator_config)
        ctx = Context()
        
        result_ctx = await validator.run("invalid-email", ctx)
        
        assert result_ctx.shared_state["email_validator_status"] == "failed"
        assert result_ctx.shared_state["email_validator_result"]["is_valid"] == False
        assert len(result_ctx.shared_state["email_validator_result"]["errors"]) > 0
    
    @pytest.mark.asyncio
    async def test_validator_agent_length_valid(self, length_validator_config):
        """Test ValidatorAgent with valid length."""
        validator = ValidatorAgent(length_validator_config)
        ctx = Context()
        
        result_ctx = await validator.run("hello", ctx)
        
        assert result_ctx.shared_state["length_validator_status"] == "success"
        assert result_ctx.shared_state["length_validator_result"]["is_valid"] == True
    
    @pytest.mark.asyncio
    async def test_validator_agent_length_invalid(self, length_validator_config):
        """Test ValidatorAgent with invalid length."""
        validator = ValidatorAgent(length_validator_config)
        ctx = Context()
        
        result_ctx = await validator.run("ab", ctx)  # Too short
        
        assert result_ctx.shared_state["length_validator_status"] == "failed"
        assert result_ctx.shared_state["length_validator_result"]["is_valid"] == False
    
    @pytest.mark.asyncio
    async def test_validator_agent_range_valid(self, range_validator_config):
        """Test ValidatorAgent with valid range."""
        validator = ValidatorAgent(range_validator_config)
        ctx = Context()
        
        result_ctx = await validator.run("50", ctx)
        
        assert result_ctx.shared_state["range_validator_status"] == "success"
        assert result_ctx.shared_state["range_validator_result"]["is_valid"] == True
    
    @pytest.mark.asyncio
    async def test_validator_agent_range_invalid(self, range_validator_config):
        """Test ValidatorAgent with invalid range."""
        validator = ValidatorAgent(range_validator_config)
        ctx = Context()
        
        result_ctx = await validator.run("150", ctx)  # Too high
        
        assert result_ctx.shared_state["range_validator_status"] == "failed"
        assert result_ctx.shared_state["range_validator_result"]["is_valid"] == False
    
    @pytest.mark.asyncio
    async def test_validator_agent_fail_fast(self):
        """Test ValidatorAgent with fail_fast option."""
        config = ValidatorConfig(
            name="fail_fast_validator",
            rules=[
                {"type": "required", "name": "required_check"},
                {"type": "email", "name": "email_format"}
            ],
            fail_fast=True
        )
        validator = ValidatorAgent(config)
        ctx = Context()
        
        # Empty string should fail required rule and stop there
        result_ctx = await validator.run("", ctx)
        
        assert result_ctx.shared_state["fail_fast_validator_status"] == "failed"
        result = result_ctx.shared_state["fail_fast_validator_result"]
        assert result["is_valid"] == False
        # Should have only one error due to fail_fast
        assert len(result["errors"]) == 1
    
    @pytest.mark.asyncio
    async def test_validator_agent_raise_on_error(self):
        """Test ValidatorAgent with raise_on_error option."""
        config = ValidatorConfig(
            name="raise_validator",
            rules=[{"type": "required", "name": "required_check"}],
            raise_on_error=True
        )
        validator = ValidatorAgent(config)
        ctx = Context()
        
        # Should raise exception on validation failure
        with pytest.raises(ValueError):
            await validator.run("", ctx)
    
    @pytest.mark.asyncio
    async def test_validator_agent_custom_rules(self):
        """Test ValidatorAgent with custom validation rules."""
        def is_positive(data, context):
            try:
                return float(data) > 0
            except:
                return False
        
        config = ValidatorConfig(name="custom_validator")
        custom_rule = CustomFunctionRule(is_positive, "Must be positive number")
        validator = ValidatorAgent(config, [custom_rule])
        ctx = Context()
        
        # Test valid case
        result_ctx = await validator.run("10", ctx)
        assert result_ctx.shared_state["custom_validator_status"] == "success"
        
        # Test invalid case
        result_ctx = await validator.run("-5", ctx)
        assert result_ctx.shared_state["custom_validator_status"] == "failed"
    
    def test_validator_agent_add_rule(self):
        """Test adding validation rules to ValidatorAgent."""
        config = ValidatorConfig(name="test_validator")
        validator = ValidatorAgent(config)
        
        initial_count = len(validator.get_rules())
        
        new_rule = RequiredRule("new_required")
        validator.add_rule(new_rule)
        
        assert len(validator.get_rules()) == initial_count + 1
        assert new_rule in validator.get_rules()


class TestValidatorUtilities:
    """Test cases for validator utility functions."""
    
    def test_create_email_validator(self):
        """Test create_email_validator utility function."""
        validator = create_email_validator("test_email")
        
        assert validator.name == "test_email"
        assert len(validator.get_rules()) == 2  # required + email format
    
    def test_create_required_validator(self):
        """Test create_required_validator utility function."""
        validator = create_required_validator("test_required")
        
        assert validator.name == "test_required"
        assert len(validator.get_rules()) == 1  # required only
    
    def test_create_length_validator(self):
        """Test create_length_validator utility function."""
        validator = create_length_validator(min_length=5, max_length=15, name="test_length")
        
        assert validator.name == "test_length"
        assert len(validator.get_rules()) == 1  # length only
    
    def test_create_custom_validator(self):
        """Test create_custom_validator utility function."""
        def always_true(data, context):
            return True
        
        validator = create_custom_validator(always_true, "Always valid", "test_custom")
        
        assert validator.name == "test_custom"
        assert len(validator.get_rules()) == 1  # custom rule only
    
    @pytest.mark.asyncio
    async def test_utility_validators_integration(self):
        """Test that utility validators work end-to-end."""
        # Test email validator
        email_validator = create_email_validator()
        ctx = Context()
        
        result_ctx = await email_validator.run("test@example.com", ctx)
        assert result_ctx.shared_state["email_validator_status"] == "success"
        
        result_ctx = await email_validator.run("invalid", ctx)
        assert result_ctx.shared_state["email_validator_status"] == "failed"
        
        # Test required validator
        required_validator = create_required_validator()
        ctx = Context()
        
        result_ctx = await required_validator.run("something", ctx)
        assert result_ctx.shared_state["required_validator_status"] == "success"
        
        result_ctx = await required_validator.run("", ctx)
        assert result_ctx.shared_state["required_validator_status"] == "failed" 
