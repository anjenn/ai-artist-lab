# Blue Garage AI Artist Lab

AI artist fan chatbot with persona control, fan memory, RAG grounding, streaming responses, and an evaluation dashboard.

[한국어 README](README.md)

The demo centers on a fictional AI artist named **LUMI NOA**. The important engineering idea is that the chat endpoint does not stuff everything into one prompt. It loads and logs separate layers: artist persona, short-term conversation, long-term fan memory, conversation summary, retrieved artist knowledge, safety rules, prompt version, response metadata, and evaluation scores.

## What Runs Now

- FastAPI backend with modular routers and services
- SQLite database with SQLAlchemy models
- Idempotent seed data for LUMI NOA, a demo fan, prompt versions through `v0.7-real-person-texture`, and fan memories
- Local RAG over `knowledge_base/*.md` with ChromaDB when available and a deterministic local fallback
- Server-Sent Events chat streaming at `POST /chat/stream`
- Deterministic local LLM mock when `OPENAI_API_KEY` is not set
- Heuristic response evaluator for persona, context, memory, RAG, safety, boundary, warmth, hallucination risk, and overall quality
- V2 prompt-quality layer with named strategies, technique tags, output contracts, quality checks, and untrusted-content boundaries
- Prompt-injection detection metadata for retrieved knowledge chunks
- V3 research-backed persona lab from `researches/v3_research_2_chatbot_persona`
- V3 seed data for purpose-aware DISC modes and manner-memory guidance
- V3/V4 research-referenced artist persona refresh with concrete public metadata and real-person texture
- Persona Editor `Save version` flow that persists artist settings and creates a new runtime `PromptVersion`
- V4 technical-architecture layer from `researches/v4_overall_technical_researches.md`
- V4 model-route metadata, bounded-fandom safety labels, usage-log schema, memory privacy gates, and layered eval gates
- Automatic post-turn memory extraction through the v4 privacy gate, with sensitive content blocked from auto-save
- Executable prompt regression, RAG retrieval eval, pairwise prompt judge, and automated leaderboard updates
- Stage-level latency timings for first token, total response, RAG, prompt build, streaming, eval, and logging
- Prompt-version CRUD, conversation selection, Memory Center workflows, manual eval review, and persona feedback metrics
- Alembic migration scaffold, demo access-key gate, request tracing, usage reconciliation, deployment notes, and demo data export/import
- Provider-selectable RAG embeddings with deterministic hash embeddings by default and OpenAI embeddings available when configured
- `/dashboard/persona-research`, `/dashboard/technical-research`, and `/dashboard/version-benchmark` dashboard endpoints
- Fan memory preview/export/delete-all endpoints for privacy-control workflows
- Research-backed RAG notes for prompt quality, persona design, technical architecture, fan-boundary safety, memory privacy, and evaluation strategy
- Single-file `index.html` frontend upgraded from mockup to live API client with mock fallback, English/Korean language toggle, v4 benchmark, and technical architecture cards
- Pytest coverage for prompt building, memory filtering, RAG retrieval, safety, API routers, SSE streaming, Korean localization, technical-research metadata, and evaluation

## Benchmark: v1 vs v2 vs v3 vs v4

Metric-based comparison between the saved `v1` runnable MVP, v2 prompt-quality/localization build, v3 research-seeded persona lab, and v4 technical-architecture build.

