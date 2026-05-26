from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FeatureFlagRouter:
    brand_safety_enabled: bool = True
    shadow_mode: bool = False

    def can_run_primary(self) -> bool:
        return self.brand_safety_enabled

    def should_run_shadow(self) -> bool:
        return self.shadow_mode
