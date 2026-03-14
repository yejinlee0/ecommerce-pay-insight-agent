import pandas as pd

REGION_MAP = {
    'SP': 'Southeast', 'RJ': 'Southeast', 'MG': 'Southeast', 'ES': 'Southeast',
    'BA': 'Northeast', 'CE': 'Northeast', 'PE': 'Northeast', 'MA': 'Northeast',
    'PB': 'Northeast', 'RN': 'Northeast', 'AL': 'Northeast', 'SE': 'Northeast',
    'PI': 'Northeast', 'RS': 'South',     'PR': 'South',     'SC': 'South',
    'PA': 'North',     'AM': 'North',     'RO': 'North',     'AC': 'North',
    'AP': 'North',     'RR': 'North',     'TO': 'North',
    'GO': 'Central-West', 'MT': 'Central-West',
    'MS': 'Central-West', 'DF': 'Central-West',
}

class DataTransformer:
    """전처리 및 파생 컬럼 생성 클래스"""

    def transform(self, tables: dict) -> dict:
        """전체 변환 실행 후 dim/fact 딕셔너리 반환"""
        print("  변환 시작...")
        dim_customer = self._build_dim_customer(tables['customers'])
        dim_product  = self._build_dim_product(tables['products'], tables['category'], tables['items'])
        dim_seller   = self._build_dim_seller(tables['sellers'])
        dim_date     = self._build_dim_date(tables['orders'])
        dim_campaign = self._build_dim_campaign()
        fact_orders  = self._build_fact_orders(tables)

        print("  변환 완료")
        return {
            'dim_customer': dim_customer,
            'dim_product' : dim_product,
            'dim_seller'  : dim_seller,
            'dim_date'    : dim_date,
            'dim_campaign': dim_campaign,
            'fact_orders' : fact_orders,
        }

    def _build_dim_customer(self, customers):
        df = customers.copy()
        df['region_group'] = df['customer_state'].map(REGION_MAP).fillna('Other')
        return df[['customer_id','customer_unique_id','customer_city','customer_state','region_group']]

    def _build_dim_product(self, products, category, items):
        df = products.merge(category, on='product_category_name', how='left')
        df['product_category_name_english'] = df['product_category_name_english'].fillna('Unknown')
        df['product_weight_g']  = df['product_weight_g'].fillna(df['product_weight_g'].median())
        df['product_photos_qty']= df['product_photos_qty'].fillna(0)

        avg_price = items.groupby('product_id')['price'].mean().reset_index()
        avg_price.columns = ['product_id', 'avg_price']
        df = df.merge(avg_price, on='product_id', how='left')
        df['price_tier'] = df['avg_price'].apply(self._get_price_tier)

        result = df[['product_id','product_category_name_english','price_tier','product_weight_g','product_photos_qty']].copy()
        result.columns = ['product_id','category_name_en','price_tier','weight_g','photos_qty']
        return result

    def _build_dim_seller(self, sellers):
        df = sellers.copy()
        df['region_group'] = df['seller_state'].map(REGION_MAP).fillna('Other')
        return df[['seller_id','seller_city','seller_state','region_group']]

    def _build_dim_date(self, orders):
        orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
        date_range = pd.date_range(
            start=orders['order_purchase_timestamp'].min().date(),
            end=orders['order_purchase_timestamp'].max().date(),
            freq='D'
        )
        return pd.DataFrame({
            'date_id'   : [int(d.strftime('%Y%m%d')) for d in date_range],
            'year'      : [d.year     for d in date_range],
            'month'     : [d.month    for d in date_range],
            'quarter'   : [d.quarter  for d in date_range],
            'weekday'   : [d.weekday()for d in date_range],
            'is_weekend': [d.weekday() >= 5 for d in date_range],
        })

    def _build_dim_campaign(self):
        return pd.DataFrame([
            (1, 'Voucher_Campaign',  '바우처 결제 캠페인'),
            (2, 'Installment_Promo', '할부 프로모션 (6회 이상)'),
            (3, 'Standard',          '일반 결제'),
        ], columns=['campaign_id','campaign_type','description'])

    def _build_fact_orders(self, tables):
        orders   = tables['orders'].copy()
        payments = tables['payments']
        items    = tables['items']
        reviews  = tables['reviews']

        # 날짜 변환 및 파생 컬럼
        orders['order_purchase_timestamp']      = pd.to_datetime(orders['order_purchase_timestamp'])
        orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
        orders['delivery_days'] = (
            orders['order_delivered_customer_date'] -
            orders['order_purchase_timestamp']
        ).dt.days

        # 이상치 처리
        orders.loc[orders['delivery_days'] > 100, 'delivery_days'] = None
        orders.loc[orders['delivery_days'] == 0,  'delivery_days'] = 1

        orders['converted']  = (orders['order_status'] == 'delivered').astype(int)
        orders['is_delayed'] = orders['delivery_days'] > 14
        orders['date_id']    = orders['order_purchase_timestamp'].dt.strftime('%Y%m%d').astype(int)

        # payments 집계
        pay_agg = payments.groupby('order_id').agg(
            payment_type         =('payment_type',         'first'),
            payment_value        =('payment_value',        'sum'),
            payment_installments =('payment_installments', 'max'),
        ).reset_index()
        pay_agg['campaign_type'] = pay_agg.apply(self._get_campaign_type, axis=1)
        pay_agg['campaign_id']   = pay_agg['campaign_type'].map({
            'Voucher_Campaign': 1, 'Installment_Promo': 2, 'Standard': 3
        })

        # items, reviews 집계
        items_agg   = items.groupby('order_id').agg(
            product_id   =('product_id',   'first'),
            seller_id    =('seller_id',    'first'),
            freight_value=('freight_value','sum'),
        ).reset_index()
        reviews_agg = reviews.groupby('order_id')['review_score'].mean().reset_index()

        # 전체 조인
        fact = orders[[
            'order_id','customer_id','date_id',
            'order_status','delivery_days','converted','is_delayed'
        ]].merge(pay_agg,    on='order_id', how='left') \
          .merge(items_agg,  on='order_id', how='left') \
          .merge(reviews_agg,on='order_id', how='left')

        fact['review_score'] = fact['review_score'].round(0).astype('Int64')

        return fact[[
            'order_id','customer_id','product_id','seller_id','date_id',
            'campaign_id','payment_type','payment_value','payment_installments',
            'freight_value','review_score','order_status','delivery_days',
            'converted','is_delayed','campaign_type'
        ]]

    @staticmethod
    def _get_price_tier(price):
        if pd.isna(price):  return 'Unknown'
        elif price < 50:    return 'Low'
        elif price < 150:   return 'Mid'
        elif price < 500:   return 'High'
        else:               return 'Premium'

    @staticmethod
    def _get_campaign_type(row):
        if row['payment_type'] == 'voucher': return 'Voucher_Campaign'
        elif row['payment_installments'] >= 6: return 'Installment_Promo'
        else: return 'Standard'