| Metric | Unit | v1 | v2 | v3 | v4 | Delta vs v3 | v4 Improvement | Evidence |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Automated regression tests | tests | 9 | 20 | 25 | 76 | +51 | +204% | pytest service/API/SSE suite |
| Prompt strategy metadata | fields | 0 | 6 | 7 | 10 | +3 | +42.9% | adds model route, safety labels, usage log IDs |
| RAG provenance metadata | fields/chunk | 2 | 6 | 6 | 6 | 0 | 0% | source, chunk ID, citation, role, trust, injection risk |
| Prompt security guardrails | checks | 2 | 5 | 6 | 10 | +4 | +66.7% | adds bounded-fandom and memory-gate checks |
| Korean intent coverage | routes | 0 | 4 | 7 | 10 | +3 | +42.9% | adds Korean boundary and private-location coverage |
| Prompt quality artifacts | files | 0 | 9 | 11 | 14 | +3 | +27.3% | adds v4 technical, fan policy, and benchmark artifacts |
| Frontend language modes | modes | 1 | 2 | 2 | 2 | 0 | 0% | English/Korean top-nav switch retained |
| Research source coverage | sources | 0 | 0 | 4 | 5 | +1 | +25% | v4 technical research added |
| Knowledge-base documents | documents | 5 | 5 | 6 | 8 | +2 | +33.3% | adds `technical_research_v4.md` and policy updates |
| Model routing policies | routes | 0 | 0 | 0 | 4 | +4 | new | default chat, escalation, structured eval, judge adjudication |
| Runtime usage log fields | fields | 0 | 0 | 0 | 23 | +23 | new | hashed user, route, tokens, retrieval, memory, eval version |
| Memory privacy controls | controls | 1 | 1 | 2 | 6 | +4 | +200% | preview, create, list, single delete, export, delete all |
| Bounded-fandom safety labels | labels | 0 | 2 | 3 | 8 | +5 | +166.7% | normal, dependency, crisis, minors, stalking, and related labels |
| Evaluation layers | layers | 1 | 2 | 2 | 4 | +2 | +100% | unit, heuristic, judge-ready rubric, human review queue |

Benchmark basis: `/dashboard/version-benchmark`, `/dashboard/persona-research`, `/dashboard/technical-research`, automated tests, Python compile check, frontend JavaScript syntax check, HTML parse, live SSE debug metadata, live Korean RAG search, and research-source analysis.

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

## Persona Refresh And Save Flow

The current LUMI NOA persona is stored in the knowledge base and seeded into the runtime as `v0.7-real-person-texture`.

The refresh uses the local research notes this way:

- The 2018 DISC chatbot study informs purpose-aware routing: casual chat, support-like turns, and factual tasks use different persona modes.
- KIRINO informs the separation between stable artist persona, fan manner preferences, and retrieved knowledge.
- The K-pop metadata notebook supports concrete public artist fields such as stage name, debut track, genre palette, and public project role while avoiding body metrics or private identity claims.

The Persona Editor in `index.html` now has a real `Save version` action. It calls `POST /artists/{artist_id}/persona-version`, updates the artist profile fields, and creates a new `PromptVersion`. The chat endpoint always loads the latest prompt version by creation time, so saved persona drafts become the next runtime prompt layer.

The save flow is intentionally scoped: it edits the demo artist profile and prompt version, but it does not rewrite markdown files in `knowledge_base/`. To change the official RAG knowledge base, edit the markdown files and re-index.

## V4 Technical Architecture

V4 uses `researches/v4_overall_technical_researches.md` to turn the research recommendations into runtime metadata and dashboard surfaces:

- Model route metadata distinguishes default fan chat, boundary-sensitive escalation, structured eval, and judge adjudication routes.
- Chat debug output includes `model_route`, `usage_log`, `v4_eval`, request trace, and stage-level latency metadata.
- Usage logs hash the fan ID and record route, runtime model, recommended model, token estimates, provider reconciliation fields, retrieval IDs, memory IDs, eval version, and `store=false`.
- Safety detection now emits bounded-fandom labels such as `romance_escalation`, `dependency`, `stalking_or_doxxing`, `minor_safety`, `crisis`, and `impersonation_jailbreak`.
- Memory privacy gates classify candidate memories as auto-save, confirmation-required, or do-not-store; the post-turn extraction path only auto-saves low-risk, high-confidence candidates.
- Fan memory privacy endpoints support preview, export, single delete, and delete-all workflows.
- RAG embedding selection supports the local deterministic provider by default and OpenAI embeddings when API credentials are configured.
- `/dashboard/technical-research` exposes model routes, request-log schema, memory policy, eval layers, and implementation caveats.

The current local runtime still works without an OpenAI key. In that mode the route metadata records a `local-mock` runtime model while preserving the research-backed recommended model route for production planning.

## Latest Research Knowledge Base

The app indexes `knowledge_base/*.md`, so the research notes below are retrievable through `/kb/search` and available to the chat prompt as project knowledge.

| Local research source | Knowledge-base file | Applied guidance |
|---|---|---|
| `researches/v2_research1_google_scholar_general.md` | `knowledge_base/prompt_quality_research_v2.md` | Standard prompt sections, named strategies, RAG grounding, evaluation rubrics, prompt-injection boundaries, and prompt changelog discipline |
| `researches/v3_persona_analysis.md` plus `researches/v3_research_2_chatbot_persona/*` | `knowledge_base/persona_research_v3.md` | Purpose-routed persona modes, persona/manner memory separation, dataset coverage checks, and KIRINO-inspired eval criteria |
| `researches/v4_overall_technical_researches.md` | `knowledge_base/technical_research_v4.md` and `knowledge_base/fan_policy.md` | Model cascade guidance, streaming usage logging, hybrid retrieval, memory privacy, bounded fandom labels, deletion workflow, and layered evaluation |

