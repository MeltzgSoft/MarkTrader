import pytest
from mock import mock


@pytest.fixture
def mock_load_config(global_config):
    with mock.patch(
        "api.authentication.load_config", return_value=global_config
    ) as load_config:
        yield load_config


def test_get_auth_url(client, mock_load_config):
    config = mock_load_config.return_value
    response = client.get("/api/v1/auth/td-a")
    assert response.status_code == 200
    assert response.json["id"] == config.brokerage.id
    assert response.json["name"] == config.brokerage.name
    assert response.json["uri"] == config.brokerage.materialized_auth_url


@pytest.mark.usefixtures("mock_load_config")
def test_get_auth_url_not_found(client):
    response = client.get("/api/v1/auth/other")
    assert response.status_code == 404
    assert "Brokerage auth URI not found" in response.json["message"]
