import typing as t
from pathlib import Path

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
