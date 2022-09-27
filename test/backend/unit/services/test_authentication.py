import datetime

import keyring
import mock

from common.enums import BrokerageId
from common.models import AuthTokens
from services.authentication import AuthenticationService
from services.brokerage import TDAmeritradeBrokerageService


def test_sign_in():
    tokens = AuthTokens(
        "access", datetime.datetime.now(), "refresh", datetime.datetime.now()
    )
    with mock.patch.object(
        TDAmeritradeBrokerageService, "get_access_tokens", return_value=tokens
    ):
        auth_service = AuthenticationService()
        auth_service.sign_in(BrokerageId.TD, "access", "redirect.com")

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
            keyring.delete_password(auth_service._SYSTEM, key)
