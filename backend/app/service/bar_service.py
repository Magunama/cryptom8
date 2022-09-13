import datetime
from abc import ABC, abstractmethod

import yfinance

from app.ext import binance_db, binance_client, yfinance_db
from app.models.bar import BarMixin, BinanceBar, YFinanceBar
from app.models.symbol import SymbolMixin, BinanceSymbol, YFinanceSymbol
from app.service.utils import date_to_timestamp


class BarServiceInterface(ABC):
    @staticmethod
    @abstractmethod
    def fetch_bars_by_symbol(symbol: SymbolMixin) -> list[BarMixin]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_bars_by_symbol(symbol: SymbolMixin) -> list[BarMixin]:
        raise NotImplementedError


class BarService:

    @classmethod
    def get_service_by(cls, data_source: str) -> type(BarServiceInterface):
        data_source = data_source.lower()
        if data_source != "binance":
            return cls.YFinance

        return cls.Binance

    class Binance(BarServiceInterface):
        @staticmethod
        def fetch_bars_by_symbol(symbol: BinanceSymbol) -> list[BinanceBar]:
            # retrieve past bars
            bars: list[BinanceBar] = BarService.Binance.get_bars_by_symbol(symbol)

            # todo: take startTime from config
            start_time = date_to_timestamp(bars[-1].day) * 1000 if bars else 1269284187000
            present_time = date_to_timestamp(datetime.date.today()) * 1000

            # todo: maybe throw?
            # data is up to date, avoid external API call
            if start_time >= present_time:
                return bars

            # retrieve new data between start time and present time
            while start_time < present_time:
                data = binance_client.klines(
                    symbol=symbol.name, interval="1d", limit=1000, startTime=start_time
                )["data"]

                # no more new data
                if not data:
                    break

                for b in data:
                    b_timestamp = b[0] / 1000
                    b_date = datetime.date.fromtimestamp(b_timestamp)

                    if any(bx.day == b_date for bx in bars):
                        continue

                    bar = BinanceBar(symbol.id, b_date, *b[1:6])
                    bars.append(bar)
                    binance_db.session.add(bar)

                start_time = data[-1][0]

            # update bar status for symbol
            symbol.bars_first_day = bars[0].day
            symbol.bars_last_day = bars[-1].day

            binance_db.session.commit()
            return bars

        @staticmethod
        def get_bars_by_symbol(symbol: BinanceSymbol) -> list[BinanceBar]:
            return BinanceBar.query.with_parent(symbol).all()

    class YFinance(BarServiceInterface):
        @staticmethod
        def fetch_bars_by_symbol(symbol: YFinanceSymbol) -> list[YFinanceBar]:
            # retrieve past bars
            bars: list[YFinanceBar] = BarService.YFinance.get_bars_by_symbol(symbol)

            # todo: take startTime from config
            start_time = bars[-1].day if bars else datetime.date(2014, 7, 1)

            ticker = yfinance.Ticker(symbol.name)
            data = ticker.history(period="max", start=start_time)

            for i in range(0, data.shape[0]):
                b_timestamp = data.index[i]
                b_date = datetime.date(b_timestamp.year, b_timestamp.month, b_timestamp.day)

                if any(bx.day == b_date for bx in bars):
                    continue

                b_open = data["Open"][i]
                b_high = data["High"][i]
                b_low = data["Low"][i]
                b_close = data["Close"][i]
                b_volume = data["Volume"][i]

                bar = YFinanceBar(symbol.id, b_date, b_open, b_high, b_low, b_close, b_volume)
                bars.append(bar)
                yfinance_db.session.add(bar)

            # update bar status for symbol
            symbol.bars_first_day = bars[0].day
            symbol.bars_last_day = bars[-1].day

            yfinance_db.session.commit()

            return bars

        @staticmethod
        def get_bars_by_symbol(symbol: YFinanceSymbol) -> list[YFinanceBar]:
            return YFinanceBar.query.with_parent(symbol).all()
