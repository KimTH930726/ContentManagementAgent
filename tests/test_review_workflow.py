from brand_safety_agent.models import RiskKnowledge, Severity
from brand_safety_agent.review import ReviewWorkflow


def test_review_workflow_submit_approve() -> None:
    wf = ReviewWorkflow()
    draft = RiskKnowledge(
        risk_id="R1",
        title="테스트",
        category="기타",
        severity=Severity.MEDIUM,
        status="DRAFT",
        version=1,
    )

    pending = wf.submit(draft)
    approved = wf.approve(pending)

    assert pending.status == "PENDING"
    assert approved.status == "APPROVED"
    assert approved.version == 2
