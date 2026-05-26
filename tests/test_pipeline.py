from brand_safety_agent.pipeline import IngestionPipeline


def test_pipeline_creates_draft_records() -> None:
    pipeline = IngestionPipeline()
    payloads = [
        {
            "event_name": "세월호 참사 관련 기록물",
            "description": "2014년 해상 참사 관련",
            "type": "사회재난/참사/추모",
        }
    ]

    result = pipeline.run(source="archives", payloads=payloads)

    assert len(result.drafts) == 1
    assert result.drafts[0].status == "DRAFT"
    assert result.drafts[0].risk_id.startswith("KR-EVENT-")
    assert result.rejected == []
