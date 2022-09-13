import datetime


def test_get_binance_bars_by_symbol_when_empty_db(client, clean_dbs):
    resp = client.get("/binance/bars/BTCUSDT")

    assert resp.status_code == 200
    assert resp.json == []


def test_get_binance_bars_by_symbol_when_populated_db(client, populated_dbs):
    resp = client.get("/binance/bars/BTCUSDT")

    assert resp.status_code == 200
    assert "close" in resp.json[0]

    today_str = datetime.date.today().strftime("%a, %d %b %Y %H:%M:%S GMT")
    day = next(filter(lambda b: b["day"] == today_str, resp.json), None)
    assert day is not None


def test_fetch_binance_bars_by_symbol(client, mock_populated_dbs):
    query = {"fetch": True}
    resp = client.get("/binance/bars/BTCUSDT", query_string=query)

    assert resp.status_code == 200
    assert "close" in resp.json[0]

    today_str = datetime.date.today().strftime("%a, %d %b %Y %H:%M:%S GMT")
    day = next(filter(lambda b: b["day"] == today_str, resp.json), None)
    assert day is not None

# todo: yfinance tests
