from fastapi import APIRouter, HTTPException

from common.config import GlobalConfig
from models.authentication import AuthSignIn, AuthStatus, AuthUriInfo
from models.brokerage import BrokerageId
from services.authentication import AuthenticationService
from services.brokerage import get_brokerage_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/{brokerage_id}", response_model=AuthUriInfo)
async def get_auth_uri(brokerage_id: BrokerageId) -> AuthUriInfo:
    try:
        brokerage_service = get_brokerage_service(brokerage_id)
    except ValueError:
        raise HTTPException(
            status_code=404, detail=f"Brokerage auth URI not found for brokerage {id}"
        )

    brokerage = GlobalConfig().brokerage_map[brokerage_id]

    return AuthUriInfo(
        id=brokerage.id,
        name=brokerage.name,
        uri=brokerage_service.auth_uri,
    )


@router.get("/", response_model=AuthStatus)
async def get_auth_status() -> AuthStatus:
    auth_service = AuthenticationService()
    tokens = auth_service.active_tokens
    if not tokens:
        return AuthStatus(
            signed_in=False,
        )
    brokerage = GlobalConfig().brokerage_map[tokens.brokerage_id]
    return AuthStatus(
        id=brokerage.id,
        name=brokerage.name,
        signed_in=True,
    )


@router.post("/")
async def auth_sign_in(signin_info: AuthSignIn) -> None:
    auth_service = AuthenticationService()
    auth_service.sign_in(signin_info.id, signin_info.code)


@router.delete("/")
async def auth_sign_out() -> None:
    auth_service = AuthenticationService()
    auth_service.sign_out()
