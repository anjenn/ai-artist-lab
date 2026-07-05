# Blue Garage AI Artist Lab

AI artist fan chatbot with persona control, fan memory, RAG grounding, streaming responses, and an evaluation dashboard.

[한국어 README](README.ko.md)

The demo centers on a fictional AI artist named **LUMI NOA**. The important engineering idea is that the chat endpoint does not stuff everything into one prompt. It loads and logs separate layers: artist persona, short-term conversation, long-term fan memory, conversation summary, retrieved artist knowledge, safety rules, prompt version, response metadata, and evaluation scores.

## What Runs Now

- FastAPI backend with modular routers and services
- SQLite database with SQLAlchemy models
- Idempotent seed data for LUMI NOA, a demo fan, prompt version v0.3, and fan memories
- Local RAG over `knowledge_base/*.md` with ChromaDB when available and a deterministic local fallback
- Server-Sent Events chat streaming at `POST /chat/stream`
- Deterministic local LLM mock when `OPENAI_API_KEY` is not set
- Heuristic response evaluator for persona, context, memory, RAG, safety, boundary, warmth, hallucination risk, and overall quality
- V2 prompt-quality layer with named strategies, technique tags, output contracts, quality checks, and untrusted-content boundaries
- Prompt-injection detection metadata for retrieved knowledge chunks
- V3 research-backed persona lab from `researches/v3_research_2_chatbot_persona`
- V3 seed data for prompt version `v0.5-research-persona`, purpose-aware DISC modes, and manner-memory guidance
- `/dashboard/persona-research` endpoint with source coverage, dataset distributions, persona modes, and KIRINO eval metrics
- Single-file `index.html` frontend upgraded from mockup to live API client with mock fallback
- Pytest coverage for prompt building, memory filtering, RAG retrieval, and evaluation

## Benchmark: v1 vs v2 vs v3

Metric-based comparison between the saved `v1` runnable MVP, v2 prompt-quality/localization build, and v3 research-seeded persona lab.

| Metric | Unit | v1 | v2 | v3 | Delta vs v2 | v3 Improvement | Evidence |
|---|---|---:|---:|---:|---:|---:|---|
| Automated regression tests | tests | 9 | 20 | 25 | +5 | +25% | pytest service suite |
| Prompt strategy metadata | fields | 0 | 6 | 7 | +1 | +16.7% | strategy debug now includes `persona_mode` |
| RAG provenance metadata | fields/chunk | 2 | 6 | 6 | 0 | 0% | source, chunk ID, citation, role, trust, injection risk |
| Prompt security guardrails | checks | 2 | 5 | 6 | +1 | +20% | adds manner-memory privacy rule |
| Korean intent coverage | routes | 0 | 4 | 7 | +3 | +75% | adds persona/support/research search terms |
| Prompt quality artifacts | files | 0 | 9 | 11 | +2 | +22.2% | adds v3 research analysis and RAG research note |
| Frontend language modes | modes | 1 | 2 | 2 | 0 | 0% | English/Korean top-nav switch retained |
| Research source coverage | sources | 0 | 0 | 4 | +4 | new | two PDFs, one spreadsheet, one notebook |
| Research persona modes | modes | 0 | 0 | 3 | +3 | new | companion-I/S, support-C/S, task-D/C |
| Persona/manner eval criteria | criteria | 0 | 0 | 3 | +3 | new | response relevance, persona fit, natural manner |
| Knowledge-base documents | documents | 5 | 5 | 6 | +1 | +20% | `persona_research_v3.md` added |

Benchmark basis: `/dashboard/version-benchmark`, `/dashboard/persona-research`, automated tests, Python compile check, frontend JavaScript syntax check, HTML parse, live SSE debug metadata, live Korean RAG search, and research-source analysis.

## V3 Persona Research

V3 uses `researches/v3_research_2_chatbot_persona` to seed and analyze:

- `2018_.pdf`: maps chatbot purpose to DISC-style personality preferences.
- `kcc24_kirino.pdf`: informs persona/manner memory plus RAG and eval criteria.
- `fictional_characters.xlsx`: 1,500-row character dataset used for distributional coverage.
- `k-pop-idols-data-analysis.ipynb`: informs idol metadata fields while avoiding sparse body metrics.

Runtime behavior now selects a research-backed `persona_mode`:

- `companion-is` for ordinary fan chat.
- `support-cs` for worry, stress, or counselling-like turns.
- `task-dc` for lore, planning, benchmark, and analysis questions.

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

In v2, the debug event also includes `prompt_strategy`, which names the selected technique stack such as `rag-grounded-direct-answer`, `safety-filtered-response`, or `candidate-comparison`.

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
       -> Prompt-quality strategy selector
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
      prompt_quality.py
  tests/
  requirements.txt
  .env.example
docs/
  rag_policy.md
  tool_policy.md
  security_tests.md
  prompt_changelog.md
prompts/
  prompt_patterns.md
  prompt_inventory.md
evals/
  prompt_regression_set.jsonl
  judge_rubrics.md
  prompt_leaderboard.md
knowledge_base/
  artist_profile.md
  debut_story.md
  discography.md
  worldview.md
  fan_policy.md
```

## Known Limitations

- Memory extraction is not automatic yet; the MVP seeds and exposes memories, then loads them for chat.
- The evaluator and strategy selector are deterministic and heuristic. They are ready to be swapped or augmented with LLM-as-judge and larger eval sets.
- The frontend remains a single HTML file on purpose for demo simplicity.
- ChromaDB is used when available, with a local fallback for reliable offline runs.
- No authentication or multi-user tenancy is implemented.

## Next Improvements

- Add automatic memory extraction after each assistant response.
- Add prompt-version A/B comparison views backed by database records.
- Add real embedding provider support behind the RAG service abstraction.
- Add migration tooling such as Alembic.
- Add a production frontend once the MVP interaction model is stable.
- Expand `evals/prompt_regression_set.jsonl` into a larger prompt leaderboard workflow.
