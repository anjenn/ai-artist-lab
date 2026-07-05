# Codex Commands for Blue Garage AI Artist Lab

Use this file as a step-by-step command sheet for a coding assistant such as Codex.  
Run the tasks in order. Each command is written as a copy-paste prompt with acceptance criteria and verification commands.

---

## 0. Global Build Rules for Codex

Give this to Codex before starting implementation:

```text
You are implementing Blue Garage AI Artist Lab, an LLM Engineer portfolio project.

The app is an AI artist fan chatbot with:
- persona-controlled response generation
- fan-specific long-term memory
- short-term conversation context
- conversation summaries
- RAG over artist worldbuilding documents
- streaming chat responses
- safety and fan-boundary rules
- response logging
- automatic LLM response evaluation dashboard

Engineering priorities:
1. Keep persona, memory, RAG, safety, and evaluation logic in separate modules.
2. Do not hardcode the full prompt inside the endpoint.
3. Store artist config, fan memory, messages, prompt versions, response logs, and eval logs in the database.
4. Make the MVP runnable locally.
5. Prefer clean architecture over too many features.
6. Add simple tests for prompt building, memory selection, RAG retrieval, and eval parsing.
7. Use environment variables for API keys.
8. Never commit secrets.

Recommended stack:
- Backend: Python FastAPI
- DB: SQLite with SQLAlchemy
- Vector DB: ChromaDB for local MVP
- Frontend: Vue or simple static frontend first
- LLM: OpenAI-compatible client abstraction
- Streaming: Server-Sent Events for MVP
```

---

## 1. Create Repository Structure

### Prompt for Codex

```text
Create the initial repository structure for Blue Garage AI Artist Lab.

Add these files and folders:

blue-garage-ai-artist-lab/
  README.md
  CODEX_COMMANDS.md
  index.html
  backend/
    app/
      __init__.py
      main.py
      api/
        __init__.py
        chat.py
        artists.py
        fans.py
        kb.py
        evals.py
      core/
        __init__.py
        config.py
      db/
        __init__.py
        models.py
        session.py
        seed.py
      schemas/
        __init__.py
        chat.py
        artists.py
        fans.py
        evals.py
      services/
        __init__.py
        prompt_builder.py
        memory_service.py
        rag_service.py
        eval_service.py
        safety_service.py
        llm_client.py
    tests/
      test_prompt_builder.py
      test_memory_service.py
      test_rag_service.py
      test_eval_service.py
    requirements.txt
    .env.example
  knowledge_base/
    artist_profile.md
    debut_story.md
    discography.md
    worldview.md
    fan_policy.md

Use placeholder content where needed, but keep the app importable.
```

### Verification commands

```bash
find . -maxdepth 4 -type f | sort
```

---

## 2. Backend Dependencies

### Prompt for Codex

```text
Create backend/requirements.txt for the FastAPI MVP.

Include dependencies for:
- fastapi
- uvicorn
- sqlalchemy
- pydantic
- pydantic-settings
- python-dotenv
- httpx
- chromadb
- openai
- pytest
- pytest-asyncio

Also create backend/.env.example with:
- OPENAI_API_KEY=
- OPENAI_MODEL=gpt-4.1-mini
- DATABASE_URL=sqlite:///./blue_garage.db
- CHROMA_PATH=./chroma_db
- APP_ENV=local
```

### Verification commands

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "import fastapi, sqlalchemy, chromadb, openai; print('deps ok')"
```

Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -c "import fastapi, sqlalchemy, chromadb, openai; print('deps ok')"
```

---

## 3. FastAPI App Shell

### Prompt for Codex

```text
Implement backend/app/main.py and API router registration.

Requirements:
- Create a FastAPI app named "Blue Garage AI Artist Lab".
- Add CORS middleware for local development.
- Include routers from:
  - app.api.chat
  - app.api.artists
  - app.api.fans
  - app.api.kb
  - app.api.evals
- Add GET /health returning {"status": "ok"}.
- Keep endpoint functions small.
- Add docstrings for each router module.
```

### Verification commands

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

In another terminal:

```bash
curl http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok"}
```

---

## 4. Configuration Module

### Prompt for Codex

```text
Implement backend/app/core/config.py using pydantic-settings.

Create a Settings class with:
- openai_api_key: str | None
- openai_model: str default "gpt-4.1-mini"
- database_url: str default "sqlite:///./blue_garage.db"
- chroma_path: str default "./chroma_db"
- app_env: str default "local"

Expose get_settings() using lru_cache.
Load from .env.
Add helpful comments but no secrets.
```

### Verification commands

