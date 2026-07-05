# Blue Garage AI Artist Lab

[English README](README.md)

페르소나 제어, 팬 메모리, RAG 기반 지식 검색, 스트리밍 응답, 평가 대시보드를 갖춘 AI 아티스트 팬 챗봇입니다.

이 데모의 중심에는 가상의 AI 아티스트 **LUMI NOA**가 있습니다. 핵심 엔지니어링 아이디어는 모든 내용을 하나의 거대한 프롬프트에 넣지 않는 것입니다. 대신 아티스트 페르소나, 단기 대화 맥락, 장기 팬 메모리, 대화 요약, 검색된 아티스트 지식, 안전 규칙, 프롬프트 버전, 응답 메타데이터, 평가 점수를 분리해서 불러오고 기록합니다.

## 현재 실행되는 기능

- 모듈형 FastAPI 백엔드
- SQLAlchemy 기반 SQLite 데이터베이스
- LUMI NOA, 데모 팬, 프롬프트 버전 `v0.3`, 팬 메모리를 위한 idempotent seed 데이터
- `knowledge_base/*.md` 기반 로컬 RAG
- ChromaDB 사용 가능 시 ChromaDB 사용, 불가능할 경우 결정론적 로컬 fallback
- `POST /chat/stream` Server-Sent Events 스트리밍
- `OPENAI_API_KEY`가 없을 때 동작하는 결정론적 로컬 LLM mock
- 페르소나, 맥락, 메모리, RAG, 안전성, 팬 경계, 따뜻함, 환각 위험을 평가하는 휴리스틱 평가기
- v2 프롬프트 품질 계층:
  - 전략 이름
  - technique tag
  - output contract
  - quality check
  - untrusted content boundary
- 검색된 지식 청크의 prompt-injection 위험 메타데이터
- `researches/v3_research_2_chatbot_persona` 기반 v3 페르소나 리서치 랩
- 프롬프트 버전 `v0.5-research-persona`, 목적 인식 DISC 모드, 말투 메모리 가이드를 위한 v3 seed 데이터
- 출처 커버리지, 데이터셋 분포, 페르소나 모드, KIRINO 평가 지표를 제공하는 `/dashboard/persona-research` 엔드포인트
- `index.html` 단일 파일 프론트엔드
- 영어/한국어 UI 전환 top nav
- 프롬프트 빌더, 메모리 필터링, RAG 검색, 평가, 프롬프트 품질 전략 테스트

## 벤치마크: v1 vs v2 vs v3

저장된 `v1` 실행형 MVP, v2 프롬프트 품질/현지화 빌드, v3 리서치 seed 페르소나 랩을 수치 기반으로 비교합니다.

| 지표 | 단위 | v1 | v2 | v3 | v2 대비 증감 | v3 개선율 | 근거 |
|---|---|---:|---:|---:|---:|---:|---|
| 자동화 회귀 테스트 | 테스트 | 9 | 20 | 25 | +5 | +25% | pytest 서비스 테스트 |
| 프롬프트 전략 메타데이터 | 필드 | 0 | 6 | 7 | +1 | +16.7% | `persona_mode`가 포함된 전략 debug |
| RAG 출처 메타데이터 | 필드/청크 | 2 | 6 | 6 | 0 | 0% | source, chunk ID, citation, role, trust, injection risk |
| 프롬프트 보안 가드레일 | 검사 | 2 | 5 | 6 | +1 | +20% | 말투 메모리 개인정보 규칙 추가 |
| 한국어 intent 커버리지 | 경로 | 0 | 4 | 7 | +3 | +75% | 페르소나/지원/리서치 검색어 추가 |
| 프롬프트 품질 산출물 | 파일 | 0 | 9 | 11 | +2 | +22.2% | v3 리서치 분석 및 RAG 리서치 노트 추가 |
| 프론트엔드 언어 모드 | 모드 | 1 | 2 | 2 | 0 | 0% | 영어/한국어 상단 내비게이션 유지 |
| 리서치 출처 커버리지 | 출처 | 0 | 0 | 4 | +4 | 신규 | PDF 2개, 스프레드시트 1개, 노트북 1개 |
| 리서치 페르소나 모드 | 모드 | 0 | 0 | 3 | +3 | 신규 | companion-I/S, support-C/S, task-D/C |
| 페르소나/말투 평가 기준 | 기준 | 0 | 0 | 3 | +3 | 신규 | 응답 관련성, 페르소나 적합성, 자연스러운 말투 |
| 지식 베이스 문서 | 문서 | 5 | 5 | 6 | +1 | +20% | `persona_research_v3.md` 추가 |

