# I.R.I.S. Smart Terminal 增强开发计划

> 融合 OpenClaw 与 Hermes Agent 优点的智能化升级路线图

---

## 一、当前架构分析

### 现有模块

| 模块 | 功能 | 现状 |
|------|------|------|
| `agent_core/core` | Agent核心引擎 | ✅ 基础ReAct循环 |
| `agent_core/memory` | 会话记忆管理 | ✅ SQLite存储 |
| `agent_core/memrag` | 向量检索增强 | ✅ Embeddings+RAG |
| `agent_core/collaboration` | Agent协作编排 | ✅ 委托/并行/顺序 |
| `agent_core/project_room` | 智能会议室 | ✅ 会议+白板 |
| `agent_core/skills_registry` | 技能注册系统 | ✅ 基础实现 |
| `agent_core/providers` | LLM提供商 | ✅ OpenAI/DeepSeek |
| `server/routers` | FastAPI路由 | ✅ RESTful API |
| `server/ws_manager` | WebSocket管理 | ✅ 实时通信 |

### 差距分析

| 能力 | I.R.I.S. | OpenClaw | Hermes | 优先级 |
|------|-----------|----------|--------|--------|
| 多平台消息网关 | ❌ | ✅ 11+平台 | ✅ 15+平台 | 高 |
| Agent人格系统 | ❌ | ✅ SOUL.md | ❌ | 高 |
| 持久记忆架构 | ⚠️ 基础 | ✅ Markdown | ✅ 双层+SQLite | 高 |
| 自我进化能力 | ❌ | ❌ | ✅ GEPA | 高 |
| 技能渐进式披露 | ⚠️ 基础 | ✅ | ✅ Level 0/1/2 | 中 |
| 子代理并行 | ⚠️ 协作模式 | ❌ | ✅ RPC风格 | 中 |
| 健康监控/Heartbeat | ❌ | ✅ | ❌ | 中 |
| 企业级安全 | ⚠️ 基础 | ✅ | ✅ 零CVE | 中 |
| 模型路由 | ❌ | ❌ | ✅ 关键词路由 | 低 |
| Profile多实例 | ❌ | ❌ | ✅ | 低 |

---

## 二、增强开发计划

### Phase 1: 核心强化（第1-2周）

#### 1.0 核心引擎边界测试（TDD先行）✅ 已完成

**目标**: 在重构前建立测试基准，确保重构过程无回归

**具体任务**:
- [x] 消息角色交替错误测试
  - `test_agent_role_validation.py` - 验证合法/非法角色转换
- [x] 并发工具调用幂等性测试
  - `test_concurrent_tool_calls.py` - 验证并发场景下的幂等性
- [x] 上下文压缩信息保留率测试
  - `test_context_compression.py` - 验证关键信息保留
- [x] 建立回归测试套件
  - `test_engine_regression_suite.py` - 核心引擎回归测试

**文件变更**:
```
tests/
├── unit/
│   ├── test_agent_role_validation.py  ✅
│   ├── test_concurrent_tool_calls.py  ✅
│   └── test_context_compression.py    ✅
└── regression/
    └── test_engine_regression_suite.py ✅
```

#### 1.1 AIAgent 核心引擎重构 ✅ 已完成

**目标**: 构建更强大的Agent执行引擎

**具体任务**:
- [x] 重构 `agent_core/core/ai_agent.py`
  - ✅ 实现可中断的API调用机制 (InterruptibleContext)
  - ✅ 添加并发工具执行支持 (ThreadPoolExecutor)
  - ✅ 实现消息角色交替校验 (RoleValidator)
  - ✅ 添加迭代预算跟踪 (IterationBudget)

- [x] 实现三种API模式支持
  - ✅ `chat_completions`: OpenAI兼容端点
  - ✅ `anthropic_messages`: Anthropic原生格式
  - ✅ `codex_responses`: Codex响应API

- [x] 上下文压缩机制
  - ✅ 自动压缩中间轮次 (CompressionEngine)
  - ✅ 保护首尾消息 (head_protection_count, tail_protection_count)
  - ✅ Resolved/Pending状态追踪 (MessageState)
  - ✅ LLM摘要辅助 (_llm_summarize)

**文件变更**:
```
agent_core/core/
├── ai_agent.py       ✅ 重构为AIAgent类
├── prompt_builder.py ✅ Prompt构建器
├── api_adapter.py    ✅ API模式适配器
├── compression.py    ✅ 上下文压缩
└── callback.py       ✅ 回调机制
```

#### 1.2 双层持久记忆架构 ✅ 已完成

**目标**: 参考Hermes的MEMORY.md + USER.md模式

**具体任务**:
- [x] 实现 `MEMORY.md` - 环境事实和经验教训
  - ✅ `memory_md.py` - MemoryManager
  - ✅ 自动定期持久化评估
  - ✅ Prompt注入安全扫描 (MemoryScanner)
  - ✅ 可配置字符限制（默认2200）

- [x] 实现 `USER.md` - 用户偏好存储
  - ✅ `memory_md.py` - UserPreferencesManager
  - ✅ 用户偏好自动学习 (learn_from_interaction)
  - ✅ 跨会话保持

