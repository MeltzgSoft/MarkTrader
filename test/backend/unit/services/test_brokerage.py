import datetime

import mock
import pytest

from common.enums import BrokerageId
from common.models import AuthTokens
from config import GlobalConfig
from services.brokerage import TDAmeritradeBrokerageService


@pytest.mark.usefixtures("global_config")
class TestTDAmeritradeBrokerageService:
    @pytest.fixture
    def old_tokens(self):
        return AuthTokens(
            BrokerageId.TD,
            "access_token",
            datetime.datetime.now() + datetime.timedelta(seconds=1),
            "refresh_token",
            datetime.datetime.now() + datetime.timedelta(days=30),
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
