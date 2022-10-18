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
    auth_uri: str
    client_id: str
    redirect_uri: str

    @property
    def materialized_auth_url(self) -> str:
        return self.auth_uri.format(
            redirect_uri=quote_plus(self.redirect_uri),
            client_id=quote_plus(self.client_id),
        )


class GlobalConfig(ConfZ):
    server: ServerConfig
    brokerages: t.List[BrokerageConfig]

    CONFIG_SOURCES = ConfZFileSource(file=Path("./config.yml"))

    @property
    def brokerage_map(self) -> t.Dict[BrokerageId, BrokerageConfig]:
        return {b.id: b for b in self.brokerages}
