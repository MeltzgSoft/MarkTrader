import datetime
from typing import NamedTuple

from common.enums import BrokerageId


class AuthTokens(NamedTuple):
    brokerage_id: BrokerageId
    access_token: str
    access_expiry: datetime.datetime
    refresh_token: str
    refresh_expiry: datetime.datetime
