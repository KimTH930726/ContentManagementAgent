from __future__ import annotations

from .models import CandidateEvent, RiskKnowledge, Severity


class EnrichmentService:
    """Deterministic fallback enrichment for MVP.

    In production this module should call an LLM and keep the output as DRAFT,
    followed by a human approval workflow.
    """

    def enrich_candidate(self, candidate: CandidateEvent) -> RiskKnowledge:
        title = candidate.title.strip() or "Unnamed Event"
        normalized = title.lower()

        severity = Severity.MEDIUM
        if any(token in normalized for token in ["참사", "침몰", "붕괴", "희생"]):
            severity = Severity.HIGH

        return RiskKnowledge(
            risk_id=self._build_risk_id(title),
            title=title,
            category=candidate.category or "기타",
            severity=severity,
            text_triggers=[title],
            risk_patterns=["상업 프로모션과 민감 사건 연상 요소 결합 금지"],
            status="DRAFT",
        )

    @staticmethod
    def _build_risk_id(title: str) -> str:
        compact = "".join(ch for ch in title.upper() if ch.isalnum())[:20] or "EVENT"
        return f"KR-EVENT-{compact}"
