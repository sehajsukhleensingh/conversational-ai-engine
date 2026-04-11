# Lucein – Conversational AI Engine

Lucein is a stateful conversational AI system built using LangGraph, FastAPI, and Streamlit, designed to handle multi-threaded conversations with persistent memory and real-time streaming responses.

## Features

### Thread-based Conversations
- Each chat session is uniquely identified using a thread_id
- Supports switching between past conversations

### Persistent Memory
- Conversation history is stored using SQLite
- Powered by LangGraph Checkpointing

### Real-time Streaming Responses
- Token-by-token streaming using Server-Sent Events (SSE)
- Smooth UI updates with Streamlit

### Modular Architecture
- Clean separation between frontend, backend, and core logic

### API-based Communication
- FastAPI handles all backend communication

## Architecture Overview

```
Frontend (Streamlit)
        ↓
FastAPI Backend (/chat endpoint)
        ↓
LangGraph Execution Engine
        ↓
LLM (Google Gemini)
        ↓
SQLite (Persistent Memory)
        ↓
Streaming Response (SSE)
        ↓
Frontend Rendering
```

## Project Structure

```
backend/
├── api/
│   └── routes.py        # API endpoints
├── app/
│   ├── app.py           # App initialization
│   └── config.py        # Config management
├── core/
│   └── chatbot.py       # LangGraph logic
├── utils/
│   └── helper.py        # Utility functions
├── data/
│   └── convos.db        # SQLite database

frontend/
└── main.py              # Streamlit UI
```

## How It Works

1. User enters a message in the Streamlit UI
2. Request is sent to FastAPI /chat endpoint
3. LangGraph processes the input using a stateful graph
4. Conversation state is saved via SQLite checkpointer
5. LLM generates response (streamed token-by-token)
6. Response is sent back and rendered live

## Memory System

Uses LangGraph Checkpointing

Each conversation is tied to a unique thread_id

Enables:
- Persistent chat history
- Multi-session handling
- Context-aware responses

## Tech Stack

- Frontend: Streamlit
- Backend: FastAPI
- LLM Framework: LangGraph + LangChain
- Model: Google Gemini (via langchain_google_genai)
- Database: SQLite
- Streaming: Server-Sent Events (SSE)

## Running the Project

1. Start Backend
   ```
   uvicorn backend.app.app:app --reload
   ```

2. Start Frontend
   ```
   streamlit run frontend/main.py
   ```

## Future Improvements

- Tool calling integration
- Retrieval-Augmented Generation (RAG)
- LangSmith logging & observability
- Performance optimizations

## Author

Built by Sehaj Sukhleen Singh
