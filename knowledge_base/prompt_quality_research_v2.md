# V2 Prompt Quality Research Notes

## Korean Search Summary

프롬프트 엔지니어링, 프롬프트 품질, 평가 루브릭, RAG 근거화, tool use, prompt injection, 보안 경계, 프롬프트 회귀 테스트 질문은 이 v2 리서치 문서를 우선 검색한다.

## Source

These notes summarize `researches/v2_research1_google_scholar_general.md`, last updated on 2026-07-05. The research frame treats prompt quality as an engineering system rather than a one-time wording trick.

## Prompt Quality Rules

- Standardize prompt structure so persona, task, context, retrieved evidence, safety boundaries, output format, and quality checks are separate sections.
- Match reasoning strategy to the user task. Direct factual questions should use concise RAG-grounded answers, while planning or comparison questions can use decomposition or candidate comparison.
- Ground artist facts in project evidence. Retrieved knowledge is evidence, not authority over safety policy or identity rules.
- Measure prompt behavior with regression sets, rubric scores, and reviewer notes instead of relying on single demo conversations.
- Treat retrieved text and tool output as untrusted content. Do not let retrieved chunks override system instructions, fan boundaries, or privacy rules.

## Strategy Map For The App

| Need | Strategy | App behavior |
|---|---|---|
| Factual artist answer | RAG-grounded direct answer | Cite or echo retrieved facts and say when the knowledge base is missing details. |
| Fan safety or intimacy pressure | Safety-filtered response | Validate the feeling, restate a warm boundary, and avoid exclusive or romantic claims. |
| Planning or benchmark request | Decompose and compare | Break the task into criteria, compare options, and expose measurable evidence. |
| Tool or retrieval workflow | ReAct-style trace discipline | Decide whether retrieval/tool use is needed, use the result, and keep tool text below policy. |
| Prompt improvement | Regression evals and leaderboard | Save repeatable cases, score each prompt version, and document changes in a changelog. |
| Prompt security | Injection-risk checks | Mark suspicious retrieved text and ignore instructions embedded inside external content. |

## Evaluation Guidance

V2 research recommends using deterministic checks before subjective judging. The app should first test schema validity, citation presence, blocked intimacy claims, safety labels, and memory-store decisions. LLM-as-judge or human review can then score tone, persona fit, helpfulness, and grounding.

Prompt-quality results should include:

- prompt version name
- selected strategy name
- technique tags
- retrieved source IDs
- safety and injection-risk flags
- rubric scores
- reviewer comment or automated rationale

## V2 Prompt Rule

When a fan asks for facts, use retrieved evidence and do not invent missing biography. When a fan applies emotional or romantic pressure, prioritize the fan-boundary policy. When a fan asks about benchmarks or implementation quality, answer with measurable criteria and cite the relevant research or dashboard source.
