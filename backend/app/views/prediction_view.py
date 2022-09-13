from flask import Blueprint, request, abort, jsonify
from pandas import DataFrame

from app.models.prediction import PredictionMixin
from app.service.bar_service import BarServiceInterface, BarService
from app.service.nn_model_service import NNModelServiceInterface, NNModelService
from app.service.prediction_service import PredictionServiceInterface, PredictionService
from app.service.utils import validate_data_source

prediction_blueprint = Blueprint('prediction', __name__)


@prediction_blueprint.get("/<string:data_source>/predictions")
@validate_data_source
def get_all_predictions(data_source: str):
    """Returns a list of all predictions in the database."""
    service = PredictionService.get_service_by(data_source)
    return jsonify(service.get_all_predictions())


@prediction_blueprint.post("/<string:data_source>/predictions")
@validate_data_source
def add_prediction(data_source: str):
    """Creates a prediction. Requires model Id in the request body, otherwise will throw BadRequest. Will throw
    NotFound if model is not found for Id. Returns prediction result."""
    model_service: NNModelServiceInterface = NNModelService.get_service_by(data_source)
    prediction_service: PredictionServiceInterface = PredictionService.get_service_by(data_source)
    bar_service: BarServiceInterface = BarService.get_service_by(data_source)

    data = request.get_json()
    if "model_id" not in data:
        abort(400)

    model = model_service.get_model_by_id(data["model_id"])
    if not model:
        abort(404)

    bars = bar_service.get_bars_by_symbol(model.symbol)
    if not bars:
        abort(404)

    prediction: PredictionMixin = prediction_service.create_prediction(model, DataFrame(bars))
    return jsonify(prediction), 201
