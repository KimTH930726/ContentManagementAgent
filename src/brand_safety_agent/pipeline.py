from __future__ import annotations

from dataclasses import dataclass

from .collector import RawRecord, SourceCollector
from .enrichment import EnrichmentService
from .models import RiskKnowledge
from .normalizer import Normalizer


@dataclass(slots=True)
class IngestionResult:
    drafts: list[RiskKnowledge]
    rejected: list[RawRecord]


class IngestionPipeline:
    """Collector -> Normalizer -> Enrichment draft creation pipeline."""

    def __init__(self) -> None:
        self.collector = SourceCollector()
        self.normalizer = Normalizer()
        self.enrichment = EnrichmentService()

    def run(self, source: str, payloads: list[dict]) -> IngestionResult:
        raw_items = self.collector.collect_from_payloads(source=source, payloads=payloads)
        drafts: list[RiskKnowledge] = []
        rejected: list[RawRecord] = []

        for raw in raw_items:
            try:
                normalized = self.normalizer.normalize(source=raw.source, payload=raw.payload)
                candidate = self.normalizer.to_candidate(normalized)
                drafts.append(self.enrichment.enrich_candidate(candidate))
            except Exception:
                rejected.append(raw)

        return IngestionResult(drafts=drafts, rejected=rejected)
