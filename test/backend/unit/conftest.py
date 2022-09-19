from tempfile import NamedTemporaryFile
from textwrap import dedent

import pytest

from config.app_config import ServerConfig, BrokerageConfig, GlobalConfig


@pytest.fixture
def server_config():
    return ServerConfig(9001)


@pytest.fixture
def td_brokerage():
    return BrokerageConfig(
        "td-a",
        "TD Ameritrade",
        "http://authorize.me/client_id={client_id}&redirect_uri={redirect_uri}asdf",
        "my id",
        "http://my-site.com/",
    )


@pytest.fixture
def global_config(server_config, td_brokerage):
    return GlobalConfig(server_config, td_brokerage)


@pytest.fixture
def app_config_yaml(server_config, td_brokerage):
    with NamedTemporaryFile() as f:
        f.write(
            dedent(
                f"""
        server:
            port: {server_config.port}
        brokerage:
            id: {td_brokerage.id}
            name: {td_brokerage.name}
            auth_uri: {td_brokerage.auth_uri}
            client_id: {td_brokerage.client_id}
            redirect_uri: {td_brokerage.redirect_uri}
        """
            ).encode("utf-8")
        )
        f.flush()
        f.seek(0)
        yield f.name
