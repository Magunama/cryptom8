def test_landing(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json == {"hello": "world"}


def test_not_found(client):
    resp = client.get("/ohnoanyway")
    assert "error" in resp.json
    assert resp.status_code == 404
