import datetime

import pytest
from mock.mock import PropertyMock, patch

from app import app
from common.enums import BrokerageId
from common.models import AuthTokens
from services.authentication import AuthenticationService


@pytest.fixture
def trader_app():
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture
def client(trader_app):
    return trader_app.test_client()


@pytest.fixture
def runner(trader_app):
    return trader_app.test_cli_runner()


@pytest.fixture
def tokens():
    return AuthTokens(
        BrokerageId.TD,
        "access_token",
        datetime.datetime.now() + datetime.timedelta(minutes=30),
        "refresh_token",
        datetime.datetime.now() + datetime.timedelta(days=30),
    )


@pytest.fixture
def auth_service_signed_out():
    with patch.object(
        AuthenticationService, "active_tokens", new_callable=PropertyMock
    ) as mock_tokens:
        mock_tokens.return_value = None
        yield


@pytest.fixture
def auth_service_signed_in(tokens):
    with patch.object(
        AuthenticationService, "active_tokens", new_callable=PropertyMock
    ) as mock_tokens:
        mock_tokens.return_value = tokens
        yield
