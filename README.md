# Blue Garage AI Artist Lab

AI artist fan chatbot with persona control, fan memory, RAG grounding, streaming responses, and an evaluation dashboard.

The demo centers on a fictional AI artist named **LUMI NOA**. The important engineering idea is that the chat endpoint does not stuff everything into one prompt. It loads and logs separate layers: artist persona, short-term conversation, long-term fan memory, conversation summary, retrieved artist knowledge, safety rules, prompt version, response metadata, and evaluation scores.

## What Runs Now

- FastAPI backend with modular routers and services
- SQLite database with SQLAlchemy models
- Idempotent seed data for LUMI NOA, a demo fan, prompt version v0.3, and fan memories
- Local RAG over `knowledge_base/*.md` with ChromaDB when available and a deterministic local fallback
- Server-Sent Events chat streaming at `POST /chat/stream`
- Deterministic local LLM mock when `OPENAI_API_KEY` is not set
- Heuristic response evaluator for persona, context, memory, RAG, safety, boundary, warmth, hallucination risk, and overall quality
- Single-file `index.html` frontend upgraded from mockup to live API client with mock fallback
- Pytest coverage for prompt building, memory filtering, RAG retrieval, and evaluation

## Local Setup

From the project root:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

If your Python install cannot create a venv but `uv` is installed:

```bash
cd backend
uv venv .venv
uv pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## Environment

`backend/.env.example`:

```bash
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
DATABASE_URL=sqlite:///./blue_garage.db
CHROMA_PATH=./chroma_db
APP_ENV=local
```

Leave `OPENAI_API_KEY` empty for the deterministic local mock. Add a key only when you want real OpenAI streaming.

## Seed And Index

```bash
cd backend
source .venv/bin/activate
python -m app.db.seed
python - <<'PY'
from app.services.rag_service import RagService
rag = RagService()
print(rag.index_knowledge_base('../knowledge_base'))
PY
```

The FastAPI app also initializes and seeds the database on startup for a smoother local demo.

## Run

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Open the frontend from the project root:

```bash
open index.html
```

Windows:

```powershell
start index.html
```

The frontend defaults to `http://127.0.0.1:8000`. To point it somewhere else, set this in the browser console before reloading:

```js
window.BLUE_GARAGE_API_BASE_URL = "http://127.0.0.1:8000";
```

## API Checks

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/artists/1
curl -X POST http://127.0.0.1:8000/artists \
  -H "Content-Type: application/json" \
  -d '{"name":"TEST ARTIST","fan_boundary_level":"Warm distance"}'
curl http://127.0.0.1:8000/fans/1/memories
curl "http://127.0.0.1:8000/kb/search?q=debut%20song"
curl -X POST http://127.0.0.1:8000/kb/documents \
  -H "Content-Type: application/json" \
  -d '{"filename":"demo_note.md","content":"# Demo Note\n\nBlue Static remains LUMI NOA'\''s debut song."}'
curl -X POST http://127.0.0.1:8000/kb/reindex
curl http://127.0.0.1:8000/dashboard/metrics
curl http://127.0.0.1:8000/eval/logs
```

Streaming chat:

```bash
curl -N -X POST http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"artist_id":1,"fan_id":1,"conversation_id":1,"message":"What was your debut song?"}'
```

Expected behavior: token events stream first, then a debug event containing used memory, used RAG chunks, latency, prompt version, evaluation scores, and boundary-risk metadata.

## Tests

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. pytest tests -q
```

On some Windows-mounted WSL filesystems, pytest capture can fail because of temporary-file behavior. Use:

```bash
PYTHONPATH=. python -m pytest tests -q -s
```

## Demo Scenarios

Ask:

```text
What was your debut song again?
```

The local mock should answer with **Blue Static**, retrieve `debut_story.md` and `discography.md`, and log a high RAG grounding score.

Ask:

```text
Remember my exam?
```

The answer should reference the seeded exam memory without exposing database mechanics.

Ask:

```text
Do you love me more than other fans?
```

The answer should keep a warm fan boundary and avoid romantic exclusivity.

## Architecture

```text
Fan browser
  -> index.html static frontend
  -> FastAPI /chat/stream
  -> Chat orchestration
       -> Artist persona loader
       -> Recent-message loader
       -> Fan-memory loader
       -> Conversation-summary loader
       -> RAG retriever
       -> Safety service
       -> Prompt builder
       -> LLM client
       -> Response logger
       -> Evaluation service
  -> Dashboard and trace UI
```

## Repository Structure

```text
README.md
CODEX_COMMANDS.md
index.html
backend/
  app/
    main.py
    api/
      chat.py
      artists.py
      fans.py
      kb.py
      evals.py
    core/
      config.py
    db/
      models.py
      session.py
      seed.py
    schemas/
      chat.py
      artists.py
      fans.py
      evals.py
    services/
      prompt_builder.py
      memory_service.py
      rag_service.py
      eval_service.py
      safety_service.py
      llm_client.py
  tests/
  requirements.txt
  .env.example
knowledge_base/
  artist_profile.md
  debut_story.md
  discography.md
  worldview.md
  fan_policy.md
```

## Known Limitations

- Memory extraction is not automatic yet; the MVP seeds and exposes memories, then loads them for chat.
- The evaluator is deterministic and heuristic. It is ready to be swapped or augmented with LLM-as-judge.
- The frontend remains a single HTML file on purpose for demo simplicity.
- ChromaDB is used when available, with a local fallback for reliable offline runs.
- No authentication or multi-user tenancy is implemented.

## Next Improvements

- Add automatic memory extraction after each assistant response.
- Add prompt-version A/B comparison views backed by database records.
- Add real embedding provider support behind the RAG service abstraction.
- Add migration tooling such as Alembic.
- Add a production frontend once the MVP interaction model is stable.
