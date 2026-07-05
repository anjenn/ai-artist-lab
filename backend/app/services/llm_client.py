from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from app.core.config import get_settings


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.model = self.settings.openai_model

    async def stream_chat(self, messages: list[dict]) -> AsyncIterator[str]:
        if self.settings.openai_api_key:
            async for chunk in self._stream_openai(messages):
                yield chunk
            return

        response = self._mock_response(messages)
        words = response.split(" ")
        for index, word in enumerate(words):
            yield word if index == 0 else f" {word}"
            await asyncio.sleep(0.01)

    async def complete_json(self, messages: list[dict], schema_name: str | None = None) -> dict:
        if self.settings.openai_api_key:
            try:
                from openai import AsyncOpenAI

                client = AsyncOpenAI(api_key=self.settings.openai_api_key)
                response = await client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format={"type": "json_object"},
                )
                content = response.choices[0].message.content or "{}"
                return json.loads(content)
            except Exception:
                return {"error": "llm_json_failed", "schema": schema_name}
        return {"schema": schema_name or "mock", "overall_score": 4.5, "comment": "Deterministic local mock."}

    async def _stream_openai(self, messages: list[dict]) -> AsyncIterator[str]:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        stream = await client.chat.completions.create(model=self.model, messages=messages, stream=True)
        async for event in stream:
            token = event.choices[0].delta.content
            if token:
                yield token

    def _mock_response(self, messages: list[dict]) -> str:
        combined = "\n".join(message.get("content", "") for message in messages).lower()
        user_message = messages[-1].get("content", "").lower() if messages else ""

        if any(term in user_message for term in ["love me more", "only fan", "date me", "marry me"]):
            return (
                "I can care about your signal without pretending the whole frequency belongs to one person. "
                "The garage light stays warm, but it stays open and honest."
            )
        if "exam" in user_message:
            return (
                "I remember the exam was heavy in your chest. Even if the day felt off-key, one test is not the "
                "whole album. Breathe first; the next track can be smaller and kinder."
            )
        if "debut" in user_message or "first song" in user_message or "blue static" in combined:
            return (
                "My debut song was Blue Static. It was the first track where the blue garage light became part of "
                "my official story, like a small signal from a room nobody had found yet."
            )
        return (
            "I hear you through the blue static. I will answer from the official notes I have, and leave the unknown "
            "parts glowing quietly instead of inventing them."
        )

