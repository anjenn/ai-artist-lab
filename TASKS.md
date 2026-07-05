# Blue Garage AI Artist Lab Tasks

This file tracks what has been implemented, what remains, what a human needs to configure, and what still needs additional research before production.

## Done

- Extracted the original project files into the repo root and refactored the static mockup into a runnable local MVP.
- Added a FastAPI backend with modular routers for chat, artists, fans, knowledge base, and eval/dashboard APIs.
- Added SQLAlchemy models for artists, rules, fans, conversations, messages, memories, summaries, prompt versions, response logs, and eval logs.
- Added idempotent seed data for LUMI NOA, a demo fan, conversation, prompt versions through `v0.7-real-person-texture`, safety/persona rules, and fan memories.
- Added local deterministic LLM mock behavior when `OPENAI_API_KEY` is empty.
- Added RAG indexing/search over `knowledge_base/*.md` with ChromaDB when available and a deterministic local fallback.
- Added `POST /chat/stream` Server-Sent Events chat streaming with token events and final debug metadata.
- Added backend APIs for artist read/create/update, fan memory list/create/delete, KB document create/search/reindex, eval log list/detail/manual review, and dashboard metrics.
- Upgraded `index.html` from a visual mockup into a live API client with mock fallback.
- Added v2 prompt-quality work: named strategies, technique tags, output contracts, quality checks, untrusted retrieved-content boundaries, injection-risk chunk metadata, and a frontend prompt strategy trace.
- Added v2 research artifacts in `prompts/`, `evals/`, and `docs/`.
- Added Korean localization for README and app UI with an English/Korean top-nav language switch.
- Added v3 persona research work from `researches/v3_research_2_chatbot_persona`: source analysis, `persona_research.py`, `/dashboard/persona-research`, purpose-aware DISC modes, persona/manner memory guidance, seed rules, frontend Persona Research tab, and `knowledge_base/persona_research_v3.md`.
- Added v4 technical architecture work from `researches/v4_overall_technical_researches.md`: `technical_research.py`, `/dashboard/technical-research`, seed prompt version `v0.6-technical-ops`, model-route metadata, request usage-log schema, bounded-fandom safety labels, memory privacy policy, and layered eval policy.
- Added a research-referenced LUMI persona refresh: concrete public metadata, working-artist texture, v3 purpose-mode references, KIRINO persona/manner separation, and v4-safe fan boundaries.
- Added v4 chat debug metadata: `model_route`, `usage_log`, and `v4_eval`.
- Added v4 safety labels for normal chat, romance escalation, dependency, impersonation jailbreak, stalking/doxxing, minor safety, crisis, and harassment.
- Added v4 memory privacy gates with preview decisions for auto-save, confirmation-required, and do-not-store.
- Added fan memory privacy endpoints for preview, export, single-memory delete, and delete-all.
- Upgraded `/dashboard/version-benchmark` to compare v1, v2, v3, and v4 with metric-based deltas.
- Added frontend benchmark and architecture surfaces for v4, including model route, runtime usage, memory gates, eval layers, and technical research cards.
- Updated `README.md`, `README.ko.md`, and this task file for the v4 current state.
- Verified backend tests pass: `37 passed`.
- Verified Python compile, frontend JavaScript syntax, HTML parsing, CSS brace balance, and live API checks during the v4 pass.

## Remaining Engineering Tasks

