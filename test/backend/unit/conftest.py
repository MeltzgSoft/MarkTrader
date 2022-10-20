import pytest
from confz import ConfZDataSource

from config import GlobalConfig


@pytest.fixture
def server_config():
    return {"port": 9001, "host": "http://my-site.com"}


@pytest.fixture
def td_brokerage():
    return {
        "id": "td-a",
        "name": "TD Ameritrade",
        "auth_uri": "http://authorize.me/client_id={client_id}&redirect_uri={redirect_uri}asdf",
        "client_id": "my id",
    }


@pytest.fixture
def global_config(server_config, td_brokerage):
    with GlobalConfig.change_config_sources(
        ConfZDataSource(data={"server": server_config, "brokerages": [td_brokerage]})
    ):
        yield
