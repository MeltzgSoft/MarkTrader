import typing as t
from pathlib import Path
from urllib.parse import quote_plus

from confz import ConfZ, ConfZFileSource

from common.enums import BrokerageId


class ServerConfig(ConfZ):
    port: int


class BrokerageConfig(ConfZ):
    id: BrokerageId
    name: str
    client_id: str
    redirect_uri: str


class GlobalConfig(ConfZ):
    server: ServerConfig
    brokerages: t.List[BrokerageConfig]

    CONFIG_SOURCES = ConfZFileSource(file=Path("./config.yml"))

    @property
    def brokerage_map(self) -> t.Dict[BrokerageId, BrokerageConfig]:
        return {b.id: b for b in self.brokerages}
