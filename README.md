# AI Agent API

A FastAPI-based Personal Research Agent that reasons step by step, decides which tools to use, executes them, and returns a final answer with full reasoning trace.

Built from scratch without hiding complexity — raw LangGraph, Redis, PostgreSQL, and Ollama.

---

## How It Works

The agent uses the **ReAct pattern** (Reasoning + Acting):

```
User question
    ↓
Agent thinks: "What do I need?"
    ↓
Agent calls tool (web search, calculator, code executor)
    ↓
Agent sees result, thinks again
    ↓
Repeat until satisfied
    ↓
Final answer + full reasoning trace
```

---

## Features

- **ReAct agent loop** — LangGraph-based reasoning and acting cycle
- **Tool calling** — web search, calculator, safe code execution
- **Two-layer memory** — Redis for active sessions, PostgreSQL for permanent history
- **PostgreSQL context fallback** — when Redis session expires, last 3 conversations injected as context so LLM is never completely blank
- **JWT authentication** — register, login, refresh tokens, logout
- **Per-user isolation** — users only see their own conversations
- **Full reasoning trace** — every tool call and result returned in response

---

## Tech Stack

| Tool | Purpose |
|---|---|
| FastAPI | API framework |
| LangGraph | Agent workflow orchestration |
| Ollama + Llama3.1 | Local LLM inference |
| Redis | Short-term session memory (TTL 24h) |
| PostgreSQL + SQLAlchemy | Persistent conversation storage |
| JWT | Authentication |
| Docker | PostgreSQL + Redis containers |
| pytest | Tests |

---

## Project Structure

```
ai-agent-api/
├── main.py
├── core/
│   ├── config.py           # env vars
│   ├── database.py         # SQLAlchemy async engine
│   ├── security.py         # JWT auth
│   ├── limiter.py          # rate limiting
│   └── redis.py            # Redis connection
├── agent/
│   ├── graph.py            # LangGraph ReAct loop
│   ├── state.py            # agent state schema
│   └── tools/
│       ├── calculator.py   # safe math evaluation (AST-based)
│       ├── web_search.py   # DuckDuckGo search
│       └── code_executor.py # safe Python execution (subprocess)
├── services/
│   ├── memory_service.py       # Redis session memory
│   ├── conversation_service.py # PostgreSQL operations
│   └── session_service.py      # session ID generation
├── models/
│   └── conversation.py     # SQLAlchemy models
├── schemas/
│   └── agent.py            # Pydantic schemas
├── routes/
│   ├── agent.py            # agent endpoints
│   └── auth.py             # auth endpoints
└── tests/
    ├── test_tools.py
    ├── test_agent.py
    ├── test_memory.py
    └── test_routes.py
```

---

## Setup

**Requirements:**
- Docker
- Python 3.12+
- Ollama with llama3.1 model

**1 — Clone and create virtual environment:**
```bash
git clone https://github.com/YOUR_USERNAME/ai-agent-api
cd ai-agent-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**2 — Configure environment:**
```bash
cp .env.example .env
# edit .env with your settings
```

**3 — Start PostgreSQL and Redis:**
```bash
docker compose up -d
```

**4 — Run migrations:**
```bash
alembic upgrade head
```

**5 — Pull Ollama model:**
```bash
ollama pull llama3.1
```

**6 — Start the API:**
```bash
uvicorn main:app --reload
```

---

## API Endpoints

### Auth
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | NO | Create account |
| POST | `/auth/login` | NO | Get tokens |
| POST | `/auth/refresh` | NO | Refresh access token |
| POST | `/auth/logout` | YES | Invalidate refresh token |
| GET | `/auth/me` | YES | Current user info |

### Agent
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/agent/run` | YES | Run agent with a question |
| GET | `/agent/history` | YES | Get conversation history |
| GET | `/health` | NO | Health check |

---

## Example

**Request:**
```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the current gold price and what is 15% of that?"}'
```

**Response:**
```json
{
  "answer": "The current gold price is $2,340/oz. 15% of that is $351.",
  "steps": [
    {"tool": "web_search", "input": "gold price today", "output": "..."},
    {"tool": "calculator", "input": "2340 * 0.15", "output": "351.0"}
  ],
  "session_id": "abc-123"
}
```

---

## Tools

### calculator
Safe math evaluation using Python AST — never uses eval().
```
input:  "2340 * 0.15"
output: "351.0"
```

### web_search
DuckDuckGo search — free, no API key needed.
```
input:  "gold price today"
output: "Title: ...\nURL: ...\nSummary: ..."
```

### code_executor
Safe Python execution in subprocess with timeout and import restrictions.
```
input:  "print(sum([1,2,3,4,5]))"
output: "15"
```

---

## Memory Architecture

```
Active session (Redis, TTL 24h):
  key: session:{user_id}:{session_id}
  value: full message history as JSON

Permanent storage (PostgreSQL):
  table: conversations
  fields: user_id, session_id, question, answer, steps, created_at

Fallback (when Redis expires):
  load last 3 conversations from PostgreSQL
  inject as context so LLM is not completely blank
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Branches

| Branch | Description |
|---|---|
| `main` | V1 — LangGraph + manual tools (raw fundamentals) |
| `feature/adk-v2` | V2 — Google ADK + MCP tools (coming soon) |

---

## Related Project

[RAG Document Assistant](https://github.com/Salman4M/RAG-Document-Assistant) — semantic document search with FastAPI, ChromaDB, and local LLMs.