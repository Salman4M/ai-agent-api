# Multi-Tool AI Agent API — plan.md

## What We're Building

A FastAPI app where a user sends a complex question and an AI agent reasons
step by step, decides which tools to use, executes them, and returns a final
answer with full reasoning trace.

Built without hiding complexity — raw LangGraph, Redis, WebSockets, and Ollama.
Framed as a **Personal Research Agent** (practical, demonstrates real AI engineering skills).

Two branches:
- `main` — V1 LangGraph + manual tools (understand fundamentals)
- `feature/adk-v2` — V2 Google ADK + MCP tools (industry approach)

---

## What Makes This Different From RAG Project

| Feature | RAG Project | Agent Project |
|---|---|---|
| Core pattern | Retrieve → Answer | Reason → Act → Answer |
| Memory | PostgreSQL only | Redis (short-term) + PostgreSQL (long-term) |
| Real time | SSE upload progress | WebSocket agent thoughts |
| Background tasks | None | Celery |
| Tools | None | Web search, calculator, code execution, RAG |
| New AI concept | RAG pipeline | Agent loop, tool use, function calling |
| Orchestration | Manual | LangGraph |
| V2 framework | — | Google ADK + MCP |

---

## Tech Stack

| Tool | Purpose |
|---|---|
| FastAPI | API framework |
| LangGraph | Agent workflow orchestration |
| Redis | Short-term session memory + Celery broker |
| PostgreSQL + SQLAlchemy | Persistent conversation storage |
| Ollama + Qwen2.5 / Llama3.1 | Local LLM inference |
| fastembed | Embeddings (reuse from RAG project) |
| WebSockets | Stream agent reasoning in real time |
| Celery | Background task processing |
| JWT | Authentication (reuse from RAG project) |
| slowapi | Per-user rate limiting |
| Docker | Containerization |
| pytest | Tests |

---

## Project Structure

```
ai-agent-api/
├── main.py
├── .env
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── plan.md
│
├── core/
│   ├── config.py               # env vars
│   ├── database.py             # SQLAlchemy async engine
│   ├── security.py             # JWT auth
│   ├── limiter.py              # rate limiting
│   └── redis.py                # Redis connection
│
├── agent/
│   ├── graph.py                # LangGraph agent definition
│   ├── state.py                # agent state schema
│   └── tools/
│       ├── __init__.py
│       ├── web_search.py       # search the web (DuckDuckGo)
│       ├── calculator.py       # evaluate math expressions safely
│       ├── code_executor.py    # run Python safely in subprocess
│       └── rag_tool.py         # query uploaded documents (V2)
│
├── services/
│   ├── memory_service.py       # Redis short-term + PostgreSQL long-term
│   ├── session_service.py      # session management
│   └── celery_app.py           # Celery configuration (V2)
│
├── models/
│   └── conversation.py         # SQLAlchemy models
│
├── schemas/
│   └── agent.py                # Pydantic request/response schemas
│
├── routes/
│   ├── agent.py                # agent REST endpoints
│   ├── auth.py                 # auth endpoints
│   └── ws.py                   # WebSocket endpoint (V2)
│
└── tests/
    ├── test_tools.py
    ├── test_agent.py
    ├── test_memory.py
    └── test_routes.py
```

---

## How The Agent Works — ReAct Loop

ReAct = Reasoning + Acting. The agent thinks before it acts.

```
User question arrives
    ↓
Agent thinks: "What do I need to answer this?"
    ↓
Agent decides: "I need tool X"
    ↓
Agent calls tool X
    ↓
Agent gets result
    ↓
Agent thinks: "Do I have enough to answer?"
    ↓
    If no → pick next tool → repeat
    If yes → generate final answer
    ↓
Return answer + full reasoning trace
```

LangGraph models this as a graph:

```
[START] → [reason] → [call_tool] → [reason] → [call_tool] → [answer] → [END]
                          ↑___________________________|
                     (loop until agent is satisfied or MAX_STEPS reached)
```

---

## Endpoints

### POST /agent/run
Send a question, get a reasoned answer. Blocking — waits for full response.

**Request:**
```json
{
  "question": "What is the current price of gold and what is 15% of that?"
}
```

**Response:**
```json
{
  "answer": "The current price of gold is $2,340/oz. 15% of that is $351.",
  "steps": [
    {"tool": "web_search", "input": "gold price today", "output": "..."},
    {"tool": "calculator", "input": "2340 * 0.15", "output": "351"}
  ],
  "session_id": "abc-123"
}
```

