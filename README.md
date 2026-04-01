# ecommerce-pay-insight-agent
## 💳 E-Commerce Pay Insight Agent

> 자연어로 질문하면 AI가 SQL 생성 → 차트 → 인사이트까지 자동으로 분석하는 Text2SQL Agent 시스템

---

## 프로젝트 개요

브라질 이커머스 데이터(10만+ 행, 9개 테이블)를 활용해 마케팅 담당자가 SQL을 몰라도
자연어 질문만으로 데이터를 분석하고 인사이트를 얻을 수 있는 환경을 구축

**"지역별 평균 배송일은?"** 이라고 입력하면
AI가 SQL을 생성하고, 차트를 그리고, 비즈니스 인사이트까지 자동으로 설명

---

## 아키텍처
```
[Olist 9개 CSV]
      ↓
[ETL 파이프라인] — Loader / Validator / Transformer / Writer
      ↓
[DuckDB Star Schema] — fact_orders + dim 5개 + vw_order_full (Semantic Flat View)
      ↓
[LangChain Text2SQL Agent]
  - Qdrant: 스키마/Few-shot 벡터 검색
  - GPT-4o-mini: SQL 생성 + 인사이트 해석
  - DuckDB: SQL 실행
      ↓
┌─────────────────────────────────────┐
│  Streamlit  — 자연어 채팅 + 자동 차트    │
│  Superset   — KPI 대시보드            │
└─────────────────────────────────────┘
```

---

## 핵심 설계

### Semantic Flat View
9개 테이블을 22개 컬럼의 단일 뷰로 통합해 LLM이 조인 없이
단순한 SQL로 대부분의 비즈니스 질문에 답할 수 있도록 설계

### Vector-based Schema Retrieval
스키마 메타데이터와 Few-shot 예시를 Qdrant에 임베딩해두고
질문이 들어오면 유사한 컨텍스트를 동적으로 검색해 프롬프트에 주입

### 모듈화 ETL
```
etl/
├── loader.py      # CSV 9개 로드
├── validator.py   # 데이터 품질 검증
├── transformer.py # Star Schema 변환 + 파생 컬럼 생성
├── writer.py      # DuckDB 적재
└── pipeline.py    # 전체 실행 진입점
```

---

## 기술 스택

| 역할 | 기술 |
|---|---|
| 데이터마트 | DuckDB |
| ETL | Pandas |
| LLM | OpenAI GPT-4o-mini |
| 벡터DB | Qdrant |
| Agent | LangChain |
| UI | Streamlit + Plotly |
| 대시보드 | Apache Superset |

---

## QA 벤치마크 결과

| 난이도 | 정확도 |
|---|---|
| 단순 집계 | 2/2 |
| 조건 필터 | 2/2 |
| 멀티 분석 | 1/1 |
| **전체** | **5/5 (100%)** |
