# ContentManagementAgent

브랜드 이미지 평판 검수 에이전트의 MVP 코드 스캐폴딩입니다.

## 실행

```bash
PYTHONPATH=src python -m brand_safety_agent.cli
```

## 포함 모듈

- `models.py`: Risk Knowledge / Review Report 데이터 모델
- `enrichment.py`: 후보 이벤트를 Risk Knowledge 초안으로 변환하는 기본 로직
- `reasoner.py`: 이미지 맥락과 Risk Knowledge를 매칭해 위험 리포트 생성
- `cli.py`: 샘플 입력으로 동작 확인


## 테스트

```bash
PYTHONPATH=src python -m pytest -q
```


## 현재 구현 범위

- Ingestion: collector -> normalizer -> enrichment draft
- Review Workflow: DRAFT/PENDING/APPROVED/REJECTED 상태 전이
- Retrieval: in-memory vector store(token overlap)
- End-to-end: approved knowledge 등록 후 이미지 검수
