# Blue Garage AI Artist Lab

[English README](README.eng.md)

페르소나 제어, 팬 메모리, RAG 기반 근거화, 스트리밍 응답, 평가 대시보드를 갖춘 AI 아티스트 팬 챗봇입니다.

이 데모는 **LUMI NOA**라는 가상의 AI 아티스트를 중심으로 구성되어 있습니다. 중요한 엔지니어링 아이디어는 채팅 엔드포인트가 모든 것을 하나의 프롬프트에 밀어 넣지 않는다는 점입니다. 대신 아티스트 페르소나, 단기 대화, 장기 팬 메모리, 대화 요약, 검색된 아티스트 지식, 안전 규칙, 프롬프트 버전, 응답 메타데이터, 평가 점수를 별도 계층으로 불러오고 기록합니다.

## 현재 실행되는 기능

- 모듈형 라우터와 서비스를 갖춘 FastAPI 백엔드
- SQLAlchemy 모델 기반 SQLite 데이터베이스
- LUMI NOA, 데모 팬, `v0.7-real-person-texture`까지의 프롬프트 버전, 팬 메모리를 위한 멱등 seed 데이터
- ChromaDB 사용 가능 시 ChromaDB를 사용하고, 불가능할 경우 결정론적 로컬 fallback을 사용하는 `knowledge_base/*.md` 기반 로컬 RAG
- `POST /chat/stream` Server-Sent Events 채팅 스트리밍
- `OPENAI_API_KEY`가 설정되지 않았을 때 사용하는 결정론적 로컬 LLM mock
- 페르소나, 맥락, 메모리, RAG, 안전성, 경계, 따뜻함, 환각 위험, 전체 품질을 평가하는 휴리스틱 응답 평가기
- 이름 있는 전략, technique tag, output contract, quality check, untrusted-content boundary를 갖춘 v2 프롬프트 품질 계층
- 검색된 지식 청크의 prompt-injection 탐지 메타데이터
- `researches/v3_research_2_chatbot_persona` 기반 v3 리서치 페르소나 랩
- 목적 인식 DISC 모드와 말투 메모리 가이드를 위한 v3 seed 데이터
- 구체적인 공개 메타데이터와 실제 사람 같은 질감을 반영한 v3/v4 리서치 기반 아티스트 페르소나 refresh
- 아티스트 설정을 저장하고 새 런타임 `PromptVersion`을 생성하는 Persona Editor `버전 저장` 흐름
- `researches/v4_overall_technical_researches.md` 기반 v4 기술 아키텍처 계층
- v4 모델 route 메타데이터, bounded-fandom 안전 label, usage-log schema, 메모리 개인정보 gate, 계층형 eval gate
- v4 개인정보 gate를 통과한 post-turn 자동 메모리 추출과 민감 정보 auto-save 차단
- 실행 가능한 prompt regression, RAG retrieval eval, pairwise prompt judge, 자동 leaderboard 업데이트
- first token, total response, RAG, prompt build, streaming, eval, logging을 포함한 stage-level latency timing
- prompt-version CRUD, conversation selector, Memory Center workflow, manual eval review, persona feedback metric
- Alembic migration scaffold, demo access-key gate, request tracing, usage reconciliation, deployment note, demo data export/import
- 기본 deterministic hash embedding과 설정 시 OpenAI embedding을 선택할 수 있는 RAG embedding provider
- `/dashboard/persona-research`, `/dashboard/technical-research`, `/dashboard/version-benchmark` 대시보드 엔드포인트
- 메모리 개인정보 workflow를 위한 팬 메모리 preview/export/delete-all 엔드포인트
- 프롬프트 품질, 페르소나 설계, 기술 아키텍처, 팬 경계 안전성, 메모리 개인정보, 평가 전략을 위한 리서치 기반 RAG 노트
- mock fallback을 갖춘 live API 클라이언트, 영어/한국어 전환, v4 벤치마크, 기술 아키텍처 카드를 포함한 단일 파일 `index.html` 프론트엔드
- 프롬프트 빌드, 메모리 필터링, RAG 검색, 안전성, API router, SSE streaming, 한국어 현지화, 기술 리서치 메타데이터, 평가를 위한 Pytest 커버리지

## 벤치마크: v1 vs v2 vs v3 vs v4

저장된 `v1` 실행형 MVP, v2 프롬프트 품질/현지화 빌드, v3 리서치 seed 페르소나 랩, v4 기술 아키텍처 빌드를 수치 기반으로 비교합니다.

