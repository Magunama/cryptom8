from flask import Blueprint, jsonify
from werkzeug.exceptions import BadRequest, NotFound, MethodNotAllowed, Conflict

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def hello_world():
    return {"hello": "world"}


@main_blueprint.app_errorhandler(BadRequest)
def bad_request(e):
    """APP Error Handler"""
    return jsonify(error=str(e)), 400


@main_blueprint.app_errorhandler(NotFound)
def not_found(e):
    """APP Error Handler"""
    return jsonify(error=str(e)), 404


@main_blueprint.app_errorhandler(MethodNotAllowed)
def method_not_allowed(e):
    """APP Error Handler"""
    return jsonify(error=str(e)), 405


@main_blueprint.app_errorhandler(Conflict)
def conflict(e):
    """APP Error Handler"""
    return jsonify(error=str(e)), 409
