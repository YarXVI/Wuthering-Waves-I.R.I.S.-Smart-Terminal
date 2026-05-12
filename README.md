# I.R.I.S. Agent Core v2

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.104-orange.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-AGPLv3-blue.svg" alt="License">
</p>

A production-ready agent framework built on onion architecture, featuring Lazy Context Materialization (LCM), Chinese Thinking Skill, and progressive skill disclosure.

## Core Capabilities

### 1. LCM (Lazy Context Materialization)
- **Chunk-based context storage** with LRU caching and JSONL persistence
- **Sentinel detection** for on-demand context loading via `[NEED_CHUNK:xxx]` markers
- **State machine driven** context injection (IDLE → GENERATING → WAITING_CHUNK → RESUMING → COMPLETED)
- **Content encoding layer** with pluggable encoders (Chinese Think, Identity, and extensible)

### 2. Chinese Thinking Skill
- **Native Chinese reasoning chains** with structured thinking output
- **Metaphor enhancement** using Chinese cognitive patterns
- **Dialectical thinking** support (thesis → antithesis → synthesis)
- **Dual-mode integration**: standalone skill for ReAct loops + LCM encoding plugin

### 3. Skill Engine
- **Progressive disclosure levels** (Level 0/1/2) based on trust and usage
- **Automatic skill distillation** from successful tool-call conversations
- **Feedback-driven evolution** with versioning and performance tracking
- **Keyword-based recommendation** engine for contextual skill matching

### 4. Personality System
- **Configurable agent personalities** with traits, values, behaviors, and boundaries
- **LLM parameter modulation** per personality (temperature, max_tokens, formality)
- **Built-in personas**: IRIS (friendly assistant), Pro (formal consultant), Muse (creative partner)
- **Dynamic system prompt generation** from personality configuration

### 5. Memory Management
- **Tiered memory architecture**: working, short-term, long-term
- **Agent-isolated storage** with JSONL persistence
- **User profile tracking** and importance-based retrieval
- **Keyword search** across memory entries

## Architecture

```
Onion Architecture:
  4. Interfaces       - FastAPI routers (agents, skills, memory, personality, usage)
  3. Application      - AgentService orchestration layer
  2. Domain           - Core business logic (AgentRuntime, Personality, ChineseThinking)
  1. Infrastructure   - Adapters (LCMEngine, SkillEngine, MemoryManager, ProviderRouter)
```

## Quick Start

### Installation

```bash
git clone https://github.com/YarXVI/Wuthering-Waves-I.R.I.S.-Smart-Terminal.git
cd Wuthering-Waves-I.R.I.S.-Smart-Terminal
pip install -r agent_core/requirements.txt
```

### Basic Usage

```python
from agent_core.v2 import AgentService, ProviderConfig, Chunk, LCMEngine

# Create service
service = AgentService()
service.provider.register(ProviderConfig(
    name="default",
    model="gpt-4o",
    api_key="sk-...",
))

# Add LCM chunk
service.lcm.store.add(Chunk(
    chunk_id="auth_handler",
    content="def login(): ...",
    summary="Authentication handler",
))

# Chat with agent
result = await service.chat(
    agent_id="iris",
    user_message="Review the authentication handler",
)
print(result.content)
```

### Enable Chinese Thinking

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

## Project Structure

```
agent_core/v2/
├── __init__.py              # Public API exports
├── domain/                  # Core business logic
│   ├── agent_runtime.py     # ReAct loop with LCM + Chinese Thinking
│   ├── chinese_thinking.py  # ChineseThinkingSkill + ChineseThinkEncoding
│   ├── execution_context.py # Immutable execution context
│   ├── execution_result.py  # Standardized result with tool calls
│   ├── lazy_context.py      # Lightweight shard-based LCM
│   └── personality.py       # Personality system with built-in personas
├── infrastructure/          # External adapters
│   ├── chunk_store.py       # Chunk storage with LRU cache
│   ├── content_encoding.py  # Pluggable encoding registry
│   ├── lcm_engine.py        # Full LCM protocol with state machine
│   ├── memory_manager.py    # Tiered memory management
│   ├── memory_v2.py         # Agent-isolated memory store
│   ├── provider_router.py   # LLM provider routing
│   ├── sentinel_detector.py # Sentinel marker detection
│   └── skill_engine.py      # Skill lifecycle management
├── application/             # Use case layer
│   └── agent_service.py     # High-level service API
└── interfaces/              # API layer
    ├── api_router.py        # Agent chat endpoints
    ├── memory_router.py     # Memory management endpoints
    ├── personality_router.py # Personality endpoints
    ├── skills_router.py     # Skill execution endpoints
    └── usage_router.py      # Usage tracking endpoints
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v2/agents/chat` | POST | Chat with an agent |
| `/v2/agents/register` | POST | Register a new agent |
| `/skills/list` | GET | List all skills |
| `/skills/{id}/execute` | POST | Execute a skill |
| `/memory/{agent_id}` | GET | Load agent memory |
| `/personality/list` | GET | List personalities |
| `/personality/{id}` | GET | Get personality details |

Full API documentation available at `/docs` when server is running.

## Configuration

Key environment variables (`.env`):

```env
# LLM Provider
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# Service
HOST=127.0.0.1
PORT=8765

# Logging
LOG_LEVEL=INFO
```

## License

This project is licensed under [AGPLv3](https://www.gnu.org/licenses/agpl-3.0.html).

- **Open source use**: Welcome under AGPLv3 terms
- **Commercial use**: Contact shenshengtiantang@outlook.com for licensing
- **Modification**: Modified versions must be open-sourced under AGPLv3

## Third-Party Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [LangChain](https://www.langchain.com/) - LLM application framework

> **Disclaimer**: The names "Wuthering Waves" and "I.R.I.S." referenced in this project are intellectual properties of Kuro Game. This project is for personal interest and fan creation only.