---

### GET /agent/history
Get conversation history for current user.

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "abc-123",
      "question": "What is gold price...",
      "answer": "...",
      "created_at": "2026-03-03T12:00:00"
    }
  ]
}
```

---

### GET /health
```json
{ "status": "ok" }
```

---

### Auth endpoints (reused from RAG project)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | ❌ | Create account |
| POST | `/auth/login` | ❌ | Get tokens |
| POST | `/auth/refresh` | ❌ | Refresh access token |
| POST | `/auth/logout` | ✅ | Invalidate refresh token |
| GET | `/auth/me` | ✅ | Current user info |

---

## Agent State Schema

LangGraph passes this state between every node in the graph:

```python
class AgentState(TypedDict):
    question: str               # original user question
    messages: list[dict]        # full conversation so far
    tool_calls: list[dict]      # tools called this run + their outputs
    final_answer: str | None    # set when agent is done
    user_id: int                # for per-user memory isolation
    session_id: str             # for Redis session key
    steps: int                  # current step count — stop at MAX_STEPS
```

---

## Tools — V1

### web_search
Searches the internet using DuckDuckGo — free, no API key needed.

```python
def web_search(query: str) -> str:
    # call DuckDuckGo search API
    # return top 3 results as formatted string
    # format: "Title: ...\nURL: ...\nSummary: ...\n\n"
```

### calculator
Safely evaluates mathematical expressions. Never uses eval().

```python
def calculator(expression: str) -> str:
    # use ast module to parse and evaluate safely
    # only allow: +, -, *, /, **, ()
    # reject anything that isn't a math expression
    # return result as string or error message
```

### code_executor
Runs Python code safely in a subprocess with timeout and restrictions.

```python
def code_executor(code: str) -> str:
    # run in subprocess with 10 second timeout
    # restricted: no os, no sys, no file access, no network
    # capture stdout and stderr
    # return output or error message
```

---

## Memory Architecture

Two layers — same pattern as production AI systems:

**Redis — short-term (session memory):**
- Last N messages in current session
- Key: session:{user_id}:{session_id}
- TTL: 24 hours — auto-expires
- Fast in-memory access

**PostgreSQL — long-term (persistent history):**
- All conversations ever stored
- Loaded on demand for /agent/history
- Survives server restarts

```python
# Redis key structure
f"session:{user_id}:{session_id}"  # → last 10 messages as JSON

# PostgreSQL table
class Conversation(Base):
    id: int
    user_id: int
    session_id: str
    question: str
    answer: str
    steps: list[dict]   # JSON — tool calls and outputs
    created_at: datetime
```

---

## Config (.env)

```
# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1

