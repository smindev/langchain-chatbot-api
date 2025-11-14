# LangChain Chatbot API

A complete chatbot system using FastAPI + LangChain with FAISS vector search and a minimal React frontend.

- Backend: FastAPI, `/chat` streaming endpoint, `/ingest` for loading documents
- Vector store: FAISS (persisted locally in `storage/faiss`)
- LLMs: OpenAI (set `OPENAI_API_KEY`) or Ollama (`LLM_PROVIDER=ollama`)
- Frontend: Vite + React with streaming parsing
- Structure: `routes/`, `services/`, `schemas/`, `frontend/`

## Prereqs
- Python 3.10–3.12
- Node.js 18+
- One LLM provider:
  - OpenAI: export `OPENAI_API_KEY`
  - Ollama (local): install Ollama and pull a model (e.g. `ollama pull llama3.1`), then `export LLM_PROVIDER=ollama`

## Setup

### Backend
```
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Env options:
- `EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2`
- `FAISS_DIR=storage/faiss`
- `LLM_PROVIDER=openai|ollama` (auto picks `openai` if `OPENAI_API_KEY` is set)
- `OPENAI_MODEL=gpt-4o-mini` (or any)
- `OLLAMA_MODEL=llama3.1`

Health check:
```
curl http://localhost:8000/health
```

Ingest text (splits into chunks and indexes):
```
curl -X POST http://localhost:8000/ingest \
  -H 'content-type: application/json' \
  -d '{"texts": ["Your docs text here"]}'
```

Chat (non-stream):
```
curl -X POST http://localhost:8000/chat \
  -H 'content-type: application/json' \
  -d '{"messages":[{"role":"user","content":"Hello"}], "stream": false}'
```

### Frontend
```
cd frontend
npm i
npm run dev
```
Vite proxies requests to `http://localhost:8000` for `/chat`, `/ingest`, `/health`.

## Project Structure
- `main.py` FastAPI app
- `routes/` API routers (`chat.py`, `ingest.py`)
- `services/` vector store + RAG (`vectorstore.py`, `rag.py`)
- `schemas/` request/response pydantic models
- `frontend/` Vite + React app
- `storage/` FAISS index
- `data/` optional local data

## Notes
- First, ingest some text. Then chat. The RAG prompt only uses retrieved context.
- Ensure `storage/faiss` is writable for persistence.
