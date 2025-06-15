#!/usr/bin/env python3
"""
ValidatorAgent Examples
ValidatorAgentの使用例

This example demonstrates how to use ValidatorAgent for data validation
and business rule enforcement in various scenarios.
この例では、様々なシナリオでデータ検証とビジネスルール適用のために
ValidatorAgentを使用する方法を示します。
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire.agents.validator import (
    ValidatorAgent, ValidatorConfig, ValidationRule,
    RequiredRule, EmailFormatRule, LengthRule, RangeRule, RegexRule, CustomFunctionRule,
    create_email_validator, create_required_validator, create_length_validator, create_custom_validator
)
from refinire.context import Context


async def example_1_basic_validation():
    """
    Example 1: Basic validation with built-in rules.
    例1: ビルトインルールを使った基本的な検証。
    """
    print("\n" + "="*60)
    print("Example 1: Basic Validation")
    print("例1: 基本的な検証")
    print("="*60)
    
    # Create validator configuration with multiple rules
    # 複数のルールを持つバリデーター設定を作成
    config = ValidatorConfig(
        name="user_registration_validator",
        rules=[
            {"type": "required", "name": "username_required"},
            {"type": "length", "name": "username_length", "min_length": 3, "max_length": 20},
            {"type": "regex", "name": "username_format", "pattern": r"^[a-zA-Z0-9_]+$"}
        ]
    )
    
    validator = ValidatorAgent(config)
    
    # Test cases
    # テストケース
    test_cases = [
        ("valid_user123", "Valid username"),
        ("ab", "Too short username"),
        ("", "Empty username"),
        ("invalid-user!", "Invalid characters"),
        ("this_username_is_way_too_long_for_our_system", "Too long username")
    ]
    
    for test_input, description in test_cases:
        print(f"\nTesting: {description}")
        print(f"テスト中: {description}")
        print(f"Input: '{test_input}'")
        
        ctx = Context()
        result_ctx = await validator.run(test_input, ctx)
        
        status = result_ctx.shared_state.get("user_registration_validator_status")
        result = result_ctx.shared_state.get("user_registration_validator_result")
        
        print(f"Status: {status}")
        print(f"Valid: {result['is_valid']}")
        
        if result['errors']:
            print("Errors:")
            for error in result['errors']:
                print(f"  - {error}")


async def example_2_email_validation():
    """
    Example 2: Email validation using utility function.
    例2: ユーティリティ関数を使ったメール検証。
    """
    print("\n" + "="*60)
    print("Example 2: Email Validation")
    print("例2: メール検証")
    print("="*60)
    
    # Create email validator using utility function
    # ユーティリティ関数を使ってメールバリデーターを作成
    email_validator = create_email_validator("email_checker")
    
    # Test various email formats
    # 様々なメール形式をテスト
    email_test_cases = [
        ("user@example.com", "Valid email"),
        ("admin+tag@company.co.jp", "Valid email with tag and country domain"),
        ("", "Empty email"),
        ("invalid-email", "Missing @ symbol"),
        ("@example.com", "Missing local part"),
        ("user@", "Missing domain"),
        ("user@.com", "Invalid domain format")
    ]
    
    for email, description in email_test_cases:
        print(f"\nTesting: {description}")
        print(f"Email: '{email}'")
        
        ctx = Context()
        result_ctx = await email_validator.run(email, ctx)
        
        status = result_ctx.shared_state.get("email_checker_status")
        result = result_ctx.shared_state.get("email_checker_result")
        
        print(f"Status: {status}")
        if result['errors']:
            print("Validation errors:")
            for error in result['errors']:
                print(f"  - {error}")


async def example_3_numeric_validation():
    """
    Example 3: Numeric range validation.
    例3: 数値範囲検証。
    """
    print("\n" + "="*60)
    print("Example 3: Numeric Range Validation")
    print("例3: 数値範囲検証")
    print("="*60)
    
    # Create validator for numeric score (0-100)
    # 数値スコア（0-100）用のバリデーターを作成
    config = ValidatorConfig(
        name="score_validator",
        rules=[
            {"type": "required", "name": "score_required"},
            {"type": "range", "name": "score_range", "min_value": 0, "max_value": 100}
        ]
    )
    
    score_validator = ValidatorAgent(config)
    
    # Test various score values
    # 様々なスコア値をテスト
    score_test_cases = [
        ("75", "Valid score"),
        ("100", "Maximum score"),
        ("0", "Minimum score"),
        ("-10", "Below minimum"),
        ("150", "Above maximum"),
        ("", "Empty score"),
        ("not_a_number", "Invalid format")
    ]
    
    for score, description in score_test_cases:
        print(f"\nTesting: {description}")
        print(f"Score: '{score}'")
        
        ctx = Context()
        result_ctx = await score_validator.run(score, ctx)
        
        status = result_ctx.shared_state.get("score_validator_status")
        result = result_ctx.shared_state.get("score_validator_result")
        
        print(f"Status: {status}")
        if result['errors']:
            print("Validation errors:")
            for error in result['errors']:
                print(f"  - {error}")


async def example_4_custom_validation():
    """
    Example 4: Custom validation rules.
    例4: カスタム検証ルール。
    """
    print("\n" + "="*60)
    print("Example 4: Custom Validation Rules")
    print("例4: カスタム検証ルール")
    print("="*60)
    
    # Define custom validation functions
    # カスタム検証関数を定義
    def is_strong_password(password, context):
        """Check if password meets strength requirements."""
        if not isinstance(password, str):
            return False
        
        # Password must be at least 8 characters
        # パスワードは最低8文字
        if len(password) < 8:
            return False
        
        # Must contain at least one uppercase, one lowercase, one digit, one special char
        # 大文字、小文字、数字、特殊文字をそれぞれ最低1つ含む必要がある
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return has_upper and has_lower and has_digit and has_special
    
    def is_business_day(date_str, context):
        """Check if date is a business day (simplified)."""
        # This is a simplified example - in practice, you'd parse the date
        # これは簡略化された例 - 実際には日付をパースします
        return "saturday" not in date_str.lower() and "sunday" not in date_str.lower()
    
    # Create validator with custom rules
    # カスタムルールを持つバリデーターを作成
    config = ValidatorConfig(name="password_validator")
    
    custom_rules = [
        CustomFunctionRule(
            is_strong_password,
            "Password must be at least 8 characters with uppercase, lowercase, digit, and special character",
            "password_strength"
        )
    ]
    
    password_validator = ValidatorAgent(config, custom_rules)
    
    # Test password strength
    # パスワード強度をテスト
    password_test_cases = [
        ("MyP@ssw0rd", "Strong password"),
        ("password", "Weak password - no uppercase, digits, or special chars"),
        ("PASSWORD123", "Missing lowercase and special chars"),
        ("Pass@1", "Too short"),
        ("", "Empty password")
    ]
    
    for password, description in password_test_cases:
        print(f"\nTesting: {description}")
        print(f"Password: '{password}'")
        
        ctx = Context()
        result_ctx = await password_validator.run(password, ctx)
        
        status = result_ctx.shared_state.get("password_validator_status")
        result = result_ctx.shared_state.get("password_validator_result")
        
        print(f"Status: {status}")
        if result['errors']:
            print("Validation errors:")
            for error in result['errors']:
                print(f"  - {error}")


async def example_5_fail_fast_validation():
    """
    Example 5: Fail-fast validation behavior.
    例5: フェイルファスト検証の動作。
    """
    print("\n" + "="*60)
    print("Example 5: Fail-Fast Validation")
    print("例5: フェイルファスト検証")
    print("="*60)
    
    # Create validator with fail_fast enabled
    # fail_fastを有効にしたバリデーターを作成
    config_fail_fast = ValidatorConfig(
        name="fail_fast_validator",
        rules=[
            {"type": "required", "name": "required_check"},
            {"type": "email", "name": "email_format"},
            {"type": "length", "name": "length_check", "min_length": 10, "max_length": 50}
        ],
        fail_fast=True
    )
    
    # Create validator without fail_fast for comparison
    # 比較のためfail_fastなしのバリデーターを作成
    config_normal = ValidatorConfig(
        name="normal_validator",
        rules=[
            {"type": "required", "name": "required_check"},
            {"type": "email", "name": "email_format"},
            {"type": "length", "name": "length_check", "min_length": 10, "max_length": 50}
        ],
        fail_fast=False
    )
    
    fail_fast_validator = ValidatorAgent(config_fail_fast)
    normal_validator = ValidatorAgent(config_normal)
    
    # Test with invalid input that violates multiple rules
    # 複数のルールに違反する無効な入力でテスト
    test_input = ""  # Empty string violates required and length rules
    
    print("\nTesting with empty string (violates multiple rules)")
    print("空文字列でテスト（複数のルールに違反）")
    
    # Test fail-fast validator
    print("\n--- Fail-Fast Validator ---")
    ctx1 = Context()
    result_ctx1 = await fail_fast_validator.run(test_input, ctx1)
    result1 = result_ctx1.shared_state.get("fail_fast_validator_result")
    print(f"Number of errors: {len(result1['errors'])}")
    print("Errors:")
    for error in result1['errors']:
        print(f"  - {error}")
    
    # Test normal validator
    print("\n--- Normal Validator ---")
    ctx2 = Context()
    result_ctx2 = await normal_validator.run(test_input, ctx2)
    result2 = result_ctx2.shared_state.get("normal_validator_result")
    print(f"Number of errors: {len(result2['errors'])}")
    print("Errors:")
    for error in result2['errors']:
        print(f"  - {error}")


async def example_6_context_integration():
    """
    Example 6: Integration with context and shared state.
    例6: コンテキストと共有状態との統合。
    """
    print("\n" + "="*60)
    print("Example 6: Context Integration")
    print("例6: コンテキスト統合")
    print("="*60)
    
    # Create multiple validators for a workflow
    # ワークフロー用の複数のバリデーターを作成
    username_validator = create_required_validator("username_validator")
    email_validator = create_email_validator("email_validator")
    password_validator = create_length_validator(
        min_length=8, max_length=50, name="password_validator"
    )
    
    # Simulate user registration workflow
    # ユーザー登録ワークフローをシミュレート
    ctx = Context()
    
    print("Simulating user registration workflow:")
    print("ユーザー登録ワークフローをシミュレート:")
    
    # Step 1: Validate username
    print("\nStep 1: Username validation")
    result_ctx = await username_validator.run("john_doe", ctx)
    print(f"Username status: {result_ctx.shared_state.get('username_validator_status')}")
    
    # Step 2: Validate email
    print("\nStep 2: Email validation")
    result_ctx = await email_validator.run("john.doe@example.com", result_ctx)
    print(f"Email status: {result_ctx.shared_state.get('email_validator_status')}")
    
    # Step 3: Validate password
    print("\nStep 3: Password validation")
    result_ctx = await password_validator.run("mypassword123", result_ctx)
    print(f"Password status: {result_ctx.shared_state.get('password_validator_status')}")
    
    # Check overall validation status
    print("\nOverall validation status:")
    print("全体の検証状況:")
    all_passed = all([
        result_ctx.shared_state.get('username_validator_status') == 'success',
        result_ctx.shared_state.get('email_validator_status') == 'success',
        result_ctx.shared_state.get('password_validator_status') == 'success'
    ])
    print(f"All validations passed: {all_passed}")
    
    # Show all validation results stored in context
    print("\nValidation results in context:")
    print("コンテキスト内の検証結果:")
    for key, value in result_ctx.shared_state.items():
        if "validator" in key:
            print(f"  {key}: {value}")


async def main():
    """
    Main function to run all examples.
    全ての例を実行するメイン関数。
    """
    print("ValidatorAgent Examples")
    print("ValidatorAgent使用例")
    print("=" * 80)
    
    examples = [
        example_1_basic_validation,
        example_2_email_validation,
        example_3_numeric_validation,
        example_4_custom_validation,
        example_5_fail_fast_validation,
        example_6_context_integration
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
            print(f"エラー in {example.__name__}: {e}")
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("全ての例が完了しました！")


if __name__ == "__main__":
    asyncio.run(main()) 
