import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Union

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import declared_attr, relationship

from app.ext import binance_db, yfinance_db
from app.models.prediction import PredictionMixin
from app.service.utils import CustomIntEnum


class PredictionWindow(enum.IntEnum):
    TINY = 0
    SMALL = 1
    MEDIUM = 2

    def get_time_period(self):
        if self == self.TINY:
            return 1
        elif self == self.SMALL:
            return 7
        else:
            return 15


class NNAlgorithm(enum.IntEnum):
    LSTM = 0
    JORDAN = 1
    LSTM_SEQ = 2
    JORDAN_SEQ = 3


class NNModelStatus(enum.IntEnum):
    CREATED = 0
    IN_TRAINING = 1
    TRAINED = 2
    ERRORED = 3


@dataclass
class NNModelMixin(object):
    predictions: list[PredictionMixin]
    symbol_name: str

    @property
    def symbol_name(self) -> str:
        return self.symbol.name

    @declared_attr
    def symbol_id(self):
        return Column(Integer, ForeignKey("symbol.id"))

    @declared_attr
    def symbol(self):
        return relationship("SymbolMixin", back_populates="models")

    @declared_attr
    def predictions(self):
        return relationship("PredictionMixin", cascade="all,delete", back_populates="model")

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    algorithm: type(NNAlgorithm) = Column(CustomIntEnum(NNAlgorithm), nullable=False)
    status: type(NNModelStatus) = Column(CustomIntEnum(NNModelStatus), nullable=False)
    prediction_window: type(PredictionWindow) = Column(CustomIntEnum(PredictionWindow), nullable=False)

    # @declared_attr
    # def predictions(self):
    #     return relationship("PredictionMixin", backref="model", lazy=True)

    created: datetime.date = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated: datetime.date = Column(DateTime, onupdate=datetime.utcnow)

    def __init__(self, algorithm: Union[str, int], symbol_id: int, prediction_window: Union[str, int]):
        # todo: maybe move this in service
        self.algorithm = algorithm
        if isinstance(self.algorithm, str):
            self.algorithm = NNAlgorithm[algorithm]

        self.prediction_window = prediction_window
        if isinstance(self.prediction_window, str):
            self.prediction_window = PredictionWindow[prediction_window]

        self.symbol_id = symbol_id
        self.status = NNModelStatus.CREATED


class BinanceNNModel(NNModelMixin, binance_db.Model):
    __tablename__ = "model"
    __bind_key__ = None  # default bind

    @declared_attr
    def symbol(self):
        return relationship("BinanceSymbol", back_populates="models")

    @declared_attr
    def predictions(self):
        return relationship("BinancePrediction", cascade="all,delete", back_populates="model")


class YFinanceNNModel(NNModelMixin, yfinance_db.Model):
    __tablename__ = "model"
    __bind_key__ = "yfinance"

    @declared_attr
    def symbol(self):
        return relationship("YFinanceSymbol", back_populates="models")

    @declared_attr
    def predictions(self):
        return relationship("YFinancePrediction", cascade="all,delete", back_populates="model")
