# Brand Safety Agent 처리 흐름

## 1) Ingestion 흐름
1. `SourceCollector`가 원시 payload 수집
2. `Normalizer`가 공통 스키마로 정규화
3. `EnrichmentService`가 `RiskKnowledge(DRAFT)` 생성
4. `ReviewWorkflow`로 PENDING/APPROVED 전이
5. 승인 데이터만 저장소 upsert

## 2) Review 흐름
1. 클라이언트가 이미지 문맥(ocr/objects/mood)을 전달
2. `BrandSafetyAgentService`가 저장소 검색(top-k)
3. `RiskReasoner`가 트리거 중첩 분석 + 점수화
4. 결과를 `ReviewReport`로 반환

## 3) SMAgent 통합 흐름
1. 앱 startup에서 `BrandSafetyAgent` 인스턴스 생성
2. `AgentRegistry.register(agent)` 등록
3. `stream_chat` 호출 시 payload -> `ImageContext` 변환
4. feature flag 확인 후 review 실행
5. 표준 응답 또는 표준 에러 payload 반환
