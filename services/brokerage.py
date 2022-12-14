import abc
import datetime
import logging
import typing as t
from abc import ABC
from urllib.parse import quote_plus

import requests

from common.config import APP_NAME, GlobalConfig
from models.authentication import AuthTokens
from models.brokerage import BrokerageId

LOGGER = logging.getLogger(f"{APP_NAME}.brokerage_service")


class BaseBrokerageService(ABC):
    brokerage_id: t.Optional[BrokerageId] = None

    def __init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.brokerage_id is None:
            raise RuntimeError("brokerage_id must not be None")

    @abc.abstractmethod
    def get_access_tokens(self, access_code: str) -> AuthTokens:
        raise NotImplemented

    @abc.abstractmethod
    def refresh_tokens(
        self,
        auth_tokens: AuthTokens,
        update_refresh_token: bool = False,
    ) -> AuthTokens:
        raise NotImplemented

    @property
    @abc.abstractmethod
    def auth_uri(self) -> str:
        raise NotImplemented


class TDAmeritradeBrokerageService(BaseBrokerageService):
    brokerage_id = BrokerageId.TD

    OAUTH_URI_FORMATTER = "https://auth.tdameritrade.com/auth?response_type=code&redirect_uri={redirect_uri}&client_id={client_id}%40AMER.OAUTHAP"

    def get_access_tokens(self, access_code: str) -> AuthTokens:
        LOGGER.info(
            f"Brokerage {self.brokerage_id}: Get access tokens",
            extra={"brokerage_id": self.brokerage_id},
        )

        brokerage = GlobalConfig().brokerage_map[self.brokerage_id]

        body = {
            "grant_type": "authorization_code",
            "access_type": "offline",
            "code": access_code,
            "client_id": brokerage.client_id,
            "redirect_uri": GlobalConfig().server.redirect_uri,
        }

        return self._make_access_token_request(body)

    def refresh_tokens(
        self,
        auth_tokens: AuthTokens,
        update_refresh_token: bool = False,
    ) -> AuthTokens:
        brokerage = GlobalConfig().brokerage_map[self.brokerage_id]
        body = {
            "grant_type": "refresh_token",
            "client_id": brokerage.client_id,
            "redirect_uri": GlobalConfig().server.redirect_uri,
            "refresh_token": auth_tokens.refresh_token,
        }
        if update_refresh_token:
            body["access_type"] = "offline"

        return self._make_access_token_request(body, auth_tokens)

    @property
    def auth_uri(self) -> str:
        brokerage = GlobalConfig().brokerage_map[self.brokerage_id]
        return self.OAUTH_URI_FORMATTER.format(
            redirect_uri=quote_plus(GlobalConfig().server.redirect_uri),
            client_id=quote_plus(brokerage.client_id),
        )

    def _make_access_token_request(
        self, body: t.Dict[str, str], old_tokens: t.Optional[AuthTokens] = None
    ) -> AuthTokens:
        response = requests.post(
            "https://api.tdameritrade.com/v1/oauth2/token",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if response.status_code != 200:
            LOGGER.error(
                f"unexpected response for post access token: ({response.status_code}) {str(response.content)}",
                extra={
                    "status_code": response.status_code,
                    "content": response.content,
                },
            )
            raise RuntimeError("unexpected response for post access token")

        response_body = response.json()
        LOGGER.info(
            f"Brokerage {self.brokerage_id}: Login successful",
            extra={"brokerage_id": self.brokerage_id},
        )
        if old_tokens:
            default_refresh_token = old_tokens.refresh_token
            default_refresh_expiry = old_tokens.refresh_expiry
        else:
            default_refresh_token = None
            default_refresh_expiry = datetime.datetime.now()

        return AuthTokens(
            brokerage_id=self.brokerage_id,
            access_token=response_body["access_token"],
            access_expiry=datetime.datetime.now()
            + datetime.timedelta(seconds=response_body["expires_in"]),
            refresh_token=response_body.get("refresh_token", default_refresh_token),
            refresh_expiry=datetime.datetime.now()
            + datetime.timedelta(seconds=response_body["refresh_token_expires_in"])
            if "refresh_token_expires_in" in response_body
            else default_refresh_expiry,
        )


def get_brokerage_service(brokerage_id: BrokerageId) -> BaseBrokerageService:
    if brokerage_id == BrokerageId.TD:
        return TDAmeritradeBrokerageService()
    raise ValueError(f"unrecognized brokerage ID {brokerage_id}")
