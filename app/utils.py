import duckdb
import pandas as pd

def run_query(sql: str, db_path: str = 'data/ecommerce_payinsight.duckdb') -> pd.DataFrame:
    # SQL 실행 후 DataFrame 반환
    con = duckdb.connect(db_path, read_only=True)
    try:
        return con.execute(sql).df()
    except Exception as e:
        return pd.DataFrame({'error': [str(e)]})
    finally:
        con.close()