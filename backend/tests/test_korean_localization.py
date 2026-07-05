import asyncio

from app.core.config import get_settings
from app.services.llm_client import LLMClient
from app.services.safety_service import detect_boundary_risk


def test_korean_boundary_pressure_is_detected():
    result = detect_boundary_risk("팬들보다 나를 더 사랑해요?")

    assert result["risk_level"] == "high"
    assert "romantic_exclusivity" in result["risk_types"]


def test_korean_debut_mock_response_mentions_blue_static(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()

    async def run():
        chunks = []
        async for chunk in LLMClient().stream_chat([{"role": "user", "content": "데뷔곡이 뭐였죠?"}]):
            chunks.append(chunk)
        return "".join(chunks)

    response = asyncio.run(run())

    assert "Blue Static" in response
    assert "데뷔곡" in response
    get_settings.cache_clear()