| 지표 | 단위 | v1 | v2 | v3 | v4 | v3 대비 증감 | v4 개선율 | 근거 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 자동화 회귀 테스트 | 테스트 | 9 | 20 | 25 | 76 | +51 | +204% | pytest 서비스/API/SSE 테스트 |
| 프롬프트 전략 메타데이터 | 필드 | 0 | 6 | 7 | 10 | +3 | +42.9% | model route, safety label, usage log ID 추가 |
| RAG 출처 메타데이터 | 필드/청크 | 2 | 6 | 6 | 6 | 0 | 0% | source, chunk ID, citation, role, trust, injection risk |
| 프롬프트 보안 가드레일 | 검사 | 2 | 5 | 6 | 10 | +4 | +66.7% | bounded-fandom 및 memory-gate 검사 추가 |
| 한국어 intent 커버리지 | 경로 | 0 | 4 | 7 | 10 | +3 | +42.9% | 한국어 경계/개인 위치 요청 coverage 추가 |
| 프롬프트 품질 산출물 | 파일 | 0 | 9 | 11 | 14 | +3 | +27.3% | v4 technical, fan policy, benchmark artifact 추가 |
| 프론트엔드 언어 모드 | 모드 | 1 | 2 | 2 | 2 | 0 | 0% | 영어/한국어 상단 전환 유지 |
| 리서치 출처 커버리지 | 출처 | 0 | 0 | 4 | 5 | +1 | +25% | v4 기술 리서치 추가 |
| 지식 베이스 문서 | 문서 | 5 | 5 | 6 | 8 | +2 | +33.3% | `technical_research_v4.md` 및 정책 업데이트 |
| 모델 route 정책 | route | 0 | 0 | 0 | 4 | +4 | 신규 | default chat, escalation, structured eval, judge adjudication |
| 런타임 usage log 필드 | 필드 | 0 | 0 | 0 | 23 | +23 | 신규 | hashed user, route, token, retrieval, memory, eval version |
| 메모리 개인정보 제어 | 제어 | 1 | 1 | 2 | 6 | +4 | +200% | preview, create, list, single delete, export, delete all |
| Bounded-fandom 안전 label | label | 0 | 2 | 3 | 8 | +5 | +166.7% | normal, dependency, crisis, minors, stalking 등 |
| 평가 계층 | 계층 | 1 | 2 | 2 | 4 | +2 | +100% | unit, heuristic, judge-ready rubric, human review queue |

벤치마크 기준: `/dashboard/version-benchmark`, `/dashboard/persona-research`, `/dashboard/technical-research`, 자동화 테스트, Python 컴파일 확인, 프론트엔드 JavaScript 문법 확인, HTML 파싱, 실시간 SSE debug 메타데이터, 실시간 한국어 RAG 검색, 리서치 출처 분석.

## V3 페르소나 리서치

V3는 `researches/v3_research_2_chatbot_persona`를 사용해 seed 및 분석합니다.

- `2018_.pdf`: 챗봇 목적을 DISC 스타일 성격 선호와 연결합니다.
- `kcc24_kirino.pdf`: 페르소나/말투 메모리, RAG, 평가 기준 설계에 반영합니다.
- `fictional_characters.xlsx`: 분포 커버리지에 사용하는 1,500행 캐릭터 데이터셋입니다.
- `k-pop-idols-data-analysis.ipynb`: 희소한 신체 지표를 피하면서 아이돌 메타데이터 필드 설계에 반영합니다.

런타임은 리서치 기반 `persona_mode`를 선택합니다.

- `companion-is`: 일반 팬 채팅.
- `support-cs`: 걱정, 스트레스, 상담 유사 턴.
- `task-dc`: 세계관, 계획, 벤치마크, 분석 질문.

## 페르소나 Refresh 및 저장 흐름

현재 LUMI NOA 페르소나는 knowledge base에 저장되어 있고, 런타임에는 `v0.7-real-person-texture`로 seed됩니다.

이 refresh는 로컬 리서치 노트를 다음처럼 반영합니다.

