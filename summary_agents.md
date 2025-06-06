# 繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝医け繝ｩ繧ｹ豈碑ｼ・ぎ繧､繝・

## 讎りｦ・

agents-sdk-models縺ｫ縺ｯ3縺､縺ｮ荳ｻ隕√↑繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝医け繝ｩ繧ｹ縺後≠繧翫∪縺呻ｼ・

- **AgentPipeline** ・磯撼謗ｨ螂ｨ・会ｼ壼ｾ捺擂縺ｮ繧ｪ繝ｼ繝ｫ繧､繝ｳ繝ｯ繝ｳ蝙九ヱ繧､繝励Λ繧､繝ｳ
- **GenAgent**・壹Δ繝繝ｳ縺ｪ繝・く繧ｹ繝育函謌舌・螟画鋤繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝・
- **ClarifyAgent**・壼ｯｾ隧ｱ蝙玖ｦ∽ｻｶ譏守｢ｺ蛹悶お繝ｼ繧ｸ繧ｧ繝ｳ繝・

譛ｬ譁・嶌縺ｧ縺ｯ蜷・け繝ｩ繧ｹ縺ｮ繧､繝ｳ繧ｿ繝ｼ繝輔ぉ繝ｼ繧ｹ縲∵ｩ溯・縲・←逕ｨ蝣ｴ髱｢繧定ｩｳ縺励￥豈碑ｼ・＠縺ｾ縺吶・

## 繧｢繝ｼ繧ｭ繝・け繝√Ε讎りｦ・

```mermaid
graph TB
    subgraph "Agent Pipeline Architecture"
        AP[AgentPipeline] --> OAPISDK[OpenAI Agents SDK]
        AP --> |deprecated| Warning[v0.1.0縺ｧ蜑企勁莠亥ｮ咯
    end
    
    subgraph "Modern Flow/Step Architecture"
        GA[GenAgent] --> LLM[LLMPipeline]
        CA[ClarifyAgent] --> CP[ClearifyPipeline]
        CP --> LLM
        
        GA --> |extends| Step
        CA --> |extends| Step
        
        Step --> Flow[Flow Workflow]
    end
    
    style AP fill:#ffcccc
    style Warning fill:#ff9999
    style GA fill:#ccffcc
    style CA fill:#ccccff
```

## 隧ｳ邏ｰ豈碑ｼ・｡ｨ

### 蝓ｺ譛ｬ螻樊ｧ豈碑ｼ・

| 鬆・岼 | AgentPipeline | GenAgent | ClarifyAgent |
|------|---------------|----------|---------------|
| **繧ｹ繝・・繧ｿ繧ｹ** | 圷 髱樊耳螂ｨ・・0.1.0縺ｧ蜑企勁・・| 笨・謗ｨ螂ｨ | 笨・謗ｨ螂ｨ |
| **繧｢繝ｼ繧ｭ繝・け繝√Ε** | 迢ｬ遶句梛繝代う繝励Λ繧､繝ｳ | Flow/Step邨ｱ蜷・| Flow/Step邨ｱ蜷・|
| **蜀・Κ螳溯｣・* | OpenAI Agents SDK逶ｴ謗･蛻ｩ逕ｨ | LLMPipeline菴ｿ逕ｨ | ClearifyPipeline菴ｿ逕ｨ |
| **蟇ｾ隧ｱ諤ｧ** | 蜊倡匱螳溯｡・| 蜊倡匱螳溯｡・| 螟壹ち繝ｼ繝ｳ蟇ｾ隧ｱ |
| **荳ｻ縺ｪ逕ｨ騾・* | 逕滓・繝ｻ隧穂ｾ｡繝ｻ謾ｹ蝟・| 逕滓・繝ｻ螟画鋤 | 隕∽ｻｶ譏守｢ｺ蛹・|

### 讖溯・豈碑ｼ・

