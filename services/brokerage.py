import abc
import datetime
import logging
import typing as t
from abc import ABC
from urllib.parse import quote_plus, urlencode

import requests
from requests import Response

from common.config import GlobalConfig
from models.authentication import AuthTokens
from models.brokerage import (
    BrokerageId,
    FrequencyType,
    PeriodType,
    PriceCandle,
    PriceHistory,
)
from models.exceptions import InvalidInput
from services.authentication import AuthenticationService

LOGGER = logging.getLogger(__name__)


def _make_authenticated_request(
    url: str,
    method: str = "get",
    data: t.Optional[t.Dict[str, t.Any]] = None,
    headers: t.Optional[t.Dict[str, t.Any]] = None,
) -> Response:
    active_tokens = AuthenticationService().active_tokens
    if not active_tokens:
        raise ValueError("Cannot make request without tokens")
    headers = headers or {}
    headers.update({"Authorization": f"Bearer {active_tokens.access_token}"})
    if data:
        headers.update({"Content-Type": "application/json"})

    return requests.request(method, url, headers=headers, data=data)


class BaseBrokerageService(ABC):
    brokerage_id: t.Optional[BrokerageId] = None

    def __init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.brokerage_id is None:
            raise RuntimeError("brokerage_id must not be None")

    def get_price_histories(
        self,
        symbols: t.List[str],
        period_type: t.Optional[PeriodType] = None,
        periods: t.Optional[int] = None,
        frequency_type: t.Optional[FrequencyType] = None,
        frequency: t.Optional[int] = None,
        start_date: t.Optional[datetime.datetime] = None,
        end_date: t.Optional[datetime.datetime] = None,
    ) -> t.List[PriceHistory]:
        if not start_date and not end_date:
            periods = periods or 1
            frequency = frequency or 1
        elif periods or frequency:
            raise InvalidInput(
                "Cannot specify both period/frequency and start/end dates"
            )
        elif start_date and end_date and start_date >= end_date:
            raise InvalidInput("Start date must be before end date")

        return self._get_price_histories(
            symbols,
            period_type,
            periods,
            frequency_type,
            frequency,
            start_date,
            end_date,
        )

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

    @abc.abstractmethod
    def _get_price_histories(
        self,
        symbols: t.List[str],
        period_type: t.Union[PeriodType, None],
        periods: t.Union[int, None],
        frequency_type: t.Union[FrequencyType, None],
        frequency: t.Union[int, None],
        start_date: t.Union[datetime.datetime, None],
        end_date: t.Union[datetime.datetime, None],
    ) -> t.List[PriceHistory]:
        raise NotImplemented

    @property
    @abc.abstractmethod
    def auth_uri(self) -> str:
        raise NotImplemented


class TDAmeritradeBrokerageService(BaseBrokerageService):
    brokerage_id = BrokerageId.TD

    OAUTH_URI_FORMATTER = "https://auth.tdameritrade.com/auth?response_type=code&redirect_uri={redirect_uri}&client_id={client_id}%40AMER.OAUTHAP"
    API_ROOT = "https://api.tdameritrade.com/v1/"

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

    def _get_price_histories(
        self,
        symbols: t.List[str],
        period_type: t.Union[PeriodType, None],
        periods: t.Union[int, None],
        frequency_type: t.Union[FrequencyType, None],
        frequency: t.Union[int, None],
        start_date: t.Union[datetime.datetime, None],
        end_date: t.Union[datetime.datetime, None],
    ) -> t.List[PriceHistory]:
        histories = []

        start_date_ms = start_date.timestamp() * 1000 if start_date else None
        end_date_ms = end_date.timestamp() * 1000 if end_date else None

        query_parameters = {
            "periodType": period_type.value,
            "period": periods,
            "frequencyType": frequency_type.value,
            "frequency": frequency,
            "startDate": start_date_ms,
            "endDate": end_date_ms,
        }
        query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
        query_string = urlencode(query_parameters)
        route_format = (
            f"{self.API_ROOT}marketdata/{{symbol}}/pricehistory?{query_string}"
        )

        for symbol in symbols:
            route = route_format.format(symbol=symbol)
            response = _make_authenticated_request(route, "get")
            if response.status_code == 200:
                candles = [
                    PriceCandle(**candle) for candle in response.json()["candles"]
                ]
            else:
                LOGGER.error(
                    f"Could not retrieve price data for symbol {symbol}. Response: {response}"
                )
                candles = []
            histories.append(PriceHistory(symbol=symbol, prices=candles))

        return histories

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
            f"{self.API_ROOT}oauth2/token",
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
