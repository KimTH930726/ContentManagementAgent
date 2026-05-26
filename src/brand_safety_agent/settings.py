from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(slots=True)
class BrandSafetySettings:
    feature_enabled: bool = True
    query_top_k: int = 5
    external_http_timeout_seconds: float = 10.0
    retry_max_attempts: int = 2

    @classmethod
    def from_env(cls) -> "BrandSafetySettings":
        return cls(
            feature_enabled=os.getenv("BSA_FEATURE_ENABLED", "true").lower() == "true",
            query_top_k=int(os.getenv("BSA_QUERY_TOP_K", "5")),
            external_http_timeout_seconds=float(os.getenv("BSA_HTTP_TIMEOUT_SECONDS", "10")),
            retry_max_attempts=int(os.getenv("BSA_RETRY_MAX_ATTEMPTS", "2")),
        )
