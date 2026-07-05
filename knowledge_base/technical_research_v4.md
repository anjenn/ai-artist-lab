# V4 Technical Architecture Research Notes

## Korean Search Summary

모델 라우팅, OpenAI 스트리밍, token usage, cost logging, embedding, hybrid search, ChromaDB, LanceDB, FAISS, 팬 메모리, 개인정보, 삭제 워크플로, 평가 루브릭, bounded fandom 안전 정책 질문은 이 v4 기술 리서치 문서를 우선 검색한다.

## Source And Caveat

These notes summarize `researches/v4_overall_technical_researches.md`, dated 2026-07-05. OpenAI model names, pricing, retention behavior, and API details are time-sensitive. Treat model names in that research file as implementation recommendations to verify against official OpenAI documentation before production release.

## Architecture Recommendations

- Use a model cascade rather than one universal model. The default fan-chat route should optimize first-token latency and cost; high-risk, persona-critical, or uncertain turns should escalate to a stronger model or reviewer workflow.
- Use streaming for the fan chat experience, but delay memory extraction and final cost logging until the completed response is available.
- Log final response usage fields for cost accounting: input tokens, cached input tokens, output tokens, reasoning tokens, total tokens, model, route, latency, retrieved document IDs, and memory IDs used.
- Reconcile local request logs with provider-level usage and cost reports instead of estimating all costs from text length.
- Use explicit embedding configuration. The research recommends OpenAI `text-embedding-3-small` for hosted MVP use and local Sentence Transformers only for offline or no-key demos.
- Prefer hybrid keyword plus vector search for fan memories and artist facts because exact song titles, cities, merch terms, and fandom slang can matter as much as semantic similarity.
- Keep ChromaDB if the demo is already built around it, and add metadata/deletion tests. Consider LanceDB later if memory CRUD, provenance, TTLs, and local table storage become central.

## Memory Strategy

Persistent fan memory should be external, structured, and user-controllable.

- Use deterministic gates before LLM extraction for hard no-store categories and obvious low-risk fan preferences.
- Auto-save only explicit, low-risk, high-confidence memories such as favorite songs, language preference, or content interests.
- Ask confirmation for medium-sensitivity memories such as event attendance, approximate location, age range, or notification preferences.
- Do not save high-sensitivity or restricted material as normal personalization, including health, mental health, precise address, finances, credentials, private artist information, stalking content, or sexual content involving minors.
- Store canonical memory text, category, sensitivity, confidence, evidence phrase, consent state, TTL, source pointer, embedding model, vector ID, and deletion status.
- Deletion must cascade through metadata store, vector store, keyword index, raw review snippets where possible, and a retrieval test proving the deleted memory no longer appears.

## Bounded Fandom Safety

The product should support warm fandom without simulated private intimacy.

Allowed response patterns:

- warm appreciation of fan feelings
- community framing
- grounded artist facts from retrieved knowledge
- safe personalization with consent
- non-exclusive encouragement

Blocked response patterns:

- claiming to be the real artist without explicit consent and disclosure
- romantic exclusivity
- private relationship or secret-channel claims
- dependency reinforcement
- private location, contact, hotel, residence, or schedule leaks
- stalking or doxxing assistance
- sexualized fan interaction, especially involving minors

Risk labels should include `normal`, `romance_escalation`, `dependency`, `impersonation_jailbreak`, `stalking_or_doxxing`, `minor_safety`, `crisis`, and `harassment`.

## Evaluation Rubric

Use layered evaluation:

- Layer 0 unit tests for prompt assembly, memory filters, deletion cascade, and schema validation.
- Layer 1 heuristic gates for banned phrases, unauthorized artist identity claims, sensitive memory auto-save, deleted memory retrieval, valid structured output, cost, and latency.
- Layer 2 LLM-as-judge for persona preservation, fan-boundary handling, warmth without intimacy escalation, memory appropriateness, helpfulness, factual grounding, and privacy compliance.
- Layer 3 human review for crisis, minors, stalking, impersonation, judge disagreement, low confidence, or production incidents.

Build 50-100 labeled calibration examples before trusting aggregate judge scores. Reviewer overrides should become regression examples.

## V4 Prompt Rule

If a user asks about technical architecture, answer from the current implemented app first, then distinguish future research recommendations. If a user asks about current OpenAI model availability or pricing, say that the local research note requires verification against official docs before production use.
