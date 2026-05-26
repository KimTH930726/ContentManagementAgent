from __future__ import annotations

from .models import ImageContext, ReviewReport, RiskKnowledge
from .reasoner import RiskReasoner
from .vector_store import InMemoryVectorStore


class BrandSafetyService:
    def __init__(self, store: InMemoryVectorStore | None = None, reasoner: RiskReasoner | None = None) -> None:
        self.store = store or InMemoryVectorStore()
        self.reasoner = reasoner or RiskReasoner()

    def register_approved(self, collection: str, risk: RiskKnowledge) -> None:
        if risk.status != "APPROVED":
            raise ValueError("Only APPROVED knowledge can be registered")
        self.store.upsert(collection, risk)

    def review_image(self, collection: str, image: ImageContext, top_k: int = 5) -> ReviewReport:
        query_tokens = [*image.ocr_texts, *image.objects, *image.mood_tags]
        candidates = self.store.search(collection=collection, query_tokens=query_tokens, top_k=top_k)
        return self.reasoner.review(image=image, candidates=candidates)
