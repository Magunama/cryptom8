import datetime
import os
import shutil
from collections import deque
from functools import wraps
from typing import Union

import numpy as np
from keras import Sequential, backend, activations, initializers
from keras.callbacks import EarlyStopping
from keras.layers import LSTM, Dropout, BatchNormalization, Dense, AbstractRNNCell, RNN
from keras.metrics import SparseCategoricalAccuracy
from keras.models import load_model
from keras.optimizers import Adam
from keras.utils import CustomObjectScope
from numpy import ndarray
from numpy.random import shuffle
from pandas import DataFrame
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import TypeDecorator, Integer
from talib import abstract
from werkzeug.exceptions import abort


def validate_data_source(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data_source = kwargs["data_source"].lower()

        # todo: add error msg?
        # raise bad request
        if data_source not in ["binance", "yfinance"]:
            abort(400)

        return f(*args, **kwargs)

    return decorated_function


def is_fetch_requested(args) -> bool:
    return args.get("fetch", "false").lower() == "true"


class CustomIntEnum(TypeDecorator):
    """Allows having int in db for enums instead of strings"""
    impl = Integer

    def __init__(self, enum_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enum_type = enum_type

    def process_bind_param(self, value, dialect):
        if isinstance(value, int):
            return value

        return value.value

    def process_result_value(self, value, dialect):
        return self._enum_type(value)


def date_to_timestamp(d: datetime.date) -> int:
    """Converts datetime date to timestamp in seconds"""
    return int(datetime.datetime.combine(d, datetime.datetime.min.time()).timestamp())


def string_to_date(date_str: Union[str, None], fmt="%Y-%m-%dT%H:%M:%S.%fZ") -> Union[datetime.date, None]:
    """Converts date str to date object"""
    if date_str is None:
        return None
    return datetime.datetime.strptime(date_str, fmt).date()


class NNModelUtils:
    """NNModel utils namespace"""

    class JordanRNN(RNN):
        pass

    class MinimalJordanCell(AbstractRNNCell):

        def __init__(self, units, activation='tanh', kernel_initializer='uniform', recurrent_initializer='orthogonal',
                     bias_initializer='zeros', **kwargs):
            super().__init__(**kwargs)
            self.units = units
            self.activation = activations.get(activation)
            # self.kernel_initializer = initializers.get("glorot_uniform")
            self.kernel_initializer = initializers.get(kernel_initializer)
            self.recurrent_initializer = initializers.get(recurrent_initializer)
            self.bias_initializer = initializers.get(bias_initializer)

        @property
        def state_size(self):
            return self.units

        def build(self, input_shape):
            # default_caching_device = _caching_device(self)

            self.kernel = self.add_weight(
                shape=(input_shape[-1], self.units),
                initializer=self.kernel_initializer,
                name='kernel'
            )
            self.recurrent_kernel = self.add_weight(
                shape=(self.units, self.units),
                initializer=self.recurrent_initializer,
                name='recurrent_kernel')
            self.bias = self.add_weight(
                shape=(self.units,),
                initializer=self.bias_initializer,
                name='bias'
            )

        def call(self, inputs, states):
            prev_output = states[0]
            h = backend.dot(inputs, self.kernel)

            # bias step
            h = backend.bias_add(h, self.bias)

            output = h + backend.dot(prev_output, self.recurrent_kernel)

            # activation step
            act = activations.get(self.activation)
            output = act(output)

            return output, output

        def get_config(self):
            config = {
                'units':
                    self.units,
                'activation':
                    activations.serialize(self.activation),
                'kernel_initializer':
                    initializers.serialize(self.kernel_initializer),
                'recurrent_initializer':
                    initializers.serialize(self.recurrent_initializer),
                'bias_initializer':
                    initializers.serialize(self.bias_initializer)
            }

            base_config = super().get_config()
            return dict(list(base_config.items()) + list(config.items()))

        @classmethod
        def from_config(cls, config):
            return cls(**config)

    @staticmethod
    def build_Jordan_model(input_shape=(60, 12)):
        model = Sequential()

        model.add(
            NNModelUtils.JordanRNN(NNModelUtils.MinimalJordanCell(128), input_shape=input_shape, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(BatchNormalization())  # normalizes activation outputs

        model.add(NNModelUtils.JordanRNN(NNModelUtils.MinimalJordanCell(128), return_sequences=True))
        model.add(Dropout(0.1))
        model.add(BatchNormalization())

        model.add(NNModelUtils.JordanRNN(NNModelUtils.MinimalJordanCell(128)))
        model.add(Dropout(0.2))
        model.add(BatchNormalization())

        model.add(Dense(32, activation='relu'))
        model.add(Dropout(0.2))

        model.add(Dense(5, activation='softmax'))

        return model

    @staticmethod
    def build_LSTM_model(input_shape=(60, 12)):
        model = Sequential()

        model.add(LSTM(128, input_shape=input_shape, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(BatchNormalization())  # normalizes activation outputs

        model.add(LSTM(128, return_sequences=True))
        model.add(Dropout(0.1))
        model.add(BatchNormalization())

        model.add(LSTM(128))
        model.add(Dropout(0.2))
        model.add(BatchNormalization())

        model.add(Dense(32, activation='relu'))
        model.add(Dropout(0.2))

        model.add(Dense(5, activation='softmax'))

        return model

    @staticmethod
    def build_model(algorithm):
        from app.models.nn_model import NNAlgorithm
        if algorithm == NNAlgorithm.LSTM.name:
            return NNModelUtils.build_LSTM_model((12, 1))
        elif algorithm == NNAlgorithm.LSTM_SEQ.name:
            return NNModelUtils.build_LSTM_model()
        elif algorithm == NNAlgorithm.JORDAN.name:
            return NNModelUtils.build_Jordan_model((12, 1))
        else:
            return NNModelUtils.build_Jordan_model()

    @staticmethod
    def save_model(data_source: str, algorithm, symbol_name: str, model_id: int):
        from app.models.nn_model import NNAlgorithm
        if isinstance(algorithm, NNAlgorithm):
            algorithm = algorithm.name

        path = f"tmp/{data_source}/{algorithm}/{symbol_name}/{model_id}"
        os.makedirs(path, exist_ok=True)

        model = NNModelUtils.build_model(algorithm)
        opt = Adam(learning_rate=0.003, decay=1e-6)
        model.compile(
            loss='sparse_categorical_crossentropy',
            optimizer=opt,
            metrics=['accuracy', SparseCategoricalAccuracy()]
        )

        model.save(path)

    @staticmethod
    def load_model(data_source: str, algorithm, symbol_name: str, model_id: int):
        from app.models.nn_model import NNAlgorithm
        if isinstance(algorithm, NNAlgorithm):
            algorithm = algorithm.name

        path = f"tmp/{data_source}/{algorithm}/{symbol_name}/{model_id}"
        # todo: check if path exists
        with CustomObjectScope(
                {"MinimalJordanCell": NNModelUtils.MinimalJordanCell, "JordanRNN": NNModelUtils.JordanRNN}):
            return load_model(path)

    @staticmethod
    def remove_model(data_source: str, algorithm, symbol_name: str, model_id: int):
        from app.models.nn_model import NNAlgorithm
        if isinstance(algorithm, NNAlgorithm):
            algorithm = algorithm.name

        path = f"tmp/{data_source}/{algorithm}/{symbol_name}/{model_id}"
        shutil.rmtree(path)

    @staticmethod
    def _normalize(col):
        """Normalize column"""
        scaler = MinMaxScaler()

        if len(col.shape) == 2:
            return scaler.fit_transform(col)

        return np.array([scaler.fit_transform(ck) for ck in col])

    @staticmethod
    def _classify(col):
        """Classify target column"""
        ss = -0.05
        s = -0.01
        b = -s
        sb = -ss

        def _classify_cell(cell):
            # price was higher n days ago so STRONG SELL
            if cell < ss:
                return 4
            # SELL
            elif ss <= cell < s:
                return 3
            # HODL
            elif s <= cell < b:
                return 2
            # BUY
            elif b <= cell < sb:
                return 1
            # STRONG BUY
            else:
                return 0

        return np.array([[_classify_cell(cell)] for cell in col])

    @staticmethod
    def _apply_indicators(prediction_window_size: int, df: DataFrame) -> DataFrame:
        """Apply indicators and append resulted columns to df"""
        inputs = {
            'open': df.open,
            'high': df.high,
            'low': df.low,
            'close': df.close,
            'volume': df.volume
        }

        df["upper"], df["middle"], df["lower"] = abstract.BBANDS(inputs)

        df["willr"] = abstract.WILLR(inputs)

        df["rsi"] = abstract.RSI(inputs)

        df["adx"] = abstract.ADX(inputs)

        df["macd"], df["macdsignal"], df["macdhist"] = abstract.MACD(inputs)

        df["rocp"] = abstract.ROCP(inputs)

        df["rocn"] = abstract.ROCP(inputs, timeperiod=prediction_window_size)

        return df.dropna()

    @staticmethod
    def _make_sequences(x: np.array, y: np.array, seq_len=60, lower_bound=True) -> (np.array, np.array):
        sequential_data = []  # sequence array
        prev_days = deque(maxlen=seq_len)

        for x_part, y_part in zip(x, y):
            prev_days.append(x_part)  # store all but the target
            if len(prev_days) == seq_len:
                sequential_data.append([np.array(prev_days), y_part[0]])

        if lower_bound:
            buys = []
            sells = []
            holds = []
            strong_buys = []
            strong_sells = []

            for seq, target in sequential_data:
                if target == 0:
                    strong_buys.append([seq, target])
                elif target == 1:
                    buys.append([seq, target])
                elif target == 2:
                    holds.append([seq, target])
                elif target == 3:
                    sells.append([seq, target])
                else:
                    strong_sells.append([seq, target])

            shuffle(buys)
            shuffle(sells)
            shuffle(holds)
            shuffle(strong_buys)
            shuffle(strong_sells)

            lower_bound = min(len(buys), len(sells), len(holds), len(strong_buys), len(strong_sells))

            # make sure all lists are only up to the shortest length
            buys = buys[:lower_bound]
            sells = sells[:lower_bound]
            holds = holds[:lower_bound]
            strong_sells = strong_sells[:lower_bound]
            strong_buys = strong_buys[:lower_bound]

            sequential_data = buys + sells + holds + strong_buys + strong_sells  # merge the lists

        # ensure the model doesn't get confused with only one class
        shuffle(sequential_data)

        x = []
        y = []
        for seq, target in sequential_data:
            x.append(seq)  # X represents sequences
            y.append(target)  # y is target(s)

        return np.array(x), np.array(y)

    @staticmethod
    def preprocess_data(algorithm, prediction_window_size: int, df: DataFrame):
        # todo: preprocess according to datasource?

        df = NNModelUtils._apply_indicators(prediction_window_size, df)
        df = df.drop(['day', 'open', 'high', 'low', 'volume'], axis=1)

        x = np.array(df)
        y = NNModelUtils._classify(df.rocn)

        # sequencing is requested
        from app.models.nn_model import NNAlgorithm
        if algorithm in (NNAlgorithm.LSTM_SEQ.name, NNAlgorithm.JORDAN_SEQ.name):
            # todo: maybe use prediction window size as sequence len
            x, y = NNModelUtils._make_sequences(x, y)

        x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.8, shuffle=False)

        # normalize dataset to fit in range [0, 1]
        x_train = NNModelUtils._normalize(x_train)
        x_test = NNModelUtils._normalize(x_test)

        return x_train, y_train, x_test, y_test

    @staticmethod
    def train_model(model, feature, label, x_test, y_test, patience: int):
        batch_size = 64
        epochs = 125

        import logging
        logger = logging.getLogger("training")
        fh = logging.FileHandler('training.log')
        logger.addHandler(fh)
        logger.debug(feature.shape)

        # early stopping
        es = EarlyStopping(monitor='val_accuracy', patience=patience)

        history = model.fit(
            feature, label,
            batch_size=batch_size,
            epochs=epochs,
            validation_data=(x_test, y_test),
            callbacks=[es],
        )

        # Score model
        # todo: maybe remove?
        score = model.evaluate(x_test, y_test, verbose=0)

        print('Test loss:', score[0])
        print('Test accuracy:', score[1])

    @staticmethod
    def make_prediction(data_source: str, algorithm, symbol_name: str, model_id: int, pred_input: ndarray,
                        pred_window) -> tuple:
        """Perform model prediction and sum up results"""
        # todo: move this next line to prediction service?
        model = NNModelUtils.load_model(data_source, algorithm, symbol_name, model_id)
        output = model.predict(pred_input)
        output = output[-pred_window:]

        # todo: maybe rethink using np.argmax(output, 1)
        # compute average confidence for each label
        output_avg = np.average(output, 0)
        # select best label
        result = np.argmax(output, 1)

        unique, counts = np.unique(result, return_counts=True)
        result_dict = dict(zip(unique, counts))
        most_likely_result = max(result_dict, key=result_dict.get)

        return most_likely_result, (
                output_avg[most_likely_result] + (result_dict[most_likely_result] / pred_window)) / 2
