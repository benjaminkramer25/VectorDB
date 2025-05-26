import pytest, uuid
from fastapi.testclient import TestClient
from app.main import create_app

client = TestClient(create_app())

def test_end_to_end():
    # 1. new library
    resp = client.post("/api/v1/libraries/", json={"name": "demo"})
    lib_id = resp.json()["id"]

    # 2. add chunk
    text = "hello vector world"
    client.post("/api/v1/chunks/", json={"lib_id": lib_id, "text": text})

    # 3. build index
    client.post(f"/api/v1/libraries/{lib_id}/index", json={})

    # 4. query
    emb = [1.0]*26           # dummy 26-dim vec
    res = client.post(f"/api/v1/libraries/{lib_id}/query", json={"embedding": emb})
    assert res.status_code == 200
    assert len(res.json()) > 0
