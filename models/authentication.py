import datetime
from typing import Optional

from pydantic import BaseModel

from models.brokerage import BrokerageId


class AuthTokens(BaseModel):
    brokerage_id: BrokerageId
    access_token: str
    access_expiry: datetime.datetime
    refresh_token: str
    refresh_expiry: datetime.datetime


class AuthUriInfo(BaseModel):
    id: BrokerageId
    name: str
    uri: str


class AuthStatus(BaseModel):
    id: Optional[BrokerageId]
    name: Optional[str]
    signed_in: bool


class AuthSignIn(BaseModel):
    id: BrokerageId
    code: str
