from binance.spot import Spot
from flask_sqlalchemy import SQLAlchemy

# class NoNameMeta(BindMetaMixin, DeclarativeMeta):
#     pass


binance_db = SQLAlchemy()
yfinance_db = SQLAlchemy()

binance_client = Spot(show_limit_usage=True)
# binance_client = Spot(key='R9Q1vfr6y8kAGmffC8wuIVXOyy6E5z35ufPfcIGbPCmVSBaQ9WzUUYOatkHOyqgl',
#                       secret='ALPaJdnQu6t5g1cqPQLHxf96GLsSj0EpUBYINs3S6zzcjOeSayW29Y9c532GskE6', show_limit_usage=True)
