import json
import uuid

from ..RabbitMQ.rabbitmq_send import RabbitMQ


class CatalogMock:

    def __init__(self) -> None:
        with open('rabbitMessages.json') as j:
            self.data = json.load(j)

    def send_itemsInStock(self, orderId):
        payload = self.data['OrderStockConfirmedIntegrationEvent']
        payload['OrderId'] = orderId
        payload['Id'] = str(uuid.uuid4())
        payload['CreationDate'] = get_current_time()

        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key='OrderStockConfirmedIntegrationEvent',
                       body=json.dumps(self.payload))

    def send_invalidStock(self, orderId):
        payload = self.data['OrderStockRejectedIntegrationEvent']
        payload['OrderId'] = orderId
        payload['Id'] = str(uuid.uuid4())
        payload['CreationDate'] = get_current_time()

        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key='OrderStockRejectedIntegrationEvent',
                       body=json.dumps(self.payload))
