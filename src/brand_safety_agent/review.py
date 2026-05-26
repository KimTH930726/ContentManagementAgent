from __future__ import annotations

from dataclasses import replace
from enum import Enum

from .models import RiskKnowledge


class ReviewStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ReviewWorkflow:
    def submit(self, draft: RiskKnowledge) -> RiskKnowledge:
        if draft.status != ReviewStatus.DRAFT.value:
            raise ValueError("Only DRAFT can be submitted")
        return replace(draft, status=ReviewStatus.PENDING.value)

    def approve(self, pending: RiskKnowledge, *, version_bump: bool = True) -> RiskKnowledge:
        if pending.status not in {ReviewStatus.PENDING.value, ReviewStatus.DRAFT.value}:
            raise ValueError("Only PENDING/DRAFT can be approved")
        version = pending.version + 1 if version_bump else pending.version
        return replace(pending, status=ReviewStatus.APPROVED.value, version=version)

    def reject(self, pending: RiskKnowledge) -> RiskKnowledge:
        if pending.status not in {ReviewStatus.PENDING.value, ReviewStatus.DRAFT.value}:
            raise ValueError("Only PENDING/DRAFT can be rejected")
        return replace(pending, status=ReviewStatus.REJECTED.value)