OpenAI-specific model names, pricing, retention behavior, and API details in the local v4 research note are treated as time-sensitive recommendations. Re-check official OpenAI docs before production release.

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
curl -X POST http://127.0.0.1:8000/artists/1/persona-version \
  -H "Content-Type: application/json" \
  -d '{"artist_name":"LUMI NOA","fan_boundary_level":"Warm distance","speech_style":"Evidence first, then one concrete studio image.","personality":"Careful, grounded, lightly funny, never possessive.","forbidden_statements":"No romance, dependency, professional advice, or invented lore.","worldview_summary":"Blue Garage is a working studio with tape hiss and a blue lamp."}'
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

Expected behavior: token events stream first, then a debug event containing used memory, used RAG chunks, latency, prompt version, evaluation scores, boundary-risk metadata, selected model route, v4 eval gates, and usage-log metadata.

The debug event also includes `prompt_strategy`, which names the selected technique stack such as `rag-grounded-direct-answer`, `safety-filtered-response`, or `candidate-comparison`.

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

Latest local verification after the production-readiness pass: `76 passed`.

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
       -> Intent classifier
       -> Prompt-quality strategy selector
       -> V4 model-route selector
       -> Safety service
       -> Memory privacy gate
       -> Automatic memory extractor
       -> Prompt builder
       -> LLM client
       -> Response logger
       -> Request tracing and usage reconciliation
       -> V4 usage-log builder
       -> Evaluation service
       -> Persona feedback metrics
       -> V4 technical research service
  -> Dashboard and trace UI
```

## Repository Structure

```text
README.md
README.eng.md
CODEX_COMMANDS.md
index.html
backend/
  app/
    main.py
    api/
      chat.py
      artists.py
      conversations.py
      demo.py
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
      demo_data.py
      eval_runner.py
      prompt_builder.py
      memory_service.py
      rag_service.py
      eval_service.py
      intent_classifier.py
      safety_service.py
      llm_client.py
      observability.py
      pairwise_judge.py
      persona_feedback.py
      prompt_quality.py
      persona_research.py
      research_ingestion.py
      technical_research.py
      version_benchmark.py
  tests/
  migrations/
  requirements.txt
  .env.example
docs/
  deployment.md
  rag_policy.md
  tool_policy.md
  security_tests.md
  prompt_changelog.md
prompts/
  prompt_patterns.md
  prompt_inventory.md
evals/
  prompt_regression_set.jsonl
  rag_retrieval_set.jsonl
  pairwise_prompt_ab_set.jsonl
  judge_rubrics.md
  prompt_leaderboard.md
knowledge_base/
  artist_profile.md
  debut_story.md
  discography.md
  worldview.md
  fan_policy.md
  prompt_quality_research_v2.md
  persona_research_v3.md
  technical_research_v4.md
```

## Known Limitations

- Memory extraction is automatic but intentionally conservative; thresholds, TTLs, and consent copy still need real-user calibration.
- The evaluator and strategy selector are deterministic and heuristic. They are ready to be augmented with LLM-as-judge, reviewer agreement tracking, and larger eval sets.
- The frontend remains a single HTML file on purpose for demo simplicity.
- ChromaDB is used when available, with a local fallback for reliable offline runs.
- An optional demo access-key gate exists, but full authentication, authorization, and multi-user tenancy are not implemented.
- Model availability, pricing, and provider retention details in research notes must be re-verified before production use.

## Next Improvements

- Calibrate eval rubrics with human reviewer agreement, especially for crisis, minors, stalking, impersonation, deleted-memory retrieval, and persona drift.
- Expand prompt, RAG, safety, and latency eval sets so every roadmap change produces a measurable regression signal.
- Compare embedding providers and hybrid keyword/vector retrieval against a larger retrieval benchmark.
- Connect real provider usage fields into daily cost reporting in hosted mode.
- Add production alerting for latency, failed eval gates, unsafe safety labels, and provider errors.
- Add a production frontend once the MVP interaction model is stable.
