import requests
import openpyxl as op
from temporary_files import tmp


class GetParams:
    def __init__(self):
        self.base_url = tmp.sima_base_url
        self.sign_in = self.base_url + 'signin'
        self.item_url = self.base_url + 'item/'
        self.api_key = None
        self.params = {
            'by_sid': True
        }
        self.wholesale_category = {'Опт', 'Опт «Зоотовары»'}
        self.headers = None
        self.body = {
            "email": tmp.sima_email,
            "password": tmp.sima_password,
            "phone": tmp.sima_phone,
            "regulation": True
        }
        self.work_book = op.load_workbook(tmp.articles_file, data_only=True)
        self.work_sheet = self.work_book.active

    def get_api_key(self):
        '''
        Get JWT token
        '''
        try:
            response = requests.post(self.sign_in, json=self.body)
            response.raise_for_status()
            if response.status_code == 200:
                self.api_key = response.json().get('token')
                self.headers = {
                    'token': self.api_key,
                    'Authorization': self.api_key
                }
        except requests.exceptions.RequestException as e:
            print(f'Error during API key retrieval: {e}')

    def get_json_from_api(self, article):
        try:
            json = requests.get(f'{self.item_url}{article[0].value}', params=self.params, headers=self.headers)
            json.raise_for_status()
            if json.status_code == 401:
                self.get_api_key()
            elif json.status_code == 200:
                return json.json()
        except requests.exceptions.RequestException as e:
            print(f'Error during json retrieval: {e}')
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        return None

    def process_api_response(self, json):
        if json.get('wholesale').get('label') in self.wholesale_category:
            price = json.get('wholesale_price') * json.get('minimum_order_quantity')
        else:
            price = json.get('price') * json.get('minimum_order_quantity')
        amount_tuple = json.get('settlements_balance')[0]
        amount = amount_tuple.get('balance', amount_tuple.get('balance_text'))
        return price, amount

    def update_excel_data(self, pos, price, amount):
        self.work_sheet[f'B{pos + 2}'] = price
        if amount == 'Достаточно':
            self.work_sheet[f'C{pos + 2}'] = 100
        elif amount < 3:
            self.work_sheet[f'C{pos + 2}'] = 0
        else:
            self.work_sheet[f'C{pos + 2}'] = amount

    def save_excel_file(self):
        self.work_book.save(tmp.articles_file)

    def get_data(self):
        if not self.api_key:
            self.get_api_key()

        for pos, article in enumerate(self.work_sheet.iter_rows(min_row=2, max_col=1)):
            if article[0].value is not None:
                json = self.get_json_from_api(article)
                if json is not None:
                    price, amount = self.process_api_response(json)
                    self.update_excel_data(pos, price, amount)
        self.save_excel_file()


obj = GetParams()
obj.get_data()


