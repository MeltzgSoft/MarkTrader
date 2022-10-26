import datetime

import keyring
import mock
import pytest

from common.enums import BrokerageId
from common.models import AuthTokens
from config import GlobalConfig
from services.authentication import AuthenticationService, refresh_access
from services.brokerage import TDAmeritradeBrokerageService

pytestmark = pytest.mark.usefixtures("global_config")


@pytest.fixture
def mock_start_daemon():
    with mock.patch("services.authentication.start_daemon") as mock_start:
        yield mock_start


def test_sign_in(mock_start_daemon):
    tokens = AuthTokens(
        BrokerageId.TD,
        "access",
        datetime.datetime.now(),
        "refresh",
        datetime.datetime.now(),
    )

    auth_service = AuthenticationService("TEST")
    assert auth_service.active_brokerage is None

    with mock.patch.object(
        TDAmeritradeBrokerageService, "get_access_tokens", return_value=tokens
    ):

        auth_service.sign_in(BrokerageId.TD, "access")

        assert mock_start_daemon.call_count == 2

        for key, expected_value in [
            (auth_service._ACTIVE_BROKERAGE_KEY, BrokerageId.TD.value),
            (auth_service._ACCESS_TOKEN_KEY, tokens.access_token),
            (auth_service._REFRESH_TOKEN_KEY, tokens.refresh_token),
            (auth_service._ACCESS_EXPIRY_KEY, str(tokens.access_expiry.timestamp())),
            (auth_service._REFRESH_EXPIRY_KEY, str(tokens.refresh_expiry.timestamp())),
        ]:
            assert (
                keyring.get_password(auth_service._SYSTEM, key) == expected_value
            ), key

        assert auth_service.active_brokerage == BrokerageId.TD
        assert auth_service.active_tokens == tokens

        for key in auth_service._ALL_KEYS:
            keyring.delete_password(auth_service._SYSTEM, key)


def test_sign_out(mock_start_daemon):
    tokens = AuthTokens(
        BrokerageId.TD,
        "access",
        datetime.datetime.now(),
        "refresh",
        datetime.datetime.now(),
    )

    auth_service = AuthenticationService("TEST")
    assert auth_service.active_brokerage is None

    with mock.patch.object(
        TDAmeritradeBrokerageService, "get_access_tokens", return_value=tokens
    ):
        auth_service.sign_in(BrokerageId.TD, "access")
        assert auth_service.active_brokerage == BrokerageId.TD
        assert auth_service.active_tokens == tokens
        auth_service.sign_out()
        assert auth_service.active_brokerage is None
        assert auth_service.active_tokens is None

        assert mock_start_daemon.call_count == 3


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
                BrokerageId.TD,
                "access_token",
                datetime.datetime.now() + datetime.timedelta(minutes=30),
                "refresh_token",
                datetime.datetime.now() + datetime.timedelta(days=30),
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
                BrokerageId.TD,
                "access_token",
                datetime.datetime.now() + datetime.timedelta(days=30),
                "refresh_token",
                datetime.datetime.now() + datetime.timedelta(minutes=30),
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
                BrokerageId.TD,
                "access_token",
                datetime.datetime.now() + datetime.timedelta(seconds=1),
                "refresh_token",
                datetime.datetime.now() + datetime.timedelta(days=30),
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
            BrokerageId.TD,
            "new-access_token",
            datetime.datetime.now() + datetime.timedelta(minutes=30),
            "new-refresh_token",
            datetime.datetime.now() + datetime.timedelta(days=30),
        )
        with mock.patch("services.authentication.safe_sleep") as mock_sleep, mock.patch(
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
        with mock.patch("services.authentication.safe_sleep") as mock_sleep, mock.patch(
            "services.brokerage.TDAmeritradeBrokerageService.refresh_tokens"
        ) as mock_refresh:
            refresh_access(auth_service)
            mock_refresh.assert_not_called()
            mock_sleep.assert_called_once_with(
                GlobalConfig().authentication.login_check_delay_seconds
            )
