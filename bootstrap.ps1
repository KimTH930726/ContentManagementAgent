$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path "src\brand_safety_agent" | Out-Null
New-Item -ItemType Directory -Force -Path "tests" | Out-Null

@'
# ContentManagementAgent

브랜드 이미지 평판 검수 에이전트의 MVP 코드 스캐폴딩입니다.

## 실행

```bash
PYTHONPATH=src python -m brand_safety_agent.cli
```

## 테스트

```bash
PYTHONPATH=src python -m pytest -q
```
'@ | Set-Content -Encoding UTF8 "README.md"

@'
"""Brand image reputation review agent core package."""

from .models import CandidateEvent, ImageContext, MatchedRisk, RiskKnowledge, ReviewReport, SourceRef
from .pipeline import IngestionPipeline
from .reasoner import RiskReasoner
from .review import ReviewWorkflow, ReviewStatus
from .service import BrandSafetyService
from .vector_store import InMemoryVectorStore
'@ | Set-Content -Encoding UTF8 "src\brand_safety_agent\__init__.py"

@'
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any

class Severity(str, Enum):
    LOW = "LOW"; MEDIUM = "MEDIUM"; HIGH = "HIGH"; CRITICAL = "CRITICAL"
class RiskLevel(str, Enum):
    SAFE = "SAFE"; CAUTION = "CAUTION"; HIGH_RISK = "HIGH RISK"
VALID_STATUSES = {"DRAFT", "PENDING", "APPROVED", "REJECTED"}

@dataclass(slots=True)
class SourceRef: source:str; source_name:str; source_id:str; url:str
@dataclass(slots=True)
class CandidateEvent: source:str; title:str; summary:str; category:str; raw:dict[str,Any]
@dataclass(slots=True)
class RiskKnowledge:
    risk_id:str; title:str; category:str; severity:Severity
    sensitive_dates:list[str]=field(default_factory=list); locations:list[str]=field(default_factory=list)
    visual_triggers:list[str]=field(default_factory=list); text_triggers:list[str]=field(default_factory=list)
    risk_patterns:list[str]=field(default_factory=list); safe_usage_notes:list[str]=field(default_factory=list)
    sources:list[SourceRef]=field(default_factory=list); status:str="APPROVED"; version:int=1
    def __post_init__(self):
        if not self.risk_id.strip(): raise ValueError("risk_id must not be empty")
        if self.status not in VALID_STATUSES: raise ValueError(f"Invalid status: {self.status}")
        if self.version < 1: raise ValueError("version must be >= 1")
@dataclass(slots=True)
class ImageContext: ocr_texts:list[str]; objects:list[str]; mood_tags:list[str]=field(default_factory=list)
@dataclass(slots=True)
class MatchedRisk: risk_id:str; title:str; matched_elements:list[str]; reason:str
@dataclass(slots=True)
class ReviewReport:
    risk_level:RiskLevel; score:int; summary:str; matched_risks:list[MatchedRisk]
    recommendations:list[str]; requires_human_review:bool; reviewed_at:date=field(default_factory=date.today)
'@ | Set-Content -Encoding UTF8 "src\brand_safety_agent\models.py"

@'
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
@dataclass(slots=True)
class RawRecord: source:str; payload:dict[str,Any]
class SourceCollector:
    def collect_from_payloads(self, source:str, payloads:list[dict[str,Any]])->list[RawRecord]:
        return [RawRecord(source=source,payload=p) for p in payloads]
'@ | Set-Content -Encoding UTF8 "src\brand_safety_agent\collector.py"

@'
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .models import CandidateEvent
@dataclass(slots=True)
class NormalizedRecord: source:str; title:str; summary:str; category:str; raw:dict[str,Any]
class Normalizer:
    def normalize(self, source:str, payload:dict[str,Any])->NormalizedRecord:
        title = payload.get("title") or payload.get("event_name") or "제목없음"
        summary = payload.get("summary") or payload.get("description") or ""
        category = payload.get("category") or payload.get("type") or "기타"
        return NormalizedRecord(source,str(title).strip(),str(summary).strip(),str(category).strip(),payload)
    @staticmethod
    def to_candidate(record:NormalizedRecord)->CandidateEvent:
        return CandidateEvent(record.source,record.title,record.summary,record.category,record.raw)