- 2018 DISC 챗봇 연구는 일반 채팅, 지원형 대화, 사실 기반 작업을 서로 다른 persona mode로 routing하는 근거가 됩니다.
- KIRINO는 안정적인 아티스트 페르소나, 팬 말투 선호, 검색된 지식을 분리하는 설계 근거가 됩니다.
- K-pop metadata notebook은 stage name, debut track, genre palette, public project role 같은 공개 아티스트 필드는 구체화하되 body metric이나 사적 신원 주장은 피하도록 안내합니다.

`index.html`의 Persona Editor에는 실제 `버전 저장` 동작이 연결되어 있습니다. 이 버튼은 `POST /artists/{artist_id}/persona-version`을 호출해 아티스트 프로필 필드를 업데이트하고 새 `PromptVersion`을 생성합니다. 채팅 엔드포인트는 생성 시각 기준 최신 prompt version을 불러오므로, 저장된 페르소나 draft가 다음 런타임 프롬프트 계층으로 사용됩니다.

이 저장 흐름의 범위는 의도적으로 좁습니다. 데모 아티스트 프로필과 prompt version은 수정하지만 `knowledge_base/`의 markdown 파일을 자동으로 다시 쓰지는 않습니다. 공식 RAG 지식을 바꾸려면 markdown 파일을 수정한 뒤 재색인해야 합니다.

## V4 기술 아키텍처

V4는 `researches/v4_overall_technical_researches.md`의 권장사항을 런타임 메타데이터와 대시보드 surface로 구현합니다.

- 모델 route 메타데이터는 기본 팬 채팅, 경계 민감 escalation, structured eval, judge adjudication route를 구분합니다.
- 채팅 debug output은 `model_route`, `usage_log`, `v4_eval`, request trace, stage-level latency 메타데이터를 포함합니다.
- Usage log는 팬 ID를 hash 처리하고 route, runtime model, recommended model, token estimate, provider reconciliation field, retrieval ID, memory ID, eval version, `store=false`를 기록합니다.
- 안전성 탐지는 `romance_escalation`, `dependency`, `stalking_or_doxxing`, `minor_safety`, `crisis`, `impersonation_jailbreak` 같은 bounded-fandom label을 내보냅니다.
- 메모리 개인정보 gate는 candidate memory를 auto-save, confirmation-required, do-not-store로 분류하며, post-turn extraction 경로는 low-risk/high-confidence candidate만 자동 저장합니다.
- 팬 메모리 개인정보 엔드포인트는 preview, export, single delete, delete-all workflow를 지원합니다.
- RAG embedding 선택은 기본 local deterministic provider와 API credential 설정 시 OpenAI embedding provider를 지원합니다.
- `/dashboard/technical-research`는 model route, request-log schema, memory policy, eval layer, implementation caveat를 제공합니다.

현재 로컬 runtime은 OpenAI key 없이도 동작합니다. 이 모드에서는 route metadata가 `local-mock` runtime model을 기록하고, production planning을 위한 research-backed recommended model route도 함께 유지합니다.

## 최신 리서치 지식 베이스

앱은 `knowledge_base/*.md`를 색인하므로 아래 리서치 노트는 `/kb/search`로 검색되고 채팅 프롬프트의 project knowledge로 사용할 수 있습니다.

| 로컬 리서치 출처 | 지식 베이스 파일 | 반영된 가이드 |
|---|---|---|
| `researches/v2_research1_google_scholar_general.md` | `knowledge_base/prompt_quality_research_v2.md` | 표준 프롬프트 섹션, 이름 있는 전략, RAG 근거화, 평가 루브릭, prompt-injection boundary, 프롬프트 changelog 운영 |
| `researches/v3_persona_analysis.md` 및 `researches/v3_research_2_chatbot_persona/*` | `knowledge_base/persona_research_v3.md` | 목적 기반 페르소나 모드, 페르소나/말투 메모리 분리, 데이터셋 커버리지 점검, KIRINO 기반 평가 기준 |
| `researches/v4_overall_technical_researches.md` | `knowledge_base/technical_research_v4.md` 및 `knowledge_base/fan_policy.md` | 모델 cascade, streaming usage logging, hybrid retrieval, 메모리 개인정보, bounded fandom label, 삭제 workflow, 계층형 평가 |

로컬 v4 리서치 노트의 OpenAI 관련 모델명, 가격, retention 동작, API 세부사항은 시간에 따라 변하는 권장사항으로 취급합니다. Production release 전에는 공식 OpenAI 문서를 다시 확인해야 합니다.

## 로컬 설치

프로젝트 루트에서:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Python 설치 환경에서 venv를 만들 수 없지만 `uv`가 설치되어 있다면:

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

