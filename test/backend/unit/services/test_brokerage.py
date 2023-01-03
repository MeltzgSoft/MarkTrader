import datetime
import re
from test.backend.unit.helpers import MockResponse
from urllib.parse import parse_qsl, urlparse

import mock
import pytest

from common.config import GlobalConfig
from models.authentication import AuthTokens
from models.brokerage import BrokerageId, FrequencyType, PeriodType, PriceCandle
from models.exceptions import InvalidInput
from services.authentication import AuthenticationService
from services.brokerage import TDAmeritradeBrokerageService


def convert_strmillis_to_datetime(millis: str) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(float(millis) / 1000)


class TestTDAmeritradeBrokerageService:
    @pytest.fixture
    def old_tokens(self):
        return AuthTokens(
            brokerage_id=BrokerageId.TD,
            access_token="access_token",
            access_expiry=datetime.datetime.now() + datetime.timedelta(seconds=1),
            refresh_token="refresh_token",
            refresh_expiry=datetime.datetime.now() + datetime.timedelta(days=30),
        )

    def test_get_access_tokens(self):
        with mock.patch("services.brokerage.requests.post") as mock_post:
            mock_body = {
                "access_token": "access",
                "expires_in": 700,
                "refresh_token": "refresh",
                "refresh_token_expires_in": 3600,
            }
            mock_response = mock.Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_body

            mock_post.return_value = mock_response

            expected_call = {
                "grant_type": "authorization_code",
                "access_type": "offline",
                "code": "access code",
                "client_id": GlobalConfig().brokerages[0].client_id,
                "redirect_uri": GlobalConfig().server.redirect_uri,
            }
            auth_tokens = TDAmeritradeBrokerageService().get_access_tokens(
                expected_call["code"]
            )

            assert auth_tokens.access_token == mock_body["access_token"]
            assert auth_tokens.refresh_token == mock_body["refresh_token"]
            assert (
                auth_tokens.access_expiry - datetime.datetime.now()
            ).total_seconds() - mock_body["expires_in"] < 1
            assert (
                auth_tokens.refresh_expiry - datetime.datetime.now()
            ).total_seconds() - mock_body["refresh_token_expires_in"] < 1

            assert mock_post.call_args.kwargs["data"] == expected_call

    def test_refresh_tokens_no_new_rerfesh(self, old_tokens):
        with mock.patch("services.brokerage.requests.post") as mock_post:
            mock_body = {
                "access_token": "access",
                "expires_in": 700,
            }
            mock_response = mock.Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_body

            mock_post.return_value = mock_response

            expected_call = {
                "grant_type": "refresh_token",
                "client_id": GlobalConfig().brokerages[0].client_id,
                "redirect_uri": GlobalConfig().server.redirect_uri,
                "refresh_token": old_tokens.refresh_token,
            }
            auth_tokens = TDAmeritradeBrokerageService().refresh_tokens(old_tokens)

            assert auth_tokens.access_token == mock_body["access_token"]
            assert auth_tokens.refresh_token == old_tokens.refresh_token
            assert (
                auth_tokens.access_expiry - datetime.datetime.now()
            ).total_seconds() - mock_body["expires_in"] < 1
            assert auth_tokens.refresh_expiry == old_tokens.refresh_expiry

            assert mock_post.call_args.kwargs["data"] == expected_call

    def test_refresh_tokens_do_new_rerfesh(self, old_tokens):
        with mock.patch("services.brokerage.requests.post") as mock_post:
            mock_body = {
                "access_token": "access",
                "expires_in": 700,
                "refresh_token": "refresh",
                "refresh_token_expires_in": 3600,
            }
            mock_response = mock.Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_body

            mock_post.return_value = mock_response

            expected_call = {
                "grant_type": "refresh_token",
                "client_id": GlobalConfig().brokerages[0].client_id,
                "redirect_uri": GlobalConfig().server.redirect_uri,
                "access_type": "offline",
                "refresh_token": old_tokens.refresh_token,
            }
            auth_tokens = TDAmeritradeBrokerageService().refresh_tokens(
                old_tokens, True
            )

            assert auth_tokens.access_token == mock_body["access_token"]
            assert auth_tokens.refresh_token == mock_body["refresh_token"]
            assert (
                auth_tokens.access_expiry - datetime.datetime.now()
            ).total_seconds() - mock_body["expires_in"] < 1
            assert (
                auth_tokens.refresh_expiry - datetime.datetime.now()
            ).total_seconds() - mock_body["refresh_token_expires_in"] < 1

            assert mock_post.call_args.kwargs["data"] == expected_call

    @pytest.mark.parametrize(
        "expected_query, expected_error",
        [
            pytest.param({}, None, id="default_args"),
            pytest.param(
                {
                    "period_type": PeriodType.YEAR,
                    "periods": 5,
                    "frequency_type": FrequencyType.MONTHLY,
                    "frequency": 3,
                },
                None,
                id="frequency",
            ),
            pytest.param(
                {
                    "start_date": datetime.datetime.now() - datetime.timedelta(days=5),
                    "end_date": datetime.datetime.now(),
                },
                None,
                id="start_end",
            ),
            pytest.param(
                {"start_date": datetime.datetime.now() - datetime.timedelta(days=5)},
                None,
                id="start_only",
            ),
            pytest.param(
                {
                    "frequency": 5,
                    "start_date": datetime.datetime.now() - datetime.timedelta(days=5),
                },
                "Cannot specify both",
                id="freq_dates",
            ),
            pytest.param(
                {
                    "periods": 5,
                    "start_date": datetime.datetime.now() - datetime.timedelta(days=5),
                },
                "Cannot specify both",
                id="period_dates",
            ),
            pytest.param(
                {
                    "end_date": datetime.datetime.now() - datetime.timedelta(days=5),
                    "start_date": datetime.datetime.now(),
                },
                "Start date must be before end date",
                id="start_after_end",
            ),
        ],
    )
    def test_get_price_histories(self, user_settings, expected_query, expected_error):
        mock_response = MockResponse(
            {
                "symbol": "sym",
                "empty": False,
                "candles": [
                    {
                        "open": 1,
                        "close": 2,
                        "high": 3,
                        "low": 4,
                        "volume": 5,
                        "datetime": datetime.datetime.now().timestamp() * 1000,
                    }
                ],
            },
            200,
        )
        expected_candle = PriceCandle(**mock_response.json()["candles"][0])

        with mock.patch("services.brokerage.requests.request") as mock_request:
            mock_request.return_value = mock_response
            if expected_error:
                with pytest.raises(InvalidInput, match=expected_error):
                    TDAmeritradeBrokerageService().get_price_histories(
                        user_settings.symbols, **expected_query
                    )
                    mock_request.assert_not_called()
            else:
                history = TDAmeritradeBrokerageService().get_price_histories(
                    user_settings.symbols, **expected_query
                )
                for entry in history:
                    assert entry.prices == [expected_candle]
                assert mock_request.call_count == len(user_settings.symbols)

                if "periods" in expected_query:
                    expected_query["period"] = expected_query.pop("periods")
                for (method, url), kwargs in mock_request.call_args_list:
                    url_parts = urlparse(url)
                    actual_query = dict(
                        map(
                            lambda tup: (
                                re.sub(r"(?<!^)(?=[A-Z])", "_", tup[0]).lower(),
                                tup[1],
                            ),
                            parse_qsl(url_parts.query),
                        )
                    )

                    for k, to_type in [
                        ("period_type", PeriodType),
                        ("frequency_type", FrequencyType),
                        ("period", int),
                        ("frequency", int),
                        ("start_date", convert_strmillis_to_datetime),
                        ("end_date", convert_strmillis_to_datetime),
                    ]:
                        if k in actual_query:
                            actual_query[k] = to_type(actual_query[k])

                    if not expected_query:
                        expected_query = {
                            "period_type": PeriodType.DAY,
                            "period": 1,
                            "frequency_type": FrequencyType.MINUTE,
                            "frequency": 1,
                        }

                    assert actual_query == expected_query
                    assert method == "get"
                    assert kwargs["headers"] == {
                        "Authorization": f"Bearer {AuthenticationService().active_tokens.access_token}"
                    }