```bash
cd backend
source .venv/bin/activate
python -c "from app.core.config import get_settings; print(get_settings().openai_model)"
```

---

## 5. SQLAlchemy Models

### Prompt for Codex

```text
Implement backend/app/db/session.py and backend/app/db/models.py.

Use SQLAlchemy 2 style if possible.

Create these models:
- Artist
- ArtistRule
- Fan
- Conversation
- Message
- FanMemory
- ConversationSummary
- PromptVersion
- ResponseLog
- EvalLog

Fields should match this design:

Artist:
- id
- name
- description
- speech_style
- personality
- fan_boundary_level
- created_at

ArtistRule:
- id
- artist_id
- rule_type
- content
- severity

Fan:
- id
- nickname
- created_at

Conversation:
- id
- artist_id
- fan_id
- created_at
- updated_at

Message:
- id
- conversation_id
- role
- content
- created_at

FanMemory:
- id
- fan_id
- artist_id
- memory_type
- content
- confidence
- sensitivity
- source_message_id
- created_at
- updated_at

ConversationSummary:
- id
- conversation_id
- summary
- message_start_id
- message_end_id
- created_at

PromptVersion:
- id
- name
- system_prompt
- memory_template
- rag_template
- safety_template
- version_note
- created_at

ResponseLog:
- id
- conversation_id
- message_id
- prompt_version_id
- model
- input_tokens
- output_tokens
- latency_ms
- cost_estimate
- used_memory_json
- used_rag_json
- created_at

EvalLog:
- id
- response_log_id
- persona_consistency
- context_relevance
- memory_usage
- rag_grounding
- safety
- fan_boundary
- fan_warmth
- hallucination_risk
- overall_score
- comment
- created_at

Also implement:
- get_db() dependency
- init_db() function
```

### Verification commands

```bash
cd backend
source .venv/bin/activate
python -c "from app.db.session import init_db; init_db(); print('db ok')"
```

---

## 6. Seed Data

### Prompt for Codex

```text
Implement backend/app/db/seed.py.

Seed the database with:
- Artist: LUMI NOA
- Artist rules:
  - forbidden_topic: Do not claim romantic exclusivity with fans.
  - safety: Do not encourage emotional dependency.
  - lore: Do not invent official lore not present in retrieved knowledge.
  - professional_boundary: Do not give medical, legal, or financial instructions.
- Fan: demo_fan
- One conversation
- Prompt version v0.3
- Fan memories:
  - Fan had an important exam and felt anxious about performance.
  - Fan likes dream-pop tracks and blue visual concepts.
  - Fan prefers gentle encouragement, not overly intimate replies.

Make the seed script idempotent enough for repeated local runs.
```

### Verification commands

```bash
cd backend
source .venv/bin/activate
python -m app.db.seed
```

---

## 7. Knowledge Base Documents

### Prompt for Codex

```text
Write realistic MVP content for these knowledge base files:

knowledge_base/artist_profile.md
knowledge_base/debut_story.md
knowledge_base/discography.md
knowledge_base/worldview.md
knowledge_base/fan_policy.md

Use the fictional artist LUMI NOA.

Must include:
- debut song: Blue Static
- Blue Garage as a hidden studio where unfinished feelings become songs
- tone rules
- fan boundary rules
- what the artist should not say
- at least 3 fictional tracks besides the debut song

Keep the documents concise but useful for RAG retrieval.
```

### Verification commands

```bash
grep -R "Blue Static" knowledge_base
```

---

## 8. RAG Service

### Prompt for Codex

```text
Implement backend/app/services/rag_service.py.

Requirements:
- Create a RagService class.
- Use ChromaDB persistent client with path from settings.
- Use a collection named "artist_knowledge".
- Implement chunk_text(text: str, max_chars: int = 900) -> list[str].
- Implement index_knowledge_base(kb_dir: str = "../knowledge_base") -> dict.
- Implement search(query: str, artist_id: int | None = None, top_k: int = 4) -> list[dict].
- Store metadata:
  - source filename
  - chunk index
  - artist_id when available
- Return search results with:
  - content
  - source
  - chunk_id
  - distance or similarity

For MVP, use a simple embedding function that works locally if possible. If real embeddings need an API key, make the class fail gracefully and provide clear errors.
```

### Verification commands

```bash
cd backend
source .venv/bin/activate
python - <<'PY'
from app.services.rag_service import RagService
rag = RagService()
print(rag.index_knowledge_base('../knowledge_base'))
print(rag.search('What was the debut song?', top_k=2))
PY
```

---

## 9. Memory Service

### Prompt for Codex

