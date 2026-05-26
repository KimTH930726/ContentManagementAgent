from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .agent_module import BrandSafetyAgentService
from .errors import error_to_payload, mask_pii_text
from .feature_flags import FeatureFlagRouter
from .models import ImageContext
from .settings import BrandSafetySettings


class AgentBase(Protocol):
    agent_id: str
    metadata: dict[str, Any]

    async def stream_chat(self, payload: dict[str, Any]) -> dict[str, Any]: ...

    async def health_check(self) -> dict[str, Any]: ...


class AgentRegistry(Protocol):
    def register(self, agent: AgentBase) -> None: ...


@dataclass(slots=True)
class BrandSafetyAgent:
    """SMAgent 호환 AgentBase 구현체.

    교체 가능한 확장 포인트:
    - payload 스키마 표준화
    - stream 응답을 chunk/event 형태로 변환
    """

    service: BrandSafetyAgentService
    settings: BrandSafetySettings
    agent_id: str = "brand_safety"
    metadata: dict[str, Any] = None  # type: ignore[assignment]
    flags: FeatureFlagRouter | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {"name": "Brand Safety Agent", "version": "v1"}
        if self.flags is None:
            self.flags = FeatureFlagRouter(brand_safety_enabled=self.settings.feature_enabled)

    async def stream_chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.flags.can_run_primary():
            return {
                "code": "BSA_DISABLED",
                "message": "brand safety feature is disabled",
                "trace_id": payload.get("trace_id", "n/a"),
            }

        image = ImageContext(
            ocr_texts=payload.get("ocr_texts", []),
            objects=payload.get("objects", []),
            mood_tags=payload.get("mood_tags", []),
        )
        try:
            report = await self.service.review_image(
                collection=payload.get("collection", "risk_events"),
                image=image,
                top_k=payload.get("top_k", self.settings.query_top_k),
            )
        except Exception as exc:
            from .contracts import DomainError, ErrorCode

            err = DomainError(code=ErrorCode.UPSTREAM_FAILURE, message=mask_pii_text(str(exc)), trace_id=payload.get("trace_id", "n/a"))
            return error_to_payload(err)

        return {
            "risk_level": report.risk_level.value,
            "score": report.score,
            "summary": mask_pii_text(report.summary),
            "trace_id": payload.get("trace_id", "n/a"),
            "shadow_mode": self.flags.should_run_shadow(),
        }

    async def health_check(self) -> dict[str, Any]:
        return {"status": "ok", "agent_id": self.agent_id, "feature_enabled": self.settings.feature_enabled}


def register_brand_safety_agent(registry: AgentRegistry, agent: BrandSafetyAgent) -> None:
    registry.register(agent)
