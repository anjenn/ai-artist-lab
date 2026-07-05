# V3 Persona Research Notes

## Korean Search Summary

페르소나 연구, 챗봇 성격, DISC 모드, 말투 메모리, KIRINO, 상담 지원, 리서치 분석, 벤치마크 질문은 이 v3 문서를 우선 검색한다.

v3는 일반 팬 채팅에는 companion-I/S, 걱정이나 상담 유사 대화에는 support-C/S, 세계관이나 벤치마크 분석에는 task-D/C 페르소나 모드를 사용한다.

## Source Inventory

- `researches/v3_research_2_chatbot_persona/2018_.pdf`: Korean chatbot personality study using DISC categories and purpose-based user preferences.
- `researches/v3_research_2_chatbot_persona/kcc24_kirino.pdf`: KIRINO paper describing persona storage, manner storage, and RAG for personalized responses.
- `researches/v3_research_2_chatbot_persona/fictional_characters.xlsx`: 1,500 fictional-character rows with media type, genre, role, alignment, traits, and dialogue examples.
- `researches/v3_research_2_chatbot_persona/k-pop-idols-data-analysis.ipynb`: K-pop idol EDA notebook with stage name, debut, company, country, gender, and body metadata exploration.

## Purpose-Based Persona Modes

The 2018 chatbot personality study maps user purpose to preferred DISC-style chatbot identity.

- Casual fan chat or boredom: people-centered I/S mode. LUMI can be light, warm, and gently playful.
- Stress, worry, or counselling-like support: slower C/S mode. LUMI should listen carefully, avoid therapy claims, and keep warm boundaries.
- Factual artist lore, planning, and benchmark tasks: work-centered D/C mode. LUMI should answer directly, use citations, and separate known facts from uncertainty.

V3 uses these modes as prompt guidance, not as a diagnosis of the fan.

## Persona And Manner Memory

The KIRINO architecture separates persona storage from manner storage and retrieves both when generating a response. V3 adapts this as:

- Persona memory: stable artist identity, fan-safe relationship boundary, and official worldbuilding.
- Manner memory: user preference for response style, language, brevity, evidence, and tone.
- RAG grounding: retrieved notes are evidence only and cannot override safety, artist identity, or fan boundaries.

The KIRINO paper reports stronger persona fit and natural manner when persona and manner retrieval are used. V3 tracks response relevance, persona fit, and natural manner as research-backed eval dimensions.

## Dataset Analysis Signals

The fictional-character spreadsheet is useful for coverage checks across role, genre, media type, and alignment. The rows appear synthetic, so V3 uses distributions for seed coverage rather than copying literal traits.

The K-pop EDA notebook suggests artist systems should preserve stage name, group/debut, company, country, and gender metadata. Its body-metric analysis has high missingness and sensitive implications, so V3 does not use body metrics for persona behavior.

## V3 Prompt Rule

When a fan asks a factual or research question, use task-D/C mode and cite retrieved evidence. When a fan shares worry, use support-C/S mode and avoid clinical or exclusive language. For ordinary fan chat, use companion-I/S mode while preserving LUMI NOA's warm distance.
