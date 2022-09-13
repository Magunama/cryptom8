from flask import Blueprint, jsonify, request, abort

from app.service.symbol_service import SymbolService
from app.service.utils import is_fetch_requested, validate_data_source

symbol_blueprint = Blueprint('symbol', __name__)


@symbol_blueprint.get("/<string:data_source>/symbols")
@validate_data_source
def get_all_symbols(data_source: str):
    """By default, returns a list of all symbols in the database. Accepts argument fetch, in which case it will fetch
    new symbols from third-party services."""
    service = SymbolService.get_service_by(data_source)

    fetch: bool = is_fetch_requested(request.args)

    # get symbols from db or third party
    if fetch:
        bar_data = service.fetch_symbols()
    else:
        bar_data = service.get_all_symbols()

    return jsonify(bar_data)


@symbol_blueprint.patch("/<string:data_source>/symbols/<string:symbol_name>")
@validate_data_source
def update_symbol(data_source: str, symbol_name: str):
    """Changes symbol state according to the request body. Used for persisting a change in symbol's selected status.
    Will throw NotFound if symbol is not found. Will throw BadRequest if the request does not contain a field to be
    patched."""
    service = SymbolService.get_service_by(data_source)

    data = request.json
    if "selected" in data:
        selected = data["selected"]
        symbol = service.update_symbol_selected(symbol_name, selected)
        if not symbol:
            abort(404)
        return {}, 204
    abort(400)
