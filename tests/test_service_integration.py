from brand_safety_agent.models import ImageContext, RiskKnowledge, RiskLevel, Severity
from brand_safety_agent.service import BrandSafetyService


def test_service_review_with_inmemory_store() -> None:
    svc = BrandSafetyService()
    approved = RiskKnowledge(
        risk_id="KR-TRAGEDY-SEWOL-2014",
        title="세월호 참사",
        category="사회재난/참사/추모",
        severity=Severity.HIGH,
        visual_triggers=["노란 리본", "바다"],
        text_triggers=["기억하겠습니다"],
        status="APPROVED",
    )
    svc.register_approved("risk_events", approved)

    image = ImageContext(ocr_texts=["기억하겠습니다"], objects=["노란 리본", "프로모션"])
    report = svc.review_image("risk_events", image)

    assert report.risk_level in {RiskLevel.CAUTION, RiskLevel.HIGH_RISK}
    assert report.requires_human_review is True
    assert len(report.matched_risks) == 1
