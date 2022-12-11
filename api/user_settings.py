from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from common.config import UserSettings
from models.user_settings import UserSettingsPatch
from services.authentication import AuthenticationService

router = APIRouter(prefix="/userSettings", tags=["User Settings"])


@router.get("/", response_model=UserSettingsPatch)
async def get_user_settings() -> UserSettings:
    return UserSettings()


@router.patch("/", response_model=UserSettingsPatch)
async def update_user_settings(settings_patch: UserSettingsPatch) -> UserSettings:
    auth_service = AuthenticationService()
    user_settings = UserSettings()

    args = settings_patch.dict(exclude_unset=True)
    enable_automated_trading = args.get("enable_automated_trading")

    if enable_automated_trading is not None:
        if enable_automated_trading and not auth_service.active_tokens:
            raise HTTPException(
                status_code=422,
                detail="Cannot enable automated trading. Application does not have an active brokerage",
            )

    try:
        user_settings.update(args)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    return UserSettings()
