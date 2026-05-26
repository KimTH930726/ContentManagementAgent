from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from .models import ImageContext, ReviewReport, RiskKnowledge


class ErrorCode(str, Enum):
    TIMEOUT = "BSA_TIMEOUT"
    UPSTREAM_FAILURE = "BSA_UPSTREAM_FAILURE"
    INVALID_INPUT = "BSA_INVALID_INPUT"


@dataclass(slots=True)
class DomainError(Exception):
    code: ErrorCode
    message: str
    trace_id: str
    details: dict | None = None


class RiskKnowledgeRepository(Protocol):
    async def upsert(self, collection: str, record: RiskKnowledge) -> None: ...

    async def search(self, collection: str, query_tokens: list[str], top_k: int = 5) -> list[RiskKnowledge]: ...


class BrandSafetyUseCase(Protocol):
    async def review_image(self, collection: str, image: ImageContext, top_k: int = 5) -> ReviewReport: ...
