import pytest

from brand_safety_agent.models import RiskKnowledge, Severity


def test_risk_knowledge_rejects_invalid_status() -> None:
    with pytest.raises(ValueError):
        RiskKnowledge("R", "t", "c", Severity.LOW, status="WRONG")


def test_risk_knowledge_rejects_invalid_version() -> None:
    with pytest.raises(ValueError):
        RiskKnowledge("R", "t", "c", Severity.LOW, version=0)
