from dataclasses import dataclass
from datetime import date

from sqlalchemy import Column, Date, Float, ForeignKey, Integer
from sqlalchemy.orm import declared_attr

from app import binance_db, yfinance_db


# todo: use or404 in query
@dataclass
class BarMixin(object):

    @declared_attr
    def symbol_id(self):
        return Column(Integer, ForeignKey("symbol.id"), primary_key=True)

    day: date = Column(Date, primary_key=True)
    open: float = Column(Float, nullable=False)
    high: float = Column(Float, nullable=False)
    low: float = Column(Float, nullable=False)
    close: float = Column(Float, nullable=False)
    volume: float = Column(Float, nullable=False)

    def __init__(self, symbol_id: int, day: date, open: float, high: float, low: float, close: float,
                 volume: float) -> None:
        self.symbol_id = symbol_id
        self.day = day
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume


class BinanceBar(BarMixin, binance_db.Model):
    __tablename__ = "bar"
    __bind_key__ = None  # default bind


class YFinanceBar(BarMixin, yfinance_db.Model):
    __tablename__ = "bar"
    __bind_key__ = "yfinance"
