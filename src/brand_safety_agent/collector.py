from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RawRecord:
    source: str
    payload: dict[str, Any]


class SourceCollector:
    """Simple in-memory collector abstraction for MVP.

    Production should replace this with real HTTP/API integrations.
    """

    def collect_from_payloads(self, source: str, payloads: list[dict[str, Any]]) -> list[RawRecord]:
        return [RawRecord(source=source, payload=payload) for payload in payloads]
