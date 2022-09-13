from app import binance_db, yfinance_db
from app.models.symbol import BinanceSymbol, YFinanceSymbol


def test_binance_symbol_creation(test_app, clean_dbs):
    symbol = BinanceSymbol(name="BTCUSDT")
    with test_app.app_context():
        binance_db.session.add(symbol)
        binance_db.session.commit()

        assert symbol.name == "BTCUSDT"
        assert symbol.selected is False
        assert symbol.id == 1


def test_yfinance_symbol_creation(test_app, clean_dbs):
    symbol = YFinanceSymbol(name="BTCUSDT")
    with test_app.app_context():
        yfinance_db.session.add(symbol)
        yfinance_db.session.commit()

        assert symbol.name == "BTCUSDT"
        assert symbol.selected is False
        assert symbol.id == 1
