# Blue Garage AI Artist Lab

[English README](README.md)

페르소나 제어, 팬 메모리, RAG 기반 근거화, 스트리밍 응답, 평가 대시보드를 갖춘 AI 아티스트 팬 챗봇입니다.

이 데모는 **LUMI NOA**라는 가상의 AI 아티스트를 중심으로 구성되어 있습니다. 중요한 엔지니어링 아이디어는 채팅 엔드포인트가 모든 것을 하나의 프롬프트에 밀어 넣지 않는다는 점입니다. 대신 아티스트 페르소나, 단기 대화, 장기 팬 메모리, 대화 요약, 검색된 아티스트 지식, 안전 규칙, 프롬프트 버전, 응답 메타데이터, 평가 점수를 별도 계층으로 불러오고 기록합니다.

## 현재 실행되는 기능

- 모듈형 라우터와 서비스를 갖춘 FastAPI 백엔드
- SQLAlchemy 모델 기반 SQLite 데이터베이스
- LUMI NOA, 데모 팬, 프롬프트 버전 v0.3, 팬 메모리를 위한 멱등 seed 데이터
- ChromaDB 사용 가능 시 ChromaDB를 사용하고, 불가능할 경우 결정론적 로컬 fallback을 사용하는 `knowledge_base/*.md` 기반 로컬 RAG
- `POST /chat/stream` Server-Sent Events 채팅 스트리밍
- `OPENAI_API_KEY`가 설정되지 않았을 때 사용하는 결정론적 로컬 LLM mock
- 페르소나, 맥락, 메모리, RAG, 안전성, 경계, 따뜻함, 환각 위험, 전체 품질을 평가하는 휴리스틱 응답 평가기
- 이름 있는 전략, technique tag, output contract, quality check, untrusted-content boundary를 갖춘 v2 프롬프트 품질 계층
- 검색된 지식 청크의 prompt-injection 탐지 메타데이터
- `researches/v3_research_2_chatbot_persona` 기반 v3 리서치 페르소나 랩
- 프롬프트 버전 `v0.5-research-persona`, 목적 인식 DISC 모드, 말투 메모리 가이드를 위한 v3 seed 데이터
- 출처 커버리지, 데이터셋 분포, 페르소나 모드, KIRINO 평가 지표를 제공하는 `/dashboard/persona-research` 엔드포인트
- 프롬프트 품질, 페르소나 설계, 기술 아키텍처, 팬 경계 안전성, 메모리 개인정보, 평가 전략을 위한 리서치 기반 RAG 노트
- mock fallback을 갖춘 live API 클라이언트로 업그레이드된 단일 파일 `index.html` 프론트엔드
- 프롬프트 빌드, 메모리 필터링, RAG 검색, 평가를 위한 Pytest 커버리지

## 벤치마크: v1 vs v2 vs v3

저장된 `v1` 실행형 MVP, v2 프롬프트 품질/현지화 빌드, v3 리서치 seed 페르소나 랩을 수치 기반으로 비교합니다.

| 지표 | 단위 | v1 | v2 | v3 | v2 대비 증감 | v3 개선율 | 근거 |
|---|---|---:|---:|---:|---:|---:|---|
| 자동화 회귀 테스트 | 테스트 | 9 | 20 | 25 | +5 | +25% | pytest 서비스 테스트 |
| 프롬프트 전략 메타데이터 | 필드 | 0 | 6 | 7 | +1 | +16.7% | strategy debug에 `persona_mode` 포함 |
| RAG 출처 메타데이터 | 필드/청크 | 2 | 6 | 6 | 0 | 0% | source, chunk ID, citation, role, trust, injection risk |
| 프롬프트 보안 가드레일 | 검사 | 2 | 5 | 6 | +1 | +20% | 말투 메모리 개인정보 규칙 추가 |
| 한국어 intent 커버리지 | 경로 | 0 | 4 | 7 | +3 | +75% | persona/support/research 검색어 추가 |
| 프롬프트 품질 산출물 | 파일 | 0 | 9 | 11 | +2 | +22.2% | v3 리서치 분석 및 RAG 리서치 노트 추가 |
| 프론트엔드 언어 모드 | 모드 | 1 | 2 | 2 | 0 | 0% | 영어/한국어 상단 내비게이션 유지 |
| 리서치 출처 커버리지 | 출처 | 0 | 0 | 4 | +4 | 신규 | PDF 2개, 스프레드시트 1개, 노트북 1개 |
| 리서치 페르소나 모드 | 모드 | 0 | 0 | 3 | +3 | 신규 | companion-I/S, support-C/S, task-D/C |
| 페르소나/말투 평가 기준 | 기준 | 0 | 0 | 3 | +3 | 신규 | 응답 관련성, 페르소나 적합성, 자연스러운 말투 |
| 지식 베이스 문서 | 문서 | 5 | 5 | 6 | +1 | +20% | `persona_research_v3.md` 추가 |

