from etl.loader      import DataLoader
from etl.validator   import DataValidator
from etl.transformer import DataTransformer
from etl.writer      import DataWriter

def run_pipeline(data_path: str, db_path: str):
    print("=" * 50)
    print("ETL 파이프라인 시작")
    print("=" * 50)

    # 1. 로드
    print("\n[1/4] 데이터 로드")
    loader = DataLoader(data_path)
    tables = loader.load_all()

    # 2. 검증
    print("\n[2/4] 데이터 품질 검증")
    validator = DataValidator()
    issues    = validator.validate(tables)
    validator.report()

    # 3. 변환
    print("\n[3/4] 데이터 변환")
    transformer = DataTransformer()
    transformed = transformer.transform(tables)

    # 4. 적재
    print("\n[4/4] DuckDB 적재")
    writer = DataWriter(db_path)
    writer.write_all(transformed)
    writer.close()

    print("\n" + "=" * 50)
    print("ETL 파이프라인 완료")
    print("=" * 50)


if __name__ == '__main__':
    run_pipeline(
        data_path='data/raw',
        db_path  ='data/ecommerce_payinsight.duckdb'
    )