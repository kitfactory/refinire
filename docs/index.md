# Agents SDK Models へようこそ

OpenAI Agents SDK を拡張し、複数のLLMプロバイダーを統一インターフェースで扱えるモデルアダプター＆ワークフロー拡張集です。

## 主な特徴

- OpenAI, Gemini, Claude, Ollama など主要LLMを簡単切替
- 生成・評価・ツール・ガードレールを1つのパイプラインで統合
- モデル名とプロンプトだけで自己改善サイクルも実現
- Pydanticによる構造化出力対応
- Python 3.9+ / Windows, Linux, MacOS対応

## インストール

### PyPI から
```bash
pip install agents-sdk-models
```

### uv を使う場合
```bash
uv pip install agents-sdk-models
```

## 開発用（推奨）
```bash
git clone https://github.com/kitfactory/agents-sdk-models.git
cd agents-sdk-models
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
uv pip install -e .[dev]
```

## サポート環境
- Python 3.9+
- OpenAI Agents SDK 0.0.9+
- Windows, Linux, MacOS 