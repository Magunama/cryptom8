from dataclasses import dataclass
from datetime import date

from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy import Date
from sqlalchemy.orm import declared_attr, relationship

from app.ext import binance_db, yfinance_db


# todo: use or404 in query
@dataclass
class SymbolMixin(object):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String, nullable=False, unique=True)
    selected: bool = Column(Boolean, nullable=False, default=False)

    # todo: maybe replace with some method
    bars_first_day: date = Column(Date)
    bars_last_day: date = Column(Date)

    @declared_attr
    def models(self):
        return relationship("NNModelMixin", back_populates="symbol")

    def __init__(self, name):
        self.name = name


class BinanceSymbol(SymbolMixin, binance_db.Model):
    __tablename__ = "symbol"
    __bind_key__ = None  # default bind

    @declared_attr
    def bars(self):
        return relationship("BinanceBar", backref="symbol", lazy=True)

    @declared_attr
    def models(self):
        return relationship("BinanceNNModel", back_populates="symbol", lazy=True)


class YFinanceSymbol(SymbolMixin, yfinance_db.Model):
    __tablename__ = "symbol"
    __bind_key__ = "yfinance"

    @declared_attr
    def bars(self):
        return relationship("YFinanceBar", backref="symbol", lazy=True)

    @declared_attr
    def models(self):
        return relationship("YFinanceNNModel", back_populates="symbol", lazy=True)