'@ | Set-Content -Encoding UTF8 "src\brand_safety_agent\normalizer.py"

@'
from __future__ import annotations
from .models import CandidateEvent, RiskKnowledge, Severity
class EnrichmentService:
    def enrich_candidate(self, candidate:CandidateEvent)->RiskKnowledge:
        title=candidate.title.strip() or "Unnamed Event"
        severity=Severity.HIGH if any(x in title for x in ["참사","침몰","붕괴","희생"]) else Severity.MEDIUM
        return RiskKnowledge(risk_id=self._build_risk_id(title), title=title, category=candidate.category or "기타", severity=severity, text_triggers=[title], status="DRAFT")
    @staticmethod
    def _build_risk_id(title:str)->str:
        compact="".join(ch for ch in title.upper() if ch.isalnum())[:20] or "EVENT"
        return f"KR-EVENT-{compact}"
'@ | Set-Content -Encoding UTF8 "src\brand_safety_agent\enrichment.py"

@'
from __future__ import annotations
from dataclasses import dataclass
from .collector import RawRecord, SourceCollector
from .enrichment import EnrichmentService
from .models import RiskKnowledge
from .normalizer import Normalizer
@dataclass(slots=True)
class IngestionResult: drafts:list[RiskKnowledge]; rejected:list[RawRecord]
class IngestionPipeline:
    def __init__(self): self.collector=SourceCollector(); self.normalizer=Normalizer(); self.enrichment=EnrichmentService()
    def run(self, source:str, payloads:list[dict])->IngestionResult:
        raws=self.collector.collect_from_payloads(source,payloads); drafts=[]; rejected=[]
        for r in raws:
            try: drafts.append(self.enrichment.enrich_candidate(self.normalizer.to_candidate(self.normalizer.normalize(r.source,r.payload))))
            except Exception: rejected.append(r)
        return IngestionResult(drafts,rejected)
'@ | Set-Content -Encoding UTF8 "src\brand_safety_agent\pipeline.py"

@'
from __future__ import annotations
from dataclasses import replace
from enum import Enum
from .models import RiskKnowledge
class ReviewStatus(str, Enum): DRAFT="DRAFT"; PENDING="PENDING"; APPROVED="APPROVED"; REJECTED="REJECTED"
class ReviewWorkflow:
    def submit(self, draft:RiskKnowledge)->RiskKnowledge:
        if draft.status!="DRAFT": raise ValueError("Only DRAFT can be submitted")
        return replace(draft,status="PENDING")
    def approve(self, pending:RiskKnowledge, version_bump:bool=True)->RiskKnowledge:
        if pending.status not in {"PENDING","DRAFT"}: raise ValueError("Only PENDING/DRAFT can be approved")
        return replace(pending,status="APPROVED",version=pending.version + (1 if version_bump else 0))
    def reject(self, pending:RiskKnowledge)->RiskKnowledge:
        if pending.status not in {"PENDING","DRAFT"}: raise ValueError("Only PENDING/DRAFT can be rejected")
        return replace(pending,status="REJECTED")
'@ | Set-Content -Encoding UTF8 "src\brand_safety_agent\review.py"

@'
from __future__ import annotations
from collections import defaultdict
from .models import RiskKnowledge
class InMemoryVectorStore:
    def __init__(self): self._collections:dict[str,list[RiskKnowledge]]=defaultdict(list)
    def upsert(self, collection:str, record:RiskKnowledge)->None:
        bucket=self._collections[collection]
        for i,e in enumerate(bucket):
            if e.risk_id==record.risk_id: bucket[i]=record; return
        bucket.append(record)
    def search(self, collection:str, query_tokens:list[str], top_k:int=5)->list[RiskKnowledge]:
        tokens={t.strip().lower() for t in query_tokens if t.strip()}; scored=[]
        for rec in self._collections.get(collection,[]):
            tr={*(v.lower() for v in rec.visual_triggers),*(t.lower() for t in rec.text_triggers)}
            s=len(tokens.intersection(tr))
            if s>0: scored.append((s,rec))
        scored.sort(key=lambda x:x[0], reverse=True)
        return [r for _,r in scored[:top_k]]