| 讖溯・ | AgentPipeline | GenAgent | ClarifyAgent |
|------|---------------|----------|---------------|
| **繝・く繧ｹ繝育函謌・* | 笨・| 笨・| 笨・ｼ郁ｳｪ蝠冗函謌撰ｼ・|
| **蜩∬ｳｪ隧穂ｾ｡** | 笨・| 笨・| 笨・|
| **繝ｪ繝医Λ繧､讖溯・** | 笨・| 笨・| 笨・|
| **讒矩蛹門・蜉・* | 笨・| 笨・| 笨・|
| **螟壹ち繝ｼ繝ｳ蟇ｾ隧ｱ** | 笶・| 笶・| 笨・|
| **隕∽ｻｶ譏守｢ｺ蛹・* | 笶・| 笶・| 笨・|
| **繧ｿ繝ｼ繝ｳ蛻ｶ蠕｡** | 笶・| 笶・| 笨・|
| **莨夊ｩｱ迥ｶ諷狗ｮ｡逅・* | 笶・| 笶・| 笨・|
| **Flow繝ｯ繝ｼ繧ｯ繝輔Ο繝ｼ邨ｱ蜷・* | 笶鯉ｼ医Λ繝・ヱ繝ｼ蠢・ｦ・ｼ・| 笨・| 笨・|

### 繧､繝ｳ繧ｿ繝ｼ繝輔ぉ繝ｼ繧ｹ豈碑ｼ・

#### 菴懈・髢｢謨ｰ

| 繧ｯ繝ｩ繧ｹ | 蝓ｺ譛ｬ菴懈・髢｢謨ｰ | 隧穂ｾ｡莉倥″菴懈・髢｢謨ｰ |
|--------|-------------|------------------|
| AgentPipeline | `AgentPipeline(...)` | 蜷御ｸ繧ｳ繝ｳ繧ｹ繝医Λ繧ｯ繧ｿ |
| GenAgent | `create_simple_gen_agent(...)` | `create_evaluated_gen_agent(...)` |
| ClarifyAgent | `create_simple_clarify_agent(...)` | `create_evaluated_clarify_agent(...)` |

#### 繧ｳ繝ｳ繧ｹ繝医Λ繧ｯ繧ｿ繝代Λ繝｡繝ｼ繧ｿ

##### 蜈ｱ騾壹ヱ繝ｩ繝｡繝ｼ繧ｿ

| 繝代Λ繝｡繝ｼ繧ｿ | AgentPipeline | GenAgent | ClarifyAgent |
|------------|---------------|----------|---------------|
| `name` | 笨・str | 笨・str | 笨・str |
| `generation_instructions` | 笨・str | 笨・str | 笨・str |
| `evaluation_instructions` | 笨・Optional[str] | 笨・Optional[str] | 笨・Optional[str] |
| `model` | 笨・str | 笨・str = "gpt-4o-mini" | 笨・str |
| `evaluation_model` | 笨・Optional[str] | 笨・Optional[str] | 笨・Optional[str] |
| `threshold` | 笨・int = 85 | 笨・float = 85.0 | 笨・int = 85 |
| `retries` | 笨・int = 3 | 笨・int = 3 | 笨・int = 3 |

##### 蝗ｺ譛峨ヱ繝ｩ繝｡繝ｼ繧ｿ

**AgentPipeline蝗ｺ譛・*
- `input_guardrails` / `output_guardrails`
- `generation_tools` / `evaluation_tools` 
- `routing_func`
- `session_history` / `history_size`
- `improvement_callback`
- `dynamic_prompt`
- `retry_comment_importance`
- `locale`

**GenAgent蝗ｺ譛・*
- `output_model` (Pydantic)
- `temperature` / `max_tokens` / `timeout`
- `next_step` / `store_result_key`

