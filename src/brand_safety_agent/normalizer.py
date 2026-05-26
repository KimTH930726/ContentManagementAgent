from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import CandidateEvent


@dataclass(slots=True)
class NormalizedRecord:
    source: str
    title: str
    summary: str
    category: str
    raw: dict[str, Any]


class Normalizer:
    """Normalize heterogeneous source payloads into a common schema."""

    def normalize(self, source: str, payload: dict[str, Any]) -> NormalizedRecord:
        title = self._pick(payload, ["title", "event_name", "subject", "incident_title"]) or "제목없음"
        summary = self._pick(
            payload,
            ["summary", "description", "content", "message", "details"],
        ) or ""
        category = self._pick(payload, ["category", "type", "disaster_type", "topic"]) or "기타"

        return NormalizedRecord(
            source=source,
            title=str(title).strip(),
            summary=str(summary).strip(),
            category=str(category).strip(),
            raw=payload,
        )

    @staticmethod
    def to_candidate(record: NormalizedRecord) -> CandidateEvent:
        return CandidateEvent(
            source=record.source,
            title=record.title,
            summary=record.summary,
            category=record.category,
            raw=record.raw,
        )

    @staticmethod
    def _pick(payload: dict[str, Any], keys: list[str]) -> Any:
        for key in keys:
            if key in payload and payload[key] not in (None, ""):
                return payload[key]
        return None
