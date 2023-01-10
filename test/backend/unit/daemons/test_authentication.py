import datetime

import mock
import pytest

from common.config import GlobalConfig
from daemons.authentication import refresh_access
from models.authentication import AuthTokens
from models.brokerage import BrokerageId
from services.authentication import AuthenticationService


class TestRefreshAccess:
    @pytest.fixture
    def auth_service_not_signed_in(self):
        auth_service = AuthenticationService("TEST-no-sign-in")
        assert not auth_service.active_tokens
        yield auth_service
        auth_service.sign_out()

    @pytest.fixture
    def auth_service_access_first(self):
        auth_service = AuthenticationService("TEST-access-first")
        auth_service.set_access_keys(
            AuthTokens(
                brokerage_id=BrokerageId.TD,
                access_token="access_token",
                access_expiry=datetime.datetime.now() + datetime.timedelta(minutes=30),
                refresh_token="refresh_token",
                refresh_expiry=datetime.datetime.now() + datetime.timedelta(days=30),
            )
        )
        assert auth_service.active_tokens
        yield auth_service
        auth_service.sign_out()

    @pytest.fixture
    def auth_service_refresh_first(self):
        auth_service = AuthenticationService("TEST-refresh-first")
        auth_service.set_access_keys(
            AuthTokens(
                brokerage_id=BrokerageId.TD,
                access_token="access_token",
                access_expiry=datetime.datetime.now() + datetime.timedelta(days=30),
                refresh_token="refresh_token",
                refresh_expiry=datetime.datetime.now() + datetime.timedelta(minutes=30),
            )
        )
        assert auth_service.active_tokens
        yield auth_service
        auth_service.sign_out()

    @pytest.fixture
    def auth_service_expire_before_buffer(self):
        auth_service = AuthenticationService("TEST-immediate")
        auth_service.set_access_keys(
            AuthTokens(
                brokerage_id=BrokerageId.TD,
                access_token="access_token",
                access_expiry=datetime.datetime.now() + datetime.timedelta(seconds=1),
                refresh_token="refresh_token",
                refresh_expiry=datetime.datetime.now() + datetime.timedelta(days=30),
            )
        )
        assert auth_service.active_tokens
        yield auth_service
        auth_service.sign_out()

    @pytest.mark.parametrize(
        "auth_service, update_refresh, expected_sleep",
        [
            pytest.param(
                "auth_service_access_first",
                False,
                lambda val: 0 < val < 30 * 60,
                id="access",
            ),
            pytest.param(
                "auth_service_refresh_first",
                True,
                lambda val: 0 < val < 30 * 60,
                id="refresh",
            ),
            pytest.param(
                "auth_service_expire_before_buffer",
                False,
                lambda val: val == 0,
                id="immediate",
            ),
        ],
    )
    def test_refresh_correct_tokens(
        self, request, auth_service, update_refresh, expected_sleep
    ):
        auth_service = request.getfixturevalue(auth_service)
        old_tokens = auth_service.active_tokens
        new_tokens = AuthTokens(
            brokerage_id=BrokerageId.TD,
            access_token="new-access_token",
            access_expiry=datetime.datetime.now() + datetime.timedelta(minutes=30),
            refresh_token="new-refresh_token",
            refresh_expiry=datetime.datetime.now() + datetime.timedelta(days=30),
        )
        with mock.patch("daemons.authentication.safe_sleep") as mock_sleep, mock.patch(
            "services.brokerage.TDAmeritradeBrokerageService.refresh_tokens",
            return_value=new_tokens,
        ) as mock_refresh:
            refresh_access(auth_service)
            mock_refresh.assert_called_once_with(
                old_tokens, update_refresh_token=update_refresh
            )
            mock_sleep.assert_called()
            assert expected_sleep(mock_sleep.call_args[0][0])
            assert auth_service.active_tokens == new_tokens

    def test_refresh_not_signed_in(self, auth_service_not_signed_in):
        auth_service = auth_service_not_signed_in
        with mock.patch("daemons.authentication.safe_sleep") as mock_sleep, mock.patch(
            "services.brokerage.TDAmeritradeBrokerageService.refresh_tokens"
        ) as mock_refresh:
            refresh_access(auth_service)
            mock_refresh.assert_not_called()
            mock_sleep.assert_called_once_with(
                GlobalConfig().authentication.login_check_delay_seconds
            )
