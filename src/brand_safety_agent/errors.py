from __future__ import annotations

from dataclasses import asdict

from .contracts import DomainError


def error_to_payload(err: DomainError) -> dict:
    return {
        "code": err.code.value,
        "message": err.message,
        "trace_id": err.trace_id,
        "details": err.details or {},
    }


def mask_pii_text(text: str) -> str:
    # 교체 가능한 확장 포인트: 정책 기반 마스킹 엔진 연결
    if "@" in text:
        return "***@***"
    return text
