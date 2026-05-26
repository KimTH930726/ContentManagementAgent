"""Brand image reputation review agent core package."""

from .adapters import AsyncInMemoryRiskRepository
from .agent_module import BrandSafetyAgentService
from .collector import RawRecord, SourceCollector
from .contracts import BrandSafetyUseCase, DomainError, ErrorCode, RiskKnowledgeRepository
from .enrichment import EnrichmentService
from .errors import error_to_payload, mask_pii_text
from .feature_flags import FeatureFlagRouter
from .models import (
    CandidateEvent,
    ImageContext,
    MatchedRisk,
    ReviewReport,
    RiskKnowledge,
    SourceRef,
)
from .normalizer import NormalizedRecord, Normalizer
from .pipeline import IngestionPipeline, IngestionResult
from .reasoner import RiskReasoner
from .review import ReviewStatus, ReviewWorkflow
from .service import BrandSafetyService
from .settings import BrandSafetySettings
from .smagent_bridge import BrandSafetyAgent, register_brand_safety_agent
from .vector_store import InMemoryVectorStore

__all__ = [
    "AsyncInMemoryRiskRepository",
    "BrandSafetyAgent",
    "BrandSafetyAgentService",
    "BrandSafetyService",
    "BrandSafetySettings",
    "BrandSafetyUseCase",
    "CandidateEvent",
    "DomainError",
    "EnrichmentService",
    "ErrorCode",
    "FeatureFlagRouter",
    "ImageContext",
    "IngestionPipeline",
    "IngestionResult",
    "InMemoryVectorStore",
    "MatchedRisk",
    "NormalizedRecord",
    "Normalizer",
    "RawRecord",
    "register_brand_safety_agent",
    "ReviewReport",
    "ReviewStatus",
    "ReviewWorkflow",
    "RiskKnowledge",
    "RiskKnowledgeRepository",
    "RiskReasoner",
    "SourceCollector",
    "SourceRef",
    "error_to_payload",
    "mask_pii_text",
]