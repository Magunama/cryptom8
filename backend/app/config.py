class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///../tmp/binance.sqlite"
    SQLALCHEMY_BINDS = {
        "yfinance": "sqlite:///../tmp/yfinance.sqlite"
    }
    CELERY_BROKER_URL = "redis://localhost:6379"
    CELERY_RESULT_BACKEND = "redis://localhost:6379"
    # CELERY_TASK_SERIALIZER = "json"
    # CELERY_RESULT_SERIALIZER = "json"
    # CELERY_ACCEPT_CONTENT = "json"


class TestConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_BINDS = {
        "yfinance": "sqlite://"
    }