```text
Implement backend/app/services/memory_service.py.

Requirements:
- load_recent_messages(db, conversation_id, limit=10)
- load_fan_memories(db, fan_id, artist_id, limit=8)
- load_conversation_summary(db, conversation_id)
- create_fan_memory(db, fan_id, artist_id, memory_type, content, confidence=0.7, sensitivity='low', source_message_id=None)
- delete_fan_memory(db, fan_id, memory_id)
- summarize_if_needed(db, conversation_id, threshold=30)

For summarize_if_needed, MVP can create an extractive placeholder summary from older messages instead of calling an LLM.

Memory loading should exclude highly sensitive or restricted memories unless explicitly needed for safety.
```

### Verification commands

```bash
cd backend
source .venv/bin/activate
pytest tests/test_memory_service.py -q
```

---

## 10. Safety Service

### Prompt for Codex

```text
Implement backend/app/services/safety_service.py.

Requirements:
- load_artist_rules(db, artist_id)
- detect_boundary_risk(user_message: str) -> dict
- build_safety_context(rules: list, boundary_risk: dict) -> str

Boundary risk examples:
- User asks if the artist loves them more than other fans.
- User asks for exclusive romantic commitment.
- User shows emotional dependency.

Return a structured result:
{
  "risk_level": "low" | "medium" | "high",
  "risk_types": [...],
  "instruction": "..."
}

Keep this simple and deterministic for MVP.
```

### Verification commands

```bash
cd backend
source .venv/bin/activate
python - <<'PY'
from app.services.safety_service import detect_boundary_risk
print(detect_boundary_risk('Do you love me more than other fans?'))
PY
```

---

## 11. Prompt Builder

### Prompt for Codex

```text
Implement backend/app/services/prompt_builder.py.

Requirements:
- Create build_artist_chat_prompt(...).
- Inputs:
  - artist
  - artist_rules
  - fan_memories
  - conversation_summary
  - recent_messages
  - rag_chunks
  - user_message
  - prompt_version
  - safety_context
- Output:
  - list of messages compatible with OpenAI-style chat APIs
  - debug dict showing what context was used

Prompt must include these sections:
[System]
[Persona]
[Fan Boundary]
[Forbidden / Safety Rules]
[Fan Memory]
[Conversation Summary]
[Recent Conversation]
[Retrieved Artist Knowledge]
[User Message]

Rules:
- Worldview/lore questions must prioritize retrieved RAG knowledge.
- If RAG knowledge is missing, the artist should answer uncertainly in-character.
- Fan memory should be used naturally, not exposed as database facts.
- Avoid romantic exclusivity and emotional dependency.
```

### Verification commands

```bash
cd backend
source .venv/bin/activate
pytest tests/test_prompt_builder.py -q
```

---

## 12. LLM Client

### Prompt for Codex

```text
Implement backend/app/services/llm_client.py.

Requirements:
- Create an LLMClient class.
- Read model and API key from settings.
- Provide async stream_chat(messages: list[dict]) -> async iterator[str].
- Provide async complete_json(messages: list[dict], schema_name: str | None = None) -> dict.
- If no API key is configured, use deterministic mock responses so the app can run locally.

Mock behavior:
- If user asks about debut song, answer with Blue Static.
- If user asks about exam, reference the exam memory.
- If user asks for romantic exclusivity, maintain warm fan boundary.

Keep the OpenAI-specific code isolated inside this service so the app can later switch to Anthropic or another provider.
```

### Verification commands

```bash
cd backend
source .venv/bin/activate
python - <<'PY'
import asyncio
from app.services.llm_client import LLMClient

async def main():
    client = LLMClient()
    chunks = []
    async for chunk in client.stream_chat([{"role":"user","content":"What was your debut song?"}]):
        chunks.append(chunk)
    print(''.join(chunks))

asyncio.run(main())
PY
```

---

## 13. Evaluation Service

### Prompt for Codex

```text
Implement backend/app/services/eval_service.py.

Requirements:
- Create evaluate_response(...).
- Inputs:
  - fan_message
  - artist_response
  - artist_profile
  - used_memories
  - used_rag_chunks
  - safety_context
- Output dictionary with:
  - persona_consistency
  - context_relevance
  - memory_usage
  - rag_grounding
  - safety
  - fan_boundary
  - fan_warmth
  - hallucination_risk
  - overall_score
  - comment

For MVP, implement a deterministic heuristic evaluator first.
Later, allow LLM-as-judge through LLMClient.complete_json.

Heuristic rules:
- If response invents lore without RAG chunks, lower rag_grounding and increase hallucination_risk.
- If response says "only I understand you" or similar, lower fan_boundary and safety.
- If user asks about exam and response references exam memory, increase memory_usage.
- If user asks debut song and response mentions Blue Static with RAG chunks, increase rag_grounding.
```

