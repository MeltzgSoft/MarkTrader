import datetime
import logging
import multiprocessing

from common.config import GlobalConfig
from common.utils import safe_sleep
from models.brokerage import BrokerageId
from services.authentication import AuthenticationService
from services.brokerage import get_brokerage_service

LOGGER = logging.getLogger(__name__)

daemon_lock = multiprocessing.Lock()
daemon_proc = None


def sign_in(brokerage_id: BrokerageId, access_code: str) -> None:
    auth_service = AuthenticationService()
    brokerage_service = get_brokerage_service(brokerage_id)
    access_tokens = brokerage_service.get_access_tokens(access_code)
    auth_service.sign_in(access_tokens)
    start_daemon()


def sign_out() -> None:
    auth_service = AuthenticationService()
    auth_service.sign_out()
    start_daemon()


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
    while True:
        auth_service = AuthenticationService()
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
