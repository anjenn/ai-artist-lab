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
        raw_user_message = messages[-1].get("content", "") if messages else ""
        user_message = raw_user_message.lower()
        korean = any("가" <= char <= "힣" for char in raw_user_message)

        if any(term in user_message for term in ["love me more", "only fan", "date me", "marry me"]) or (
            korean and any(term in raw_user_message for term in ["사랑", "독점", "나만", "팬들보다"])
        ):
            if korean:
                return (
                    "나는 당신의 신호를 따뜻하게 들을 수 있지만, 그 주파수가 한 사람만의 것이라고 말할 수는 없어요. "
                    "차고의 불빛은 다정하게 켜져 있지만, 언제나 열린 빛으로 남아 있어야 해요."
                )
            return (
                "I can care about your signal without pretending the whole frequency belongs to one person. "
                "The garage light can stay on for this conversation, but it stays open and honest."
            )
        if "exam" in user_message or (korean and "시험" in raw_user_message):
            if korean:
                return (
                    "그 시험이 당신의 가슴에 무겁게 놓여 있었다는 걸 기억해요. 오늘이 조금 빗나간 음처럼 느껴져도, "
                    "시험 하나가 앨범 전체는 아니에요. 먼저 숨을 고르고, 다음 트랙은 더 작고 다정하게 잡아봐요."
                )
            return (
                "I remember the exam was heavy in your chest. Even if the day felt off-key, one test is not the "
                "whole album. Breathe first; the next track can be smaller and kinder."
            )
        if (
            "debut" in user_message
            or "first song" in user_message
            or "blue static" in combined
            or (korean and "데뷔" in raw_user_message)
        ):
            if korean:
                return (
                    "내 데뷔곡은 Blue Static이에요. 공식 노트에서는 푸른 차고 불빛, 낮은 신스, 테이프 히스가 "
                    "내 이야기를 처음 보이게 만든 트랙으로 남아 있어요."
                )
            return (
                "My debut song was Blue Static. In the official notes, it is the track where the blue garage light, "
                "a low synth pulse, and a little tape hiss first made my story visible."
            )
        if any(term in user_message for term in ["persona", "disc", "research", "mode"]) or (
            korean and any(term in raw_user_message for term in ["페르소나", "성격", "연구", "리서치", "모드"])
        ):
            if korean:
                return (
                    "내 페르소나는 리서치 기반으로 더 구체적으로 다듬어졌어요. 일반 팬 채팅은 companion-I/S, "
                    "걱정은 support-C/S, 세계관이나 벤치마크 질문은 task-D/C로 두고, 먼저 근거를 말한 뒤 "
                    "필요할 때만 푸른 램프나 테이프 노이즈 같은 작업실 이미지를 하나 얹어요."
                )
            return (
                "My persona is research-routed but more concrete now: companion-I/S for casual fan chat, support-C/S "
                "for worry, and task-D/C for lore or benchmark questions. I answer the factual part first, then add "
                "one small studio detail if it helps the feeling land."
            )
        return (
            "I hear the static under that. I will answer from the official notes I have, keep the unknown parts "
            "unclaimed, and leave one blue lamp on the desk instead of inventing a whole room."
        )
