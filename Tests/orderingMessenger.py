import json
import uuid

from ..Utils.RabbitMQ.rabbitmq_send import RabbitMQ
from ..Utils.useful_functions import get_current_time


class OrderingMessenger:

    def __init__(self) -> None:
        with open('..Data.rabbitMessages.json') as j:
            self.data = json.load(j)

    def emptyBasket(self):
        # Empty basket message is sent from ordering -> basket
        payload = self.data['OrderStartedIntegrationEvent']
        payload['Id'] = str(uuid.uuid4())
        payload['CreationDate'] = get_current_time()

        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key='OrderStartedIntegrationEvent',
                       body=json.dumps(payload))

    def verify_items_inStock(self, orderID):
        payload = self.data['OrderStatusChangedToAwaitingValidationIntegrationEvent']
        payload['OrderId'] = orderID
        payload['Id'] = str(uuid.uuid4())
        payload['CreationDate'] = get_current_time()

        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       body=json.dumps(payload))

    def verify_payment(self, orderID):
        payload = self.data['OrderStatusChangedToStockConfirmedIntegrationEvent']
        payload['OrderId'] = orderID
        payload['Id'] = str(uuid.uuid4())
        payload['CreationDate'] = get_current_time()

        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key='OrderStatusChangedToStockConfirmedIntegrationEvent',
                       body=json.dumps(payload))
