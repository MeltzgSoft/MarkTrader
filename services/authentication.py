import datetime
import logging
import multiprocessing
import typing as t

import keyring

from models.authentication import AuthTokens
from models.brokerage import BrokerageId

LOGGER = logging.getLogger(__name__)

signin_lock = multiprocessing.RLock()


class AuthenticationService:
    _ACTIVE_BROKERAGE_KEY = "ACTIVE_BROKERAGE"
    _ACCESS_TOKEN_KEY = "ACCESS_TOKEN"
    _REFRESH_TOKEN_KEY = "REFRESH_TOKEN"
    _ACCESS_EXPIRY_KEY = "ACCESS_EXPIRY"
    _REFRESH_EXPIRY_KEY = "REFRESH_EXPIRY"

    _ALL_KEYS = [
        _ACTIVE_BROKERAGE_KEY,
        _ACCESS_TOKEN_KEY,
        _ACCESS_EXPIRY_KEY,
        _REFRESH_TOKEN_KEY,
        _REFRESH_EXPIRY_KEY,
    ]

    def __init__(self, system: str = "MARK_TRADER") -> None:
        self._SYSTEM = system

    @property
    def active_brokerage(self) -> t.Optional[BrokerageId]:
        with signin_lock:
            brokerage_id = keyring.get_password(
                self._SYSTEM, self._ACTIVE_BROKERAGE_KEY
            )
            return BrokerageId(brokerage_id) if brokerage_id is not None else None

    @property
    def active_tokens(self) -> t.Optional[AuthTokens]:
        with signin_lock:
            if self.active_brokerage:
                return AuthTokens(
                    brokerage_id=self.active_brokerage,
                    access_token=keyring.get_password(
                        self._SYSTEM, self._ACCESS_TOKEN_KEY
                    ),
                    access_expiry=datetime.datetime.fromtimestamp(
                        float(
                            keyring.get_password(self._SYSTEM, self._ACCESS_EXPIRY_KEY)
                        )
                    ),
                    refresh_token=keyring.get_password(
                        self._SYSTEM, self._REFRESH_TOKEN_KEY
                    ),
                    refresh_expiry=datetime.datetime.fromtimestamp(
                        float(
                            keyring.get_password(self._SYSTEM, self._REFRESH_EXPIRY_KEY)
                        )
                    ),
                )
            return None

    def sign_in(self, access_tokens: AuthTokens) -> None:
        self.sign_out()
        self.set_access_keys(access_tokens)

    def set_access_keys(self, access_tokens: AuthTokens) -> None:
        with signin_lock:
            keyring.set_password(
                self._SYSTEM,
                self._ACTIVE_BROKERAGE_KEY,
                t.cast(str, access_tokens.brokerage_id.value),
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
            f"Brokerage {access_tokens.brokerage_id}: authentication information saved to keyring",
            extra={"brokerage_id": access_tokens.brokerage_id},
        )

    def sign_out(self) -> None:
        brokerage_id = keyring.get_password(self._SYSTEM, self._ACTIVE_BROKERAGE_KEY)
        if brokerage_id is None:
            LOGGER.warning("No active brokeage. signout is a no-op")
        else:
            LOGGER.info(f"Signing out of brokerage {brokerage_id}")
            with signin_lock:
                for key in self._ALL_KEYS:
                    LOGGER.debug(f"Removing {key} from keyring")
                    keyring.delete_password(self._SYSTEM, key)
