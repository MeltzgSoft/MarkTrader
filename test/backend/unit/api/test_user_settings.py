import pytest
from mock.mock import PropertyMock, patch

from config import UserSettings
from services.authentication import AuthenticationService


@pytest.fixture
def auth_service_signed_out():
    with patch.object(
        AuthenticationService, "active_tokens", new_callable=PropertyMock
    ) as mock_tokens:
        mock_tokens.return_value = None
        yield


def to_camel_case(snake_str):
    components = snake_str.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + "".join(x.title() for x in components[1:])


def test_get_user_settings(client, user_settings):
    response = client.get("/api/v1/userSettings/")
    assert response.status_code == 200
    assert response.json == {
        to_camel_case(k): v for k, v in user_settings.dict().items()
    }


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        pytest.param(
            {"positionSize": 5, "enableAutomatedTrading": True}, 200, id="success"
        ),
        pytest.param(
            {"positionSize": -5, "enableAutomatedTrading": True}, 422, id="fail"
        ),
    ],
)
def test_patch_user_settings(client, user_settings_from_file, payload, expected_status):
    original_settings, _ = user_settings_from_file
    original_settings = original_settings.dict()
    original_settings_camel = {
        to_camel_case(k): v for k, v in original_settings.items()
    }

    response = client.patch("/api/v1/userSettings/", json=payload)

    assert response.status_code == expected_status

    if expected_status == 200:
        original_settings_camel.update(payload)
        assert response.json == original_settings_camel
    else:
        assert UserSettings().dict() == original_settings


@pytest.mark.usefixtures("auth_service_signed_out")
def test_enable_trading_signed_out(client, user_settings_from_file):
    original_settings, _ = user_settings_from_file
    original_settings = original_settings.dict()

    response = client.patch(
        "/api/v1/userSettings/",
        json={"positionSize": 5, "enableAutomatedTrading": True},
    )

    assert response.status_code == 422

    assert UserSettings().dict() == original_settings
