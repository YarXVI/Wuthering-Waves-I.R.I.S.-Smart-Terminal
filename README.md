# 鸣潮 I.R.I.S. 智能终端

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/React-18.2-green.svg" alt="React">
  <img src="https://img.shields.io/badge/FastAPI-0.104-orange.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/Electron-28.3-purple.svg" alt="Electron">
  <img src="https://img.shields.io/badge/License-AGPLv3-blue.svg" alt="License">
</p>

> 🏢 **I.R.I.S.** 是您的虚拟办公室智能助手。基于多Agent协作系统，支持智能会议、知识管理、任务协作，让AI成为您真正的同事。

[English](README_en.md) | 中文

## 特性

### 🤖 多Agent协作
- **内置Agent**: I.R.I.S.(管理)、小码(编程)、小文(写作)
- **自定义Agent**: 无需编码即可创建专属助手
- **Agent间协作**: 支持委托、顺序执行、并行执行多种模式

### 🏛️ 智能会议室
- **多Agent讨论**: 自动组织团队讨论，达成共识
- **智能议程**: 自动分解任务，创建待办事项
- **实时协作**: WebSocket实时更新，支持绘图和看板
- **会议导出**: Markdown格式导出会议纪要

### 🧠 MemRAG 记忆增强
- **向量检索**: 基于语义的知识召回
- **跨会话记忆**: Agent记住重要上下文
- **可开关**: 按需启用/禁用记忆增强

### 💻 现代化桌面应用
- **Electron + React**: 原生桌面体验
- **即时通讯**: 实时聊天界面
- **多语言**: 中文/English
- **本地存储**: 消息持久化到本地

### 🔌 开放API
- **RESTful API**: 60+ 接口，完全开源
- **WebSocket**: 实时消息推送
- **易于集成**: 可接入现有系统

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 1. 克隆项目

```bash
git clone https://github.com/YarXVI/Wuthering-Waves-I.R.I.S.-Smart-Terminal.git
cd Wuthering-Waves-I.R.I.S.-Smart-Terminal
```

### 2. 安装后端依赖

```bash
pip install -r agent_core/requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 4. 启动后端服务

```bash
python -m server.main
# 服务地址: http://127.0.0.1:8765
```

### 5. 启动前端（开发模式）

```bash
cd desktop
npm install
npm run dev
# 访问: http://localhost:5173
```

### 6. 构建桌面应用

```bash
# 开发调试
npm run electron:dev

# 构建安装包
npm run electron:build
```

## 项目结构

```
Wuthering-Waves-I.R.I.S.-Smart-Terminal/
├── agent_core/           # 核心Agent引擎
│   ├── core/            # Agent核心实现
│   ├── collaboration/   # Agent协作逻辑
│   ├── memrag/         # 记忆增强系统
│   ├── memory/         # 会话记忆管理
│   ├── project_room/   # 会议室逻辑
│   ├── providers/      # LLM提供商
│   ├── settings/       # 设置管理
│   ├── skills_registry/# 技能注册
│   ├── tools/          # 内置工具
│   ├── utils/          # 工具函数
│   └── workflow/       # 工作流引擎
├── server/              # FastAPI服务
│   └── routers/        # API路由模块
├── desktop/             # Electron桌面应用
│   └── src/
│       ├── components/  # React组件
│       ├── pages/      # 页面
│       ├── hooks/      # 自定义Hooks
│       ├── contexts/   # React上下文
│       └── locales/    # 国际化
├── tests/               # 测试文件
├── docs/                # 文档
├── scripts/             # 启动脚本
└── config/              # 配置文件
```

## API文档

启动服务后访问:
- Swagger UI: http://127.0.0.1:8765/docs
- ReDoc: http://127.0.0.1:8765/redoc

### 主要API端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/agents` | GET | 获取Agent列表 |
| `/api/agents` | POST | 创建新Agent |
| `/api/chat/chat` | POST | 与Agent对话 |
| `/api/collaboration/call` | POST | 发起协作 |
| `/api/meetings` | GET | 获取会议列表 |
| `/api/meetings` | POST | 创建会议 |
| `/api/memory/search` | POST | 搜索记忆 |

## 配置说明

主要配置项（`.env`）:

```env
# LLM配置
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# 服务配置
HOST=127.0.0.1
PORT=8765

# 日志级别
LOG_LEVEL=INFO
```

## 开发指南

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

## 许可证

本框架采用 [AGPLv3](https://www.gnu.org/licenses/agpl-3.0.html) 开源许可。

- **开源使用**: 欢迎基于AGPLv3条款使用本框架进行开源开发
- **闭源商用**: 如需闭源商用或获得商业支持，请联系: shenshengtiantang@outlook.com
- **补充条款**: 如对本框架进行修改并重新发布，必须开源修改版本

### 第三方代码

本框架引入了以下开源组件，请注意各组件许可证的兼容性：

| 组件 | 许可证 | 兼容性说明 |
|------|--------|------------|
| FastAPI | MIT | ✅ AGPLv3兼容 |
| React | MIT | ✅ AGPLv3兼容 |
| Electron | MIT | ✅ AGPLv3兼容 |
| LangChain | MIT | ✅ AGPLv3兼容 |
| Uvicorn | BSD | ✅ AGPLv3兼容 |
| Pydantic | MIT | ✅ AGPLv3兼容 |

> ⚠️ **注意**: 请避免混用 GPL-incompatible 的库导致法律风险。如有疑问，请联系上述邮箱。

完整许可证文本请参阅 [LICENSE](LICENSE) 文件。

## 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代高效的Web框架
- [React](https://reactjs.org/) - 组件化UI库
- [Electron](https://electronjs.org/) - 跨平台桌面应用框架
- [LangChain](https://www.langchain.com/) - LLM应用开发框架
