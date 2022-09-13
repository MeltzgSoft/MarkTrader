from dataclasses import dataclass
import typing as t
from urllib.parse import quote_plus

import strictyaml as yml
from dacite import from_dict

server_schema = yml.Map(
    {
        "port": yml.Int(),
    }
)


brokerage_schema = yml.Map(
    {
        "name": yml.Str(),
        "auth_uri": yml.Str(),
        "client_id": yml.Str(),
        "redirect_uri": yml.Str(),
    }
)


config_schema = yml.Map({"server": server_schema, "brokerage": brokerage_schema})


@dataclass
class ServerConfig:
    port: int


@dataclass
class BrokerageConfig:
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


@dataclass
class GlobalConfig:
    server: ServerConfig
    brokerage: BrokerageConfig


def load_config(path: str) -> GlobalConfig:
    with open(path) as f:
        return t.cast(
            GlobalConfig,
            from_dict(
                data_class=GlobalConfig,
                data=yml.parser.load(f.read(), config_schema).data,
            ),
        )
