# AI補完設定

このページでは、agents-sdk-modelsのAI補完機能を設定する方法を説明します。

## 概要

agents-sdk-modelsでは、以下のファイルを自動生成して、IDE やエディターでのAI補完をサポートしています：

- `openai_tools.json` - OpenAI Agents SDK用のツール定義
- `.aidef` - 汎用的なAI定義ファイル
- `py.typed` - 型情報の提供

## 自動生成

### ツール定義ファイルの生成

```bash
# 仮想環境を有効にして実行
uv run python scripts/generate_ai_tools.py
```

このスクリプトは以下のファイルを生成します：

1. **openai_tools.json** - OpenAI Agents SDK向けのツール定義
2. **.aidef** - 汎用的なAI定義（マークダウン形式）

### 生成されるファイルの例

#### openai_tools.json

```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "agents_sdk_models.pipeline.Pipeline.run",
        "description": "Run the pipeline with given prompt and configuration",
        "parameters": {
          "type": "object",
          "properties": {
            "prompt": {
              "type": "str",
              "description": "Parameter prompt"
            },
            "llm": {
              "type": "LLM",
              "description": "Parameter llm"
            }
          },
          "required": ["prompt", "llm"]
        }
      }
    }
  ]
}
```

#### .aidef

```markdown
# AI Definition for agents-sdk-models
# agents-sdk-modelsのAI定義

## Module: agents_sdk_models.pipeline

### Classes / クラス

- **Pipeline**: Main pipeline class for processing prompts
  - Methods / メソッド:
    - `run`: Run the pipeline with given prompt and configuration
    - `add_step`: Add a processing step to the pipeline
```

## IDEでの設定

### VS Code

1. **Python型チェック**
   ```json
   {
     "python.linting.mypyEnabled": true,
     "python.linting.enabled": true
   }
   ```

2. **AI補完設定（Cursor）**
   - `.aidef`ファイルが自動的に認識されます
   - `openai_tools.json`はOpenAI Agents SDK設定で利用されます

### PyCharm

1. **Type hintingの有効化**
   - Settings → Editor → Inspections → Python → Type checker
   - "Mypy" を有効にする

2. **外部ツール設定**
   ```bash
   # External Tools で設定
   Program: uv
   Arguments: run python scripts/generate_ai_tools.py
   Working Directory: $ProjectFileDir$
   ```

## 型チェック

### 基本設定

`pyproject.toml`にmypy設定が含まれています：

```toml
[tool.mypy]
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
# ... その他の設定
```

### 実行方法

```bash
# 型チェック実行
uv run mypy src/

# より詳細なチェック
uv run mypy --strict src/agents_sdk_models/
```

## CI/CDでの自動実行

GitHub Actionsで自動的にAI補完ファイルを生成・検証：

```yaml
- name: Generate AI tool definitions
  run: |
    uv run python scripts/generate_ai_tools.py
    
    # Verify files were generated
    test -f openai_tools.json && echo "✓ openai_tools.json generated"
    test -f .aidef && echo "✓ .aidef generated"
```

## カスタマイズ

### 対象モジュールの変更

`scripts/generate_ai_tools.py`の`modules`リストを編集：

```python
modules = [
    "agents_sdk_models.pipeline",
    "agents_sdk_models.llm",
    "agents_sdk_models.context",
    # 新しいモジュールを追加
    "agents_sdk_models.your_new_module",
]
```

### 出力形式のカスタマイズ

生成スクリプトを編集して、出力形式をカスタマイズできます：

```python
def generate_custom_format(modules: List[str]) -> str:
    """カスタム形式でAI定義を生成"""
    # カスタム実装
    pass
```

## トラブルシューティング

### よくある問題

1. **モジュールのインポートエラー**
   ```
   Warning: Could not import agents_sdk_models.xxx: No module named 'xxx'
   ```
   → 新しいモジュールを追加した場合、`scripts/generate_ai_tools.py`の対象リストを更新

2. **型情報が認識されない**
   ```
   Cannot find module 'agents_sdk_models'
   ```
   → `py.typed`ファイルが正しく配置されているか確認

3. **AI補完が効かない**
   → `.aidef`ファイルが最新の状態か確認し、IDEを再起動

### デバッグ方法

```bash
# 生成スクリプトをデバッグモードで実行
uv run python scripts/generate_ai_tools.py --verbose

# 型チェックの詳細出力
uv run mypy --verbose src/agents_sdk_models/

# 生成されたファイルの検証
cat openai_tools.json | jq .
head -20 .aidef
```

## 貢献

AI補完機能の改善にご協力ください：

1. 新しいAI定義形式の提案
2. 生成スクリプトの機能追加
3. IDE固有の設定例の提供
4. ドキュメントの改善 