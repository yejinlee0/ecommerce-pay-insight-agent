import duckdb
import pandas as pd

class SQLExecutor:
    """DuckDB SQL 실행 클래스"""

    def __init__(self, db_path: str):
        self.con = duckdb.connect(db_path, read_only=True)

    def execute(self, sql: str) -> tuple[pd.DataFrame, str]:
        """SQL 실행 후 (DataFrame, 문자열 결과) 반환"""
        try:
            # SQL 정리
            sql = sql.strip().strip('`').strip()
            if sql.upper().startswith('SQL:'):
                sql = sql[4:].strip()

            df     = self.con.execute(sql).df()
            result = df.to_string(index=False)
            return df, result

        except Exception as e:
            return pd.DataFrame(), f"SQL 실행 오류: {str(e)}"