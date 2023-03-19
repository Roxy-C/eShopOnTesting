import os

from Tests.Simulators.basket import BasketMock
from Tests.Simulators.catalog import CatalogMock
from Tests.Simulators.payment import PaymentMock

from Utils.Docker.docker_utils import DockerManager
from Utils.Api.ordering_api import OrderingAPI
from Tests.test_ordering_service import test_mss
from Utils.DB.db_functions import *


def test_get_all_orders(ordering_api: OrderingAPI):
    reponse_body, status_code = ordering_api.get_all_orders()
    assert status_code == int(os.getenv('SUCCESS_RESPONSE_CODE'))
    assert len(reponse_body) == len(select_orders_by_buyer_id(1))


def test_get_order_by_id(ordering_api: OrderingAPI):
    assert ordering_api.get_order_by_id(3).status_code == int(os.getenv('SUCCESS_RESPONSE_CODE'))


def test_negative_get_order_by_id(ordering_api: OrderingAPI):
    assert ordering_api.get_order_by_id(0).status_code == int(os.getenv('NOT_FOUND_RESPOSE_CODE'))


def test_get_cardtypes(ordering_api: OrderingAPI):
    assert ordering_api.get_cardtypes().status_code == int(os.getenv('SUCCESS_RESPONSE_CODE'))


def test_cancel_submitted_order(ordering_api: OrderingAPI, basket: BasketMock):
    basket.send_new_order()
    assert basket.received_remove_basket() is True
    order_id = select_last_order()['Id']
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    assert ordering_api.cancel_order(order_id).status_code == int(os.getenv('SUCCESS_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('CANCELLED_STATUS')))


def test_cancel_awaitingvalidation_order(docker_manager: DockerManager, ordering_api: OrderingAPI, basket: BasketMock, catalog: CatalogMock):
    docker_manager.stop(os.getenv('ORDERING_BACKGROUND_CONTAINER'))

    basket.send_new_order()
    assert basket.received_remove_basket() is True
    order_id = select_last_order()['Id']
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    docker_manager.start(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    assert catalog.received_check_stock() is True
    assert verify_latest_order_status_id(int(os.getenv('AWAITING_VALIDATION_STATUS')))

    assert ordering_api.cancel_order(order_id).status_code == int(os.getenv('SUCCESS_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('CANCELLED_STATUS')))


def test_cancel_stockconfirmed_order(docker_manager: DockerManager, ordering_api: OrderingAPI, basket: BasketMock, catalog: CatalogMock):
    docker_manager.stop(os.getenv('ORDERING_BACKGROUND_CONTAINER'))

    basket.send_new_order()
    assert basket.received_remove_basket() is True
    order_id = select_last_order()['Id']
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    docker_manager.start(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    assert catalog.received_check_stock() is True
    assert verify_latest_order_status_id(int(os.getenv('AWAITING_VALIDATION_STATUS')))

    catalog.send_valid_stock(order_id)
    assert verify_latest_order_status_id(int(os.getenv('STOCK_CONFIRMED_STATUS')))

    assert ordering_api.cancel_order(order_id).status_code == int(os.getenv('SUCCESS_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('CANCELLED_STATUS')))


def test_negative_cancel_order_after_payment(docker_manager: DockerManager, ordering_api: OrderingAPI, basket: BasketMock, catalog: CatalogMock, payment: PaymentMock):
    test_mss(docker_manager, basket, catalog, payment)
    order_id = select_last_order()['Id']

    assert ordering_api.cancel_order(order_id).status_code == int(os.getenv('BAD_REQUEST_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('PAID_STATUS')))

    ordering_api.ship_order(order_id)
    assert verify_latest_order_status_id(int(os.getenv('SHIPPED_STATUS')))

    assert ordering_api.cancel_order(order_id).status_code == int(os.getenv('BAD_REQUEST_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('SHIPPED_STATUS')))


def test_ship_paid_order(docker_manager: DockerManager, ordering_api: OrderingAPI, basket: BasketMock, catalog: CatalogMock, payment: PaymentMock):
    test_mss(docker_manager, basket, catalog, payment)
    order_id = select_last_order()['Id']

    assert ordering_api.ship_order(order_id).status_code == int(os.getenv('SUCCESS_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('SHIPPED_STATUS')))


def test_negative_ship_order(docker_manager: DockerManager, ordering_api: OrderingAPI, basket: BasketMock, catalog: CatalogMock):
    docker_manager.stop(os.getenv('ORDERING_BACKGROUND_CONTAINER'))

    basket.send_new_order()
    assert basket.received_remove_basket() is True
    order_id = select_last_order()['Id']
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    assert ordering_api.ship_order(order_id).status_code == int(os.getenv('BAD_REQUEST_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    docker_manager.start(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    assert catalog.received_check_stock() is True
    assert verify_latest_order_status_id(int(os.getenv('AWAITING_VALIDATION_STATUS')))

    assert ordering_api.ship_order(order_id).status_code == int(os.getenv('BAD_REQUEST_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('AWAITING_VALIDATION_STATUS')))

    catalog.send_valid_stock(order_id)
    assert verify_latest_order_status_id(int(os.getenv('STOCK_CONFIRMED_STATUS')))

    assert ordering_api.ship_order(order_id).status_code == int(os.getenv('BAD_REQUEST_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('STOCK_CONFIRMED_STATUS')))

    assert ordering_api.cancel_order(order_id).status_code == int(os.getenv('SUCCESS_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('CANCELLED_STATUS')))

    assert ordering_api.ship_order(order_id).status_code == int(os.getenv('BAD_REQUEST_RESPONSE_CODE'))
    assert verify_latest_order_status_id(int(os.getenv('CANCELLED_STATUS')))
