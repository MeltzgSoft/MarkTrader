import datetime
import typing as t

import mock
import pytest

from config import GlobalConfig
from services.brokerage import TDAmeritradeBrokerageService


@pytest.mark.usefixtures("global_config")
class TestTDAmeritradeBrokerageService:
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
                "redirect_uri": "http://url.com",
            }
            auth_tokens = TDAmeritradeBrokerageService().get_access_tokens(
                expected_call["code"], t.cast(str, expected_call["redirect_uri"])
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