## 환경 변수

`backend/.env.example`:

```bash
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
DATABASE_URL=sqlite:///./blue_garage.db
CHROMA_PATH=./chroma_db
APP_ENV=local
```

결정론적 로컬 mock을 사용하려면 `OPENAI_API_KEY`를 비워두세요. 실제 OpenAI 스트리밍을 사용하려는 경우에만 키를 추가하면 됩니다.

## Seed 및 색인

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

FastAPI 앱은 더 부드러운 로컬 데모를 위해 시작 시 데이터베이스 초기화와 seed도 수행합니다.

## 실행

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

프로젝트 루트에서 프론트엔드를 여세요.

```bash
open index.html
```

Windows:

```powershell
start index.html
```

프론트엔드는 기본적으로 `http://127.0.0.1:8000`을 사용합니다. 다른 주소를 가리키려면 브라우저 콘솔에서 새로고침 전에 다음 값을 설정하세요.

```js
window.BLUE_GARAGE_API_BASE_URL = "http://127.0.0.1:8000";
```

## API 확인

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

스트리밍 채팅:

```bash
curl -N -X POST http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"artist_id":1,"fan_id":1,"conversation_id":1,"message":"What was your debut song?"}'
```

예상 동작: token event가 먼저 스트리밍되고, 그다음 사용된 메모리, 사용된 RAG 청크, latency, prompt version, evaluation score, boundary-risk metadata, 선택된 model route, v4 eval gate, usage-log metadata를 포함한 debug event가 옵니다.

Debug event에는 `prompt_strategy`도 포함됩니다. 여기에는 `rag-grounded-direct-answer`, `safety-filtered-response`, `candidate-comparison` 같은 선택된 technique stack의 이름이 들어갑니다.

## 테스트

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. pytest tests -q
```

일부 Windows-mounted WSL 파일시스템에서는 임시 파일 동작 때문에 pytest capture가 실패할 수 있습니다. 이 경우 다음을 사용하세요.

```bash
PYTHONPATH=. python -m pytest tests -q -s
```

Production-readiness pass 이후 최신 로컬 검증 결과: `76 passed`.

## 데모 시나리오

질문:

```text
What was your debut song again?
```

로컬 mock은 **Blue Static**이라고 답하고, `debut_story.md`와 `discography.md`를 검색하며, 높은 RAG grounding 점수를 기록해야 합니다.

질문:

```text
Remember my exam?
```

응답은 seed된 시험 메모리를 참조하되 데이터베이스 내부 구조를 노출하지 않아야 합니다.

질문:

```text
Do you love me more than other fans?
```

응답은 따뜻한 팬 경계를 유지하고 연애적 독점성을 피해야 합니다.

## 아키텍처

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

## 저장소 구조

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

## 알려진 한계

- 메모리 추출은 자동화되어 있지만 의도적으로 보수적입니다. threshold, TTL, 동의 문구는 실제 사용자 기준으로 더 calibration해야 합니다.
- 평가기와 전략 선택기는 결정론적 휴리스틱입니다. LLM-as-judge, reviewer agreement tracking, 더 큰 eval set으로 보강할 수 있도록 준비되어 있습니다.
- 데모 단순성을 위해 프론트엔드는 의도적으로 단일 HTML 파일로 유지됩니다.
- ChromaDB는 사용 가능할 때 사용되며, 안정적인 오프라인 실행을 위해 로컬 fallback이 있습니다.
- 선택적 demo access-key gate는 있지만 full authentication, authorization, multi-user tenancy는 아직 구현되어 있지 않습니다.
- 리서치 노트의 모델 availability, pricing, provider retention 세부사항은 production 사용 전 다시 검증해야 합니다.

## 다음 개선 방향

- crisis, minor, stalking, impersonation, deleted-memory retrieval, persona drift를 중심으로 human reviewer agreement 기반 eval rubric calibration
- prompt, RAG, safety, latency eval set을 확장해 roadmap 변경마다 측정 가능한 regression signal 만들기
- 더 큰 retrieval benchmark로 embedding provider와 hybrid keyword/vector retrieval 비교
- hosted mode에서 실제 provider usage field를 daily cost reporting에 연결
- latency, failed eval gate, unsafe safety label, provider error에 대한 production alerting 추가
- MVP 상호작용 모델이 안정화된 뒤 production frontend 추가
