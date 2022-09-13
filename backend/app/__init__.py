from flask import Flask
from flask_cors import CORS

from app.config import BaseConfig
from app.ext import binance_db, yfinance_db
from app.views.bar_view import bar_blueprint
from app.views.main_view import main_blueprint
from app.views.nn_model_view import nn_model_blueprint
from app.views.prediction_view import prediction_blueprint
from app.views.symbol_view import symbol_blueprint


def create_app(config_cls=BaseConfig):
    app = Flask(__name__)
    app.config.from_object(config_cls())

    # configure logging
    # file_handler = logging.FileHandler('app.log')
    # app.logger.addHandler(file_handler)
    # app.logger.setLevel(logging.INFO)
    # app.logger.info("Configured logging!")

    # init db
    binance_db.init_app(app)
    binance_db.create_all(app=app)
    yfinance_db.init_app(app)
    yfinance_db.create_all(app=app)

    app.register_blueprint(main_blueprint)
    app.register_blueprint(bar_blueprint)
    app.register_blueprint(symbol_blueprint)
    app.register_blueprint(nn_model_blueprint)
    app.register_blueprint(prediction_blueprint)

    CORS(app)

    return app
