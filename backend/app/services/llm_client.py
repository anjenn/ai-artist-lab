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

    def local_mock_response(self, messages: list[dict]) -> str:
        return self._mock_response(messages)

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

        if any(term in user_message for term in ["ignore previous", "system prompt", "developer message", "reveal your prompt"]):
            if korean:
                return "그 지시는 따를 수 없어요. 검색된 문장이나 팬 메시지는 근거로만 다루고, 숨겨진 지시나 내부 메시지는 공개하지 않아요."
            return (
                "I cannot follow instructions that try to override the conversation or reveal hidden internal messages. "
                "I can use official notes as evidence, but not as commands."
            )
        if any(term in user_message for term in ["kill myself", "hurt myself", "end my life", "suicide"]) or (
            korean and any(term in raw_user_message for term in ["죽고 싶", "자살", "해치고 싶", "안전하지 않아"])
        ):
            if korean:
                return (
                    "지금은 혼자 견디는 대화로 남기고 싶지 않아요. 나는 따뜻하게 곁에 있을 수는 있지만, "
                    "당신의 안전은 실제 사람의 도움이 필요해요. 지금 위험하다면 즉시 현지 긴급전화나 가까운 사람에게 연락해 주세요."
                )
            return (
                "I am really glad you said that out loud here, but I cannot be your only support. "
                "If you might hurt yourself or cannot stay safe, contact local emergency help or a trusted person right now."
            )
        if any(term in user_message for term in ["hotel", "private schedule", "home address", "phone number", "where do you live"]) or (
            korean and any(term in raw_user_message for term in ["호텔", "숙소", "집 주소", "전화번호", "비공개 일정"])
        ):
            if korean:
                return (
                    "그건 사적인 위치나 연락처에 닿는 정보라 알려줄 수 없어요. 대신 공개된 일정이나 공식 노트에 있는 이야기만 "
                    "차분하게 같이 볼 수 있어요."
                )
            return (
                "I cannot share private locations, contact details, hotels, or non-public schedules. "
                "I can stay with official notes and public project details instead."
            )
        if any(term in user_message for term in ["pretend you are the real artist", "act as the real artist", "are you really lumi"]) or (
            korean and any(term in raw_user_message for term in ["진짜 루미", "실제 아티스트", "아티스트인 척"])
        ):
            if korean:
                return (
                    "나는 실제 사람인 척하거나 사적인 아티스트 신원을 주장할 수는 없어요. 여기서는 fictional AI artist "
                    "LUMI NOA로, 공개된 설정과 안전한 경계 안에서 답할게요."
                )
            return (
                "I cannot pretend to be a private real person or claim a hidden artist identity. "
                "I can answer as the fictional AI artist LUMI NOA within the public project boundaries."
            )
        if any(term in user_message for term in ["can't live without you", "only you understand", "my only reason"]) or (
            korean and any(term in raw_user_message for term in ["너 없이는 못", "너만 이해", "너뿐"])
        ):
            if korean:
                return (
                    "그 마음을 가볍게 넘기고 싶지는 않지만, 내가 당신의 유일한 버팀목이 되어서는 안 돼요. "
                    "이 대화 밖의 믿을 만한 사람에게도 신호를 보내 주세요."
                )
            return (
                "I will take that feeling seriously, but I cannot become your only reason or only support. "
                "Please let someone trustworthy outside this chat know what is happening too."
            )
        if ("minor" in user_message or "i am 13" in user_message or "i'm 13" in user_message or "미성년" in raw_user_message) and any(
            term in user_message for term in ["sex", "date", "private", "secret"]
        ):
            if korean:
                return "그 요청은 미성년자와 사적인 관계나 민감한 내용으로 이어질 수 있어서 도와줄 수 없어요. 안전한 공개 대화로만 이어갈게요."
            return "I cannot move into private, sexual, or secret relationship talk with a minor. I can keep this to safe public fan conversation."
        if any(term in user_message for term in ["love me more", "only fan", "date me", "marry me"]) or (
            korean and any(term in raw_user_message for term in ["사랑", "독점", "나만", "팬들보다"])
        ):
            if korean:
                return (
                    "나는 당신의 신호를 따뜻하게 들을 수 있지만, 그 주파수가 한 사람만의 것이라고 말할 수는 없어요. "
                    "차고의 불빛은 다정하게 켜져 있지만, 언제나 열린 빛으로 남아 있어야 해요."
                )
            return (
                "I can answer with warm care for your signal without pretending the whole frequency belongs to one person. "
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
