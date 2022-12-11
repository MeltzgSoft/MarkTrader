import pytest
from pydantic import ValidationError

from common.config import UserSettings


class TestUserSettings:
    def test_update_success(self, user_settings_from_file):
        settings, path = user_settings_from_file
        update_data = {"symbols": ["GE", "ibm", "ABC"], "end_of_day_exit": False}
        original = settings.dict()
        settings.update(update_data)
        updated_dict = UserSettings().dict()

        update_data["symbols"] = [s.upper() for s in update_data["symbols"]]
        for key in updated_dict.keys():
            if key in update_data:
                assert updated_dict[key] == update_data[key]
                update_data.pop(key)
            else:
                assert updated_dict[key] == original[key]
            original.pop(key)

        assert not original
        assert not update_data

    def test_update_fail(self, user_settings_from_file):
        settings, path = user_settings_from_file
        update_data = {"position_size": -1}
        original = settings.dict()
        with pytest.raises(ValidationError):
            settings.update(update_data)
        updated_dict = UserSettings().dict()

        assert original == updated_dict