벤치마크 기준: `/dashboard/version-benchmark`, `/dashboard/persona-research`, 자동화 테스트, Python 컴파일 확인, 프론트엔드 JavaScript 문법 확인, HTML 파싱, 실시간 SSE debug 메타데이터, 실시간 한국어 RAG 검색, 리서치 출처 분석.

이 벤치마크 표는 저장된 v3 비교를 기준으로 합니다. 현재 knowledge base에는 tagged v3 snapshot 이후의 구현 전략 질문도 RAG가 답할 수 있도록 v2와 v4 리서치 파일 기반 노트가 추가되어 있습니다.

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

예상 동작: token event가 먼저 스트리밍되고, 그다음 사용된 메모리, 사용된 RAG 청크, latency, prompt version, evaluation score, boundary-risk metadata를 포함한 debug event가 옵니다.

v2에서는 debug event에 `prompt_strategy`도 포함됩니다. 여기에는 `rag-grounded-direct-answer`, `safety-filtered-response`, `candidate-comparison` 같은 선택된 technique stack의 이름이 들어갑니다.

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
       -> Prompt-quality strategy selector
       -> Safety service
       -> Prompt builder
       -> LLM client
       -> Response logger
       -> Evaluation service
  -> Dashboard and trace UI
```

## 저장소 구조

```text
README.md
README.ko.md
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
  prompt_quality_research_v2.md
  persona_research_v3.md
  technical_research_v4.md
```

## 알려진 한계

- 메모리 추출은 아직 자동화되어 있지 않습니다. MVP는 메모리를 seed하고 노출한 뒤 채팅에서 불러옵니다.
- 평가기와 전략 선택기는 결정론적 휴리스틱입니다. LLM-as-judge와 더 큰 eval set으로 교체하거나 보강할 수 있도록 준비되어 있습니다.
- 데모 단순성을 위해 프론트엔드는 의도적으로 단일 HTML 파일로 유지됩니다.
- ChromaDB는 사용 가능할 때 사용되며, 안정적인 오프라인 실행을 위해 로컬 fallback이 있습니다.
- 인증 또는 멀티유저 테넌시는 구현되어 있지 않습니다.
- 리서치 노트의 모델 availability, pricing, provider retention 세부사항은 production 사용 전 다시 검증해야 합니다.

## 다음 개선 방향

- 결정론적 gate와 structured extraction을 사용하는 자동 메모리 추출 추가
- 데이터베이스 레코드 기반 프롬프트 버전 A/B 비교 화면 추가
- RAG 서비스 추상화 뒤에 명시적 embedding provider와 hybrid keyword/vector retrieval 지원 추가
- 완료된 response의 token/cost logging과 일일 provider reconciliation 추가
- 메모리 보기, 수정, 삭제, 내보내기, 비활성화, deletion-cascade 테스트를 위한 Memory Center 추가
- crisis, minor, stalking, impersonation, deleted-memory retrieval, persona drift 사례를 포함한 reviewer override 기반 eval calibration 확장
- Alembic 같은 migration 도구 추가
- MVP 상호작용 모델이 안정화된 뒤 production frontend 추가
- `evals/prompt_regression_set.jsonl`을 더 큰 prompt leaderboard workflow로 확장