**ClarifyAgent蝗ｺ譛・*
- `output_data` (繧ｿ繝ｼ繧ｲ繝・ヨ繝・・繧ｿ蝙・
- `clerify_max_turns` (譛螟ｧ繧ｿ繝ｼ繝ｳ謨ｰ)
- `conversation_key` (莨夊ｩｱ迥ｶ諷九く繝ｼ)

#### 螳溯｡後Γ繧ｽ繝・ラ

| 繧ｯ繝ｩ繧ｹ | 蜷梧悄螳溯｡・| 髱槫酔譛溷ｮ溯｡・| 謌ｻ繧雁､ |
|--------|----------|------------|--------|
| AgentPipeline | `run(user_input)` | `run_async(user_input)` | 逕滓・邨先棡 or None |
| GenAgent | - | `run(user_input, ctx)` | Context |
| ClarifyAgent | - | `run(user_input, ctx)` | Context |

## 菴ｿ逕ｨ萓区ｯ碑ｼ・

### 1. 蝓ｺ譛ｬ逧・↑繝・く繧ｹ繝育函謌・

#### AgentPipeline・磯撼謗ｨ螂ｨ・・
```python
# 髱樊耳螂ｨ - 菴ｿ逕ｨ繧帝∩縺代ｋ
pipeline = AgentPipeline(
    name="simple_gen",
    generation_instructions="繝ｦ繝ｼ繧ｶ繝ｼ縺ｮ雉ｪ蝠上↓遲斐∴縺ｦ縺上□縺輔＞縲・,
    evaluation_instructions=None,
    model="gpt-4o-mini"
)
result = pipeline.run("莠ｺ蟾･遏･閭ｽ縺ｮ譛ｪ譚･縺ｫ縺､縺・※謨吶∴縺ｦ")
```

#### GenAgent・域耳螂ｨ・・
```python
from agents_sdk_models import create_simple_gen_agent, Context
import asyncio

agent = create_simple_gen_agent(
    name="simple_gen",
    instructions="繝ｦ繝ｼ繧ｶ繝ｼ縺ｮ雉ｪ蝠上↓遲斐∴縺ｦ縺上□縺輔＞縲・,
    model="gpt-4o-mini"
)

context = Context()
result_context = asyncio.run(agent.run("莠ｺ蟾･遏･閭ｽ縺ｮ譛ｪ譚･縺ｫ縺､縺・※謨吶∴縺ｦ", context))
result = result_context.shared_state.get("simple_gen_result")
```

### 2. 隧穂ｾ｡莉倥″逕滓・

#### AgentPipeline・磯撼謗ｨ螂ｨ・・
```python
# 髱樊耳螂ｨ
pipeline = AgentPipeline(
    name="evaluated_gen",
    generation_instructions="蜑ｵ騾逧・↑迚ｩ隱槭ｒ譖ｸ縺・※縺上□縺輔＞縲・,
    evaluation_instructions="蜑ｵ騾諤ｧ縺ｨ荳雋ｫ諤ｧ繧定ｩ穂ｾ｡縺励※縺上□縺輔＞縲・,
    model="gpt-4o",
    threshold=80
)
result = pipeline.run("繝ｭ繝懊ャ繝医・迚ｩ隱・)
```

#### GenAgent・域耳螂ｨ・・
```python
from agents_sdk_models import create_evaluated_gen_agent

agent = create_evaluated_gen_agent(
    name="evaluated_gen",
    generation_instructions="蜑ｵ騾逧・↑迚ｩ隱槭ｒ譖ｸ縺・※縺上□縺輔＞縲・,
    evaluation_instructions="蜑ｵ騾諤ｧ縺ｨ荳雋ｫ諤ｧ繧定ｩ穂ｾ｡縺励※縺上□縺輔＞縲・,
    model="gpt-4o",
    threshold=80.0
)

context = Context()
result_context = asyncio.run(agent.run("繝ｭ繝懊ャ繝医・迚ｩ隱・, context))
result = result_context.shared_state.get("evaluated_gen_result")
```

### 3. 隕∽ｻｶ譏守｢ｺ蛹・

#### ClarifyAgent・域眠讖溯・・・
```python
from agents_sdk_models import create_simple_clarify_agent
from pydantic import BaseModel

class ProjectInfo(BaseModel):
    name: str
    description: str
    deadline: str

agent = create_simple_clarify_agent(
    name="clarifier",
    instructions="繝励Ο繧ｸ繧ｧ繧ｯ繝域ュ蝣ｱ繧呈・遒ｺ蛹悶＠縺ｦ縺上□縺輔＞縲・,
    output_data=ProjectInfo,
    max_turns=5
)

# 螟壹ち繝ｼ繝ｳ蟇ｾ隧ｱ縺ｫ繧医ｋ譏守｢ｺ蛹・
context = Context()
result_context = asyncio.run(agent.run("譁ｰ縺励＞繝励Ο繧ｸ繧ｧ繧ｯ繝医ｒ蟋九ａ縺溘＞", context))

# 譏守｢ｺ蛹悶′螳御ｺ・☆繧九∪縺ｧ蟇ｾ隧ｱ繧堤ｶ咏ｶ・
while not agent.is_clarification_complete():
    user_response = input("霑ｽ蜉諠・ｱ: ")
    result_context = asyncio.run(agent.run(user_response, result_context))

final_result = result_context.shared_state.get("clarifier_result")
```

## 遘ｻ陦後ぎ繧､繝・

### AgentPipeline縺九ｉGenAgent縺ｸ縺ｮ遘ｻ陦・

#### Before (AgentPipeline)
```python
pipeline = AgentPipeline(
    name="content_generator",
    generation_instructions="險倅ｺ九ｒ逕滓・縺励※縺上□縺輔＞縲・,
    evaluation_instructions="蜩∬ｳｪ繧定ｩ穂ｾ｡縺励※縺上□縺輔＞縲・,
    model="gpt-4o",
    threshold=85,
    retries=3
)
result = pipeline.run("AI縺ｫ縺､縺・※縺ｮ險倅ｺ・)
```

#### After (GenAgent)
```python
from agents_sdk_models import create_evaluated_gen_agent, Flow

# Step 1: GenAgent縺ｫ螟画鋤
agent = create_evaluated_gen_agent(
    name="content_generator",
    generation_instructions="險倅ｺ九ｒ逕滓・縺励※縺上□縺輔＞縲・,
    evaluation_instructions="蜩∬ｳｪ繧定ｩ穂ｾ｡縺励※縺上□縺輔＞縲・,
    model="gpt-4o",
    threshold=85.0,
    retries=3
)

# Step 2: Flow縺ｧ螳溯｡鯉ｼ亥腰菴薙∪縺溘・繝ｯ繝ｼ繧ｯ繝輔Ο繝ｼ縺ｮ荳驛ｨ縺ｨ縺励※・・
flow = Flow("content_generation", steps={"generator": agent})
result = asyncio.run(flow.run("AI縺ｫ縺､縺・※縺ｮ險倅ｺ・))
content = result.shared_state.get("content_generator_result")
```

## 驕ｩ逕ｨ蝣ｴ髱｢蛻･謗ｨ螂ｨ莠矩・

### 1. 蜊倡ｴ斐↑繝・く繧ｹ繝育函謌舌・螟画鋤
**謗ｨ螂ｨ**: GenAgent
- 逅・罰: 繝｢繝繝ｳ縺ｪ繧｢繝ｼ繧ｭ繝・け繝√Ε縲：low邨ｱ蜷医∫ｰ｡貎斐↑API

### 2. 蜩∬ｳｪ菫晁ｨｼ縺碁㍾隕√↑逕滓・
**謗ｨ螂ｨ**: GenAgent・郁ｩ穂ｾ｡莉倥″・・
- 逅・罰: 譟碑ｻ溘↑隧穂ｾ｡險ｭ螳壹∵隼蝟・＆繧後◆繝ｪ繝医Λ繧､讖溯・

### 3. 譖匁乂縺ｪ隕∵ｱゅ・譏守｢ｺ蛹・
**謗ｨ螂ｨ**: ClarifyAgent
- 逅・罰: 蟆ら畑險ｭ險医∝､壹ち繝ｼ繝ｳ蟇ｾ隧ｱ縲∵ｧ矩蛹悶ョ繝ｼ繧ｿ蜿朱寔

### 4. 隍・尅縺ｪ繝ｯ繝ｼ繧ｯ繝輔Ο繝ｼ
**謗ｨ螂ｨ**: GenAgent + ClarifyAgent 繧巽low縺ｧ邨・∩蜷医ｏ縺・
- 逅・罰: 繧ｹ繝・ャ繝励・邨・∩蜷医ｏ縺帙∵沐霆溘↑蛻ｶ蠕｡繝輔Ο繝ｼ

### 5. 譌｢蟄倥・AgentPipeline繧ｳ繝ｼ繝・
**蟇ｾ蠢・*: 譌ｩ諤･縺ｫGenAgent縺ｫ遘ｻ陦・
- 逅・罰: AgentPipeline縺ｯv0.1.0縺ｧ蜑企勁莠亥ｮ・

## 繝吶せ繝医・繝ｩ繧ｯ繝・ぅ繧ｹ

### 1. GenAgent菴ｿ逕ｨ譎・
```python
# 笨・謗ｨ螂ｨ: Factory髢｢謨ｰ繧剃ｽｿ逕ｨ
agent = create_simple_gen_agent(
    name="my_agent",
    instructions="...",
    model="gpt-4o-mini"
)

# 笶・髱樊耳螂ｨ: 逶ｴ謗･繧ｳ繝ｳ繧ｹ繝医Λ繧ｯ繧ｿ蜻ｼ縺ｳ蜃ｺ縺暦ｼ郁､・尅・・
agent = GenAgent(
    name="my_agent",
    generation_instructions="...",
    model="gpt-4o-mini",
    # 螟壹￥縺ｮ繝代Λ繝｡繝ｼ繧ｿ...
)
```

### 2. ClarifyAgent菴ｿ逕ｨ譎・
```python
# 笨・謗ｨ螂ｨ: 譏守｢ｺ縺ｪ繝・・繧ｿ繝｢繝・Ν螳夂ｾｩ
class UserRequirement(BaseModel):
    goal: str
    constraints: List[str]
    deadline: str

agent = create_simple_clarify_agent(
    name="clarifier",
    instructions="隕∽ｻｶ繧呈・遒ｺ蛹悶＠縺ｦ縺上□縺輔＞縲・,
    output_data=UserRequirement,
    max_turns=10
)
```

### 3. Flow邨ｱ蜷域凾
```python
# 笨・謗ｨ螂ｨ: 蠖ｹ蜑ｲ繧呈・遒ｺ縺ｫ蛻・屬
clarify_agent = create_simple_clarify_agent(...)
gen_agent = create_evaluated_gen_agent(...)

flow = Flow("complete_workflow", steps={
    "clarify": clarify_agent,
    "generate": gen_agent
})
```

## 諤ｧ閭ｽ豈碑ｼ・

| 鬆・岼 | AgentPipeline | GenAgent | ClarifyAgent |
|------|---------------|----------|---------------|
| **蛻晄悄蛹夜溷ｺｦ** | 荳ｭ | 鬮・| 鬮・|
| **螳溯｡碁溷ｺｦ** | 荳ｭ | 鬮・| 荳ｭ・亥ｯｾ隧ｱ蝙具ｼ・|
| **繝｡繝｢繝ｪ菴ｿ逕ｨ驥・* | 荳ｭ | 菴・| 荳ｭ |
| **諡｡蠑ｵ諤ｧ** | 菴・| 鬮・| 鬮・|
| **菫晏ｮ域ｧ** | 菴・| 鬮・| 鬮・|

## 縺ｾ縺ｨ繧・

- **AgentPipeline**: 髱樊耳螂ｨ縲∵掠諤･縺ｫ遘ｻ陦後′蠢・ｦ・
- **GenAgent**: 繝｢繝繝ｳ縺ｪ逕滓・繝ｻ螟画鋤繧ｿ繧ｹ繧ｯ逕ｨ縲・ｫ俶ｧ閭ｽ縺ｧ諡｡蠑ｵ諤ｧ縺碁ｫ倥＞
- **ClarifyAgent**: 隕∽ｻｶ譏守｢ｺ蛹門ｰら畑縲∝ｯｾ隧ｱ蝙九ち繧ｹ繧ｯ縺ｫ譛驕ｩ

譁ｰ隕城幕逋ｺ縺ｧ縺ｯ**GenAgent**縺ｨ**ClarifyAgent**繧堤ｵ・∩蜷医ｏ縺帙◆Flow/Step繧｢繝ｼ繧ｭ繝・け繝√Ε縺ｮ謗｡逕ｨ繧貞ｼｷ縺乗耳螂ｨ縺励∪縺吶・
