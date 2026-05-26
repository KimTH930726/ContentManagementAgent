from __future__ import annotations

from collections import defaultdict

from .models import RiskKnowledge


class InMemoryVectorStore:
    """Token-overlap retriever placeholder for MVP without external DB."""

    def __init__(self) -> None:
        self._collections: dict[str, list[RiskKnowledge]] = defaultdict(list)

    def upsert(self, collection: str, record: RiskKnowledge) -> None:
        bucket = self._collections[collection]
        for i, existing in enumerate(bucket):
            if existing.risk_id == record.risk_id:
                bucket[i] = record
                return
        bucket.append(record)

    def search(self, collection: str, query_tokens: list[str], top_k: int = 5) -> list[RiskKnowledge]:
        tokens = {t.strip().lower() for t in query_tokens if t.strip()}
        scored: list[tuple[int, RiskKnowledge]] = []
        for rec in self._collections.get(collection, []):
            triggers = {*(v.lower() for v in rec.visual_triggers), *(t.lower() for t in rec.text_triggers)}
            score = len(tokens.intersection(triggers))
            if score > 0:
                scored.append((score, rec))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [rec for _, rec in scored[:top_k]]
