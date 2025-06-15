"""
Module for localized message strings
日本語/英語のメッセージ文字列を提供するモジュール
"""

import os  # English: Import os to read environment variables. 日本語: 環境変数読み取りのためosをインポート
import locale  # English: Import locale to get system locale. 日本語: システムロケール取得のためlocaleをインポート

def _detect_default_language() -> str:
    """
    Detect default language from environment variable or OS setting.
    環境変数やOS設定からデフォルトの言語を判定します。
    日本語の場合 'ja' を返し、それ以外は 'en' を返します。
    """
    # Check environment variables commonly used for locale
    for env_var in ("LANG", "LC_ALL", "LC_MESSAGES"):
        lang_val = os.environ.get(env_var, "")
        if lang_val.lower().startswith("ja"):
            return "ja"
    # Fallback to system locale
    sys_loc = locale.getdefaultlocale()[0] or ""
    if sys_loc.lower().startswith("ja"):
        return "ja"
    return "en"

DEFAULT_LANGUAGE = _detect_default_language()

# Supported languages: English (en) and Japanese (ja)
MESSAGES: dict[str, dict[str, str]] = {
    "evaluation_feedback_header": {
        "en": "Evaluation feedback:",
        "ja": "評価フィードバック："
    },
    "ai_history_header": {
        "en": "Past AI outputs:",
        "ja": "過去のAI出力："
    },
    "user_input_prefix": {
        "en": "UserInput:",
        "ja": "ユーザー入力："
    },
    # Trace labels for console tracing
    "trace_instruction": {
        "en": "Instruction:",
        "ja": "インストラクション："
    },
    "trace_prompt": {
        "en": "Prompt:",
        "ja": "プロンプト："
    },
    "trace_output": {
        "en": "Output:",
        "ja": "LLM出力："
    },
    # Evaluation format instructions
    "eval_output_format_header": {
        "en": "Output format:",
        "ja": "出力フォーマット:"
    },
    "eval_json_schema_instruction": {
        "en": "JSON with the following format:",
        "ja": "JSONで以下の形式にしてください:"
    }
}

def get_message(key: str, lang: str = DEFAULT_LANGUAGE) -> str:
    """
    Get localized message by key and language
    キーと言語からローカライズされたメッセージを取得する

    Args:
        key: Message key / メッセージキー
        lang: Language code ('en' or 'ja') / 言語コード（'en' または 'ja'）

    Returns:
        Localized message string / ローカライズされたメッセージ文字列
    """
    # Ensure lang is either 'ja' or 'en'
    use_lang = lang if lang in ("en", "ja") else DEFAULT_LANGUAGE
    return MESSAGES.get(key, {}).get(use_lang, MESSAGES.get(key, {}).get("en", "")) 
