import requests
from temporary_files import tmp


class Load_data:
    def __init__(self):
        self.base_url = tmp.ozon_base_url
        self.update_price_url = self.base_url + 'v1/product/import/prices'
        self.update_stocks_url = self.base_url + 'v1/product/import/prices'
        self.headers = {
            'Client-Id': tmp.ozon_client_id,
            'Api-Key': tmp.ozon_api_key
        }

    def update_prices(self):
        pass

    def update_stocks(self):
        pass

    def made_a_discount_on_product(self):
        pass