'@ | Set-Content -Encoding UTF8 "src\brand_safety_agent\vector_store.py"

@'
from __future__ import annotations
from .models import ImageContext, ReviewReport, RiskKnowledge
from .reasoner import RiskReasoner
from .vector_store import InMemoryVectorStore
class BrandSafetyService:
    def __init__(self, store:InMemoryVectorStore|None=None, reasoner:RiskReasoner|None=None):
        self.store=store or InMemoryVectorStore(); self.reasoner=reasoner or RiskReasoner()
    def register_approved(self, collection:str, risk:RiskKnowledge)->None:
        if risk.status!="APPROVED": raise ValueError("Only APPROVED knowledge can be registered")
        self.store.upsert(collection,risk)
    def review_image(self, collection:str, image:ImageContext, top_k:int=5)->ReviewReport:
        c=self.store.search(collection,[*image.ocr_texts,*image.objects,*image.mood_tags],top_k)
        return self.reasoner.review(image,c)
'@ | Set-Content -Encoding UTF8 "src\brand_safety_agent\service.py"

@'
from __future__ import annotations
from .models import ImageContext, MatchedRisk, ReviewReport, RiskKnowledge, RiskLevel, Severity
SEVERITY_WEIGHT={Severity.LOW:10,Severity.MEDIUM:20,Severity.HIGH:30,Severity.CRITICAL:40}
class RiskReasoner:
    def review(self, image:ImageContext, candidates:list[RiskKnowledge])->ReviewReport:
        matched=[]; tokens={v.strip().lower() for v in [*image.ocr_texts,*image.objects,*image.mood_tags] if v and v.strip()}; total=0
        for risk in candidates:
            tr={*(v.lower() for v in risk.visual_triggers),*(t.lower() for t in risk.text_triggers)}
            overlap=sorted(tokens.intersection(tr))
            if overlap: matched.append(MatchedRisk(risk.risk_id,risk.title,overlap,"이미지 맥락과 민감 이슈 트리거가 중첩됩니다.")); total += SEVERITY_WEIGHT[risk.severity]
        score=min(100,total); level=RiskLevel.HIGH_RISK if score>=70 else (RiskLevel.CAUTION if score>=20 else RiskLevel.SAFE)
        return ReviewReport(level,score,("민감 이슈 연상 가능성이 낮습니다." if not matched else f"{len(matched)}건의 민감 이슈와 연상 요소가 감지되었습니다."),matched,["추모/재난 연상 요소 대체","기념일 문구 분리","배포 전 사람 검수"],bool(matched))
'@ | Set-Content -Encoding UTF8 "src\brand_safety_agent\reasoner.py"

@'
from __future__ import annotations
import json
from dataclasses import asdict
from .models import ImageContext, RiskKnowledge, Severity
from .reasoner import RiskReasoner
image=ImageContext(["기억하겠습니다","봄 세일"],["노란 리본","바다"],["추모"])
risk=RiskKnowledge("KR-TRAGEDY-SEWOL-2014","세월호 참사","사회재난/참사/추모",Severity.HIGH,visual_triggers=["노란 리본","바다"],text_triggers=["기억하겠습니다"],status="APPROVED")
print(json.dumps(asdict(RiskReasoner().review(image,[risk])),ensure_ascii=False,indent=2,default=str))
'@ | Set-Content -Encoding UTF8 "src\brand_safety_agent\cli.py"

@'
import pytest
from brand_safety_agent.models import RiskKnowledge, Severity

def test_risk_knowledge_rejects_invalid_status():
    with pytest.raises(ValueError): RiskKnowledge("R","t","c",Severity.LOW,status="WRONG")

def test_risk_knowledge_rejects_invalid_version():
    with pytest.raises(ValueError): RiskKnowledge("R","t","c",Severity.LOW,version=0)
'@ | Set-Content -Encoding UTF8 "tests\test_models.py"

Write-Host "bootstrap.ps1 completed"