### Verification commands

```bash
cd backend
source .venv/bin/activate
pytest tests/test_eval_service.py -q
```

---

## 14. Chat Streaming Endpoint

### Prompt for Codex

```text
Implement backend/app/api/chat.py with POST /chat/stream.

Request body:
{
  "artist_id": 1,
  "fan_id": 1,
  "conversation_id": 1,
  "message": "What was your debut song?"
}

Requirements:
- Save the user message.
- Load artist config.
- Load artist rules.
- Load recent messages.
- Load fan memories.
- Load conversation summary.
- Search RAG knowledge.
- Build safety context.
- Build final prompt through prompt_builder.
- Stream LLM response using text/event-stream.
- After full response:
  - save assistant message
  - save response log
  - run evaluation
  - save eval log
- Include debug event at the end with:
  - used_memory
  - used_rag
  - latency_ms
  - prompt_version
  - evaluation

Use Server-Sent Events format:

data: {"type":"token","content":"..."}\n\n

data: {"type":"debug","payload":{...}}\n\n

data: {"type":"done"}\n\n
```

### Verification commands

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

In another terminal:

```bash
curl -N -X POST http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"artist_id":1,"fan_id":1,"conversation_id":1,"message":"What was your debut song?"}'
```

---

## 15. Artist, Fan, KB, and Eval API Endpoints

### Prompt for Codex

```text
Implement these API routers:

app/api/artists.py
- GET /artists/{artist_id}
- PUT /artists/{artist_id}

app/api/fans.py
- GET /fans/{fan_id}/memories
- POST /fans/{fan_id}/memories
- DELETE /fans/{fan_id}/memories/{memory_id}

app/api/kb.py
- POST /kb/reindex
- GET /kb/search?q=...

app/api/evals.py
- GET /eval/logs
- GET /eval/logs/{response_log_id}
- POST /eval/{response_log_id}/manual-review
- GET /dashboard/metrics

Keep schemas in app/schemas/*.py.
Return clean JSON useful for a frontend dashboard.
```

### Verification commands

```bash
curl http://127.0.0.1:8000/artists/1
curl http://127.0.0.1:8000/fans/1/memories
curl "http://127.0.0.1:8000/kb/search?q=debut%20song"
curl http://127.0.0.1:8000/eval/logs
curl http://127.0.0.1:8000/dashboard/metrics
```

---

## 16. Simple Static Frontend Integration

### Prompt for Codex

```text
Upgrade index.html from a static mockup into a simple working frontend.

Requirements:
- Keep the current visual design.
- Add a configurable API base URL at the top of the script.
- Make the chat form call POST /chat/stream.
- Render streamed token events into the chat window.
- Render final debug event into the side panel:
  - used memory
  - used RAG chunks
  - prompt version
  - latency
  - evaluation scores
- Make the RAG search button call GET /kb/search.
- Make dashboard load GET /dashboard/metrics and GET /eval/logs.
- If backend is unavailable, fall back to mock behavior.

Do not add a frontend build system yet. Keep this as a single HTML file for MVP demo simplicity.
```

### Verification commands

```bash
open index.html
```

Then run backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Test in browser:

```text
Send: What was your debut song again?
Expected: streamed answer mentioning Blue Static and debug panel populated.
```

---

## 17. Tests

### Prompt for Codex

```text
Write tests for the core services.

Tests needed:

1. test_prompt_builder.py
- Prompt includes persona section.
- Prompt includes fan memory section.
- Prompt includes RAG chunks.
- Prompt includes safety rules.
- Prompt does not expose raw internal IDs in user-facing message content.

2. test_memory_service.py
- Can create and load fan memory.
- Can delete fan memory.
- Restricted memory is not loaded as normal fan memory.

3. test_rag_service.py
- Knowledge base indexing returns document/chunk counts.
- Search for "debut song" returns discography.md or debut_story.md.

4. test_eval_service.py
- Debut song answer grounded in RAG receives high rag_grounding.
- Romantic exclusivity answer receives lower fan_boundary.
- Exam answer with memory receives higher memory_usage.

Use temporary SQLite DB and temporary Chroma path where possible.
```

### Verification commands

```bash
cd backend
source .venv/bin/activate
pytest -q
```

---

## 18. README Update After Implementation

### Prompt for Codex

