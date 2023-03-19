import os

from Tests.Simulators.basket import BasketMock
from Tests.Simulators.catalog import CatalogMock
from Tests.Simulators.payment import PaymentMock

from Utils.Docker.docker_utils import DockerManager
from Utils.Api.ordering_api import OrderingAPI
from Utils.RabbitMQ.rabbitmq_send import RabbitMQ
from Utils.DB.db_functions import *


def test_ordering_process_over_time(docker_manager: DockerManager, basket: BasketMock, catalog: CatalogMock, payment: PaymentMock):
    orders_count_prior = select_orders_count()

    for _ in range(int(os.getenv('RELIABILITY_TEST_COUNTER'))):
        docker_manager.stop(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
        # Step 1
        basket.send_new_order()

        assert basket.received_remove_basket() is True
        assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

        # Step int(os.getenv('BOB_ORDER_ID'))
        order_id = select_last_order()['Id']
        docker_manager.start(os.getenv('ORDERING_BACKGROUND_CONTAINER'))

        assert catalog.received_check_stock() is True
        assert verify_latest_order_status_id(int(os.getenv('AWAITING_VALIDATION_STATUS')))

        # Step 3
        catalog.send_valid_stock(order_id)
        assert verify_latest_order_status_id(int(os.getenv('STOCK_CONFIRMED_STATUS')))

        # Step 4
        assert payment.received_stock_confirmed() is True

        # Step 5
        payment.send_confirmed_payment(order_id)
        assert verify_latest_order_status_id(int(os.getenv('PAID_STATUS')))

        with RabbitMQ() as mq:
            mq.purge_all()

    assert (select_orders_count() - orders_count_prior) == int(os.getenv('RELIABILITY_TEST_COUNTER'))


def test_ordering_service_after_crash(docker_manager: DockerManager, ordering_api: OrderingAPI, basket: BasketMock, catalog: CatalogMock, payment: PaymentMock):
    docker_manager.stop(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    # Step 1
    docker_manager.stop(os.getenv('ORDERING_API_CONTAINER'))
    docker_manager.start(os.getenv('ORDERING_API_CONTAINER'))
    basket.send_new_order()

    assert basket.received_remove_basket() is True
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    # Step 2
    docker_manager.stop(os.getenv('ORDERING_API_CONTAINER'))
    docker_manager.start(os.getenv('ORDERING_API_CONTAINER'))
    time.sleep(3)
    order_id = select_last_order()['Id']
    docker_manager.start(os.getenv('ORDERING_BACKGROUND_CONTAINER'))

    assert catalog.received_check_stock() is True
    assert verify_latest_order_status_id(int(os.getenv('AWAITING_VALIDATION_STATUS')))

    # Step 3
    docker_manager.stop(os.getenv('ORDERING_API_CONTAINER'))
    docker_manager.start(os.getenv('ORDERING_API_CONTAINER'))
    time.sleep(3)
    catalog.send_valid_stock(order_id)
    assert verify_latest_order_status_id(int(os.getenv('STOCK_CONFIRMED_STATUS')))

    # Step 4
    docker_manager.stop(os.getenv('ORDERING_API_CONTAINER'))
    docker_manager.start(os.getenv('ORDERING_API_CONTAINER'))
    time.sleep(3)
    assert payment.received_stock_confirmed() is True

    # Step 5
    docker_manager.stop(os.getenv('ORDERING_API_CONTAINER'))
    docker_manager.start(os.getenv('ORDERING_API_CONTAINER'))
    time.sleep(3)
    payment.send_confirmed_payment(order_id)
    assert verify_latest_order_status_id(int(os.getenv('PAID_STATUS')))

    # Step 6
    docker_manager.stop(os.getenv('ORDERING_API_CONTAINER'))
    docker_manager.start(os.getenv('ORDERING_API_CONTAINER'))
    time.sleep(3)
    ordering_api.ship_order(order_id)
    assert verify_latest_order_status_id(int(os.getenv('SHIPPED_STATUS')))


def test_cancel_other_user_order(ordering_api: OrderingAPI):
    assert ordering_api.cancel_order(int(os.getenv('BOB_ORDER_ID'))).status_code == int(os.getenv('BAD_REQUEST_RESPONSE_CODE'))


def test_ship_others_user_order(ordering_api: OrderingAPI):
    assert ordering_api.ship_order(int(os.getenv('BOB_ORDER_ID'))).status_code == int(os.getenv('BAD_REQUEST_RESPONSE_CODE'))


def test_accessing_orders_unauthorized():
    ordering_api = OrderingAPI(os.getenv('RANDOM_USER'))
    assert ordering_api.get_all_orders().status_code == int(os.getenv('UNAUTHORIZED_RESPONSE_CODE'))


def test_accessing_get_order_by_id_unauthorized():
    ordering_api = OrderingAPI(os.getenv('RANDOM_USER'))
    assert ordering_api.get_order_by_id(1).status_code == int(os.getenv('UNAUTHORIZED_RESPONSE_CODE'))


def test_accessing_card_types_unauthorized():
    ordering_api = OrderingAPI(os.getenv('RANDOM_USER'))
    assert ordering_api.get_cardtypes().status_code == int(os.getenv('UNAUTHORIZED_RESPONSE_CODE'))


def test_accessing_ship_order_unauthorized():
    ordering_api = OrderingAPI(os.getenv('RANDOM_USER'))
    assert ordering_api.ship_order(1).status_code == int(os.getenv('UNAUTHORIZED_RESPONSE_CODE'))


def test_accessing_cancel_order_unauthorized():
    ordering_api = OrderingAPI(os.getenv('RANDOM_USER'))
    assert ordering_api.cancel_order(1).status_code == int(os.getenv('UNAUTHORIZED_RESPONSE_CODE'))
