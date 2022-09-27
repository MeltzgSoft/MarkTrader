import datetime
from typing import NamedTuple


class AuthTokens(NamedTuple):
    access_token: str
    access_expiry: datetime.datetime
    refresh_token: str
    refresh_expiry: datetime.datetime
