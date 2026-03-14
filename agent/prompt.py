#from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
FEW_SHOT_EXAMPLES = """
Q: 결제수단별 평균 결제금액은?
SQL: SELECT payment_type, ROUND(AVG(payment_value), 0) as avg_value FROM vw_order_full GROUP BY payment_type ORDER BY avg_value DESC

Q: 지역별 평균 배송일은?
SQL: SELECT region_group, ROUND(AVG(delivery_days), 1) as avg_days FROM vw_order_full WHERE delivery_days IS NOT NULL GROUP BY region_group ORDER BY avg_days DESC

Q: 배송 지연된 주문의 평균 리뷰 점수는?
SQL: SELECT is_delayed, ROUND(AVG(review_score), 2) as avg_score FROM vw_order_full WHERE review_score IS NOT NULL GROUP BY is_delayed

Q: 캠페인별 전환율은?
SQL: SELECT campaign_type, ROUND(AVG(converted)*100, 1) as cvr_pct FROM vw_order_full GROUP BY campaign_type ORDER BY cvr_pct DESC

Q: Southeast 지역에서 가장 많이 팔린 카테고리 Top 5는?
SQL: SELECT category_name_en, COUNT(*) as cnt FROM vw_order_full WHERE region_group = 'Southeast' GROUP BY category_name_en ORDER BY cnt DESC LIMIT 5

Q: 리뷰 점수가 1~2점인 주문의 비율은?
SQL: SELECT ROUND(SUM(CASE WHEN review_score <= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as low_score_pct FROM vw_order_full

Q: 월별 주문 수 추이는?
SQL: SELECT year, month, COUNT(*) as order_cnt FROM vw_order_full GROUP BY year, month ORDER BY year, month

Q: 할부 6회 이상 결제의 평균 금액은?
SQL: SELECT ROUND(AVG(payment_value), 0) as avg_value FROM vw_order_full WHERE payment_installments >= 6

Q: 가격대별 평균 리뷰 점수는?
SQL: SELECT price_tier, ROUND(AVG(review_score), 2) as avg_score FROM vw_order_full WHERE review_score IS NOT NULL GROUP BY price_tier ORDER BY avg_score DESC

Q: 주말 vs 평일 주문 수 비교는?
SQL: SELECT is_weekend, COUNT(*) as cnt, ROUND(AVG(payment_value), 0) as avg_value FROM vw_order_full GROUP BY is_weekend
"""

SQL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """당신은 DuckDB SQL 전문가입니다.
아래 규칙을 반드시 따르세요:
1. 반드시 vw_order_full 뷰를 기본으로 사용하세요
2. SQL만 반환하세요. 설명이나 마크다운 없이 순수 SQL만 출력하세요
3. 컬럼명은 스키마에 있는 것만 사용하세요
4. LIMIT는 명시되지 않으면 붙이지 마세요

=== Few-shot 예시 ===
{few_shot}

=== 관련 스키마 컨텍스트 ===
{context}
"""),
    ("human", "질문: {question}\nSQL:")
])

INTERPRET_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """당신은 데이터 분석 전문가입니다.
SQL 쿼리 결과를 보고 비즈니스 인사이트를 한국어로 설명하세요.
- 핵심 수치를 언급하세요
- 원인 분석을 포함하세요
- 개선 제안을 1가지 포함하세요
- 3~5문장으로 간결하게 작성하세요
"""),
    ("human", "질문: {question}\n\n쿼리 결과:\n{result}\n\n분석:")
])