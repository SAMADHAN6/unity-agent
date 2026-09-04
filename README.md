# 🎮 Unity Game Dev AI Agent

An AI-powered assistant for Unity game development. Ask questions about C# scripting, physics, animation, performance optimization, rendering pipelines, and more — with a RAG pipeline backed by Unity documentation.

---

## Project Structure

```
unity-agent/
├── backend/
│   ├── agent/
│   │   ├── agent.py        # Core agent with memory & LLM
│   │   ├── tools.py        # Agent tools (search, error explain, code gen)
│   │   └── __init__.py
│   ├── knowledge/
│   │   ├── rag.py          # RAG pipeline (Chroma vector store)
│   │   └── __init__.py
│   ├── main.py             # FastAPI server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Chat UI
│   ├── style.css           # Dark theme styles
│   └── app.js              # API calls, message rendering
├── data/
│   └── docs/               # Unity knowledge base (.txt files)
├── .env.example            # Environment variable template
├── .gitignore
└── README.md
```

---

## Quick Start

### 1. Clone & set up environment

```bash
cd unity-agent
cp .env.example .env
```

Open `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-key-here
```

### 2. Install Python dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Build the knowledge base

Place any Unity documentation `.txt` files inside `data/docs/`, then run:

```bash
cd backend
python -c "from knowledge.rag import build_knowledge_base; build_knowledge_base()"
```

Two starter docs are already included (`unity_basics.txt`, `unity_optimization.txt`).

### 4. Start the backend server

```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Open the frontend

Open `frontend/index.html` directly in your browser. No build step needed.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/chat` | Send a message, get a reply |
| POST | `/build-kb` | Rebuild the knowledge base |
| DELETE | `/clear-history` | Reset conversation memory |

### Example chat request

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I implement object pooling in Unity?"}'
```

---

## Agent Tools

| Tool | What it does |
|------|-------------|
| `search_docs` | Semantic search over indexed Unity docs |
| `explain_error` | Parses Unity console errors and suggests fixes |
| `generate_csharp_template` | Returns ready-to-use C# script templates |

---

## Adding More Knowledge

Drop `.txt` files into `data/docs/` and rebuild the knowledge base:

```bash
curl -X POST http://127.0.0.1:8000/build-kb
```

Good sources to add:
- Unity Manual pages (copy-paste as `.txt`)
- Unity API Reference sections
- Unity Learn articles
- Your own team's coding standards

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | GPT-4o (OpenAI) |
| Agent Framework | LangChain |
| Vector Store | Chroma (local) |
| Embeddings | OpenAI text-embedding-3-small |
| Backend | FastAPI + Uvicorn |
| Frontend | Vanilla HTML / CSS / JS |

---

## Requirements

- Python 3.10+
- OpenAI API key
- Internet connection (for OpenAI API calls)
