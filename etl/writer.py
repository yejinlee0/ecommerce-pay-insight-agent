import duckdb

class DataWriter:
    """DuckDB 적재 클래스"""

    def __init__(self, db_path: str):
        self.con = duckdb.connect(db_path)

    def write_all(self, transformed: dict):
        """변환된 데이터 전부 DuckDB에 적재"""
        order = [
            'dim_date', 'dim_customer', 'dim_product',
            'dim_seller', 'dim_campaign', 'fact_orders'
        ]
        for table_name in order:
            df = transformed[table_name]
            self.con.execute(f"DELETE FROM {table_name}")
            self.con.register(f'{table_name}_df', df)
            self.con.execute(f"INSERT INTO {table_name} SELECT * FROM {table_name}_df")
            print(f"  적재 완료: {table_name:15s} {len(df):>7,}행")

    def close(self):
        self.con.close()