from abc import ABC, abstractmethod

import numpy as np
from pandas import DataFrame

from app import binance_db, yfinance_db
from app.models.nn_model import NNModelMixin, NNAlgorithm
from app.models.prediction import PredictionMixin, BinancePrediction, PredictionResult, YFinancePrediction
from app.service.utils import NNModelUtils


class PredictionServiceInterface(ABC):

    @staticmethod
    @abstractmethod
    def create_prediction(model: NNModelMixin, latest_bars: DataFrame) -> PredictionMixin:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_all_predictions() -> list[PredictionMixin]:
        raise NotImplementedError


class PredictionService:
    @classmethod
    def get_service_by(cls, data_source: str) -> type(PredictionServiceInterface):
        data_source = data_source.lower()
        if data_source != "binance":
            return cls.YFinance

        return cls.Binance

    class Binance(PredictionServiceInterface):
        @staticmethod
        def create_prediction(model: NNModelMixin, df: DataFrame) -> BinancePrediction:
            """Make prediction"""

            df = NNModelUtils._apply_indicators(model.prediction_window.get_time_period(), df)
            df = df.drop(['day', 'open', 'high', 'low', 'volume'], axis=1)

            x = np.array(df)
            y = NNModelUtils._classify(df.rocn)

            # sequencing is requested
            if model.algorithm in (NNAlgorithm.LSTM_SEQ, NNAlgorithm.JORDAN_SEQ):
                x, y = NNModelUtils._make_sequences(x, y)

            # normalize dataset to fit in range [0, 1]
            pred_input = NNModelUtils._normalize(x)

            result, confidence = NNModelUtils.make_prediction(
                "binance", model.algorithm, model.symbol_name, model.id, pred_input[-60:],
                model.prediction_window.get_time_period()
            )
            result = PredictionResult(result)

            p = BinancePrediction(model_id=model.id, result=result, confidence=confidence)
            binance_db.session.add(p)
            binance_db.session.commit()
            return p

        @staticmethod
        def get_all_predictions() -> list[BinancePrediction]:
            """Return all predictions from db"""
            return BinancePrediction.query.all()

    class YFinance(PredictionServiceInterface):
        @staticmethod
        def create_prediction(model: NNModelMixin, df: DataFrame) -> YFinancePrediction:
            """Make prediction"""

            df = NNModelUtils._apply_indicators(model.prediction_window.get_time_period(), df)
            df = df.drop(['day', 'open', 'high', 'low', 'volume'], axis=1)

            x = np.array(df)
            y = NNModelUtils._classify(df.rocn)

            # sequencing is requested
            if model.algorithm in (NNAlgorithm.LSTM_SEQ, NNAlgorithm.JORDAN_SEQ):
                x, y = NNModelUtils._make_sequences(x, y)

            # normalize dataset to fit in range [0, 1]
            pred_input = NNModelUtils._normalize(x)

            result, confidence = NNModelUtils.make_prediction(
                "yfinance", model.algorithm, model.symbol_name, model.id, pred_input[-60:],
                model.prediction_window.get_time_period()
            )
            result = PredictionResult(result)

            p = YFinancePrediction(model_id=model.id, result=result, confidence=confidence)
            yfinance_db.session.add(p)
            yfinance_db.session.commit()
            return p

        @staticmethod
        def get_all_predictions() -> list[YFinancePrediction]:
            """Return all predictions from db"""
            return YFinancePrediction.query.all()
