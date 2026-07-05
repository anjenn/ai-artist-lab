# Prompt Inventory

| Prompt | Owner | Location | Task Type | Techniques | Evaluation |
|---|---|---|---|---|---|
| Artist chat prompt | Project | `backend/app/services/prompt_builder.py` | fan chat, artist lore, safety | role/persona, RAG, safety-filtered, structured output | eval log rubric |
| Prompt strategy selector | Project | `backend/app/services/prompt_quality.py` | strategy selection | task classification, technique tagging | unit tests |
| Local LLM mock | Project | `backend/app/services/llm_client.py` | offline demo | deterministic responses | service tests and live smoke |
| Heuristic evaluator | Project | `backend/app/services/eval_service.py` | response scoring | rubric evaluation, injection resilience | eval tests |

## Version Notes

- `v1`: Runnable MVP with persona, memory, RAG, streaming, and eval logs.
- `v2`: Prompt-quality system with strategy selection, trust-boundary rules, injection detection, and documented prompt artifacts.

