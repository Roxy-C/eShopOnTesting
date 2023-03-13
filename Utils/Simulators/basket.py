import json
import uuid

from ..RabbitMQ.rabbitmq_send import RabbitMQ


class BasketMock:

    def __init__(self) -> None:
        with open('rabbitMessages.json') as j:
            self.data = json.load(j)

    def send_new_order(self):
        payload = self.data['UserCheckoutAcceptedIntegrationEvent']

        payload['RequestId'] = str(uuid.uuid4())
        payload['Id'] = str(uuid.uuid4())
        payload['CreationDate'] = get_current_time()

        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key='UserCheckoutAcceptedIntegrationEvent',
                       body=json.dumps(payload))
