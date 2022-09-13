from abc import ABC, abstractmethod
from typing import Union

from app.ext import binance_client, binance_db, yfinance_db
from app.models.symbol import BinanceSymbol, SymbolMixin, YFinanceSymbol


class SymbolServiceInterface(ABC):
    @staticmethod
    @abstractmethod
    def fetch_symbols() -> list[SymbolMixin]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_all_symbols() -> list[SymbolMixin]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_symbol_by_name(symbol_name: str) -> Union[SymbolMixin, None]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def update_symbol_selected(symbol_name: str, selected: bool) -> Union[SymbolMixin, None]:
        raise NotImplementedError


class SymbolService:
    @classmethod
    def get_service_by(cls, data_source: str) -> type(SymbolServiceInterface):
        data_source = data_source.lower()
        if data_source != "binance":
            return cls.YFinance

        return cls.Binance

    class Binance(SymbolServiceInterface):
        @staticmethod
        def fetch_symbols() -> list[BinanceSymbol]:
            """Fetch symbols from Binance"""
            data = binance_client.exchange_info()["data"]

            # retrieve past symbols
            symbols = SymbolService.Binance.get_all_symbols()

            for s in data["symbols"]:
                s_name = s["symbol"]

                if any(sx.name == s_name for sx in symbols):
                    continue

                symbol = BinanceSymbol(s_name)
                symbols.append(symbol)
                binance_db.session.add(symbol)
            binance_db.session.commit()

            return symbols

        @staticmethod
        def get_all_symbols() -> list[BinanceSymbol]:
            """Return symbols from db"""
            return BinanceSymbol.query.order_by(BinanceSymbol.name).all()

        @staticmethod
        def get_symbol_by_name(symbol_name: str) -> Union[SymbolMixin, None]:
            """Return symbol by name from db"""
            symbol_name = symbol_name.upper()
            return BinanceSymbol.query.filter_by(name=symbol_name).first()

        @staticmethod
        def update_symbol_selected(symbol_name: str, selected: bool) -> Union[BinanceSymbol, None]:
            symbol: BinanceSymbol = BinanceSymbol.query.filter_by(name=symbol_name).first()

            if not symbol:
                return None

            symbol.selected = selected
            binance_db.session.commit()

            return symbol

    class YFinance(SymbolServiceInterface):
        @staticmethod
        def fetch_symbols() -> list[YFinanceSymbol]:
            """Fetch symbols from Binance and convert them for use in YahooFinance!"""
            data = binance_client.exchange_info()["data"]

            # retrieve past symbols
            symbols = SymbolService.YFinance.get_all_symbols()

            for s in data["symbols"]:
                s_name = s["baseAsset"] + "-USD"

                if any(sx.name == s_name for sx in symbols):
                    continue

                symbol = YFinanceSymbol(s_name)
                symbols.append(symbol)
                yfinance_db.session.add(symbol)
            yfinance_db.session.commit()

            return symbols

        @staticmethod
        def get_all_symbols() -> list[YFinanceSymbol]:
            """Return symbols from db"""
            return YFinanceSymbol.query.order_by(YFinanceSymbol.name).all()

        @staticmethod
        def get_symbol_by_name(symbol_name: str) -> Union[YFinanceSymbol, None]:
            symbol_name = symbol_name.upper()
            return YFinanceSymbol.query.filter_by(name=symbol_name).first()

        @staticmethod
        def update_symbol_selected(symbol_name: str, selected: bool) -> Union[YFinanceSymbol, None]:
            symbol: YFinanceSymbol = YFinanceSymbol.query.filter_by(name=symbol_name).first()

            if not symbol:
                return None

            symbol.selected = selected
            yfinance_db.session.commit()

            return symbol
