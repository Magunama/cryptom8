def test_get_all_binance_symbols_when_empty_db(client, clean_dbs):
    resp = client.get("/binance/symbols")

    assert resp.status_code == 200
    assert resp.json == []


def test_get_all_binance_symbols_when_populated_db(client, mock_populated_dbs):
    resp = client.get("/binance/symbols")

    assert resp.status_code == 200
    assert len(resp.json) == 2
    assert resp.json[0]["name"] == "BTCUSDT"


def test_update_binance_symbol(client, mock_populated_dbs):
    patch_data = {"selected": True}
    resp = client.patch("/binance/symbols/BTCUSDT", json=patch_data)
    assert resp.status_code == 204


def test_update_binance_symbol_when_symbol_not_found(client, clean_dbs):
    patch_data = {"selected": True}
    resp = client.patch("/binance/symbols/BTCUSDT", json=patch_data)
    assert resp.status_code == 404


def test_update_binance_symbol_when_wrong_payload(client, clean_dbs):
    patch_data = {"foo": "bar"}
    resp = client.patch("/binance/symbols/BTCUSDT", json=patch_data)
    assert resp.status_code == 400

# todo: yfinance tests
