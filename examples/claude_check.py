# English: Example to connect to Claude using OpenAI SDK compatibility (beta)
# 日本語: OpenAI SDK互換API（ベータ）でClaudeに接続するサンプル

import openai
import os

# English: Set Anthropic API key and base_url for OpenAI SDK compatibility
# 日本語: OpenAI SDK互換用にAnthropicのAPIキーとbase_urlを設定
openai.api_key = os.environ.get("ANTHROPIC_API_KEY")
openai.base_url = "https://api.anthropic.com/v1/"

# English: Model name for Claude (latest version)
# 日本語: Claudeのモデル名（最新版）
model_name = "claude-3-5-sonnet-latest"

# English: Send a simple message to Claude
# 日本語: Claudeにシンプルなメッセージを送信
response = openai.chat.completions.create(
    model=model_name,
    messages=[{"role": "user", "content": "Hello, Claude"}],
    max_tokens=1024,
)

# English: Print the response from Claude
# 日本語: Claudeからのレスポンスを表示
print(response.choices[0].message.content) 
