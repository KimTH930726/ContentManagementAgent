from __future__ import annotations

from .models import ImageContext, MatchedRisk, ReviewReport, RiskKnowledge, RiskLevel, Severity


SEVERITY_WEIGHT = {
    Severity.LOW: 10,
    Severity.MEDIUM: 20,
    Severity.HIGH: 30,
    Severity.CRITICAL: 40,
}


class RiskReasoner:
    """Simple rule-based reasoner for MVP baseline."""

    def review(self, image: ImageContext, candidates: list[RiskKnowledge]) -> ReviewReport:
        matched: list[MatchedRisk] = []

        tokens = set(self._normalize_tokens(image))
        total_score = 0
        for risk in candidates:
            triggers = set(t.lower() for t in [*risk.visual_triggers, *risk.text_triggers])
            overlap = sorted(tokens.intersection(triggers))
            if overlap:
                matched.append(
                    MatchedRisk(
                        risk_id=risk.risk_id,
                        title=risk.title,
                        matched_elements=overlap,
                        reason="이미지 맥락과 민감 이슈 트리거가 중첩됩니다.",
                    )
                )
                total_score += SEVERITY_WEIGHT[risk.severity]

        score = min(100, total_score)
        if score >= 70:
            level = RiskLevel.HIGH_RISK
        elif score >= 20:
            level = RiskLevel.CAUTION
        else:
            level = RiskLevel.SAFE

        summary = (
            "민감 이슈 연상 가능성이 낮습니다."
            if not matched
            else f"{len(matched)}건의 민감 이슈와 연상 요소가 감지되었습니다."
        )

        recommendations = [
            "추모/재난 연상 색상·오브젝트를 일반 디자인 요소로 대체",
            "기념일/사건 관련 숫자·문구를 프로모션 문맥과 분리",
            "최종 배포 전 사람 검수(브랜드/법무) 재확인",
        ]

        return ReviewReport(
            risk_level=level,
            score=score,
            summary=summary,
            matched_risks=matched,
            recommendations=recommendations,
            requires_human_review=bool(matched),
        )

    @staticmethod
    def _normalize_tokens(image: ImageContext) -> list[str]:
        values = [*image.ocr_texts, *image.objects, *image.mood_tags]
        return [v.strip().lower() for v in values if v and v.strip()]
