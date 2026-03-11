# AI Agent API

A FastAPI-based Personal Research Agent tbuilt in two versions — V1 from scratch with raw LangGraph, V2 with Google ADK and MCP tools.

The agent reasons step by step, decides which tools to use, executes them, and returns a final answer.

---
## Versions

| Version | Stack | Status |
|---|---|---|
| V1 | LangGraph + Ollama + manual tools | Complete |
| V2 | Google ADK + Groq + FastMCP + MCP protocol | Complete |

Both versions live on `main`. V1 endpoints at `/agent/`, V2 at `/v2/agent/`.

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

**V1** — LangGraph manually defines every node, edge, and state transition. Full control, maximum learning value.

**V2** — Google ADK handles the ReAct loop. Tools are exposed via a FastMCP server over MCP protocol. Agent connects to the MCP server and discovers tools dynamically.

---


## Tech Stack

### V1
| Tool | Purpose |
|---|---|
| FastAPI | API framework |
| LangGraph | Agent workflow orchestration |
| Ollama + Llama3.1 | Local LLM inference |
| Redis | Short-term session memory (TTL 24h) |
| PostgreSQL + SQLAlchemy | Persistent conversation storage |
| JWT | Authentication |
| Docker | PostgreSQL + Redis containers |
| pytest | 28 passing tests |


### V2
| Tool | Purpose |
|---|---|
| FastAPI | API framework |
| Google ADK | Agent orchestration framework |
| Groq + llama-3.3-70b-versatile | LLM inference |
| FastMCP | MCP server exposing tools |
| MCP Protocol | Tool discovery and execution |
| JWT | Authentication (shared with V1) |

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
├── agent/                  # V1 LangGraph agent
│   ├── graph.py            # LangGraph ReAct loop
│   ├── state.py            # agent state TypedDict
│   └── tools/
│       ├── calculator.py   # safe math evaluation (AST-based)
│       ├── web_search.py   # DuckDuckGo search
│       └── code_executor.py# safe Python execution (subprocess)
├── agent_v2/               # V2 Google ADK agent
│   ├── agent.py            # ADK LlmAgent + McpToolset
│   └── tools.py            # tool functions with docstrings
├── mcp_server/
│   └── server.py           # FastMCP server exposing tools
├── services/
│   ├── memory_service.py       # Redis session memory
│   ├── conversation_service.py # PostgreSQL operations
│   └── session_service.py      # session ID generation
├── models/
│   └── conversation.py     # SQLAlchemy models
├── schemas/
│   └── agent.py            # Pydantic schemas
├── routes/
│   ├── agent.py            # V1 endpoints
│   ├── agent_v2.py         # V2 endpoints
│   └── auth.py             # auth endpoints
└── tests/
    ├── test_tools.py
    ├── test_agent.py
    └── test_routes.py
```

---

## Setup

**Requirements:**
- Docker
- Python 3.12+
- Ollama with llama3.1 model (V1)
- Groq API key (V2)


```bash
git clone https://github.com/YOUR_USERNAME/ai-agent-api
cd ai-agent-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   
docker compose up db redis -d
alembic upgrade head
uvicorn main:app --reload
```



## API Endpoints

### Auth
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | NO | Create account |
| POST | `/auth/login` | NO | Get tokens |
| POST | `/auth/refresh` | NO | Refresh access token |
| POST | `/auth/logout` | YES | Invalidate refresh token |
| GET | `/auth/me` | YES | Current user info |

### V1 Agent
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/agent/run` | YES | Run agent with a question |
| GET | `/agent/history` | YES | Get conversation history |
| GET | `/health` | NO | Health check |

### V2 Agent (Google ADK + MCP)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/v2/agent/run` | YES | Run V2 agent |

---

## Example

**V1:**
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

**V2:**
```bash
curl -X POST http://localhost:8000/v2/agent/run \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "How is the weather in Baku?"}'
```
```json
{
  "answer": "Current weather in Baku: 11°C, cloudy, winds NNW 10-20 mph.",
  "steps": [],
  "session_id": "xyz-456"
}
```

---

## V1 vs V2 Comparison

| | V1 LangGraph | V2 Google ADK |
|---|---|---|
| ReAct loop | Written manually | Handled by framework |
| Tool registration | Manual TOOL_DESCRIPTIONS prompt | Function docstrings |
| Tool protocol | Direct function calls | MCP protocol via FastMCP |
| Tool discovery | Hardcoded in prompt | Dynamic via MCP server |
| LLM | Ollama llama3.1 (local) | Groq llama-3.3-70b (cloud) |
| Learning value | Understand internals | Understand abstractions |

---

## Memory Architecture (V1)

```
Active session   → Redis (TTL 24h)      key: session:{user_id}:{session_id}
Permanent store  → PostgreSQL           table: conversations
Fallback         → last 3 PostgreSQL conversations injected as context
```

---

## Running Tests

```bash
pytest tests/ -v
#28 tests passing
```

---

## Related Project

[RAG Document Assistant](https://github.com/Salman4M/RAG-Document-Assistant) — semantic document search with FastAPI, ChromaDB, and local LLMs.