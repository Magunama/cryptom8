from flask import Blueprint, jsonify, abort, request
from pandas import DataFrame

from app.models.nn_model import NNModelStatus, NNAlgorithm, NNModelMixin, PredictionWindow
from app.service.bar_service import BarServiceInterface, BarService
from app.service.nn_model_service import NNModelService, NNModelServiceInterface
from app.service.symbol_service import SymbolServiceInterface, SymbolService
from app.service.utils import validate_data_source, string_to_date

nn_model_blueprint = Blueprint('nn_model', __name__)


@nn_model_blueprint.post("/<string:data_source>/models")
@validate_data_source
def add_model(data_source: str):
    """Creates a new neural network model (metadata + object). Requires symbol name and algorithm in the request body,
    otherwise will throw BadRequest. Will throw NotFound if symbol is not found. Returns model metadata and object
    creation is executed in a separate thread."""
    symbol_service: SymbolServiceInterface = SymbolService.get_service_by(data_source)
    model_service: NNModelServiceInterface = NNModelService.get_service_by(data_source)

    data = request.get_json()
    if "symbol_name" not in data:
        abort(400)

    symbol_name = data["symbol_name"]
    symbol = symbol_service.get_symbol_by_name(symbol_name)
    if not symbol:
        abort(404)

    algorithm = data.get("algorithm", NNAlgorithm.LSTM.value)
    if not isinstance(algorithm, int):
        abort(400)

    prediction_window = data.get("prediction_window", PredictionWindow.TINY.value)
    if not isinstance(prediction_window, int):
        abort(400)

    algorithm = NNAlgorithm(algorithm)
    prediction_window = PredictionWindow(prediction_window)

    model = model_service.create_model(symbol, algorithm, prediction_window)
    return jsonify(model), 201


@nn_model_blueprint.get("/<string:data_source>/models")
@validate_data_source
def get_all_models(data_source: str):
    """Returns a list of all neural network models (metadata) in the database. Each model also contains a list of
    predictions."""
    service: NNModelServiceInterface = NNModelService.get_service_by(data_source)

    models = service.get_all_models()
    return jsonify(models)


@nn_model_blueprint.delete("/<string:data_source>/models/<int:model_id>")
@validate_data_source
def remove_model(data_source: str, model_id: int):
    service: NNModelServiceInterface = NNModelService.get_service_by(data_source)

    model = service.delete_model(model_id)
    if not model:
        abort(404)
    return {}, 204


@nn_model_blueprint.patch("/<string:data_source>/models/<int:model_id>")
@validate_data_source
def update_model(data_source: str, model_id: int):
    """Changes neural network model (metadata) state according to the request body. Used for persisting a change in the
    model's status. Will throw NotFound if symbol is not found. Will throw \textit{BadRequest} if the request does not
    contain a field to be updated. Will throw Conflict if the model's status is \verb|IN_TRAINING| and there is a
    request to change it to the same status. If the requested status is \verb|IN_TRAINING| also trains the model object
    in a separate thread."""
    model_service: NNModelServiceInterface = NNModelService.get_service_by(data_source)

    data = request.json
    if "status" not in data:
        abort(400)

    status = data["status"]
    if isinstance(status, str):
        status = NNModelStatus[status]

    # training requested
    if status == NNModelStatus.IN_TRAINING:
        model: NNModelMixin = model_service.get_model_by_id(model_id)
        if not model:
            abort(404)

        # training has already started (conflict)
        if model.status == NNModelStatus.IN_TRAINING:
            abort(409)

        bar_service: BarServiceInterface = BarService.get_service_by(data_source)
        bars = bar_service.get_bars_by_symbol(model.symbol)

        # returns fallback value or index of x in bars
        index_finder = lambda x, fallback: fallback if x is None else next(
            (i for (i, b) in enumerate(bars) if b.day == x), fallback)

        # slice data if needed
        data_start = string_to_date(data.get("data_start", None))
        start_index = index_finder(data_start, 0)
        data_end = string_to_date(data.get("data_end", None))
        end_index = index_finder(data_end, len(bars))
        # too little data
        if end_index - start_index - 1 < 30:
            abort(400)
        # don't make a copy (slice) if not needed
        if start_index != 0 and end_index != len(bars):
            bars = bars[start_index: end_index]

        # default patience level (in epochs)
        patience = data.get("patience", 60)

        # train actual model
        bars = DataFrame(bars)
        model_service.train_model(model, bars, patience)

    model: NNModelMixin = model_service.update_model_status(model_id, status)
    if not model:
        abort(404)

    return {}, 204
