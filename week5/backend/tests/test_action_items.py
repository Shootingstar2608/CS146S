def test_create_and_complete_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1


def test_filter_completed(client):
    client.post("/action-items/", json={"description": "open item"})
    r2 = client.post("/action-items/", json={"description": "done item"})
    client.put(f"/action-items/{r2.json()['id']}/complete")

    r = client.get("/action-items/", params={"completed": "false"})
    assert r.status_code == 200
    assert all(not i["completed"] for i in r.json())

    r = client.get("/action-items/", params={"completed": "true"})
    assert r.status_code == 200
    assert all(i["completed"] for i in r.json())


def test_filter_all(client):
    client.post("/action-items/", json={"description": "a"})
    client.post("/action-items/", json={"description": "b"})

    r = client.get("/action-items/")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_bulk_complete(client):
    r1 = client.post("/action-items/", json={"description": "bulk 1"})
    r2 = client.post("/action-items/", json={"description": "bulk 2"})
    ids = [r1.json()["id"], r2.json()["id"]]

    r = client.post("/action-items/bulk-complete", json={"ids": ids})
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 2
    assert all(i["completed"] for i in results)


def test_bulk_complete_not_found(client):
    r = client.post("/action-items/bulk-complete", json={"ids": [99999]})
    assert r.status_code == 404


def test_bulk_complete_empty_ids(client):
    r = client.post("/action-items/bulk-complete", json={"ids": []})
    assert r.status_code == 422


def test_complete_not_found(client):
    r = client.put("/action-items/99999/complete")
    assert r.status_code == 404


def test_create_empty_description(client):
    r = client.post("/action-items/", json={"description": ""})
    assert r.status_code == 422
    body = r.json()
    assert body["ok"] is False
