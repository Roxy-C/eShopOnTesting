import requests
import uuid
from bearer_tokenizer import BearerTokenizer


class OrderingAPI:
    def __init__(self, username='alice', password='Pass123$'):
        self.base_url = 'http://localhost:5102'
        self.bearer_token = BearerTokenizer(username, password).bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}

    def get_order_by_id(self, order_id):
        order = requests.get(f'{self.base_url}/api/v1/orders/{order_id}', headers=self.headers)
        return order

    def get_all_orders(self):
        orders = requests.get(
            f'{self.base_url}/api/v1/Orders', headers=self.headers)
        return orders

    def get_cardtypes(self):
        card_types = requests.get(
            f'{self.base_url}/api/v1/Orders/cardtypes', headers=self.headers)
        return card_types

    def cancel_order(self, orderID):
        body = {'orderNumber': orderID}
        requestID = str(uuid.uuid4())
        headers = self.headers
        headers['x-requestid'] = requestID
        request = requests.put(f'{self.base_url}/api/v1/Orders/cancel', json=body, headers=headers)
        return request.status_code

    def ship_order(self, orderID):
        body = {'orderNumber': orderID}
        requestID = str(uuid.uuid4())
        headers = self.headers
        headers['x-requestid'] = requestID
        request = requests.put(f'{self.base_url}/api/v1/Orders/ship', json=body, headers=headers)
        return request.status_code

# if __name__ == '__main__':
#     import pprint
#     api = OrderingAPI()
#     pprint.pprint(api.get_card_types().json())