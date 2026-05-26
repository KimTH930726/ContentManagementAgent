from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskLevel(str, Enum):
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    HIGH_RISK = "HIGH RISK"


VALID_STATUSES = {"DRAFT", "PENDING", "APPROVED", "REJECTED"}


@dataclass(slots=True)
class SourceRef:
    source: str
    source_name: str
    source_id: str
    url: str


@dataclass(slots=True)
class CandidateEvent:
    source: str
    title: str
    summary: str
    category: str
    raw: dict[str, Any]


@dataclass(slots=True)
class RiskKnowledge:
    risk_id: str
    title: str
    category: str
    severity: Severity
    sensitive_dates: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    visual_triggers: list[str] = field(default_factory=list)
    text_triggers: list[str] = field(default_factory=list)
    risk_patterns: list[str] = field(default_factory=list)
    safe_usage_notes: list[str] = field(default_factory=list)
    sources: list[SourceRef] = field(default_factory=list)
    status: str = "APPROVED"
    version: int = 1

    def __post_init__(self) -> None:
        if not self.risk_id.strip():
            raise ValueError("risk_id must not be empty")
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {self.status}")
        if self.version < 1:
            raise ValueError("version must be >= 1")


@dataclass(slots=True)
class ImageContext:
    ocr_texts: list[str]
    objects: list[str]
    mood_tags: list[str] = field(default_factory=list)
    extracted_dates: list[str] = field(default_factory=list)
    regions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MatchedRisk:
    risk_id: str
    title: str
    matched_elements: list[str]
    reason: str


@dataclass(slots=True)
class ReviewReport:
    risk_level: RiskLevel
    score: int
    summary: str
    matched_risks: list[MatchedRisk]
    recommendations: list[str]
    requires_human_review: bool
    reviewed_at: date = field(default_factory=date.today)