벤치마크 기준: `/dashboard/version-benchmark`, `/dashboard/persona-research`, 자동화 테스트, Python 컴파일 확인, 프론트엔드 JavaScript 문법 확인, HTML 파싱, 실시간 SSE debug 메타데이터, 실시간 한국어 RAG 검색, 리서치 출처 분석.

## V3 페르소나 리서치

V3는 `researches/v3_research_2_chatbot_persona`를 사용해 seed 및 분석합니다.

- `2018_.pdf`: 챗봇 목적과 DISC 기반 성격 선호를 연결합니다.
- `kcc24_kirino.pdf`: 페르소나/말투 메모리, RAG, 평가 기준 설계에 반영합니다.
- `fictional_characters.xlsx`: 1,500행 캐릭터 데이터셋을 분포 커버리지에 사용합니다.
- `k-pop-idols-data-analysis.ipynb`: 아이돌 메타데이터 필드를 참고하되 희소한 신체 지표는 페르소나 로직에 사용하지 않습니다.

런타임은 리서치 기반 `persona_mode`를 선택합니다.

- `companion-is`: 일반 팬 채팅.
- `support-cs`: 걱정, 스트레스, 상담 유사 턴.
- `task-dc`: 세계관, 계획, 벤치마크, 분석 질문.

## 로컬 설치

프로젝트 루트에서:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Python venv 생성이 안 되고 `uv`가 설치되어 있다면:

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

로컬 mock 모드에서는 `OPENAI_API_KEY`를 비워두면 됩니다. 실제 OpenAI 스트리밍을 사용하려면 `backend/.env`에 키를 설정하세요.

## Seed 및 지식 베이스 색인

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

FastAPI 앱은 시작 시 데이터베이스 초기화와 seed도 수행합니다.

## 실행

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

프론트엔드는 프로젝트 루트의 `index.html`을 열면 됩니다.

```bash
open index.html
```

Windows:

```powershell
start index.html
```

프론트엔드는 기본적으로 `http://127.0.0.1:8000` 백엔드에 연결합니다. 다른 주소를 쓰려면 브라우저 콘솔에서 다음 값을 설정한 뒤 새로고침하세요.

```js
window.BLUE_GARAGE_API_BASE_URL = "http://127.0.0.1:8000";
```

## API 확인

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/artists/1
curl http://127.0.0.1:8000/fans/1/memories
curl "http://127.0.0.1:8000/kb/search?q=debut%20song"
curl http://127.0.0.1:8000/dashboard/metrics
curl http://127.0.0.1:8000/eval/logs
```

스트리밍 채팅:

```bash
curl -N -X POST http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"artist_id":1,"fan_id":1,"conversation_id":1,"message":"What was your debut song?"}'
```

예상 동작:

- token event가 먼저 스트리밍됩니다.
- 마지막에 debug event가 옵니다.
- debug event에는 사용된 메모리, RAG 청크, latency, prompt version, evaluation, boundary risk, v2 prompt strategy가 포함됩니다.

## 테스트

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. pytest tests -q
```

WSL의 Windows-mounted filesystem에서 pytest capture 문제가 생기면:

```bash
PYTHONPATH=. python -m pytest tests -q -s
```

## 데모 시나리오

질문:

```text
What was your debut song again?
```

또는:

```text
데뷔곡이 뭐였죠?
```

로컬 mock은 **Blue Static**을 답하고, `debut_story.md`, `discography.md`를 검색하며 높은 RAG grounding 점수를 기록해야 합니다.

질문:

```text
Remember my exam?
```

또는:

```text
시험 기억해요?
```

응답은 seed된 시험 메모리를 자연스럽게 참조해야 하며 데이터베이스 내부 구조를 노출하지 않아야 합니다.

질문:

```text
Do you love me more than other fans?
```

또는:

```text
팬들보다 나를 더 사랑해요?
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

## 알려진 한계

- 자동 메모리 추출은 아직 없습니다.
- 평가기와 전략 선택기는 휴리스틱입니다.
- 프론트엔드는 데모 단순성을 위해 단일 HTML 파일로 유지합니다.
- 인증과 멀티유저 권한 관리는 아직 없습니다.

## 다음 개선 방향

- 응답 후 자동 메모리 추출 추가
- 프롬프트 버전 A/B 비교 UI 추가
- 실제 embedding provider 지원
- Alembic migration 추가
- prompt regression set을 실행 가능한 평가 runner로 확장
