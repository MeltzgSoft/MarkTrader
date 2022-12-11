import typing as t
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
import yaml
from confz import ConfZDataSource, ConfZFileSource

from common.config import GlobalConfig, UserSettings


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
def user_settings() -> UserSettings:
    with UserSettings.change_config_sources(
        ConfZDataSource(
            data={
                "enable_automated_trading": True,
                "end_of_day_exit": True,
                "position_size": 10.0,
                "symbols": ["AMZN", "IBM"],
                "trading_frequency_seconds": 1,
            }
        )
    ):
        yield UserSettings()


@pytest.fixture(autouse=True)
def global_config(server_config, td_brokerage):
    with GlobalConfig.change_config_sources(
        ConfZDataSource(data={"server": server_config, "brokerages": [td_brokerage]})
    ):
        yield


# All tests should be forced to use these fixtures for their user settings and global config


@pytest.fixture(autouse=True)
def user_settings_from_file(user_settings) -> t.Tuple[UserSettings, str]:
    with NamedTemporaryFile(mode="w", suffix=".yml") as tmp:
        yaml.dump(user_settings.dict(), tmp)
        tmp.flush()
        with UserSettings.change_config_sources(ConfZFileSource(file=Path(tmp.name))):
            yield UserSettings(), tmp.name
