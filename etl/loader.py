import pandas as pd
from pathlib import Path

class DataLoader:
    """Olist CSV 9개 파일을 로드하는 클래스"""

    def __init__(self, data_path: str):
        self.data_path = Path(data_path)

    def load_all(self) -> dict:
        """9개 테이블 전부 로드 후 딕셔너리로 반환"""
        files = {
            'orders'   : 'olist_orders_dataset.csv',
            'payments' : 'olist_order_payments_dataset.csv',
            'customers': 'olist_customers_dataset.csv',
            'reviews'  : 'olist_order_reviews_dataset.csv',
            'items'    : 'olist_order_items_dataset.csv',
            'products' : 'olist_products_dataset.csv',
            'sellers'  : 'olist_sellers_dataset.csv',
            'geo'      : 'olist_geolocation_dataset.csv',
            'category' : 'product_category_name_translation.csv',
        }

        tables = {}
        for name, filename in files.items():
            path = self.data_path / filename
            tables[name] = pd.read_csv(path)
            print(f"  로드 완료: {name:12s} {tables[name].shape[0]:>7,}행")

        return tables