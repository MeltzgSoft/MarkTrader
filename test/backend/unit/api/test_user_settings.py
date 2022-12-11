import pytest

from common.config import UserSettings


def test_get_user_settings(client, user_settings):
    response = client.get("/api/v1/userSettings/")
    assert response.status_code == 200
    assert response.json() == user_settings.dict()


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        pytest.param(
            {"position_size": 5, "enable_automated_trading": True}, 200, id="success"
        ),
        pytest.param(
            {"position_size": -5, "enable_automated_trading": True}, 422, id="fail"
        ),
    ],
)
@pytest.mark.usefixtures("auth_service_signed_in")
def test_patch_user_settings(client, user_settings_from_file, payload, expected_status):
    original_settings, _ = user_settings_from_file
    original_settings = original_settings.dict()

    response = client.patch("/api/v1/userSettings/", json=payload)

    assert response.status_code == expected_status, response.json

    if expected_status == 200:
        original_settings.update(payload)
        assert response.json() == original_settings
    else:
        assert UserSettings().dict() == original_settings


@pytest.mark.usefixtures("auth_service_signed_out")
def test_enable_trading_signed_out(client, user_settings_from_file):
    original_settings, _ = user_settings_from_file
    original_settings = original_settings.dict()

    response = client.patch(
        "/api/v1/userSettings/",
        json={"position_size": 5, "enable_automated_trading": True},
    )

    assert response.status_code == 422

    assert UserSettings().dict() == original_settings
