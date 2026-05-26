# Brand Safety Agent 아키텍처

## 1. 목표
브랜드 이미지 배포 전 민감 이슈 연상 리스크를 사전 탐지하는 백엔드 모듈을 제공한다.

## 2. 모듈 경계
- `models.py`: 도메인 모델/DTO
- `pipeline.py`: 수집->정규화->초안 생성
- `review.py`: DRAFT/PENDING/APPROVED/REJECTED 상태 전이
- `reasoner.py`: 이미지 맥락 기반 리스크 점수화
- `service.py` / `agent_module.py`: 유스케이스 오케스트레이션
- `adapters.py` / `vector_store.py`: 저장소/검색 어댑터
- `smagent_bridge.py`: SMAgent 런타임 연결(AgentBase 호환)
- `settings.py` / `feature_flags.py`: 설정/병행운영 제어
- `errors.py` / `contracts.py`: 에러코드/계약 표준화

## 3. 의존성 방향
- 비즈니스 로직(`reasoner`, `review`)은 프레임워크 비의존.
- 외부 I/O는 어댑터 계층(`adapters`, `vector_store`)으로 한정.
- 브리지 계층(`smagent_bridge`)이 런타임 호출 계약을 캡슐화.

## 4. 장애/복구 전략
- feature flag 비활성 시 즉시 graceful return.
- 저장소 조회 실패 시 표준 에러 payload 반환.
- shadow mode 플래그로 병행운영 가능.

## 5. 확장 포인트
- `AsyncInMemoryRiskRepository` -> pgvector repository 교체
- `RiskReasoner` -> LLM reasoner 하이브리드 확장
- `mask_pii_text` -> 정책 기반 마스킹 엔진 교체
