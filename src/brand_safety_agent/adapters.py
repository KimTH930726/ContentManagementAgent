from __future__ import annotations

import asyncio
from .contracts import DomainError, ErrorCode
from .models import RiskKnowledge
from .vector_store import InMemoryVectorStore


class AsyncInMemoryRiskRepository:
    """교체 가능한 확장 포인트: pgvector 기반 저장소로 대체 가능."""

    def __init__(self, store: InMemoryVectorStore | None = None) -> None:
        self.store = store or InMemoryVectorStore()
        self._lock = asyncio.Lock()

    async def upsert(self, collection: str, record: RiskKnowledge) -> None:
        async with self._lock:
            self.store.upsert(collection, record)

    async def search(self, collection: str, query_tokens: list[str], top_k: int = 5) -> list[RiskKnowledge]:
        try:
            return self.store.search(collection=collection, query_tokens=query_tokens, top_k=top_k)
        except Exception as exc:
            raise DomainError(
                code=ErrorCode.UPSTREAM_FAILURE,
                message="risk repository search failed",
                trace_id="local-trace",
                details={"error": str(exc)},
            ) from exc
