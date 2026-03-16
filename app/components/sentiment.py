import duckdb
import pandas as pd

def get_sentiment_summary(db_path: str = 'data/ecommerce_payinsight.duckdb') -> dict:
    # 리뷰 점수 기반 감성 분석
    con = duckdb.connect(db_path, read_only=True)
    try:
        # 감성 분류 (긍정/중립/부정)
        summary = con.execute("""
            SELECT
                CASE
                    WHEN review_score >= 4 THEN '긍정 (4~5점)'
                    WHEN review_score = 3  THEN '중립 (3점)'
                    ELSE                       '부정 (1~2점)'
                END as sentiment,
                COUNT(*) as cnt,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as pct
            FROM vw_order_full
            WHERE review_score IS NOT NULL
            GROUP BY sentiment
            ORDER BY cnt DESC
        """).df()

        # 지역별 평균 리뷰 점수
        regional = con.execute("""
            SELECT
                region_group,
                ROUND(AVG(review_score), 2) as avg_score,
                COUNT(*) as cnt
            FROM vw_order_full
            WHERE review_score IS NOT NULL
            GROUP BY region_group
            ORDER BY avg_score ASC
        """).df()

        # 배송 지연 여부별 리뷰 점수
        delay_impact = con.execute("""
            SELECT
                CASE WHEN is_delayed THEN '지연' ELSE '정상' END as delivery_status,
                ROUND(AVG(review_score), 2) as avg_score,
                COUNT(*) as cnt
            FROM vw_order_full
            WHERE review_score IS NOT NULL
            GROUP BY is_delayed
            ORDER BY avg_score ASC
        """).df()

        return {
            "summary"      : summary,
            "regional"     : regional,
            "delay_impact" : delay_impact
        }
    finally:
        con.close()