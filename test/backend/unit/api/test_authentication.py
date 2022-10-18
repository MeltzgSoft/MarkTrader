import pytest

from config import GlobalConfig

pytestmark = pytest.mark.usefixtures("global_config")


def test_get_auth_url(client):
    config = GlobalConfig()
    response = client.get("/api/v1/auth/td-a")
    assert response.status_code == 200
    assert response.json["id"] == config.brokerages[0].id.value
    assert response.json["name"] == config.brokerages[0].name
    assert response.json["uri"] == config.brokerages[0].materialized_auth_url


def test_get_auth_url_not_found(client):
    response = client.get("/api/v1/auth/other")
    assert response.status_code == 422
    assert "Brokerage ID other is not recognized" in response.json["message"]
