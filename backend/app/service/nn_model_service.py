import datetime
from abc import ABC, abstractmethod
from typing import Union

from pandas import DataFrame

from app import binance_db, yfinance_db
from app.models.nn_model import NNModelMixin, BinanceNNModel, YFinanceNNModel, NNModelStatus, NNAlgorithm, \
    PredictionWindow
from app.models.symbol import SymbolMixin, BinanceSymbol, YFinanceSymbol
from app.service.tasks import save_model_task, train_model_task
from app.service.utils import NNModelUtils


class NNModelServiceInterface(ABC):
    @staticmethod
    @abstractmethod
    def get_all_models() -> list[NNModelMixin]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_model_by_id(model_id: int) -> Union[NNModelMixin, None]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def create_model(symbol: SymbolMixin, algorithm: Union[NNAlgorithm, str],
                     prediction_window: Union[PredictionWindow, str]) -> NNModelMixin:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def delete_model(model_id: int) -> Union[NNModelMixin, None]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def update_model_status(model_id: int, status: NNModelStatus) -> Union[NNModelMixin, None]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def train_model(model: NNModelMixin, data: DataFrame, patience: int):
        raise NotImplementedError


class NNModelService:
    @classmethod
    def get_service_by(cls, data_source: str) -> type(NNModelServiceInterface):
        data_source = data_source.lower()
        if data_source != "binance":
            return cls.YFinance

        return cls.Binance

    class Binance(NNModelServiceInterface):
        @staticmethod
        def get_all_models() -> list[BinanceNNModel]:
            """Return nn models from db"""
            return BinanceNNModel.query.all()

        @staticmethod
        def get_model_by_id(model_id: int) -> Union[BinanceNNModel, None]:
            return BinanceNNModel.query.get(model_id)

        @staticmethod
        def create_model(symbol: BinanceSymbol, algorithm: Union[NNAlgorithm, str],
                         prediction_window: Union[PredictionWindow, str]) -> BinanceNNModel:
            """Create nn model & metadata"""
            m = BinanceNNModel(symbol_id=symbol.id, algorithm=algorithm, prediction_window=prediction_window)
            binance_db.session.add(m)
            binance_db.session.commit()

            # create & save actual model file(s) (using a worker thread)
            task_payload: dict = {
                "data_source": "binance",
                "model_id": m.id,
                "algorithm": m.algorithm.name,
                "symbol_name": m.symbol_name
            }
            # save_model_task.delay(payload=task_payload)
            save_model_task(payload=task_payload)

            return m

        @staticmethod
        def delete_model(model_id: int) -> Union[BinanceNNModel, None]:
            """Delete nn model & metadata"""
            model = BinanceNNModel.query.get(model_id)
            if not model:
                return None
            symbol_name = model.symbol.name

            binance_db.session.delete(model)
            binance_db.session.commit()

            # delete actual model file(s)
            NNModelUtils.remove_model(data_source="binance", algorithm=model.algorithm, symbol_name=symbol_name,
                                      model_id=model_id)

            return model

        @staticmethod
        def update_model_status(model_id: int, status: NNModelStatus) -> Union[BinanceNNModel, None]:
            model: BinanceNNModel = NNModelService.Binance.get_model_by_id(model_id)
            if not model:
                return None

            model.status = status
            model.updated = datetime.datetime.utcnow()
            binance_db.session.commit()

            return model

        @staticmethod
        def train_model(model: BinanceNNModel, data: DataFrame, patience: int):
            # train actual model (using a worker thread as this takes a lot of time to run)
            task_payload: dict = {
                "data_source": "binance",
                "model_id": model.id,
                "algorithm": model.algorithm.name,
                "symbol_name": model.symbol_name,
                "data": data.to_dict(),
                "patience": patience,
                "prediction_window_size": model.prediction_window.get_time_period()
            }
            # train_model_task.delay(payload=task_payload)
            train_model_task(payload=task_payload)

    class YFinance(NNModelServiceInterface):
        @staticmethod
        def get_model_by_id(model_id: int) -> Union[YFinanceNNModel, None]:
            return YFinanceNNModel.query.get(model_id)

        @staticmethod
        def get_all_models() -> list[YFinanceNNModel]:
            """Return nn models from db"""
            return YFinanceNNModel.query.all()

        @staticmethod
        def create_model(symbol: YFinanceSymbol, algorithm: Union[NNAlgorithm, str],
                         prediction_window: Union[PredictionWindow, str]) -> YFinanceNNModel:
            """Create nn model & metadata"""
            m = YFinanceNNModel(symbol_id=symbol.id, algorithm=algorithm, prediction_window=prediction_window)
            yfinance_db.session.add(m)
            yfinance_db.session.commit()

            # create & save actual model file(s) (using a worker thread)
            task_payload: dict = {
                "data_source": "binance",
                "model_id": m.id,
                "algorithm": m.algorithm.name,
                "symbol_name": m.symbol_name
            }
            save_model_task.delay(payload=task_payload)

            return m

        @staticmethod
        def delete_model(model_id: int) -> Union[YFinanceNNModel, None]:
            """Delete nn model & metadata"""
            model = YFinanceNNModel.query.get(model_id)
            if not model:
                return None
            symbol_name = model.symbol.name

            yfinance_db.session.delete(model)
            yfinance_db.session.commit()

            # delete actual model file(s)
            NNModelUtils.remove_model(data_source="yfinance", algorithm=model.algorithm, symbol_name=symbol_name,
                                      model_id=model_id)

            return model

        @staticmethod
        def update_model_status(model_id: int, status: NNModelStatus) -> Union[YFinanceNNModel, None]:
            model: YFinanceNNModel = NNModelService.YFinance.get_model_by_id(model_id)
            if not model:
                return None

            model.status = status
            model.updated = datetime.datetime.utcnow()
            yfinance_db.session.commit()

            return model

        @staticmethod
        def train_model(model: YFinanceNNModel, data: DataFrame, patience: int):
            # train actual model (using a worker thread as this takes a lot of time to run)
            task_payload: dict = {
                "data_source": "yfinance",
                "model_id": model.id,
                "algorithm": model.algorithm.name,
                "symbol_name": model.symbol_name,
                "data": data.to_dict(),
                "patience": patience,
                "prediction_window_size": model.prediction_window.get_time_period()
            }
            train_model_task.delay(payload=task_payload)
