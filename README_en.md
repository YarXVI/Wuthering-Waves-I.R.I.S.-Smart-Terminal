# Wuthering Waves I.R.I.S. Smart Terminal

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/React-18.2-green.svg" alt="React">
  <img src="https://img.shields.io/badge/FastAPI-0.104-orange.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/Electron-28.3-purple.svg" alt="Electron">
  <img src="https://img.shields.io/badge/License-AGPLv3-blue.svg" alt="License">
</p>

> **⚠️ Third-Party Disclaimer**:
> The trademarks and character names "Wuthering Waves" and "I.R.I.S." used in this project's name are intellectual property of Kuro Game. This project is for personal interest and fan creation only, with no intention to create confusion with the official product, nor does it represent official views.
> If any rights holder believes this project constitutes infringement, please contact me for renaming or removal.
>
> **Code License**: Except for the third-party names mentioned above, all code written in this project is licensed under the [GNU Affero General Public License v3 (AGPLv3)](https://www.gnu.org/licenses/agpl-3.0.html). You are free to use, modify, and distribute this code, subject to all terms of AGPLv3.

> 🏢 **I.R.I.S.** - Your Virtual Office AI Assistant. Based on multi-Agent collaboration system, supporting intelligent meetings, knowledge management, and task collaboration. Making AI your true colleague.

[中文](README.md) | English

## Features

### 🤖 Multi-Agent Collaboration
- **Built-in Agents**: I.R.I.S. (Manager), Xiaoma (Developer), Xiaowen (Writer)
- **Custom Agents**: Create specialized assistants without coding
- **Inter-Agent Collaboration**: Support delegation, sequential execution, and parallel execution modes

### 🏛️ Intelligent Meeting Room
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
- **RESTful API**: 60+ endpoints, fully open source
- **WebSocket**: Real-time message push
- **Easy Integration**: Can connect to existing systems

## 🚀 Quick Start

### Requirements
- Python 3.10+
- Node.js 18+
- npm or yarn

### 1. Clone the project

```bash
git clone https://github.com/YarXVI/Wuthering-Waves-I.R.I.S.-Smart-Terminal.git
cd Wuthering-Waves-I.R.I.S.-Smart-Terminal
```

### 2. Install backend dependencies

```bash
pip install -r agent_core/requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env and add your API Key
```

### 4. Start the backend server

```bash
python -m server.main
# Server address: http://127.0.0.1:8765
```

### 5. Start the frontend (development mode)

```bash
cd desktop
npm install
npm run dev
# Access: http://localhost:5173
```

### 6. Build desktop application

```bash
# Development debugging
npm run electron:dev

# Build installer
npm run electron:build
```

## Project Structure

```
Wuthering-Waves-I.R.I.S.-Smart-Terminal/
├── agent_core/           # Core Agent engine
│   ├── core/            # Agent core implementation
│   ├── collaboration/   # Agent collaboration logic
│   ├── memrag/          # Memory enhancement system
│   ├── memory/          # Session memory management
│   ├── project_room/    # Meeting room logic
│   ├── providers/       # LLM providers
│   ├── settings/        # Settings management
│   ├── skills_registry/ # Skills registry
│   ├── tools/           # Built-in tools
│   ├── utils/           # Utility functions
│   └── workflow/        # Workflow engine
├── server/              # FastAPI server
│   └── routers/        # API route modules
├── desktop/             # Electron desktop application
│   └── src/
│       ├── components/  # React components
│       ├── pages/       # Pages
│       ├── hooks/       # Custom hooks
│       ├── contexts/    # React contexts
│       └── locales/     # Internationalization
├── tests/               # Test files
├── docs/                # Documentation
├── scripts/             # Startup scripts
└── config/             # Configuration files
```

## API Documentation

After starting the server, visit:
- Swagger UI: http://127.0.0.1:8765/docs
- ReDoc: http://127.0.0.1:8765/redoc

### Main API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/agents` | GET | Get agent list |
| `/api/agents` | POST | Create new agent |
| `/api/chat/chat` | POST | Chat with agent |
| `/api/collaboration/call` | POST | Start collaboration |
| `/api/meetings` | GET | Get meeting list |
| `/api/meetings` | POST | Create meeting |
| `/api/memory/search` | POST | Search memory |

## Configuration

Main configuration items (`.env`):

```env
# LLM Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# Server Configuration
HOST=127.0.0.1
PORT=8765

# Log Level
LOG_LEVEL=INFO
```

## Development Guide

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

This framework is licensed under the [AGPLv3](https://www.gnu.org/licenses/agpl-3.0.html) open source license.

- **Open Source Use**: Welcome to use this framework for open source development under AGPLv3 terms
- **Commercial Use**: For closed-source commercial use or commercial support, please contact: shenshengtiantang@outlook.com
- **Additional Terms**: If you modify and redistribute this framework, you must release the modified version as open source

### Third-Party Code

This framework uses the following open source components. Please note the license compatibility of each component:

| Component | License | Compatibility |
|-----------|---------|---------------|
| FastAPI | MIT | ✅ AGPLv3 Compatible |
| React | MIT | ✅ AGPLv3 Compatible |
| Electron | MIT | ✅ AGPLv3 Compatible |
| LangChain | MIT | ✅ AGPLv3 Compatible |
| Uvicorn | BSD | ✅ AGPLv3 Compatible |
| Pydantic | MIT | ✅ AGPLv3 Compatible |

> ⚠️ **Warning**: Avoid mixing GPL-incompatible libraries to prevent legal risks. For questions, please contact the email above.

See the [LICENSE](LICENSE) file for the full license text.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, high-performance web framework
- [React](https://reactjs.org/) - Component-based UI library
- [Electron](https://electronjs.org/) - Cross-platform desktop application framework
- [LangChain](https://www.langchain.com/) - LLM application development framework