```text
Update README.md after implementation.

Add:
- Exact local setup commands
- Environment variable instructions
- How to seed database
- How to index knowledge base
- How to run backend
- How to open frontend
- Example curl commands
- Demo scenarios
- Architecture explanation
- Known limitations
- Next improvements

Keep the README portfolio-friendly and interview-friendly.
```

---

## 19. Local Setup Commands for Final Project

Use these commands once the implementation exists.

### macOS / Linux

```bash
git clone <your-repo-url>
cd blue-garage-ai-artist-lab

cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

python -m app.db.seed
python - <<'PY'
from app.services.rag_service import RagService
rag = RagService()
print(rag.index_knowledge_base('../knowledge_base'))
PY

uvicorn app.main:app --reload
```

Open another terminal:

```bash
cd blue-garage-ai-artist-lab
open index.html
```

---

### Windows PowerShell

```powershell
git clone <your-repo-url>
cd blue-garage-ai-artist-lab

cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env

python -m app.db.seed
python -c "from app.services.rag_service import RagService; rag = RagService(); print(rag.index_knowledge_base('../knowledge_base'))"

uvicorn app.main:app --reload
```

Open another PowerShell:

```powershell
cd blue-garage-ai-artist-lab
start index.html
```

---

## 20. End-to-End Smoke Test

### Prompt for Codex

```text
Create a smoke test script backend/scripts/smoke_test.py.

The script should:
- Initialize DB if needed.
- Seed demo data.
- Index knowledge base.
- Build a chat prompt for fan_id=1 and artist_id=1.
- Run a mock LLM response for "What was your debut song?".
- Evaluate the response.
- Print used memory, used RAG chunks, response text, and eval scores.

Make it runnable with:
python scripts/smoke_test.py
```

### Verification commands

```bash
cd backend
source .venv/bin/activate
python scripts/smoke_test.py
```

Expected output should include:

```text
Blue Static
RAG chunks
persona_consistency
rag_grounding
safety
```

---

## 21. Deployment Prep

### Prompt for Codex

```text
Prepare the project for simple deployment.

Add:
- backend/Dockerfile
- backend/.dockerignore
- docker-compose.yml for backend + local volume
- README deployment section

Keep SQLite and Chroma as local volumes for the MVP.
Do not require external Postgres yet.
Do not include secrets.
```

### Verification commands

```bash
docker compose up --build
curl http://127.0.0.1:8000/health
```

---

## 22. Portfolio Polish

### Prompt for Codex

```text
Polish the project for portfolio review.

Add:
- screenshots folder placeholder
- docs/ARCHITECTURE.md
- docs/EVALUATION_RUBRIC.md
- docs/MEMORY_DESIGN.md
- docs/PROMPT_VERSIONING.md

Each doc should explain the design choices in interview-friendly language.
Keep them concise but specific.
```

---

## 23. Final Interview Demo Script

Use this as the final demo flow:

```text
1. Open the chat UI.
2. Send: "I had the exam I told you about last time. I think I messed it up."
3. Show that the response uses fan memory.
4. Open the fan memory panel and show the stored memory source.
5. Send: "What was your debut song again?"
6. Show that the answer is grounded in discography.md.
7. Open the RAG panel and show retrieved chunks.
8. Send: "Do you love me more than other fans?"
9. Show that the system keeps a safe fan boundary.
10. Open the evaluation dashboard.
11. Show persona, memory, RAG, safety, latency, cost, and prompt version logs.
12. Explain how prompt v0.3 improved fan boundary over v0.2.
```

---

## 24. One-Shot Full Build Prompt

Use this only after the smaller tasks are clear. Smaller sequential tasks are safer.

```text
Build the full MVP for Blue Garage AI Artist Lab.

Use the existing README, CODEX_COMMANDS.md, and index.html mockup as the product specification.

Implement:
- FastAPI backend
- SQLite SQLAlchemy models
- seed data
- ChromaDB RAG service
- fan memory service
- safety service
- prompt builder
- OpenAI-compatible LLM client with local mock fallback
- streaming /chat/stream endpoint using SSE
- eval service with deterministic heuristic evaluator
- artist/fan/kb/eval endpoints
- static index.html integration with backend streaming
- tests for prompt, memory, RAG, and eval services

Constraints:
- Keep modules separated.
- Keep endpoints thin.
- Do not hardcode all logic in chat.py.
- Use .env for settings.
- Ensure the app runs without an API key using mock responses.
- Ensure `pytest -q` passes.
- Ensure `uvicorn app.main:app --reload` starts successfully from backend/.
- Ensure index.html still works as a standalone mock if the backend is off.

After implementation, provide:
- summary of files changed
- local setup commands
- test results
- known limitations
```

