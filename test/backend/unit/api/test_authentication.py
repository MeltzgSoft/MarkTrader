import datetime

from mock.mock import PropertyMock, patch

from common.enums import BrokerageId
from common.models import AuthTokens
from config import GlobalConfig
from services.authentication import AuthenticationService
from services.brokerage import get_brokerage_service


def test_get_auth_url(client):
    config = GlobalConfig()
    response = client.get("/api/v1/auth/td-a")
    brokerage_id = config.brokerages[0].id
    assert response.status_code == 200
    assert response.json["id"] == config.brokerages[0].id.value
    assert response.json["name"] == config.brokerages[0].name
    assert response.json["uri"] == get_brokerage_service(brokerage_id).auth_uri


def test_get_auth_url_not_found(client):
    response = client.get("/api/v1/auth/other")
    assert response.status_code == 422
    assert "Brokerage ID other is not recognized" in response.json["message"]


def test_get_auth_status_signed_in(client):
    config = GlobalConfig()
    tokens = AuthTokens(
        BrokerageId.TD,
        "access_token",
        datetime.datetime.now() + datetime.timedelta(minutes=30),
        "refresh_token",
        datetime.datetime.now() + datetime.timedelta(days=30),
    )
    with patch.object(
        AuthenticationService, "active_tokens", new_callable=PropertyMock
    ) as mock_tokens:
        mock_tokens.return_value = tokens

        response = client.get("/api/v1/auth/")
        assert response.status_code == 200
        assert response.json["id"] == tokens.brokerage_id.value
        assert response.json["name"] == config.brokerage_map[tokens.brokerage_id].name
        assert response.json["signedIn"]


def test_get_auth_status_signed_out(client):
    with patch.object(
        AuthenticationService, "active_tokens", new_callable=PropertyMock
    ) as mock_tokens:
        mock_tokens.return_value = None

        response = client.get("/api/v1/auth/")
        assert response.status_code == 200
        assert not response.json["id"]
        assert not response.json["name"]
        assert not response.json["signedIn"]


def test_sign_out(client):
    with patch.object(AuthenticationService, "sign_out") as mock_sign_out:
        response = client.delete("/api/v1/auth/")
        assert response.status_code == 200
        mock_sign_out.assert_called_once()
