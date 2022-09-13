from tempfile import NamedTemporaryFile
from textwrap import dedent

import pytest

from config.app_config import ServerConfig, BrokerageConfig, load_config


@pytest.fixture
def server_config():
    return ServerConfig(9001)


@pytest.fixture
def td_brokerage():
    return BrokerageConfig(
        "TD",
        "http://authorize.me/client_id={client_id}&redirect_uri={redirect_uri}asdf",
        "my id",
        "http://my-site.com/",
    )


@pytest.fixture
def app_config_yaml(server_config, td_brokerage):
    with NamedTemporaryFile() as f:
        f.write(
            dedent(
                f"""
        server:
            port: {server_config.port}
        brokerage:
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


def test_load_config(app_config_yaml, server_config, td_brokerage):
    conf = load_config(app_config_yaml)
    assert conf.server == server_config
    assert conf.brokerage == td_brokerage


def test_materialize_redirect_uri(td_brokerage):
    assert (
        td_brokerage.materialized_auth_url
        == "http://authorize.me/client_id=my+id&redirect_uri=http%3A%2F%2Fmy-site.com%2Fasdf"
    )