# Database
DATABASE_URL=postgresql+asyncpg://agent_user:agent_pass@localhost:5432/agent_db

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Agent
MAX_AGENT_STEPS=10
SESSION_TTL_SECONDS=86400
```

---

## Tests

### test_tools.py
- calculator returns correct result for valid expression
- calculator rejects unsafe input (os.system, eval, etc.)
- web_search returns non-empty string
- code_executor runs simple print statement
- code_executor blocks import of os module
- code_executor times out after 10 seconds

### test_agent.py
- agent picks web_search for current events question
- agent picks calculator for math question
- agent stops after MAX_AGENT_STEPS
- agent returns steps list in response

### test_memory.py
- Redis stores session and retrieves it correctly
- Redis key expires after TTL
- PostgreSQL saves conversation after agent run
- GET /agent/history returns only current user sessions

### test_routes.py
- POST /agent/run returns 200 with answer and steps
- POST /agent/run returns 401 without token
- GET /agent/history returns 401 without token
- GET /health returns 200

---

## Implementation Phases

- [ ] **Phase 1 — Project setup**
  - [ ] 1.1 Create GitHub repo — ai-agent-api
  - [ ] 1.2 Create folder structure
  - [ ] 1.3 Write core/config.py
  - [ ] 1.4 Write requirements.txt
  - [ ] 1.5 Write .env and .env.example
  - [ ] 1.6 Write docker-compose.yml — PostgreSQL + Redis
  - [ ] 1.7 First commit — empty scaffold

- [ ] **Phase 2 — Auth**
  - [ ] 2.1 Copy core/security.py from RAG project
  - [ ] 2.2 Copy core/database.py from RAG project
  - [ ] 2.3 Write models/conversation.py — User + RefreshToken + Conversation
  - [ ] 2.4 Copy routes/auth.py from RAG project
  - [ ] 2.5 Run Alembic migrations
  - [ ] 2.6 Test register + login

- [ ] **Phase 3 — Tools**
  - [ ] 3.1 Write agent/tools/calculator.py
  - [ ] 3.2 Write agent/tools/web_search.py
  - [ ] 3.3 Write agent/tools/code_executor.py
  - [ ] 3.4 Test each tool independently in isolation

- [ ] **Phase 4 — Agent Core**
  - [ ] 4.1 Write agent/state.py — AgentState TypedDict
  - [ ] 4.2 Write agent/graph.py — LangGraph ReAct loop
  - [ ] 4.3 Connect tools to agent graph
  - [ ] 4.4 Test agent with simple questions manually
  - [ ] 4.5 Test agent stops at MAX_AGENT_STEPS

- [ ] **Phase 5 — Memory**
  - [ ] 5.1 Write core/redis.py — Redis connection
  - [ ] 5.2 Write services/memory_service.py — Redis get/set/expire
  - [ ] 5.3 Write PostgreSQL conversation save after each agent run
  - [ ] 5.4 Inject Redis session history into agent on each request

- [ ] **Phase 6 — API Routes**
  - [ ] 6.1 Write schemas/agent.py — request/response Pydantic models
  - [ ] 6.2 Write routes/agent.py — POST /agent/run
  - [ ] 6.3 Write routes/agent.py — GET /agent/history
  - [ ] 6.4 Write GET /health
  - [ ] 6.5 Wire everything in main.py
  - [ ] 6.6 Test full flow: login → ask question → get answer with steps

- [ ] **Phase 7 — Tests**
  - [ ] 7.1 Write tests/test_tools.py
  - [ ] 7.2 Write tests/test_agent.py
  - [ ] 7.3 Write tests/test_memory.py
  - [ ] 7.4 Write tests/test_routes.py

- [ ] **Phase 8 — Docker + GitHub**
  - [ ] 8.1 Write Dockerfile
  - [ ] 8.2 Complete docker-compose.yml with app service
  - [ ] 8.3 Write README.md
  - [ ] 8.4 Final commit + push

---

## What We're NOT Building in V1

- No WebSocket streaming — V2
- No Celery background tasks — V2
- No RAG tool — V2
- No MCP integration — V2
- No rate limiting — V3
- No multi-agent system — V3
- No frontend — future

---

## V2 Features (feature/adk-v2 branch)

### V2.1 — WebSocket Streaming
Stream agent reasoning steps in real time as they happen.
Client sees the agent thinking, not just the final answer.

### V2.2 — Google ADK Refactor
Rewrite agent using Google ADK instead of raw LangGraph.
Compare the two approaches side by side — what ADK abstracts, what it hides.

### V2.3 — MCP Tool Integration
Connect to existing MCP servers instead of building tools manually.
Two tools replace everything: search() to discover, execute() to act.

MCP servers to connect:
- Web search MCP server
- File system MCP server
- PostgreSQL MCP server

### V2.4 — RAG Tool
Add document querying as an agent tool.
Reuses ChromaDB + fastembed from RAG project.
Agent decides when to search documents vs web vs calculate.

### V2.5 — Celery Background Tasks
Heavy tool calls run as Celery tasks.
Redis as Celery broker and result backend.

---

## V3 Features (future)

### V3.1 — Multi-Agent System
Multiple specialized agents collaborate under one orchestrator.

### V3.2 — Rate Limiting
Per-user limits. Reuse slowapi from RAG project.

### V3.3 — Agent Memory Extraction
Agent automatically extracts and remembers facts about user across sessions.

---

## Key Differences: LangGraph vs Google ADK

| | LangGraph (V1 — main) | Google ADK (V2 — feature/adk-v2) |
|---|---|---|
| Control | Full — you define every node and edge | High level — framework handles routing |
| Complexity | Higher — more code | Lower — less code |
| Flexibility | Maximum | Opinionated |
| Learning value | Understand internals | Understand abstractions |
| MCP support | Manual | Built-in |
| Model support | Any via Ollama | Optimized for Gemini, model-agnostic |
| Community | Large, mature | New, growing fast (Google-backed) |