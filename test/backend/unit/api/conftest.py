import pytest

from app import app


@pytest.fixture
def trader_app():
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture
def client(trader_app):
    return trader_app.test_client()


@pytest.fixture
def runner(trader_app):
    return trader_app.test_cli_runner()
