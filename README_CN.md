# I.R.I.S. Agent Core v2

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.104-orange.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

**I.R.I.S.** = **I**ntelligent **R**esponsive **I**ntegrated **S**ystem（智能响应式一体化系统）

基于洋葱架构的量产级智能体框架，具备惰性上下文物化（LCM）、中文思考技能和渐进式技能披露能力。

## 核心能力

### 1. LCM（惰性上下文物化）
- **基于 Chunk 的上下文存储**，支持 LRU 缓存和 JSONL 持久化
- **哨兵检测**，通过 `[NEED_CHUNK:xxx]` 标记实现按需加载
- **状态机驱动** 的上下文注入（IDLE → GENERATING → WAITING_CHUNK → RESUMING → COMPLETED）
- **内容编码层**，支持可插拔编码器（中文思考、身份编码及可扩展编码）

### 2. 中文思考技能
- **原生中文推理链**，结构化思考输出
- **隐喻增强**，运用中文认知模式
- **辩证思维** 支持（正 → 反 → 合）
- **双模式集成**：独立技能供 ReAct 循环使用 + LCM 编码插件

### 3. 技能引擎
- **渐进式披露等级**（Level 0/1/2），基于信任度和使用频率
- **自动技能蒸馏**，从成功的工具调用对话中提取
- **反馈驱动进化**，支持版本管理和性能追踪
- **关键词推荐引擎**，实现上下文技能匹配

### 4. 人格系统
- **可配置智能体人格**，包含特质、价值观、行为和边界
- **LLM 参数调制**，按人格调整 temperature、max_tokens、formality
- **内置人格**：IRIS（友好助手）、Pro（正式顾问）、Muse（创意伙伴）
- **动态系统提示词生成**，基于人格配置

### 5. 记忆管理
- **分层记忆架构**：工作记忆、短期记忆、长期记忆
- **智能体隔离存储**，JSONL 持久化
- **用户画像追踪**，基于重要性的检索
- **关键词搜索**，跨记忆条目检索

## 相关项目

- [lcm-prompt](https://github.com/YarXVI/lcm-prompt) —— 惰性上下文物化协议独立实现
- [chinese-think-skills](https://github.com/YarXVI/chinese-think-skills) —— 中文思考技能独立模块

## 架构

```
洋葱架构：
  4. 接口层       - FastAPI 路由（agents、skills、memory、personality、usage）
  3. 应用层       - AgentService 编排层
  2. 领域层       - 核心业务逻辑（AgentRuntime、Personality、ChineseThinking）
  1. 基础设施层   - 适配器（LCMEngine、SkillEngine、MemoryManager、ProviderRouter）
```

## 快速开始

### 安装

```bash
git clone https://github.com/YarXVI/Wuthering-Waves-I.R.I.S.-Smart-Terminal.git
cd Wuthering-Waves-I.R.I.S.-Smart-Terminal
pip install -r agent_core/requirements.txt
```

### 基础用法

```python
from agent_core.v2 import AgentService, ProviderConfig, Chunk, LCMEngine

# 创建服务
service = AgentService()
service.provider.register(ProviderConfig(
    name="default",
    model="gpt-4o",
    api_key="sk-...",
))

# 添加 LCM chunk
service.lcm.store.add(Chunk(
    chunk_id="auth_handler",
    content="def login(): ...",
    summary="认证处理器",
))

# 与智能体对话
result = await service.chat(
    agent_id="iris",
    user_message="审查认证处理器",
)
print(result.content)
```

### 启用中文思考

```python
from agent_core.v2 import AgentRuntime, RuntimeConfig

runtime = AgentRuntime(
    provider_router=provider,
    memory_manager=memory,
    skill_engine=skills,
    config=RuntimeConfig(
        enable_chinese_thinking=True,
        chinese_thinking_depth="deep",
    ),
)
```

## 项目结构

```
agent_core/v2/
├── __init__.py              # 公共 API 导出
├── domain/                  # 核心业务逻辑
│   ├── agent_runtime.py     # ReAct 循环 + LCM + 中文思考
│   ├── chinese_thinking.py  # ChineseThinkingSkill + ChineseThinkEncoding
│   ├── execution_context.py # 不可变执行上下文
│   ├── execution_result.py  # 标准化结果（含工具调用）
│   ├── lazy_context.py      # 轻量级 shard-based LCM
│   └── personality.py       # 人格系统（含内置人格）
├── infrastructure/          # 外部适配器
│   ├── chunk_store.py       # Chunk 存储 + LRU 缓存
│   ├── content_encoding.py  # 可插拔编码注册表
│   ├── lcm_engine.py        # 完整 LCM 协议 + 状态机
│   ├── memory_manager.py    # 分层记忆管理
│   ├── memory_v2.py         # 智能体隔离记忆存储
│   ├── provider_router.py   # LLM 提供商路由
│   ├── sentinel_detector.py # 哨兵标记检测
│   └── skill_engine.py      # 技能生命周期管理
├── application/             # 用例层
│   └── agent_service.py     # 高层服务 API
└── interfaces/              # API 层
    ├── api_router.py        # 智能体对话端点
    ├── memory_router.py     # 记忆管理端点
    ├── personality_router.py # 人格端点
    ├── skills_router.py     # 技能执行端点
    └── usage_router.py      # 用量追踪端点
```

## API 端点

| 端点 | 方法 | 说明 |
|----------|--------|-------------|
| `/v2/agents/chat` | POST | 与智能体对话 |
| `/v2/agents/register` | POST | 注册新智能体 |
| `/skills/list` | GET | 列出所有技能 |
| `/skills/{id}/execute` | POST | 执行技能 |
| `/memory/{agent_id}` | GET | 加载智能体记忆 |
| `/personality/list` | GET | 列出人格 |
| `/personality/{id}` | GET | 获取人格详情 |

服务运行后，完整 API 文档可在 `/docs` 查看。

## 配置

关键环境变量（`.env`）：

```env
# LLM 提供商
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# 服务
HOST=127.0.0.1
PORT=8765

# 日志
LOG_LEVEL=INFO
```

## 开源协议

本项目采用 [MIT 协议](LICENSE) 开源。

- **自由使用**：可用于个人和商业项目
- **修改分发**：允许修改和再分发
- **保留声明**：需保留原始版权声明

## 第三方致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Web 框架
- [Pydantic](https://docs.pydantic.dev/) - 数据验证
- [LangChain](https://www.langchain.com/) - LLM 应用框架