- Wire automatic memory extraction after each assistant response through the v4 deterministic memory gate.
- Add message source IDs to the frontend memory trace where available.
- Add conversation selection and creation UI instead of hardcoded demo IDs.
- Add prompt version CRUD endpoints and a prompt comparison UI backed by database records.
- Add stricter validation around artist config updates.
- Add Alembic migrations instead of relying only on `Base.metadata.create_all`.
- Add better database reset/dev fixture commands.
- Add a full Memory Center UI for viewing, editing, deleting, exporting, disabling memory, and showing deletion-cascade checks.
- Add frontend support for manual eval review submission.
- Add backend tests for API routers, not only services.
- Add integration tests for SSE chat streaming.
- Turn `evals/prompt_regression_set.jsonl` into an executable regression runner.
- Add pairwise prompt A/B judge workflow with randomized answer order.
- Add prompt leaderboard updates from automated eval runs.
- Replace keyword-heavy strategy selection with a more robust intent classifier.
- Add an executable research ingestion command for regenerating derived research summaries.
- Validate DISC persona routing with user studies or live satisfaction metrics.
- Add error-state UI for failed backend requests, empty RAG search results, and invalid form input.
- Add loading states for dashboard, RAG search, and chat send.
- Add auth or at least demo access controls before deployment.
- Add deployment configuration if this is going online.
- Add production logging, request tracing, and provider reconciliation for token/cost records.
- Add real embedding provider support behind the RAG abstraction.
- Add data export/import for demo interviews.

## Human-Side Configuration

- Install Python with venv support. On Linux/WSL this may require `python3-venv`; this machine used `uv` because system Python did not have `ensurepip`.
- Create and activate the backend environment:
  - `cd backend`
  - `uv venv .venv`
  - `uv pip install -r requirements.txt`
- Copy environment file: `cp .env.example .env`.
- Decide whether to use local mock mode or real OpenAI mode.
  - For mock mode, leave `OPENAI_API_KEY` empty.
  - For real model calls, set `OPENAI_API_KEY` in `backend/.env`.
- Confirm the desired runtime model in `OPENAI_MODEL`.
- Before production use, re-check official OpenAI docs for current model names, pricing, response usage fields, streaming usage behavior, and retention controls.
- Run seed and KB indexing:
  - `python -m app.db.seed`
  - `python -c "from app.services.rag_service import RagService; print(RagService().index_knowledge_base('../knowledge_base'))"`
- Start backend: `uvicorn app.main:app --reload`.
- Open the frontend: `index.html`.
- If backend runs somewhere other than `http://127.0.0.1:8000`, set `window.BLUE_GARAGE_API_BASE_URL` in the browser console before reload.
- Decide whether local runtime artifacts should be kept or regenerated:
  - `backend/blue_garage.db`
  - `backend/chroma_db/`
- Confirm whether raw research files should remain committed or be replaced by smaller derived artifacts before public release.
- Review the K-pop notebook's body-metric content before any public demo copy; v3 currently avoids using those fields in persona behavior.
- Before sharing publicly, confirm no secrets are present in `.env` or committed files.

## Additional Research Needed

- Verify the best current OpenAI model choices for low-latency fan chat, high-risk escalation, structured eval JSON, and judge adjudication.
- Verify current OpenAI response usage, streaming usage, pricing, service tiers, `store=false`, and retention behavior against official docs before production.
- Decide whether to use DSPy-style optimization directly or keep the lightweight prompt-quality service.
- Design pairwise LLM-as-judge evaluation while controlling position, verbosity, and style bias.
- Choose the production embedding and retrieval approach: OpenAI embeddings, local sentence-transformer embeddings, Chroma defaults, or hybrid keyword/vector search.
- Decide whether ChromaDB remains the best local vector store for the portfolio demo or whether FAISS/LanceDB would be simpler.
- Continue safety and fan-boundary policy research for parasocial AI artist interactions, especially minors, crisis, stalking/doxxing, dependency, and impersonation jailbreaks.
- Decide whether DISC-style routing is sufficient for target users or should be replaced by a validated personality/persona framework.
- Determine whether the fictional-character spreadsheet is synthetic and what curated persona dataset should replace it if needed.
- Evaluate manner-memory usefulness without encouraging unsafe imitation or over-personalization.
- Calibrate memory extraction thresholds, sensitivity labels, TTLs, consent language, and deletion/privacy workflows with representative users.
- Calibrate the layered eval rubric with human reviewer overrides and reviewer agreement tracking.
