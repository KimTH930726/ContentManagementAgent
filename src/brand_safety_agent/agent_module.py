from __future__ import annotations

from dataclasses import dataclass

from .adapters import AsyncInMemoryRiskRepository
from .contracts import BrandSafetyUseCase
from .models import ImageContext, ReviewReport
from .reasoner import RiskReasoner
from .settings import BrandSafetySettings


@dataclass(slots=True)
class BrandSafetyAgentService(BrandSafetyUseCase):
    repo: AsyncInMemoryRiskRepository
    reasoner: RiskReasoner
    settings: BrandSafetySettings

    async def review_image(self, collection: str, image: ImageContext, top_k: int = 5) -> ReviewReport:
        # 교체 가능한 확장 포인트: feature flag 라우팅/병행 운영 분기
        effective_top_k = top_k if top_k > 0 else self.settings.query_top_k
        candidates = await self.repo.search(collection=collection, query_tokens=[*image.ocr_texts, *image.objects, *image.mood_tags], top_k=effective_top_k)
        return self.reasoner.review(image=image, candidates=candidates)
