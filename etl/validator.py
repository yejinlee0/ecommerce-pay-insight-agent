import pandas as pd

class DataValidator:
    """데이터 품질 검증 클래스"""
    def __init__(self):
        self.issues = []

    def validate(self, tables: dict) -> list:
        """전체 품질 검증 실행"""
        self.issues = []
        self._check_missing(tables)
        self._check_duplicates(tables)
        self._check_anomalies(tables)
        return self.issues

    def _check_missing(self, tables):
        checks = [
            ('orders',   'order_delivered_customer_date'),
            ('reviews',  'review_comment_message'),
            ('products', 'product_category_name'),
        ]
        for table_name, col in checks:
            df = tables[table_name]
            cnt = df[col].isnull().sum()
            if cnt > 0:
                self.issues.append({
                    'type'    : '결측치',
                    'location': f'{table_name}.{col}',
                    'count'   : cnt,
                    'action'  : '처리 예정'
                })

    def _check_duplicates(self, tables):
        checks = [
            ('orders',   'order_id'),
            ('customers','customer_id'),
        ]
        for table_name, col in checks:
            df = tables[table_name]
            cnt = df[col].duplicated().sum()
            if cnt > 0:
                self.issues.append({
                    'type'    : '중복',
                    'location': f'{table_name}.{col}',
                    'count'   : cnt,
                    'action'  : '중복 제거'
                })

    def _check_anomalies(self, tables):
        items = tables['items']
        cnt = (items['price'] <= 0).sum()
        if cnt > 0:
            self.issues.append({
                'type'    : '이상치',
                'location': 'items.price <= 0',
                'count'   : cnt,
                'action'  : '해당 행 제거'
            })

    def report(self):
        """검증 결과 출력"""
        print(f"\n{'='*50}")
        print(f"데이터 품질 검증 결과: {len(self.issues)}개 이슈 발견")
        print(f"{'='*50}")
        for i, issue in enumerate(self.issues, 1):
            print(f"{i}. [{issue['type']}] {issue['location']}: {issue['count']:,}건")