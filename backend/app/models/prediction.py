import enum
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import declared_attr, declarative_mixin, relationship

from app import binance_db, yfinance_db
from app.service.utils import CustomIntEnum


class PredictionResult(enum.IntEnum):
    STRONG_BUY = 0
    BUY = 1
    HOLD = 2
    SELL = 3
    STRONG_SELL = 4


@declarative_mixin
@dataclass
class PredictionMixin(object):
    model_id: int
    symbol_name: str
    algorithm: int

    @declared_attr
    def model_id(self):
        return Column(Integer, ForeignKey("model.id"))

    @declared_attr
    def model(self):
        return relationship("NNModelMixin", back_populates="predictions")

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    result: type(PredictionResult) = Column(CustomIntEnum(PredictionResult), nullable=False)
    confidence: float = Column(Float, nullable=False)

    created: datetime.date = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated: datetime.date = Column(DateTime, onupdate=datetime.utcnow)

    @property
    def symbol_name(self):
        return self.model.symbol_name

    @property
    def algorithm(self):
        return self.model.algorithm

    def __init__(self, model_id: int, result: PredictionResult, confidence: float):
        self.model_id = model_id
        self.result = result
        self.confidence = confidence


class BinancePrediction(PredictionMixin, binance_db.Model):
    __tablename__ = "prediction"
    __bind_key__ = None  # default bind

    @declared_attr
    def model(self):
        return relationship("BinanceNNModel", back_populates="predictions", lazy=True)


class YFinancePrediction(PredictionMixin, yfinance_db.Model):
    __tablename__ = "prediction"
    __bind_key__ = "yfinance"

    @declared_attr
    def model(self):
        return relationship("YFinanceNNModel", back_populates="predictions", lazy=True)
