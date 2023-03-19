import os

from Tests.Simulators.basket import BasketMock
from Tests.Simulators.catalog import CatalogMock
from Tests.Simulators.payment import PaymentMock

from Utils.Docker.docker_utils import DockerManager
from Utils.DB.db_functions import *


# MSS
def test_mss(docker_manager: DockerManager, basket: BasketMock, catalog: CatalogMock, payment: PaymentMock):
    docker_manager.stop(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    prior_count = select_orders_count()
    # Step 1
    basket.send_new_order()

    assert basket.received_remove_basket() is True

    assert prior_count < select_orders_count()
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    # Step 2
    order_id = select_last_order()['Id']
    docker_manager.start(os.getenv('ORDERING_BACKGROUND_CONTAINER'))

    assert catalog.received_check_stock() is True
    assert verify_latest_order_status_id(
        int(os.getenv('AWAITING_VALIDATION_STATUS')))

    # Step 3
    catalog.send_valid_stock(order_id)
    assert verify_latest_order_status_id(
        int(os.getenv('STOCK_CONFIRMED_STATUS')))

    # Step 4
    assert payment.received_stock_confirmed() is True

    # Step 5
    payment.send_confirmed_payment(order_id)
    assert verify_latest_order_status_id(int(os.getenv('PAID_STATUS')))


def test_ordering_items_outOfStock(docker_manager: DockerManager, basket: BasketMock, catalog: CatalogMock):
    docker_manager.stop(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    # Step 1
    basket.send_new_order()
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    # Step 2
    order_id = select_last_order()['Id']
    docker_manager.start(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    assert verify_latest_order_status_id(
        int(os.getenv('AWAITING_VALIDATION_STATUS')))

    # Step 3
    catalog.send_invalid_stock(order_id)
    assert verify_latest_order_status_id(int(os.getenv('CANCELLED_STATUS')))


def test_ordering_with_invalid_payment(docker_manager: DockerManager, basket: BasketMock, catalog: CatalogMock, payment: PaymentMock):
    docker_manager.stop(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    # Step 1
    basket.send_new_order()
    assert verify_latest_order_status_id(int(os.getenv('SUBMITTED_STATUS')))

    # Step 2
    order_id = select_last_order()['Id']
    docker_manager.start(os.getenv('ORDERING_BACKGROUND_CONTAINER'))
    assert verify_latest_order_status_id(
        int(os.getenv('AWAITING_VALIDATION_STATUS')))

    # Step 3
    catalog.send_valid_stock(order_id)
    assert verify_latest_order_status_id(
        int(os.getenv('STOCK_CONFIRMED_STATUS')))

    # Step 4
    payment.send_rejected_payment(order_id)
    assert verify_latest_order_status_id(int(os.getenv('CANCELLED_STATUS')))
