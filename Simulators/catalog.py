import json
import uuid

from base import MockBase
from ..Utils.RabbitMQ.rabbitmq_send import RabbitMQ


class CatalogMock(MockBase):
    
    def send_message(self, order_id, event) -> None:
        payload = self.data[event]
        payload['OrderId'] = order_id
        payload['Id'] = str(uuid.uuid4())
        payload['CreationDate'] = get_current_time()

        with RabbitMQ() as mq:
            mq.publish(exchange='eshop_event_bus',
                       routing_key=event,
                       body=json.dumps(self.payload))
        
        
        
        
    #     payload = self.data['OrderStockConfirmedIntegrationEvent']
    #     payload['OrderId'] = orderId
    #     payload['Id'] = str(uuid.uuid4())
    #     payload['CreationDate'] = get_current_time()

    #     with RabbitMQ() as mq:
    #         mq.publish(exchange='eshop_event_bus',
    #                    routing_key='OrderStockConfirmedIntegrationEvent',
    #                    body=json.dumps(self.payload))
        

    # def send_invalidStock(self, orderId):
    #     payload = self.data['OrderStockRejectedIntegrationEvent']
    #     payload['OrderId'] = orderId
    #     payload['Id'] = str(uuid.uuid4())
    #     payload['CreationDate'] = get_current_time()

    #     with RabbitMQ() as mq:
    #         mq.publish(exchange='eshop_event_bus',
    #                    routing_key='OrderStockRejectedIntegrationEvent',
    #                    body=json.dumps(self.payload))
