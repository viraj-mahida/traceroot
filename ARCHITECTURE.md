## 🎯 **What is TraceRoot?**

**TraceRoot** is an AI-powered debugging and observability platform that helps engineers debug production issues **10× faster**. It's a Y Combinator-backed project (S25) that combines distributed tracing, logging, and AI agents to perform root cause analysis on production bugs.

Think of it as an intelligent debugging assistant that analyzes your application's traces and logs, understands your code context, and can even create GitHub issues and PRs automatically.

---

## 🏗️ **High-Level Architecture**

The codebase consists of **3 main components**:

### 1. **Backend API** (`/rest`)
- **Tech Stack**: FastAPI + Python 3.10+
- **Purpose**: REST API server that handles trace/log ingestion, AI agent orchestration, and data persistence
- **Entry Point**: `rest/main.py` (runs on port 8000)

### 2. **Frontend UI** (`/ui`)
- **Tech Stack**: Next.js 15 + React 19 + TypeScript
- **Purpose**: Web interface for viewing traces, chatting with AI agents, and managing integrations
- **Entry Point**: UI runs on port 3000

### 3. **AI Agent Framework** (`/rest/agent`)
- **Purpose**: Intelligent agents that analyze traces/logs using LLMs (OpenAI, Anthropic, etc.)
- **Core Features**: Context engineering, feature filtering, code analysis

---

## 📂 **Key Directory Structure**

```
traceroot/
├── rest/                      # Backend API (Python/FastAPI)
│   ├── main.py               # API entry point
│   ├── app.py                # FastAPI app configuration
│   ├── agent/                # 🤖 AI Agent Framework
│   │   ├── agent.py          # Core agent logic
│   │   ├── chat.py           # Chat interface
│   │   ├── context/          # Context engineering (tree construction)
│   │   ├── filter/           # LLM-based feature/structure filtering
│   │   ├── summarizer/       # Output summarization
│   │   ├── tools/            # GitHub issue/PR creation tools
│   │   └── prompts/          # AI prompts
│   ├── routers/              # API endpoints
│   │   ├── explore.py        # Main trace exploration & chat API
│   │   ├── integrate.py      # Integration management (GitHub, etc.)
│   │   ├── auth/             # Authentication
│   │   └── verify.py         # SDK verification
│   ├── service/              # External service clients
│   │   ├── aws_client.py     # AWS X-Ray integration
│   │   ├── jaeger_client.py  # Jaeger tracing backend
│   │   └── tencent_client.py # Tencent Cloud integration
│   ├── dao/                  # Data Access Objects
│   │   ├── mongodb_dao.py    # MongoDB for chat/metadata
│   │   └── sqlite_dao.py     # SQLite for local storage
│   └── config/               # Configuration models (Pydantic)
│
├── ui/                       # Frontend (Next.js)
│   ├── src/
│   │   ├── app/              # Next.js app router
│   │   │   ├── explore/      # Trace exploration page
│   │   │   ├── integrate/    # Integration settings
│   │   │   ├── settings/     # User settings
│   │   │   └── api/          # API routes (proxy to backend)
│   │   ├── components/       # React components (85 files!)
│   │   └── models/           # TypeScript data models
│
├── examples/                 # Usage examples
│   ├── python/               # Python SDK examples
│   ├── typescript/           # TypeScript SDK examples
│   └── distributed_services/ # Multi-agent demo app
│
├── docs/                     # Documentation
├── docker/                   # Docker deployment configs
└── test/                     # Unit tests
```

---

## 🧠 **The AI Agent Framework** (Core Innovation)

The agent framework (`/rest/agent`) is the heart of TraceRoot. Here's how it works:

### **Context Engineering Pipeline**:
1. **Data Mixer**: Combines source code (optional), traces, and logs
2. **Heterogeneous Tree Constructor**: Builds a tree with span nodes (traces) and log nodes
3. **Feature Filter**: LLM filters out irrelevant attributes from nodes
4. **Structure Filter**: LLM prunes unnecessary nodes from the tree
5. **Hierarchical Encoding**: Encodes the tree for LLM consumption

