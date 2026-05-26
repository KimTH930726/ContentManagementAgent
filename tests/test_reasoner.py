from brand_safety_agent.models import ImageContext, RiskKnowledge, RiskLevel, Severity
from brand_safety_agent.reasoner import RiskReasoner


def test_reasoner_returns_caution_on_single_match() -> None:
    image = ImageContext(ocr_texts=["기억하겠습니다"], objects=["노란 리본"])
    risk = RiskKnowledge(
        risk_id="R1",
        title="세월호 참사",
        category="사회재난",
        severity=Severity.HIGH,
        visual_triggers=["노란 리본"],
        text_triggers=["4.16", "기억하겠습니다"],
    )

    report = RiskReasoner().review(image=image, candidates=[risk])

    assert report.risk_level == RiskLevel.CAUTION
    assert report.score == 30
    assert report.requires_human_review is True
    assert report.matched_risks[0].risk_id == "R1"


def test_reasoner_returns_high_risk_on_multiple_critical_matches() -> None:
    image = ImageContext(ocr_texts=["a", "b"], objects=["x", "y"])
    risks = [
        RiskKnowledge("1", "r1", "c", Severity.CRITICAL, visual_triggers=["x"]),
        RiskKnowledge("2", "r2", "c", Severity.CRITICAL, text_triggers=["a"]),
    ]
    report = RiskReasoner().review(image=image, candidates=risks)
    assert report.risk_level == RiskLevel.HIGH_RISK
    assert report.score == 80
