import pytest

from ..Utils.Api.ordering_api import OrderingAPI
from ..Utils.DB.db_utils import MSSQLConnector
from ..Utils.Docker.docker_utils import DockerManager
from ..Utils.RabbitMQ.rabbitmq_send import RabbitMQ
from ..Utils.RabbitMQ.rabbitmq_receive import callback as Listener


@pytest.fixture(scope="class")
def oneTimeSetUp():
    pass


def 