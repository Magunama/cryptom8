from flask import Blueprint, jsonify, request

from app.service.bar_service import BarService
from app.service.symbol_service import SymbolService
from app.service.utils import validate_data_source, is_fetch_requested

bar_blueprint = Blueprint('bar', __name__)


# @bar_blueprint.route("/<string:data_source>/bars", methods=["GET"])
# @validate_data_source
# def get_all_bars(data_source: str):
#     service = BarService.get_service_by(data_source.lower())
#
#     fetch: bool = is_fetch_requested(request.args)
#
#     # get symbols from db or third party
#     if fetch:
#         bar_data = service.fetch_bars()
#     else:
#         bar_data = service.get_all_bars()
#
#     return jsonify(bar_data)


@bar_blueprint.get("/<string:data_source>/bars/<string:symbol_name>")
@validate_data_source
def get_bars_by_symbol(data_source: str, symbol_name: str):
    """Returns a list of all bars in database for a symbol. Accepts argument fetch, in which case it will fetch new
    bars from third-party services."""
    symbol_service = SymbolService.get_service_by(data_source)
    bar_service = BarService.get_service_by(data_source)

    fetch: bool = is_fetch_requested(request.args)

    symbol = symbol_service.get_symbol_by_name(symbol_name)
    # todo: maybe raise?
    if not symbol:
        return jsonify([])

    # get symbols from db or third party
    if fetch:
        bar_data = bar_service.fetch_bars_by_symbol(symbol)
    else:
        bar_data = bar_service.get_bars_by_symbol(symbol)

    return jsonify(bar_data)
