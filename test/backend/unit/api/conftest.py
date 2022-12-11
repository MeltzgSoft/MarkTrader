import datetime

import pytest
from mock.mock import PropertyMock, patch
from starlette.testclient import TestClient

from app import app
from models.authentication import AuthTokens
from models.brokerage import BrokerageId
from services.authentication import AuthenticationService


@pytest.fixture
def trader_app():
    yield app


@pytest.fixture
def client(trader_app):
    return TestClient(app)


@pytest.fixture
def tokens():
    return AuthTokens(
        brokerage_id=BrokerageId.TD,
        access_token="access_token",
        access_expiry=datetime.datetime.now() + datetime.timedelta(minutes=30),
        refresh_token="refresh_token",
        refresh_expiry=datetime.datetime.now() + datetime.timedelta(days=30),
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
