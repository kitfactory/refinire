# Refinire へようこそ

OpenAI Agents SDK を拡張し、複数のLLMプロバイダーを統一インターフェースで扱えるモデルアダプター＆ワークフロー拡張集です。

## 主な特徴

- OpenAI, Gemini, Claude, Ollama など主要LLMを簡単切替
- **🚀 新機能：** `Flow(steps=gen_agent)` で超シンプルなワークフロー作成
- **🚀 新機能：** `Flow(steps=[step1, step2])` で自動シーケンシャル実行
- 生成・評価・ツール・ガードレールを1つのパイプラインで統合
- モデル名とプロンプトだけで自己改善サイクルも実現
- Pydanticによる構造化出力対応
- Python 3.9+ / Windows, Linux, MacOS対応

## インストール

### PyPI から
```bash
pip install refinire
```

### uv を使う場合
```bash
uv pip install refinire
```

## 開発用（推奨）
```bash
git clone https://github.com/kitfactory/refinire.git
cd refinire
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
uv pip install -e .[dev]
```

## サポート環境
- Python 3.9+
- OpenAI Agents SDK 0.0.9+
- Windows, Linux, MacOS 

## トレーシング
本ライブラリでは OpenAI Agents SDK のトレーシング機能をサポートしています。詳細は [トレーシング](tracing.md) を参照してください。

## ドキュメント

- [APIリファレンス](api_reference_ja.md) - 主要クラス・関数の詳細
- [クイックスタート](tutorials/quickstart_ja.md) - すぐに始められるガイド
- [組み合わせ可能なフローアーキテクチャ](composable-flow-architecture_ja.md) - 高度なワークフロー構築

## 学習リソース

- [チュートリアル](tutorials/) - 段階的な学習コンテンツ
- [サンプルコード](../examples/) - 実用的な使用例
- [開発者ガイド](developer/) - 貢献者向け情報 