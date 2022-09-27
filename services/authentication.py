import logging
import typing as t

import keyring

from common.constants import APP_NAME
from common.enums import BrokerageId
from services.brokerage import get_brokerage_service

LOGGER = logging.getLogger(f"{APP_NAME}.auth_service")


class AuthenticationService:
    _ACTIVE_BROKERAGE_KEY = "ACTIVE_BROKERAGE"
    _ACCESS_TOKEN_KEY = "ACCESS_TOKEN"
    _REFRESH_TOKEN_KEY = "REFRESH_TOKEN"
    _ACCESS_EXPIRY_KEY = "ACCESS_EXPIRY"
    _REFRESH_EXPIRY_KEY = "REFRESH_EXPIRY"

    def __init__(self, system: str = "MARK_TRADER") -> None:
        self._SYSTEM = system

    def sign_in(
        self, brokerage_id: BrokerageId, access_code: str, redirect_uri: str
    ) -> None:
        LOGGER.info(
            f"Brokerage {brokerage_id}: retrieve access and refresh tokens",
            extra={"brokerage_id": brokerage_id},
        )

        brokerage = get_brokerage_service(brokerage_id)
        access_tokens = brokerage.get_access_tokens(access_code, redirect_uri)

        keyring.set_password(
            self._SYSTEM, self._ACTIVE_BROKERAGE_KEY, t.cast(str, brokerage_id.value)
        )
        keyring.set_password(
            self._SYSTEM, self._ACCESS_TOKEN_KEY, access_tokens.access_token
        )
        keyring.set_password(
            self._SYSTEM,
            self._ACCESS_EXPIRY_KEY,
            str(access_tokens.access_expiry.timestamp()),
        )
        keyring.set_password(
            self._SYSTEM, self._REFRESH_TOKEN_KEY, access_tokens.refresh_token
        )
        keyring.set_password(
            self._SYSTEM,
            self._REFRESH_EXPIRY_KEY,
            str(access_tokens.refresh_expiry.timestamp()),
        )

        LOGGER.info(
            f"Brokerage {brokerage_id}: authentication information saved to keyring",
            extra={"brokerage_id": brokerage_id},
        )
