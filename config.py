import typing as t
from pathlib import Path

import yaml
from confz import ConfZ, ConfZFileSource

from common.enums import BrokerageId


class ServerConfig(ConfZ):
    port: int
    host: str

    @property
    def redirect_uri(self) -> str:
        return f"{self.host}:{self.port}/"


class BrokerageConfig(ConfZ):
    id: BrokerageId
    name: str
    client_id: str


class AuthenticationConfig(ConfZ):
    login_check_delay_seconds: int = 5 * 60
    refresh_buffer_seconds: int = 5 * 60


class GlobalConfig(ConfZ):
    server: ServerConfig
    authentication: AuthenticationConfig = AuthenticationConfig()
    brokerages: t.List[BrokerageConfig]

    CONFIG_SOURCES = ConfZFileSource(file=Path("./config.yml"))

    @property
    def brokerage_map(self) -> t.Dict[BrokerageId, BrokerageConfig]:
        return {b.id: b for b in self.brokerages}


class UserSettings(ConfZ):
    symbols: t.List[str]
    end_of_day_exit: bool = True
    enable_automated_trading: bool = False
    trading_frequency_seconds: int = 5
    position_size: float = 0

    CONFIG_SOURCES = ConfZFileSource(file=Path("./user-settings.yml"))

    @classmethod
    def save(cls) -> None:
        with open(cls.CONFIG_SOURCES.file, mode="w") as f:
            yaml.dump(cls.confz_instance.dict(), f)
            cls.confz_instance = None
