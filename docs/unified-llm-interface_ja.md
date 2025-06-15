# Unified LLM Interface - 統一LLMインターフェース

Refinireの第一の柱である統一LLMインターフェースは、複数のLLMプロバイダーを同一のAPIで操作できる革新的な抽象化層です。

## 基本概念

複数のLLMプロバイダーを同じインターフェースで扱うことで、開発者はプロバイダー固有の実装に縛られることなく、自由に選択・切り替えできます。

### 環境変数の設定

各プロバイダーを使用するには、対応するAPIキーを環境変数に設定する必要があります：

| プロバイダー | 環境変数 | 説明 |
|------------|----------|------|
| **OpenAI** | `OPENAI_API_KEY` | OpenAI APIキー |
| **Anthropic** | `ANTHROPIC_API_KEY` | Anthropic Claude APIキー |
| **Google** | `GOOGLE_API_KEY` | Google Gemini APIキー |
| **Ollama** | `OLLAMA_BASE_URL` | Ollamaサーバーアドレス（デフォルト: http://localhost:11434） |

#### 環境変数設定例

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY = "sk-your-openai-api-key"
$env:ANTHROPIC_API_KEY = "sk-ant-your-anthropic-api-key"
$env:GOOGLE_API_KEY = "your-google-api-key"
$env:OLLAMA_BASE_URL = "http://localhost:11434"
```

**macOS/Linux (Bash):**
```bash
export OPENAI_API_KEY="sk-your-openai-api-key"
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-api-key"
export GOOGLE_API_KEY="your-google-api-key"
export OLLAMA_BASE_URL="http://localhost:11434"
```

**Python内での設定:**
```python
import os

# プログラム内で環境変数を設定
os.environ["OPENAI_API_KEY"] = "sk-your-openai-api-key"
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-your-anthropic-api-key"
os.environ["GOOGLE_API_KEY"] = "your-google-api-key"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
```

### 統一インターフェース

環境変数を設定後、すべてのプロバイダーが同じAPIで利用できます：

```python
from refinire import get_llm

# 同じインターフェースで異なるプロバイダーにアクセス
llm_openai = get_llm("gpt-4o-mini")
llm_anthropic = get_llm("claude-3-sonnet")
llm_google = get_llm("gemini-pro")
llm_ollama = get_llm("llama3.1:8b")

# すべて同じメソッドで操作
response = llm_openai.complete("こんにちは")
```

## 簡単な事例

### 1. 基本的なLLM使用

```python
from refinire import get_llm

# LLMの取得
llm = get_llm("gpt-4o-mini")

# テキスト生成
response = llm.complete("AIの将来性について教えてください")
print(response)
```

### 2. 環境変数設定の確認

```python
import os
from refinire import get_llm

def check_api_setup():
    """API設定の確認"""
    providers_check = {
        "OpenAI": "OPENAI_API_KEY",
        "Anthropic": "ANTHROPIC_API_KEY", 
        "Google": "GOOGLE_API_KEY",
        "Ollama": "OLLAMA_BASE_URL"
    }
    
    for provider, env_var in providers_check.items():
        if env_var in os.environ:
            print(f"✓ {provider}: 設定済み")
        else:
            print(f"✗ {provider}: {env_var} が未設定")

# API設定確認
check_api_setup()
```

### 3. プロバイダー切り替え

```python
def test_providers():
    """利用可能なプロバイダーでテスト実行"""
    providers = [
        ("gpt-4o-mini", "OpenAI"),
        ("claude-3-haiku-20240307", "Anthropic"),
        ("gemini-1.5-flash", "Google"),
        ("llama3.1:8b", "Ollama")
    ]
    question = "量子コンピューティングとは何ですか？"
    
    for model, provider in providers:
        try:
            llm = get_llm(model)
            response = llm.complete(question)
            print(f"✓ {provider} ({model}): {response[:100]}...")
        except Exception as e:
            print(f"✗ {provider} ({model}): エラー - {e}")

# プロバイダーテスト実行
test_providers()
```

## 中級事例

### 3. 戦略的プロバイダー使い分け

```python
class MultiProviderService:
    def __init__(self):
        self.fast_llm = get_llm("gpt-4o-mini")      # 高速
        self.smart_llm = get_llm("gpt-4o")          # 高性能
        self.creative_llm = get_llm("claude-3-sonnet")  # 創造性
    
    def quick_answer(self, question: str) -> str:
        return self.fast_llm.complete(f"簡潔に: {question}")
    
    def detailed_analysis(self, topic: str) -> str:
        return self.smart_llm.complete(f"詳細分析: {topic}")
    
    def creative_writing(self, theme: str) -> str:
        return self.creative_llm.complete(f"創作: {theme}")
```

### 4. フォールバック機構

```python
class RobustLLMService:
    def __init__(self, provider_hierarchy):
        self.provider_hierarchy = provider_hierarchy
        self.llms = {p: get_llm(p) for p in provider_hierarchy}
    
    def complete_with_fallback(self, prompt: str):
        for provider in self.provider_hierarchy:
            try:
                return self.llms[provider].complete(prompt), provider
            except Exception as e:
                print(f"{provider} 失敗: {e}")
        raise Exception("全プロバイダーで失敗")
```

## 高度な事例

### 5. インテリジェントプロバイダー選択

```python
from enum import Enum

class TaskType(Enum):
    CREATIVE = "creative"
    TECHNICAL = "technical"
    CASUAL = "casual"

class SmartProviderSelector:
    def __init__(self):
        self.profiles = {
            "gpt-4o-mini": {"strengths": [TaskType.CASUAL], "cost": 1},
            "claude-3-sonnet": {"strengths": [TaskType.CREATIVE], "cost": 2},
            "gpt-4o": {"strengths": [TaskType.TECHNICAL], "cost": 3}
        }
    
    def classify_task(self, prompt: str) -> TaskType:
        if any(word in prompt for word in ["物語", "創作"]):
            return TaskType.CREATIVE
        elif any(word in prompt for word in ["分析", "技術"]):
            return TaskType.TECHNICAL
        return TaskType.CASUAL
    
    def select_provider(self, prompt: str, priority="balanced"):
        task_type = self.classify_task(prompt)
        # 最適なプロバイダーを選択するロジック
        for provider, profile in self.profiles.items():
            if task_type in profile["strengths"]:
                return provider
        return "gpt-4o-mini"  # デフォルト
```

## メリット

- **プロバイダー透明性**: 統一されたAPIで複数プロバイダー操作
- **移行容易性**: 最小限の変更でプロバイダー切り替え
- **フォールバック**: 堅牢なエラーハンドリング
- **最適化**: タスクに応じた自動プロバイダー選択

統一LLMインターフェースにより、開発者はプロバイダーの詳細に縛られず、AIアプリケーションの価値創造に集中できます。