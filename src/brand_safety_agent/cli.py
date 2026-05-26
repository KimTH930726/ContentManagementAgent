from __future__ import annotations

import json
from dataclasses import asdict

from .models import ImageContext, RiskKnowledge, Severity
from .reasoner import RiskReasoner


def main() -> None:
    image = ImageContext(
        ocr_texts=["기억하겠습니다", "봄 세일"],
        objects=["노란 리본", "바다"],
        mood_tags=["추모"],
    )

    risk = RiskKnowledge(
        risk_id="KR-TRAGEDY-SEWOL-2014",
        title="세월호 참사",
        category="사회재난/참사/추모",
        severity=Severity.HIGH,
        visual_triggers=["노란 리본", "바다"],
        text_triggers=["기억하겠습니다", "4.16"],
        risk_patterns=["추모 상징과 상업 프로모션 결합"],
    )

    report = RiskReasoner().review(image=image, candidates=[risk])
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
