# 🧠 AI Research Platform

**Production-ready AI Research Agent** with multi-agent orchestration, hybrid RAG, hallucination detection, knowledge graph generation, and professional report export.

Rivals ChatGPT Deep Research, Perplexity AI, and NotebookLM.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Agent Pipeline** | LangGraph-powered orchestration: Planner → Searcher → Synthesizer → Verifier → Citation → Knowledge Graph → Report |
| **Hybrid RAG** | Dense (semantic) + Sparse (BM25) retrieval with Reciprocal Rank Fusion |
| **Hallucination Detection** | Classifies claims as Supported / Weak / Unsupported / Hallucination with confidence scores |
| **Deep Research Mode** | 4 depth levels (Quick → Academic) with recursive search loops |
| **Multi-LLM Support** | OpenRouter, OpenAI, Anthropic, Gemini, Groq, Ollama with automatic failover |
| **Vector DB Abstraction** | Switch between Local, ChromaDB, FAISS, Pinecone, Weaviate |
| **Citation System** | APA, IEEE, MLA, Chicago formatting with source reliability scoring (1-100) |
| **Knowledge Graphs** | LLM-extracted entity/relationship graphs in React Flow format |
| **Document Intelligence** | Upload & index PDF, DOCX, PPTX, TXT, CSV, Markdown |
| **Web Search** | Tavily, Serper, DuckDuckGo (free fallback) |
| **Professional Reports** | Structured academic reports with export capabilities |
| **Analytics Dashboard** | Token usage, costs, latencies, confidence trends |
| **Authentication** | JWT with bcrypt password hashing |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                         │
│   React + TypeScript + Tailwind + Framer Motion + React Flow │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────────┐
│                    Backend (FastAPI)                          │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ Planner  │→│ Searcher  │→│Synthesizer│→│  Verifier   │  │
│  └──────────┘  └──────────┘  └──────────┘  └─────┬──────┘  │
│                                                    │         │
│       ┌─── (loop if ungrounded + budget) ─────────┘         │
│       ▼                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Citation  │→│ KG Builder│→│Report Gen │→ Response        │
│  └──────────┘  └──────────┘  └──────────┘                  │
│                                                              │
│  Services: LLM Manager │ Vector DB │ Embeddings │ Reranker  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- At least one LLM API key (OpenRouter recommended)

### 1. Clone & Configure

```bash
git clone https://github.com/Devaraj0007/research-agent.git
cd research-agent
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Backend Setup

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

Backend runs at **http://localhost:8000** (API docs at /docs)

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:3000**

### 4. Docker (Alternative)

```bash
docker-compose up --build
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register user |
| POST | `/api/v1/auth/token` | Login (JWT) |
| GET | `/api/v1/auth/me` | Current user |
| POST | `/api/v1/projects` | Create workspace |
| GET | `/api/v1/projects` | List workspaces |
| POST | `/api/v1/upload` | Upload & index document |
| POST | `/api/v1/research` | Run research pipeline |
| POST | `/api/v1/chat` | Simple chat |
| POST | `/api/v1/search` | Hybrid search |
| POST | `/api/v1/compare` | Compare entities |
| GET | `/api/v1/analytics` | Dashboard metrics |
| GET | `/api/v1/models` | Available models |
| GET | `/api/v1/reports` | List reports |
| GET | `/api/v1/reports/:id` | Get report |
| GET | `/api/v1/knowledge-graph/:id` | Get graph data |
| GET | `/health` | Health check |

---

## 🔧 Configuration

All settings are configurable via environment variables (see `.env.example`):

- **LLM Providers**: `DEFAULT_LLM_PROVIDER`, `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, etc.
- **Vector DB**: `VECTOR_DB_TYPE` (local / chroma / faiss)
- **Embeddings**: `EMBEDDING_MODEL` (all-MiniLM-L6-v2, BAAI/bge-large-en, etc.)
- **Reranking**: `RERANKER_TYPE` (hybrid / cohere / cross-encoder / bm25)
- **Web Search**: `TAVILY_API_KEY`, `SERPER_API_KEY`, or DuckDuckGo (free)

---

## 🧪 Testing

```bash
cd backend
python -m pytest tests/ -v
```

---

## 📊 Tech Stack

**Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS, Framer Motion, React Flow, Chart.js, Zustand, TanStack Query

**Backend**: Python 3.11, FastAPI, LangGraph, LangChain, SQLAlchemy, Pydantic v2, Redis, Celery

**AI**: OpenRouter, OpenAI, Anthropic, Gemini, Groq, Ollama (with automatic failover)

**Vector DBs**: Local (numpy), ChromaDB, FAISS, Pinecone, Weaviate

**Embeddings**: SentenceTransformers, OpenAI Embeddings, BGE, E5, Nomic

**Reranking**: BM25, Cohere Rerank, CrossEncoder, Hybrid RRF

---

## 📚 Documentation

- 🏛️ [Architecture Overview](docs/architecture.md)
- 🛠️ [Development Setup](docs/development.md)
- 🚀 [Deployment Guide](docs/deployment.md)
- ⚡ [Latency & Speed Optimization Guide](docs/latency_optimization.md)

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.
