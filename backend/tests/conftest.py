import pytest

import app
from app import binance_db, yfinance_db
from app.config import TestConfig
from app.models.symbol import BinanceSymbol


@pytest.fixture()
def test_app(scope="session"):
    a = app.create_app(config_cls=TestConfig)
    a.testing = True
    yield a


@pytest.fixture()
def client(test_app):
    yield test_app.test_client()


def __prepare_dbs(_app):
    with _app.app_context():
        binance_db.create_all(app=_app)
        yfinance_db.create_all(app=_app)


def __cleanup_dbs(_app):
    with _app.app_context():
        binance_db.drop_all()
        yfinance_db.drop_all()


def __mock_populate_dbs(_app):
    # todo: also populate yfinance db

    with _app.app_context():
        symbol1 = BinanceSymbol("BTCUSDT")
        symbol2 = BinanceSymbol("ETHBTC")

        binance_db.session.add(symbol1)
        binance_db.session.add(symbol2)

        binance_db.session.commit()


def __populate_dbs(_app, _client):
    # todo: also populate yfinance db

    with _app.app_context():
        # todo: replace with real data
        symbol1 = BinanceSymbol("BTCUSDT")
        symbol2 = BinanceSymbol("ETHBTC")

        binance_db.session.add(symbol1)
        binance_db.session.add(symbol2)

        binance_db.session.commit()

        query = {"fetch": True}
        _client.get("/binance/bars/BTCUSDT", query_string=query)
        _client.get("/binance/bars/ETHBTC", query_string=query)


@pytest.fixture()
def clean_dbs(test_app):
    __prepare_dbs(test_app)

    yield

    __cleanup_dbs(test_app)


@pytest.fixture()
def mock_populated_dbs(test_app, client):
    __prepare_dbs(test_app)
    __mock_populate_dbs(test_app)

    yield

    __cleanup_dbs(test_app)


@pytest.fixture()
def populated_dbs(test_app, client):
    __prepare_dbs(test_app)
    __populate_dbs(test_app, client)

    yield

    __cleanup_dbs(test_app)
