import datetime

import keyring

from models.authentication import AuthTokens
from models.brokerage import BrokerageId
from services.authentication import AuthenticationService


def test_sign_in():
    tokens = AuthTokens(
        brokerage_id=BrokerageId.TD,
        access_token="access_token",
        access_expiry=datetime.datetime.now(),
        refresh_token="refresh_token",
        refresh_expiry=datetime.datetime.now(),
    )

    auth_service = AuthenticationService("TEST")
    assert auth_service.active_brokerage is None

    auth_service.sign_in(tokens)

    for key, expected_value in [
        (auth_service._ACTIVE_BROKERAGE_KEY, BrokerageId.TD.value),
        (auth_service._ACCESS_TOKEN_KEY, tokens.access_token),
        (auth_service._REFRESH_TOKEN_KEY, tokens.refresh_token),
        (auth_service._ACCESS_EXPIRY_KEY, str(tokens.access_expiry.timestamp())),
        (auth_service._REFRESH_EXPIRY_KEY, str(tokens.refresh_expiry.timestamp())),
    ]:
        assert keyring.get_password(auth_service._SYSTEM, key) == expected_value, key

    assert auth_service.active_brokerage == BrokerageId.TD
    assert auth_service.active_tokens == tokens

    for key in auth_service._ALL_KEYS:
        keyring.delete_password(auth_service._SYSTEM, key)


def test_sign_out():
    tokens = AuthTokens(
        brokerage_id=BrokerageId.TD,
        access_token="access_token",
        access_expiry=datetime.datetime.now(),
        refresh_token="refresh_token",
        refresh_expiry=datetime.datetime.now(),
    )

    auth_service = AuthenticationService("TEST")
    assert auth_service.active_brokerage is None

    auth_service.sign_in(tokens)
    assert auth_service.active_brokerage == BrokerageId.TD
    assert auth_service.active_tokens == tokens
    auth_service.sign_out()
    assert auth_service.active_brokerage is None
    assert auth_service.active_tokens is None
