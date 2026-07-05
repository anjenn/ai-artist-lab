# Prompt Leaderboard

| Version | Prompt | Strategy Changes | Test Result | Known Failure Mode | Release Status |
|---|---|---|---|---|---|
| v1 | artist_chat | Persona + memory + RAG + safety sections | 9 service tests passed | Prompt-quality strategy not explicit | Released |
| v2 | artist_chat | Added strategy selector, prompt-quality contract, untrusted context boundary, injection-risk metadata | 14 service tests passed; live SSE debug includes prompt strategy and injection metadata | Heuristic strategy selection is simple | Released |
