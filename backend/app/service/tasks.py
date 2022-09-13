import logging
from time import perf_counter

import pandas as pd
from celery import Celery

from app import BaseConfig
from app.models.nn_model import NNModelStatus
from app.service.utils import NNModelUtils

celery = Celery(__name__, broker=BaseConfig.CELERY_BROKER_URL, result_backend=BaseConfig.CELERY_RESULT_BACKEND)


# logger = get_task_logger(__name__)


# @celery.task()
def save_model_task(payload: dict):
    NNModelUtils.save_model(payload["data_source"], payload["algorithm"], payload["symbol_name"], payload["model_id"])


# @celery.task()
def train_model_task(payload: dict):
    model = NNModelUtils.load_model(payload["data_source"], payload["algorithm"], payload["symbol_name"],
                                    payload["model_id"])

    # todo: maybe find a workaround for passing df to task. this might be slow
    data = pd.DataFrame.from_dict(payload["data"])

    # preprocess step
    x_train, y_train, x_test, y_test = NNModelUtils.preprocess_data(payload["algorithm"],
                                                                    payload["prediction_window_size"], data)

    logger = logging.getLogger('training')
    fh = logging.FileHandler('training.log')
    logger.addHandler(fh)
    t1_start = perf_counter()

    # training step
    NNModelUtils.train_model(model, x_train, y_train, x_test, y_test, payload["patience"])

    t1_stop = perf_counter()
    logger.debug(
        f"Done! {t1_stop - t1_start} [{payload['data_source']}][{payload['algorithm']}][{payload['symbol_name']}]"
    )

    path = f'tmp/{payload["data_source"]}/{payload["algorithm"]}/{payload["symbol_name"]}/{payload["model_id"]}'
    model.save(path)

    # todo: add try except clause for errored status
    from app.service.nn_model_service import NNModelService
    model_service = NNModelService.get_service_by(payload["data_source"])

    # celery needs app context as it runs separately
    from app import create_app
    with create_app().app_context():
        model_service.update_model_status(payload["model_id"], NNModelStatus.TRAINED)
