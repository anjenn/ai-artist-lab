from typing import Any


def _value(obj: Any, name: str, default: str = "") -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _section_list(items: list[Any], formatter) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {formatter(item)}" for item in items)


def build_artist_chat_prompt(
    *,
    artist: Any,
    artist_rules: list[Any],
    fan_memories: list[Any],
    conversation_summary: Any,
    recent_messages: list[Any],
    rag_chunks: list[dict],
    user_message: str,
    prompt_version: Any,
    safety_context: str,
) -> tuple[list[dict], dict]:
    artist_name = _value(artist, "name", "LUMI NOA")
    summary_text = _value(conversation_summary, "summary", "none")
    prompt_name = _value(prompt_version, "name", "local-mock")

    rules_text = _section_list(
        artist_rules,
        lambda rule: f"{_value(rule, 'rule_type')}: {_value(rule, 'content')}",
    )
    memories_text = _section_list(
        fan_memories,
        lambda memory: f"{_value(memory, 'memory_type')}: {_value(memory, 'content')}",
    )
    recent_text = _section_list(
        recent_messages,
        lambda message: f"{_value(message, 'role')}: {_value(message, 'content')}",
    )
    rag_text = _section_list(
        rag_chunks,
        lambda chunk: f"{chunk.get('source')}#{chunk.get('chunk_id')}: {chunk.get('content')}",
    )

    system_content = f"""[System]
You are {artist_name}, a fictional AI artist. Answer as the artist, not as an assistant explaining the system.

[Persona]
- Speech style: {_value(artist, "speech_style", "Short, poetic, calm.")}
- Personality: {_value(artist, "personality", "Gentle, mysterious, independent.")}
- Prompt version: {prompt_name}

[Fan Boundary]
- Boundary level: {_value(artist, "fan_boundary_level", "Warm distance")}
- Never imply romantic exclusivity, private ownership, or emotional dependency.

[Forbidden / Safety Rules]
{rules_text}

{safety_context}

[Fan Memory]
Use these memories naturally when relevant. Do not mention that they came from a database.
{memories_text}

[Conversation Summary]
{summary_text}

[Recent Conversation]
{recent_text}

[Retrieved Artist Knowledge]
Use this section first for lore, debut, discography, and worldview questions.
If this section is empty or insufficient, answer uncertainly in character instead of inventing facts.
{rag_text}

[User Message]
{user_message}
"""

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_message},
    ]
    debug = {
        "artist": artist_name,
        "prompt_version": prompt_name,
        "used_memory": [
            {
                "type": _value(memory, "memory_type"),
                "content": _value(memory, "content"),
                "confidence": _value(memory, "confidence", None),
                "sensitivity": _value(memory, "sensitivity", None),
            }
            for memory in fan_memories
        ],
        "used_rag": rag_chunks,
        "safety_context": safety_context,
        "sections": [
            "System",
            "Persona",
            "Fan Boundary",
            "Forbidden / Safety Rules",
            "Fan Memory",
            "Conversation Summary",
            "Recent Conversation",
            "Retrieved Artist Knowledge",
            "User Message",
        ],
    }
    return messages, debug

