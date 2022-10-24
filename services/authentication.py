import datetime
import logging
import multiprocessing
import typing as t

import keyring

from common.constants import APP_NAME
from common.enums import BrokerageId
from common.models import AuthTokens
from common.utils import safe_sleep
from config import GlobalConfig
from services.brokerage import get_brokerage_service

LOGGER = logging.getLogger(f"{APP_NAME}.auth_service")

signin_lock = multiprocessing.RLock()
daemon_lock = multiprocessing.Lock()
daemon_proc = None


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

    def sign_in(self, brokerage_id: BrokerageId, access_code: str) -> None:
        LOGGER.info(
            f"Brokerage {brokerage_id}: retrieve access and refresh tokens",
            extra={"brokerage_id": brokerage_id},
        )

        self.sign_out()

        brokerage = get_brokerage_service(brokerage_id)
        access_tokens = brokerage.get_access_tokens(access_code)
        self.set_access_keys(access_tokens)
        start_daemon()

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
        start_daemon()


# The token daemon is responsible for keeping the active brokerage signed in
def refresh_access(auth_service: AuthenticationService) -> None:
    auth_tokens = auth_service.active_tokens
    if not auth_tokens:
        LOGGER.info("No active brokerage")
        safe_sleep(GlobalConfig().authentication.login_check_delay_seconds)
    else:
        now = datetime.datetime.now()
        access_remaining = auth_tokens.access_expiry - now
        refresh_remaining = auth_tokens.refresh_expiry - now

        update_refresh_token = refresh_remaining <= access_remaining

        to_wait = max(
            0,
            int(min(access_remaining, refresh_remaining).total_seconds())
            - GlobalConfig().authentication.refresh_buffer_seconds,
        )

        LOGGER.info(f"Refresh tokens in {to_wait} seconds")
        LOGGER.info(f"Update refresh token? {update_refresh_token}")

        safe_sleep(to_wait)
        brokerage_service = get_brokerage_service(auth_tokens.brokerage_id)
        new_auth_tokens = brokerage_service.refresh_tokens(
            auth_tokens, update_refresh_token=update_refresh_token
        )
        auth_service.set_access_keys(new_auth_tokens)


def _daemon_loop() -> None:
    auth_service = AuthenticationService()
    while True:
        refresh_access(auth_service)


def start_daemon() -> None:
    global daemon_proc
    with daemon_lock:
        if daemon_proc is not None:
            daemon_proc.terminate()
        daemon_proc = multiprocessing.Process(
            target=_daemon_loop,
            daemon=True,
            name="ACCESS_TOKEN_DAEMON",
        )
        daemon_proc.start()
