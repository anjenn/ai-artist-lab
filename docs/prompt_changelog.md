# Prompt Changelog

## v2

Goal: Apply research-backed prompt quality practices from `researches/research1.md`.

Changes:

- Added prompt strategy selection in `backend/app/services/prompt_quality.py`.
- Added technique tags, task type, output contract, and quality checks to chat prompts.
- Added untrusted-context boundary language to prompt construction.
- Annotated RAG chunks with provenance, content role, trust level, and injection risk.
- Added injection-resilience scoring comments in the evaluator.
- Added frontend prompt-quality strategy trace.
- Added prompt, eval, RAG, tool, and security policy artifacts.

Acceptance criteria:

- Service tests pass.
- Frontend script parses.
- Chat stream debug payload includes `prompt_strategy`.
- RAG chunks include citation and injection-risk metadata.

## v1

Goal: Runnable MVP.

Changes:

- FastAPI backend.
- SQLite seed data.
- RAG service.
- Streaming chat.
- Eval dashboard.
- Static frontend integration.

