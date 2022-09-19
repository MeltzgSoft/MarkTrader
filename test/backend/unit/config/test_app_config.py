from config.app_config import load_config


def test_load_config(app_config_yaml, server_config, td_brokerage):
    conf = load_config(app_config_yaml)
    assert conf.server == server_config
    assert conf.brokerage == td_brokerage


def test_materialize_redirect_uri(td_brokerage):
    assert (
        td_brokerage.materialized_auth_url
        == "http://authorize.me/client_id=my+id&redirect_uri=http%3A%2F%2Fmy-site.com%2Fasdf"
    )
