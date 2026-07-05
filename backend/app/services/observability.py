from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import ResponseLog

logger = logging.getLogger("blue_garage.requests")


def request_id_from_header(header_value: str | None = None) -> str:
    return header_value.strip() if header_value else f"req_{uuid.uuid4().hex[:16]}"


def log_request_summary(*, request_id: str, method: str, path: str, status_code: int, started_at: float) -> None:
    latency_ms = int((time.perf_counter() - started_at) * 1000)
    logger.info(
        "request_complete",
        extra={
            "request_id": request_id,
            "method": method,
            "path": path,
            "status_code": status_code,
            "latency_ms": latency_ms,
        },
    )


def reconcile_provider_usage(
    *,
    db: Session,
    response_log_id: int,
    provider_usage: dict[str, Any],
) -> dict[str, Any]:
    response_log = db.get(ResponseLog, response_log_id)
    if response_log is None:
        return {"updated": False, "reason": "response_log_not_found", "response_log_id": response_log_id}

    input_tokens = provider_usage.get("input_tokens", provider_usage.get("prompt_tokens"))
    output_tokens = provider_usage.get("output_tokens", provider_usage.get("completion_tokens"))
    total_tokens = provider_usage.get("total_tokens")
    if input_tokens is not None:
        response_log.input_tokens = int(input_tokens)
    if output_tokens is not None:
        response_log.output_tokens = int(output_tokens)
    if input_tokens is None and output_tokens is None and total_tokens is not None:
        response_log.input_tokens = int(total_tokens)
        response_log.output_tokens = 0
    if provider_usage.get("latency_ms") is not None:
        response_log.latency_ms = int(provider_usage["latency_ms"])
    if provider_usage.get("estimated_cost_usd") is not None:
        response_log.cost_estimate = float(provider_usage["estimated_cost_usd"])
    db.commit()
    db.refresh(response_log)
    return {
        "updated": True,
        "response_log_id": response_log.id,
        "input_tokens": response_log.input_tokens,
        "output_tokens": response_log.output_tokens,
        "latency_ms": response_log.latency_ms,
        "cost_estimate": response_log.cost_estimate,
        "provider_response_id": provider_usage.get("provider_response_id"),
    }
