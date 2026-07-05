# V3 Persona Research Analysis

## Inputs

- `v3_research_2_chatbot_persona/2018_.pdf`
- `v3_research_2_chatbot_persona/kcc24_kirino.pdf`
- `v3_research_2_chatbot_persona/fictional_characters.xlsx`
- `v3_research_2_chatbot_persona/k-pop-idols-data-analysis.ipynb`

## What Was Extracted

- The spreadsheet contains 1,500 fictional-character rows and 15 fields: character name, media type, source, genre, role, traits, backstory, skills, appearance, alignment, hobbies, relationships, significance, description, and dialogue example.
- Role coverage is balanced enough for seed testing: sidekick, hero, villain, mentor, antagonist, and protagonist are all represented.
- Media and genre coverage are broad across TV show, movie, video game, webcomic, novel, fantasy, sci-fi, horror, mystery, romance, and thriller.
- The notebook includes K-pop idol EDA around stage name, birth date, group, debut, company, country, gender, height, weight, age, debut age, birthplace, and zodiac.
- The notebook flags high missingness in body-related fields, so v3 avoids using body metrics as a persona driver.

## Research Signals Used

- The 2018 chatbot-personality study supports purpose-aware chatbot identity:
  - casual/boredom chat: I/S, people-centered
  - counselling-like support: C/S, slower and listening-first
  - task use: D/C, work-centered and efficient
- The KIRINO paper supports separating persona memory, manner memory, and RAG retrieval.
- KIRINO reports better quality when persona/manner retrieval is used, including 26% G-Eval improvement and 38% Human Eval improvement.
- The fictional-character data is synthetic-looking, so it is used for distributional coverage rather than copied trait text.
- K-pop idol metadata supports explicit artist fields such as stage/debut/company/country while avoiding sensitive body-shape assumptions.

## V3 Product Decisions

- Added a v3 persona research API endpoint: `/dashboard/persona-research`.
- Added a v3 prompt version seed: `v0.5-research-persona`.
- Added research-backed artist rules for persona mode, manner memory, and research grounding.
- Added demo memories for evidence-first response style and metric-based benchmark preference.
- Added a RAG document: `knowledge_base/persona_research_v3.md`.
- Added prompt debug metadata for selected `persona_mode`.
- Added a frontend Persona Research tab that shows source coverage, dataset distributions, persona modes, and KIRINO eval metrics.

## V3 Persona Modes

| Mode | Purpose | DISC | Runtime Rule |
|---|---|---|---|
| `companion-is` | casual fan chat | I/S | light information, gentle fun, warm distance |
| `support-cs` | stress or worry | C/S | slower listening, no therapy claims, safe boundary |
| `task-dc` | lore, planning, benchmark | D/C | direct evidence, citations, uncertainty labels |

## Additional Research Still Needed

- Validate the synthetic-character dataset against a real curated persona dataset before using it for trait generation.
- Add a repeatable notebook or script if this research pipeline becomes part of production.
- Compare DISC routing against actual user satisfaction in the app.
- Expand manner memory extraction with explicit consent and deletion controls.
