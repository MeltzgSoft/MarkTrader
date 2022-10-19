import pytest

from config import GlobalConfig
from services.brokerage import get_brokerage_service

pytestmark = pytest.mark.usefixtures("global_config")


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