### **Key Agent Components**:
- **`agent.py`**: Main agent orchestration
- **`chat.py`**: Chat interface for user interaction
- **`context/tree.py`**: Builds heterogeneous trees from traces/logs
- **`filter/`**: LLM-based filtering to reduce context size
- **`summarizer/`**: Summarizes agent outputs for users
- **`tools/`**: GitHub integration (create issues/PRs)

---

## 🔌 **API Endpoints** (`/rest/routers`)

### **Explore Router** (`explore.py`):
- `POST /v1/explore/list_trace` - List all traces
- `POST /v1/explore/get_log_by_trace_id` - Get logs for a trace
- `POST /v1/explore/code` - Analyze code context
- `POST /v1/explore/chat` - Chat with AI agent
- `GET /v1/explore/chat_history` - Get chat history

### **Integrate Router** (`integrate.py`):
- Manage GitHub PAT tokens
- Configure integrations (Notion, Slack, etc.)

### **Auth Router** (`auth/`):
- Authentication via Clerk (JWT-based)

---

## 🛠️ **Tech Stack**

### **Backend**:
- **FastAPI**: Web framework
- **OpenAI**: LLM integration
- **PyGitHub**: GitHub API
- **MongoDB**: Chat history storage
- **SQLite**: Local data storage
- **boto3**: AWS X-Ray client
- **SlowAPI**: Rate limiting

### **Frontend**:
- **Next.js 15**: React framework
- **Clerk**: Authentication
- **Radix UI**: Component library
- **Tailwind CSS**: Styling
- **Recharts**: Data visualization
- **React Markdown**: Markdown rendering

---

## 🚀 **How It Works** (User Flow)

1. **Instrumentation**: User adds TraceRoot SDK to their app (Python/TypeScript/Java)
2. **Data Collection**: SDK sends traces/logs to TraceRoot backend
3. **Storage**: Data stored in AWS X-Ray, Jaeger, or Tencent Cloud
4. **Exploration**: User views traces in the UI
5. **AI Analysis**: User chats with AI agent about bugs
6. **Context Engineering**: Agent builds heterogeneous tree, filters irrelevant data
7. **Root Cause Analysis**: LLM analyzes filtered context
8. **Action**: Agent can create GitHub issues/PRs automatically

---

## 🐳 **Deployment**

- **Docker**: Single-command deployment via `bin/deploy-starter`
- **Cloud**: TraceRoot Cloud (hosted version with 7-day trial)
- **Self-hosted**: Manual setup via `DEVELOPMENT.md`

---

## 📦 **Key Dependencies**

```python
# Backend (pyproject.toml)
fastapi, uvicorn, openai, pymongo, boto3, PyGithub, stripe

# Frontend (ui/package.json)  
next, react, @clerk/nextjs, ai (Vercel AI SDK), recharts
```

---

## 🔑 **Key Files to Understand**

1. **`rest/app.py`**: FastAPI app setup, CORS, router registration
2. **`rest/routers/explore.py`**: Main API logic for traces/logs/chat
3. **`rest/agent/agent.py`**: Core AI agent orchestration
4. **`rest/agent/context/tree.py`**: Heterogeneous tree construction
5. **`ui/src/app/explore/page.tsx`**: Main UI page for trace exploration

---

## 💡 **Unique Features**

1. **Heterogeneous Tree**: Combines traces (spans) and logs into a single tree structure
2. **LLM-based Filtering**: Reduces context size by filtering irrelevant data
3. **Code-aware**: Can analyze source code alongside traces/logs
4. **GitHub Integration**: Automatically creates issues/PRs
5. **Multi-provider**: Supports AWS X-Ray, Jaeger, Tencent Cloud

---

## 🎓 **Getting Started as a Developer**

1. **Read**: `README.md` → `CONTRIBUTING.md` → `docs/quickstart.mdx`
2. **Explore**: Run the multi-agent example in `examples/distributed_services/`
3. **Backend**: Start with `rest/main.py` → `rest/app.py` → `rest/routers/explore.py`
4. **Agent**: Dive into `rest/agent/README.md` and `rest/agent/agent.py`
5. **Frontend**: Check `ui/src/app/explore/page.tsx`

---

This is a sophisticated observability platform with cutting-edge AI integration. The codebase is well-structured with clear separation between API, agent framework, and UI. The AI agent's context engineering approach (heterogeneous trees + LLM filtering) is the key innovation that makes debugging more efficient.