- [x] 升级 `memory_store.py`
  - ✅ 添加FTS5全文搜索 (recall.py - SessionSearchEngine)
  - ✅ 支持跨会话召回 (SessionRecall)
  - ✅ SessionDB搜索功能

**文件变更**:
```
agent_core/memory/
├── memory_md.py      ✅ 新增：MEMORY.md + USER.md 管理器
├── recall.py         ✅ 新增：跨会话召回 + FTS5搜索
└── memory_store.py   ✅ 升级：支持双层MD
```

#### 1.3 Agent Profile 接口定义（Phase 1 收尾）✅ 已完成

**目标**: 为 SOUL.md 和后续人格系统预留接口，避免后续模块重复适配

**具体任务**:
- [x] 定义 `AgentProfile` 接口规范
  ```python
  class AgentProfileData:
      id: str
      name: str
      role: str
      personality: PersonalityConfig
      values: list[ValueStatement]
      behaviors: BehaviorConfig
      boundaries: list[BoundaryRule]
  ```

- [x] 定义 `PersonalityConfig` 数据结构
  ```python
  @dataclass
  class PersonalityConfig:
      traits: list[PersonalityTrait]
      communication_style: CommunicationStyle
      humor_level: HumorLevel
      response_length: ResponseLength
  ```

- [x] 实现 `YamlProfileLoader` - SOUL.md 格式解析器基础
  - ✅ 支持 YAML frontmatter
  - ✅ 字段验证 (ValidationResult)
  - ✅ 默认值填充

- [x] 预留人格切换接口
  ```python
  class PersonaManager:
      def switch_persona(self, persona_id: str) -> bool: ...
      def get_current_persona(self) -> AgentProfileData: ...
      def register_persona(self, profile: AgentProfileData) -> bool: ...
  ```

**文件变更**:
```
agent_core/core/
├── personality.py      ✅ 人格配置数据结构
├── profile_loader.py  ✅ 配置文件加载器
├── persona_manager.py ✅ 人格切换管理器
└── agent_profile.py   ✅ 兼容旧格式
```

---

### Phase 2: 平台扩展（第3-4周）

#### 2.1 Channel Gateway 统一消息网关

**目标**: 参考OpenClaw的Channel Adapter模式

**具体任务**:
- [ ] 设计统一消息格式
  ```python
  class ChannelMessage:
      platform: str          # 平台标识
      sender_id: str         # 发送者ID
      content: str           # 消息内容
      timestamp: datetime     # 时间戳
      metadata: dict          # 平台特定元数据
  ```

- [ ] 实现平台适配器基类
  ```python
  class ChannelAdapter(ABC):
      async def connect(self): ...
      async def disconnect(self): ...
      async def send_message(self, msg: ChannelMessage): ...
      async def on_message(self) -> ChannelMessage: ...
  ```

- [ ] 实现以下平台适配器
  - [ ] Telegram Adapter
  - [ ] Discord Adapter
  - [ ] Slack Adapter

#### 2.2 GEPA 自我进化引擎

**目标**: 参考Hermes的GEPA模式，实现Agent自我进化能力

**具体任务**:
- [ ] 设计进化策略接口
- [ ] 实现技能自动生成
- [ ] 实现技能评估与选择
- [ ] 预留人工审核入口

#### 2.3 健康监控与心跳

**目标**: 参考OpenClaw的Heartbeat机制

**具体任务**:
- [ ] 实现心跳检测
- [ ] 实现健康状态报告
- [ ] 实现异常告警

---

### Phase 3: 高级功能（第5-6周）

#### 3.1 SOUL.md 人格系统

**目标**: 实现完整的SOUL.md人格系统

**具体任务**:
- [ ] 设计SOUL.md格式规范
- [ ] 实现人格加载与切换
- [ ] 实现人格影响下的行为调整

#### 3.2 技能渐进式披露

**目标**: 实现Level 0/1/2技能披露机制

**具体任务**:
- [ ] 设计技能等级定义
- [ ] 实现技能池管理
- [ ] 实现基于场景的技能推荐

#### 3.3 子代理并行优化

**目标**: 实现RPC风格的子代理并行

**具体任务**:
- [ ] 设计子代理通信协议
- [ ] 实现任务分解与聚合
- [ ] 实现结果合并策略

---

## 三、风险与缓解措施

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| LLM API调用不稳定 | 高 | 实现重试机制和降级策略 |
| 上下文窗口耗尽 | 高 | 实现智能上下文压缩 |
| 技能冲突 | 中 | 引入优先级机制和人工审核 |
| 自我进化失控 | 中 | 预留人工审核入口 |
| 第三方库GPL不兼容 | 高 | 检查所有引入库的许可证兼容性 |

---

## 四、验收标准

### Phase 1 验收
- [x] 所有单元测试通过
- [x] 回归测试套件通过
- [x] AIAgent核心引擎功能正常
- [x] 双层记忆架构正常工作
- [x] Agent Profile接口可正常使用

### Phase 2 验收
- [ ] 支持至少3个平台消息网关
- [ ] GEPA自我进化引擎可工作
- [ ] 心跳监控正常运行

### Phase 3 验收
- [ ] SOUL.md人格系统完整实现
- [ ] 技能渐进式披露正常工作
- [ ] 子代理并行任务正确执行

---

*最后更新: 2026-05-04*
