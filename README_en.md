# iris Agent - Virtual Office AI Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/React-18.2-green.svg" alt="React">
  <img src="https://img.shields.io/badge/FastAPI-0.104-orange.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/Electron-28.3-purple.svg" alt="Electron">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

> 🏢 **iris** �?Your Virtual Office AI Assistant. Based on multi-Agent collaboration system, supporting intelligent meetings, knowledge management, and task collaboration. Making AI your true colleague.

[中文](README.md) | English

## �?Features

### 🤖 Multi-Agent Collaboration
- **Built-in Agents**: iris (Manager), Codey (Developer), Xiaowen (Writer)
- **Custom Agents**: Create specialized assistants without coding
- **Inter-Agent Collaboration**: Support delegation, sequential execution, and compiled execution modes

### 🏛�?Intelligent Meeting Room
- **Multi-Agent Discussion**: Automatically organize team discussions and reach consensus
- **Smart Agenda**: Automatically break down tasks and create to-dos
- **Real-time Collaboration**: WebSocket real-time updates, supports drawing and kanban
- **Meeting Export**: Export meeting minutes in Markdown format

### 🧠 MemRAG Memory Enhancement
- **Vector Retrieval**: Semantic-based knowledge recall
- **Cross-session Memory**: Agents remember important context
- **Toggle Control**: Enable/disable memory enhancement as needed

### 💻 Modern Desktop Application
- **Electron + React**: Native desktop experience
- **Instant Messaging**: Real-time chat interface
- **Multi-language**: Chinese/English
- **Local Storage**: Messages persisted to local storage

### 🔌 Open API
- **RESTful API**: 60+ endpoints, fully open
- **WebSocket**: Real-time message push
- **Easy Integration**: Can connect to existing systems

## 🚀 Quick Start

### Requirements
- Python 3.10+
- Node.js 18+
- npm or yarn

### 1. Clone the Project

```bash
git clone https://github.com/yourusername/iris-agent.git
cd iris-agent
```

### 2. Install Backend Dependencies

```bash
pip install -r agent_core/requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env and add your API Key
```

### 4. Start Backend Service

```bash
python -m server.main
# Service address: http://127.0.0.1:8765
```

### 5. Start Frontend (Development Mode)

```bash
cd desktop
npm install
npm run dev
# Visit: http://localhost:5173
```

### 6. Build Desktop Application

```bash
# Development
npm run electron:dev

# Build
npm run build
npm run electron:build
```

## 📁 Project Structure

```
iris-agent/
├── agent_core/           # Core Agent Engine
�?  ├── core/            # Agent core implementation
�?  ├── collaboration/    # Agent collaboration logic
�?  ├── memrag/          # Memory enhancement system
�?  ├── memory/          # Session memory management
�?  ├── project_room/    # Meeting room logic
�?  ├── providers/       # LLM providers
�?  ├── settings/        # Settings management
�?  ├── skills_registry/ # Skills registry
�?  ├── tools/           # Built-in tools
�?  ├── utils/           # Utility functions
�?  └── workflow/        # Workflow engine
├── server/              # FastAPI Server
�?  └── routers/        # API route modules
├── desktop/             # Electron Desktop App
�?  └── src/
�?      ├── components/  # React components
�?      ├── pages/      # Pages
�?      ├── hooks/      # Custom Hooks
�?      ├── contexts/   # React Context
�?      ├── locales/    # Internationalization
�?      └── styles/     # Styles
├── memory/              # Runtime data
├── tests/               # Test code
└── docs/                # Documentation
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# OpenAI API Configuration (supports DeepSeek, Claude, etc.)
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash

# Local notes directory
NOTES_DIR=/path/to/your/notes

# API Server Port
AGENT_PORT=8765
```

### Supported LLM Providers

| Provider | Model Example | Config |
|----------|---------------|--------|
| DeepSeek | deepseek-v4-flash | base_url + api_key |
| OpenAI | gpt-4 | base_url + api_key |
| Anthropic | claude-3 | base_url + api_key |
| Local Models | llama2 | base_url + api_key |

## 📡 API Documentation

After starting the service, visit: http://127.0.0.1:8765/docs

### Main Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Chat with Agent |
| `/agents` | GET | Get Agent list |
| `/meetings` | GET | Meeting list |
| `/meetings/from-template` | POST | Create meeting |
| `/whiteboard/{room_id}` | GET | Whiteboard data |
| `/memrag` | GET | Memory status |

## 🧪 Run Tests

### Backend Tests

```bash
python -m pytest tests/ -v
```

### Frontend Tests

```bash
cd desktop
npm test
```

## 🛠�?Tech Stack

**Backend**
- Python 3.10+
- FastAPI - Web framework
- uvicorn - ASGI server
- pydantic - Data validation
- langchain - Agent framework

**Frontend**
- React 18
- TypeScript 5
- Vite 5
- Electron 28
- React Router 6

**Data**
- JSON file storage
- SQLite (optional)
- Vector database (optional)

## 🤝 Contributing

We welcome Issue submissions and Pull Requests!

See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 License

This project is open source under MIT License. See [LICENSE](LICENSE)

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain/langchain) - Agent framework
- [FastAPI](https://github.com/tiangolo/fastapi) - Web framework
- [React](https://github.com/facebook/react) - UI framework
- [Electron](https://github.com/electron/electron) - Desktop framework

## 📬 Contact

- GitHub Issues: [https://github.com/yourusername/iris-agent/issues](https://github.com/yourusername/iris-agent/issues)

---

**If this project is helpful to you, please give us a ⭐️**
