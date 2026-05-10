# Misl – Agentic Conversational AI Engine

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-Enabled-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-green.svg)
![LangSmith](https://img.shields.io/badge/LangSmith-Observability-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg)
![OpenAI](https://img.shields.io/badge/GPT--4o--mini-LLM-412991.svg)
![FAISS](https://img.shields.io/badge/FAISS-VectorDB-blueviolet)
![SQLite](https://img.shields.io/badge/SQLite-Stateful-lightgrey.svg)
![MCP](https://img.shields.io/badge/MCP-Integrated-red.svg)
![SSE](https://img.shields.io/badge/Streaming-SSE-orange.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)

Misl is a stateful, multi-tool agentic AI system built using LangGraph, FastAPI, and Streamlit. It supports multi-threaded conversations with persistent memory, real-time streaming responses, and an extensible tool ecosystem including MCP integration, web search, live exchange rates, and a RAG pipeline for document Q&A.

---

## Features

### Agentic Tool Routing
- LLM autonomously decides which tool to call based on user intent
- Tools available: MCP client tools, DuckDuckGo web search, live exchange rate API, RAG document retrieval
- Built on LangGraph's `ToolNode` with conditional edge routing

### MCP Integration
- Connects to an MCP server via client and pulls tools dynamically at runtime
- MCP tools are injected into the LangGraph tool node alongside custom tools

### RAG Pipeline
- PDF ingestion using PyPDFLoader with RecursiveCharacterTextSplitter (chunk size 1200, overlap 420)
- Embeddings via OpenAI `text-embedding-3-small`, stored in a FAISS vector store
- Semantic similarity retrieval (top-k=4) exposed as an LLM-callable tool
- Thread-scoped file uploads via `/upload_file` endpoint

### Thread-based Conversations
- Each session is uniquely identified by a `thread_id`
- Supports switching between and resuming past conversations

### Persistent Memory
- Full conversation state saved using LangGraph's `AsyncSqliteSaver` checkpointer
- SQLite backend — no external DB required

### Real-time Streaming Responses
- Token-by-token streaming via Server-Sent Events (SSE)
- Disconnect detection inside the generator to handle client drops gracefully

### Modular Architecture
- Clean separation between API layer, core graph logic, tools, and frontend

---

## Architecture Overview

```
Frontend (Streamlit)
        ↓
FastAPI Backend
        ↓
LangGraph Agentic Graph
   ├── chat_node (LLM with bound tools)
   └── tool_node (MCP tools, search, exchange rate, RAG)
        ↓
AsyncSqliteSaver (Persistent Checkpointing)
        ↓
Streaming Response (SSE)
        ↓
Frontend Rendering
```

---

## Project Structure

```
backend/
├── api/
│   └── routes.py              # FastAPI endpoints (chat, history, upload, health)
├── app/
│   ├── app.py                 # App initialization and startup
│   └── config.py              # Config management
├── core/
│   └── chatbot.py             # LangGraph graph definition and agentic loop
├── utils/
│   ├── tools.py               # Custom tools: RAG, exchange rate, search
│   └── mcp.py                 # MCP client setup
├── schema_models/
│   └── request.py             # Pydantic request models
├── data/
│   ├── convos.db              # SQLite checkpoint database
│   ├── uploads/               # Thread-scoped uploaded files
│   └── vector_store/          # FAISS vector stores per thread

frontend/
└── main.py                    # Streamlit UI
```

---

## How It Works

1. User sends a message via Streamlit UI
2. Request hits FastAPI `/chat` with a `thread_id` config
3. LangGraph routes through `chat_node` — LLM decides if a tool call is needed
4. If tool call: `tool_node` executes (search / exchange rate / MCP / RAG), result fed back to LLM
5. LLM produces a clean final response (raw tool output is never surfaced)
6. Response streamed token-by-token via SSE back to frontend
7. Full conversation state saved to SQLite via checkpointer

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check bot readiness |
| POST | `/chat` | Send a message, returns SSE stream |
| GET | `/chat-history` | Retrieve full conversation history for a thread |
| POST | `/upload_file` | Upload a PDF file scoped to a thread (for RAG) |

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | Streamlit |
| Backend | FastAPI |
| Agentic Framework | LangGraph + LangChain |
| LLM | GPT-4o-mini (OpenAI-compatible endpoint) |
| Tools | DuckDuckGo Search, Exchange Rate API, MCP, FAISS RAG |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector Store | FAISS |
| Memory / State | AsyncSqliteSaver (SQLite) |
| Streaming | Server-Sent Events (SSE) |

---

## Running the Project

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up environment variables
```bash
EXCHANGE_RATE_API=your_key_here
OPENAI_API_KEY=your_key_here
```

### 3. Start Backend
```bash
uvicorn backend.app.app:app --reload
```

### 4. Start Frontend
```bash
streamlit run frontend/main.py
```

---

## Roadmap

- [ ] Frontend polish and thread management UI
- [ ] Add more MCP tool integrations

---

## Author

Built by Sehaj Sukhleen Singh