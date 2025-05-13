# 対応する課題

OpenAI Agents SDKライブラリではサポートされているのは、OpenAIが提供するLLMのみである。そのため、OllamaやAnthropic,Googleなどの有力モデルを使用することができない。

そこで、OpenAI Agentsで動作する各LLMプロバイダーをさぽーとできるようにするものである。

# 対応プロバイダ

* Ollama
* Gemini
* Claude

# 対応方法

OpenAI Agentsでは各チャットモデルはModelクラスとModelFactoryクラスを提供しており、下記、URLのインターフェースにならったクラスを提供する必要がある。

@https://github.com/openai/openai-agents-python/blob/main/src/agents/models/interface.py

Modelクラスは特にOpenAIのモデルと入出力を揃える必要があり、下記の入出力に完全に合わせる必要がある。

@https://github.com/openai/openai-agents-python/blob/main/src/agents/models/openai_chatcompletions.py



