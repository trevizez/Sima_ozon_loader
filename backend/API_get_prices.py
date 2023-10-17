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

    def get_data(self):
        if not self.api_key:
            self.get_api_key()
        try:
            for pos, article in enumerate(self.work_sheet.iter_rows(min_row=2, max_col=1)):
                json = requests.get(f'{self.item_url}{article[0].value}', params=self.params, headers=self.headers)
                json.raise_for_status()
                if json.status_code == 200:
                    data = json.json()
                    print(data)
                    print(data.get('wholesale').get('label'))
                    if data.get('wholesale').get('label') == 'Опт' or data.get('wholesale').get('label') == 'Опт «Зоотовары»':
                        price = data.get('wholesale_price') * data.get('minimum_order_quantity')
                    else:
                        price = data.get('price') * data.get('minimum_order_quantity')
                    amount_tuple = data.get('settlements_balance')[0]
                    if amount_tuple.get('balance') is not None:
                        amount = amount_tuple.get('balance')
                    else:
                        amount = amount_tuple.get('balance_text')
                    print(amount)
                    self.work_sheet[f'B{pos + 2}'] = price
                    if amount == 'Достаточно':
                        self.work_sheet[f'C{pos + 2}'] = 100
                    elif amount < 3:
                        self.work_sheet[f'C{pos + 2}'] = 0
                    else:
                        self.work_sheet[f'C{pos + 2}'] = amount
        except requests.exceptions.RequestException as e:
            print(f'Error during data retrieval: {e}')
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            self.work_book.save(tmp.articles_file)


obj = GetParams()
obj.get_data()


